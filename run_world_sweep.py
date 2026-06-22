#!/usr/bin/env python3
"""
run_world_sweep.py — sweep all packs/world/*-source-grounded.json against a live
flash-tier model and write per-pack + aggregate results.

Mirrors run_s3_claude.py's prompt construction (PLACEHOLDERS fill of the pack's
prompt_template) and True/False parsing (first \\b(true|false)\\b match), so
results are comparable to existing S3 runs. ONE round per item (cost control).

Keys are read from the process environment first, then from an optional .env
file (set S3_ENV_FILE, or it defaults to ~/.env.local). Use --provider to pick
explicitly; otherwise:
  - ANTHROPIC_API_KEY set  -> Anthropic claude-haiku-4-5-20251001
  - else                   -> Google Gemini.
      Preferred: Vertex AI (global endpoint) authed via GCP_SERVICE_ACCOUNT_JSON
      (JWT signed with openssl, exchanged for an OAuth token).
      Paid-tier quotas; probes gemini-2.5-flash-lite then gemini-2.5-flash.
      Fallback: AI Studio REST with GOOGLE_API_KEY (free tier: ~15 RPM /
      1000 req/day on flash-lite — only suitable for sampled runs).
  - --provider xai         -> xAI Grok (XAI_API_KEY), default grok-4-1-fast-non-reasoning.

Pass criteria per pack: zero unresolved API errors AND every test yields a
parsed verdict or a documented "blocked" status. Accuracy is NOT a pass
criterion.

Usage:
  python3 run_world_sweep.py            # sampled run if --full not given? No:
                                        # default = FULL run (all items).
  python3 run_world_sweep.py --sample 6 # 6 items/pack (3 true / 3 false,
                                        # deterministic: first 3 of each)
  python3 run_world_sweep.py --only nl,de
  python3 run_world_sweep.py --workers 5 --max-tokens 120

Resumable: results/world/{cc}.json is written per pack as soon as it passes;
on restart, passed packs (same model + same sampling) are skipped.

Never prints API keys.
"""

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
PACK_DIR = os.path.join(ROOT, "packs", "world")
OUT_DIR = os.path.join(ROOT, "results", "world")
ENV_LOCAL = os.environ.get("S3_ENV_FILE") or os.path.expanduser("~/.env.local")
ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"
GEMINI_CANDIDATES = ["gemini-2.5-flash", "gemini-2.0-flash"]
# xAI Grok: the model that actually serves PROD /research answers, so an S3
# baseline on it reflects the live answering model. Matches CLAUDE.md's smart
# default. Override with --xai-model if needed.
XAI_MODEL = "grok-4-1-fast-non-reasoning"

# --- prompt construction: identical to run_s3_claude.py -----------------
PLACEHOLDERS = {
    "[Jurisdiction]": "jurisdiction",
    "[Code name]": "code",
    "[Code]": "code",
    "[Reference type]": "reference",
    "[Reference]": "reference",
    "[Number]": "number",
    "[Subject - Topic]": "topic",
    "[Topic]": "topic",
}
_TF = re.compile(r"\b(true|false)\b", re.IGNORECASE)


def build_prompt(template, item, pack_jurisdiction):
    out = template
    for ph, field in PLACEHOLDERS.items():
        if ph not in out:
            continue
        val = item.get(field)
        if field == "jurisdiction" and not val:
            val = pack_jurisdiction
        val = "" if val is None else str(val)
        if val == "":
            out = out.replace(" " + ph, ph)
        out = out.replace(ph, val)
    return re.sub(r"\s+", " ", out).strip()


def parse_true_false(text):
    if not text:
        return None
    m = _TF.search(text)
    if not m:
        return None
    return m.group(1).lower() == "true"


# --- providers ------------------------------------------------------------
class Blocked(Exception):
    """Provider rejected the content (safety filter etc.)."""


def _env_local(name):
    val = os.environ.get(name)
    if val:
        return val
    try:
        with open(ENV_LOCAL, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith(name + "="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except OSError:
        pass
    return None


def load_google_key():
    key = _env_local("GOOGLE_API_KEY")
    if not key:
        raise SystemExit("GOOGLE_API_KEY not found in env or .env.local")
    return key


class VertexClient:
    """Gemini via Vertex AI global endpoint, service-account OAuth.

    Paid-tier quotas (the AI Studio GOOGLE_API_KEY is free tier: ~15 RPM /
    1000 req/day, which cannot cover a 2,716-item sweep)."""

    def __init__(self, sa_json, model, max_tokens):
        self.sa = json.loads(sa_json)
        self.project = self.sa["project_id"]
        self.model = model
        self.max_tokens = max_tokens
        self.endpoint = "vertex-global"
        self._tok = None
        self._tok_exp = 0
        self._tok_lock = threading.Lock()

    def _token(self):
        with self._tok_lock:
            if self._tok and time.time() < self._tok_exp - 120:
                return self._tok
            b64 = lambda b: base64.urlsafe_b64encode(b).rstrip(b"=")
            now = int(time.time())
            si = (b64(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
                  + b"."
                  + b64(json.dumps({
                      "iss": self.sa["client_email"],
                      "scope": "https://www.googleapis.com/auth/cloud-platform",
                      "aud": "https://oauth2.googleapis.com/token",
                      "iat": now, "exp": now + 3600}).encode()))
            with tempfile.NamedTemporaryFile("w", suffix=".pem",
                                             delete=False) as kf:
                kf.write(self.sa["private_key"])
                kp = kf.name
            try:
                sig = subprocess.run(
                    ["openssl", "dgst", "-sha256", "-sign", kp],
                    input=si, capture_output=True, check=True).stdout
            finally:
                os.unlink(kp)
            jwt = (si + b"." + b64(sig)).decode()
            data = urllib.parse.urlencode({
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": jwt}).encode()
            with urllib.request.urlopen(urllib.request.Request(
                    "https://oauth2.googleapis.com/token", data=data),
                    timeout=30) as r:
                d = json.loads(r.read())
            self._tok = d["access_token"]
            self._tok_exp = now + int(d.get("expires_in", 3600))
            return self._tok

    def call(self, prompt):
        url = (f"https://aiplatform.googleapis.com/v1/projects/{self.project}"
               f"/locations/global/publishers/google/models/"
               f"{self.model}:generateContent")
        gc = {"maxOutputTokens": self.max_tokens, "temperature": 0}
        if self.model.startswith("gemini-2.5"):
            gc["thinkingConfig"] = {"thinkingBudget": 0}
        body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": gc}
        req = urllib.request.Request(
            url, data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json",
                     "Authorization": "Bearer " + self._token()},
            method="POST")
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
        fb = data.get("promptFeedback", {})
        if fb.get("blockReason"):
            raise Blocked(f"promptFeedback.blockReason={fb['blockReason']}")
        cands = data.get("candidates") or []
        if not cands:
            raise Blocked("no candidates returned")
        cand = cands[0]
        fr = cand.get("finishReason")
        if fr in ("SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST", "RECITATION"):
            raise Blocked(f"finishReason={fr}")
        parts = cand.get("content", {}).get("parts", []) or []
        text = "".join(p.get("text", "") for p in parts).strip()
        usage = data.get("usageMetadata", {})
        return text, {
            "in": usage.get("promptTokenCount", 0),
            "out": usage.get("candidatesTokenCount", 0)
            + usage.get("thoughtsTokenCount", 0),
        }


class GeminiClient:
    def __init__(self, key, model, max_tokens):
        self.key = key
        self.model = model
        self.max_tokens = max_tokens
        self.endpoint = "ai-studio"

    def call(self, prompt):
        """Return (text, usage_dict). Raises Blocked / urllib errors."""
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
               f"{self.model}:generateContent?key={self.key}")
        body = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": self.max_tokens,
                "temperature": 0,
            },
        }
        if self.model.startswith("gemini-2.5"):
            body["generationConfig"]["thinkingConfig"] = {"thinkingBudget": 0}
        req = urllib.request.Request(
            url, data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
        fb = data.get("promptFeedback", {})
        if fb.get("blockReason"):
            raise Blocked(f"promptFeedback.blockReason={fb['blockReason']}")
        cands = data.get("candidates") or []
        if not cands:
            raise Blocked("no candidates returned")
        cand = cands[0]
        fr = cand.get("finishReason")
        if fr in ("SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST", "RECITATION"):
            raise Blocked(f"finishReason={fr}")
        parts = cand.get("content", {}).get("parts", []) or []
        text = "".join(p.get("text", "") for p in parts).strip()
        usage = data.get("usageMetadata", {})
        return text, {
            "in": usage.get("promptTokenCount", 0),
            "out": usage.get("candidatesTokenCount", 0)
            + usage.get("thoughtsTokenCount", 0),
        }


class AnthropicClient:
    def __init__(self, key, model, max_tokens):
        self.key = key
        self.model = model
        self.max_tokens = max_tokens
        self.endpoint = "anthropic"

    def call(self, prompt):
        body = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=json.dumps(body).encode(),
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.key,
                "anthropic-version": "2023-06-01",
            }, method="POST")
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
        if data.get("stop_reason") == "refusal":
            raise Blocked("stop_reason=refusal")
        text = "".join(b.get("text", "") for b in data.get("content", [])
                       if b.get("type") == "text").strip()
        u = data.get("usage", {})
        return text, {"in": u.get("input_tokens", 0),
                      "out": u.get("output_tokens", 0)}


class XaiClient:
    """xAI Grok via the OpenAI-compatible Chat Completions endpoint. Honors
    temperature 0 (unlike Fable 5, so S3's 'temp 0' holds) and bills xAI
    credits, not the Anthropic console (sidesteps that spend cap)."""

    def __init__(self, key, model, max_tokens):
        self.key = key
        self.model = model
        self.max_tokens = max_tokens
        self.endpoint = "xai"

    def call(self, prompt):
        body = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": 0,
            "messages": [{"role": "user", "content": prompt}],
        }
        req = urllib.request.Request(
            "https://api.x.ai/v1/chat/completions",
            data=json.dumps(body).encode(),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self.key,
            }, method="POST")
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
        choices = data.get("choices") or []
        if not choices:
            raise Blocked("no choices returned")
        choice = choices[0]
        if choice.get("finish_reason") == "content_filter":
            raise Blocked("finish_reason=content_filter")
        text = (choice.get("message", {}).get("content") or "").strip()
        u = data.get("usage", {})
        return text, {"in": u.get("prompt_tokens", 0),
                      "out": u.get("completion_tokens", 0)}


VERTEX_CANDIDATES = ["gemini-2.5-flash-lite", "gemini-2.5-flash"]


def pick_client(max_tokens, provider="auto", xai_model=XAI_MODEL):
    # Explicit provider override; default "auto" keeps the original cascade
    # (ANTHROPIC_API_KEY -> Vertex -> AI Studio Gemini).
    if provider == "xai":
        xkey = _env_local("XAI_API_KEY")
        if not xkey:
            raise SystemExit(
                "XAI_API_KEY not found in env or .env.local. Add a line "
                "XAI_API_KEY=xai-... to your environment (or the file named by "
                "S3_ENV_FILE / ~/.env.local) to run the sweep on Grok.")
        print(f"Provider: xAI ({xai_model})")
        return XaiClient(xkey, xai_model, max_tokens)
    # "gemini" forces the Gemini cascade by skipping the Anthropic branch.
    akey = None if provider == "gemini" else os.environ.get("ANTHROPIC_API_KEY")
    if akey:
        print(f"Provider: Anthropic ({ANTHROPIC_MODEL})")
        return AnthropicClient(akey, ANTHROPIC_MODEL, max_tokens)
    sa_json = _env_local("GCP_SERVICE_ACCOUNT_JSON")
    if sa_json:
        for model in VERTEX_CANDIDATES:
            client = VertexClient(sa_json, model, max_tokens)
            try:
                text, _ = client.call(
                    "Answer with one word: True or False. 2+2=4.")
                if text:
                    print(f"Provider: Vertex AI global ({model}) — probe ok: "
                          f"{text[:40]!r}")
                    return client
                print(f"Vertex probe {model}: empty text, trying next.")
            except Exception as e:
                msg = str(e)
                print(f"Vertex probe {model}: {msg[:120]}, trying next.")
        print("Vertex unavailable; falling back to AI Studio key (free tier).")
    gkey = load_google_key()
    for model in GEMINI_CANDIDATES:
        client = GeminiClient(gkey, model, max_tokens)
        try:
            text, _ = client.call("Answer with one word: True or False. 2+2=4.")
            if text:
                print(f"Provider: Google Gemini ({model}) — probe ok: "
                      f"{text[:40]!r}")
                return client
            print(f"Probe {model}: empty text, trying next.")
        except Blocked as e:
            print(f"Probe {model}: blocked ({e}), trying next.")
        except urllib.error.HTTPError as e:
            print(f"Probe {model}: HTTP {e.code}, trying next.")
        except Exception as e:
            print(f"Probe {model}: {e}, trying next.")
    raise SystemExit("No working Gemini model found.")


# --- retry wrapper ----------------------------------------------------------
def call_with_retry(client, prompt, max_retries=5):
    """Returns dict {text, usage} or {blocked: reason} or raises after retries."""
    delay = 2.0
    last = None
    for attempt in range(max_retries):
        try:
            text, usage = client.call(prompt)
            return {"text": text, "usage": usage}
        except Blocked as e:
            return {"blocked": str(e)}
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
            if e.code in (400, 401, 403, 404):
                try:
                    detail = e.read().decode()[:300]
                except Exception:
                    detail = ""
                raise RuntimeError(f"HTTP {e.code}: {detail}")
            retry_after = e.headers.get("Retry-After") if e.headers else None
            wait = delay
            if retry_after:
                try:
                    wait = max(float(retry_after), 1.0)
                except ValueError:
                    pass
            time.sleep(min(wait, 60))
            delay = min(delay * 2, 60)
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last = str(e)
            time.sleep(delay)
            delay = min(delay * 2, 60)
    raise RuntimeError(f"exhausted {max_retries} retries: {last}")


# --- sweep ------------------------------------------------------------------
usage_lock = threading.Lock()
TOTAL_USAGE = {"in": 0, "out": 0, "calls": 0}


def run_item(client, template, pack_jur, item):
    prompt = build_prompt(item.get("prompt_template") or template, item, pack_jur)
    t0 = time.time()
    res = call_with_retry(client, prompt)
    latency = int((time.time() - t0) * 1000)
    row = {
        "id": item.get("id"),
        "expected": item.get("expected"),
        "mutation": item.get("mutation"),
        "shape": item.get("shape"),
        "latency_ms": latency,
    }
    if "blocked" in res:
        row.update(verdict="blocked", correct=False, raw=res["blocked"][:200])
        return row
    raw = res["text"]
    parsed = parse_true_false(raw)
    with usage_lock:
        TOTAL_USAGE["in"] += res["usage"]["in"]
        TOTAL_USAGE["out"] += res["usage"]["out"]
        TOTAL_USAGE["calls"] += 1
    row.update(
        verdict=parsed,
        correct=(parsed == item.get("expected")) if parsed is not None else False,
        raw=raw.replace("\n", " ").strip()[:200],
    )
    return row


def select_items(tests, sample_n):
    if not sample_n:
        return tests
    trues = [t for t in tests if t["expected"] is True][: (sample_n + 1) // 2]
    falses = [t for t in tests if t["expected"] is False][: sample_n // 2]
    return trues + falses


def run_pack(client, pack_path, cc, sample_n, workers):
    with open(pack_path, encoding="utf-8") as f:
        pack = json.load(f)
    template = pack["prompt_template"]
    pack_jur = pack.get("jurisdiction", "")
    tests = select_items(pack["tests"], sample_n)

    rows = [None] * len(tests)
    errors = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(run_item, client, template, pack_jur, t): i
                for i, t in enumerate(tests)}
        for fut in as_completed(futs):
            i = futs[fut]
            try:
                rows[i] = fut.result()
            except Exception as e:
                errors.append({"id": tests[i].get("id"), "error": str(e)[:300]})
                rows[i] = {"id": tests[i].get("id"),
                           "expected": tests[i].get("expected"),
                           "mutation": tests[i].get("mutation"),
                           "shape": tests[i].get("shape"),
                           "verdict": "error", "correct": False,
                           "raw": str(e)[:200], "latency_ms": None}

    parsed = [r for r in rows if r["verdict"] in (True, False)]
    blocked = [r for r in rows if r["verdict"] == "blocked"]
    unparsed = [r for r in rows if r["verdict"] is None]
    correct = sum(1 for r in parsed if r["correct"])
    passed = (not errors) and (not unparsed) and \
        (len(parsed) + len(blocked) == len(rows))
    result = {
        "pack": pack.get("name"),
        "country": cc.upper(),
        "jurisdiction": pack_jur,
        "model": client.model,
        "endpoint": client.endpoint,
        "sampled": sample_n or None,
        "items_run": len(rows),
        "items_in_pack": len(pack["tests"]),
        "parsed": len(parsed),
        "blocked": len(blocked),
        "unparsed": len(unparsed),
        "errors": errors,
        "accuracy": round(correct / len(parsed), 4) if parsed else None,
        "correct": correct,
        "parse_rate": round((len(parsed) + len(blocked)) / len(rows), 4),
        "passed": passed,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "results": rows,
    }
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=0,
                    help="Items per pack (balanced true/false). 0 = full pack.")
    ap.add_argument("--full", action="store_true",
                    help="Force full run (same as --sample 0).")
    ap.add_argument("--only", default="",
                    help="Comma-separated country codes to (re-)run.")
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--max-tokens", type=int, default=120)
    ap.add_argument("--force", action="store_true",
                    help="Re-run packs even if already passed.")
    ap.add_argument("--provider", choices=["auto", "xai", "gemini", "anthropic"],
                    default="auto",
                    help="Model provider. auto = ANTHROPIC_API_KEY else Gemini; "
                         "xai = Grok (needs XAI_API_KEY); gemini = force Gemini.")
    ap.add_argument("--xai-model", default=XAI_MODEL,
                    help=f"xAI model when --provider xai (default {XAI_MODEL}).")
    args = ap.parse_args()
    sample_n = 0 if args.full else args.sample

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(PACK_DIR, "index.json"), encoding="utf-8") as f:
        index = json.load(f)
    only = {c.strip().lower() for c in args.only.split(",") if c.strip()}

    client = pick_client(args.max_tokens, provider=args.provider,
                         xai_model=args.xai_model)
    t_start = time.time()
    pack_results = {}
    n_done = 0
    for entry in index:
        cc = entry["country"].lower()
        if only and cc not in only:
            # still load previously-passed result for summary
            pass
        out_path = os.path.join(OUT_DIR, f"{cc}.json")
        prior = None
        if os.path.exists(out_path):
            try:
                with open(out_path, encoding="utf-8") as f:
                    prior = json.load(f)
            except Exception:
                prior = None
        skip = (prior and prior.get("passed")
                and prior.get("model") == client.model
                and prior.get("sampled") == (sample_n or None)
                and not args.force
                and (not only or cc not in only))
        if only and cc not in only:
            if prior:
                pack_results[cc] = prior
            continue
        if skip:
            pack_results[cc] = prior
            continue
        pack_path = os.path.join(PACK_DIR, entry["file"])
        res = run_pack(client, pack_path, cc, sample_n, args.workers)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, ensure_ascii=False)
        pack_results[cc] = res
        n_done += 1
        flag = "PASS" if res["passed"] else "FAIL"
        acc = f"{res['accuracy']:.0%}" if res["accuracy"] is not None else "n/a"
        print(f"[{flag}] {cc.upper():3} {entry['countryName']:<28} "
              f"acc={acc:>4} parsed={res['parsed']}/{res['items_run']} "
              f"blocked={res['blocked']} ({n_done} run, "
              f"{time.time()-t_start:.0f}s)")
        sys.stdout.flush()

    # --- aggregate summary ---
    all_rows = []
    for cc, res in pack_results.items():
        for r in res["results"]:
            r2 = dict(r)
            r2["country"] = cc.upper()
            all_rows.append(r2)
    judged = [r for r in all_rows if r["verdict"] in (True, False)]
    summary = {
        "model": client.model,
        "endpoint": client.endpoint,
        "sampled": sample_n or None,
        "packs": len(pack_results),
        "packs_passed": sum(1 for r in pack_results.values() if r["passed"]),
        "items": len(all_rows),
        "parsed": len(judged),
        "blocked": sum(1 for r in all_rows if r["verdict"] == "blocked"),
        "accuracy": round(sum(r["correct"] for r in judged) / len(judged), 4)
        if judged else None,
        "by_expected": {},
        "by_mutation": {},
        "by_shape": {},
        "verdict_distribution": dict(Counter(
            str(r["verdict"]) for r in all_rows)),
        "usage": dict(TOTAL_USAGE),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "wall_seconds": round(time.time() - t_start, 1),
    }
    for key, field in (("by_expected", "expected"), ("by_mutation", "mutation"),
                       ("by_shape", "shape")):
        groups = {}
        for r in judged:
            g = str(r.get(field))
            groups.setdefault(g, []).append(r)
        summary[key] = {
            g: {"n": len(rs),
                "accuracy": round(sum(x["correct"] for x in rs) / len(rs), 4)}
            for g, rs in sorted(groups.items())}
    summary["per_pack"] = {
        cc.upper(): {"accuracy": res["accuracy"], "passed": res["passed"],
                     "items": res["items_run"], "blocked": res["blocked"]}
        for cc, res in sorted(pack_results.items())}
    with open(os.path.join(OUT_DIR, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1, ensure_ascii=False)

    print(f"\nPacks passed: {summary['packs_passed']}/{summary['packs']}")
    print(f"Aggregate accuracy: {summary['accuracy']}")
    print(f"Usage: {TOTAL_USAGE}")
    print(f"Wrote {os.path.join(OUT_DIR, 'summary.json')}")


if __name__ == "__main__":
    main()
