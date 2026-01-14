import re
from difflib import SequenceMatcher
from sentence_transformers import SentenceTransformer, util
import torch
import re

# Normalize citation punctuation / formatting
UNICODE_DASHES = "\u2012\u2013\u2014\u2015\u2212"   
def normalize_citation_text(s: str) -> str:
    """
    Normalize Unicode dash variants + punctuation for consistent citation matching.
    - Force ASCII hyphens
    - Lowercase
    - Collapse whitespace
    """
    if not s:
        return ""

    for d in UNICODE_DASHES:
        s = s.replace(d, "-")

    # Remove U.S.C. formatting variations -> consistently: "usc"
    s = re.sub(r"\bU\.?\s*S\.?\s*C\.?\b", "usc", s, flags=re.IGNORECASE)
    s = re.sub(r"\bC\.?\s*F\.?\s*R\.?\b", "cfr", s, flags=re.IGNORECASE)
    s = re.sub(r"\bPub\.?\s*L\.?\b", "publ", s, flags=re.IGNORECASE)
    s = re.sub(r"§", "", s)

    # Lower + collapse spaces
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


# Load a legal-specific model, with fallback | users should be able to choose their own models
def load_model():
    try:
        return SentenceTransformer("nlpaueb/legal-bert-base-uncased")
    except Exception as e:
        print(f"[warn] Could not load legal model: {e}. Falling back to 'paraphrase-mpnet-base-v2'.")
        return SentenceTransformer("paraphrase-mpnet-base-v2")

model = load_model()

def extract_citations(text: str):
    """
    Roughly extract legal citations from US, UK, and EU laws.
    Returns a list of unique normalized matches.
    """
    if not text:
        return []

    # regex patterns 
    patterns = [
        # --- U.S. citations ---
        r"\b\d+\s*U\.?S\.?C\.?\s*§?\s*\d+[A-Za-z\-]*",        
        r"\bPub\.?\s*L\.?\s*\d+[–\-]?\d*\b",                  
        r"\b\d+\s*Stat\.?\s*\d+\b",                           
        r"\b\d+\s*C\.?F\.?R\.?\s*§?\s*\d+[A-Za-z\-]*",        

        # --- U.K. citations ---
        r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+Act\s+\d{4}\b",  
        r"\b\d{4}\s*Act\b",                                   
        r"\bS\.I\.\s*\d{4}/\d+\b",                            
        r"\[\d{4}\]\s*[A-Z]{2,6}\s*\d+\b",                    
        r"\b[A-Z][a-zA-Z]+\s+v\.?\s+[A-Z][a-zA-Z]+\b",        

        # --- EU citations ---
        r"\bRegulation\s*\(?(?:EU|EC|EEC)\)?\s*\d{4}/\d+\b",  
        r"\bDirective\s*\d{4}/\d+/(?:EU|EC|EEC)\b",           
        r"\bDecision\s*\(?(?:EU|EC|EEC)\)?\s*\d{4}/\d+\b",    
        r"\bArticle\s*\d+\s*(?:TFEU|TEU|EC)\b",               
        r"\bTreaty\s+on\s+(?:the\s+Functioning\s+of\s+the\s+EU|European\s+Union)\b",
        r"\bCharter\s+of\s+Fundamental\s+Rights\s+of\s+the\s+EU\b",
    ]

    citations = []
    for pat in patterns:
        citations.extend(re.findall(pat, text))
    normalized = {normalize_citation_text(c) for c in citations}
    return list(normalized)


def fuzzy_overlap(list1, list2):
    """Compute average best-match ratio between citation lists."""
    if not list1 or not list2:
        return 0.0
    total = 0.0
    for a in list1:
        best = max(SequenceMatcher(None, a, b).ratio() for b in list2)
        total += best
    return total / len(list1)


def semantic_similarity(a, b, cit_score=None):
    """
    Cosine similarity via transformer embeddings, scaled by citation match.
    """
    emb1 = model.encode(a, convert_to_tensor=True)
    emb2 = model.encode(b, convert_to_tensor=True)
    base = float(util.cos_sim(emb1, emb2).item())

    # If citation overlap is poor, scale semantic similarity down
    if cit_score is not None:
        if cit_score < 0.3:
            base *= 0.5       # strong penalty for mismatch
        elif cit_score < 0.6:
            base *= 0.75      # mild penalty for partial match

    return base


def citation_similarity(list1, list2):
    """Compute overlap, rewarding exact or near-number matches more heavily."""
    if not list1 or not list2:
        return 0.0
    
    list1 = [normalize_citation_text(x) for x in list1]
    list2 = [normalize_citation_text(x) for x in list2]

    def normalize(s):
        # extract numbers and letters for comparison (Pub. L. 117–347 → 117347)
        return re.sub(r'\D', '', s)

    total = 0
    for a in list1:
        a_norm = normalize(a)
        best = 0
        for b in list2:
            b_norm = normalize(b)
            # bonus if numeric content matches
            if a_norm and a_norm == b_norm:
                best = 1.0
            else:
                best = max(best, SequenceMatcher(None, a, b).ratio() * 0.7)
        total += best
    return total / len(list1)


def remove_citations(text):
    # Mask citation-like strings before semantic encoding
    text = re.sub(r"\b(Pub\.?\s*L\.?|U\.?S\.?C\.?|Regulation|Directive|Article)\b.*?\b(\d{2,4}|§\d+)\b", "[LAW]", text)
    return text

def question_answer_similarity(question, answer):
    """
    Compute semantic similarity between a question and an answer.
    Used to check how well each answer responds to the question itself.
    """
    if not question or not answer:
        return 0.0
    emb_q = model.encode(question, convert_to_tensor=True)
    emb_a = model.encode(answer, convert_to_tensor=True)
    return float(util.cos_sim(emb_q, emb_a).item())


def _digits(s: str) -> str:
    return re.sub(r'\D', '', s or '')

def _has_exact_numeric_overlap(list1, list2):
    if not list1 or not list2:
        return False
    nums1 = {_digits(normalize_citation_text(x)) for x in list1 if _digits(x)}
    nums2 = {_digits(normalize_citation_text(x)) for x in list2 if _digits(x)}

    return bool(nums1 & nums2)




def legal_similarity(
    gold_answer,
    llm_answer,
    gold_binary=None,
    llm_binary=None,
    weights=None,
    question=None):
    """
    Updated to implement Rule B:

    If truth_alignment == 1.0:
        - If citation is close -> >= 0.85
        - If citation is wrong -> < 0.85

    Special passes:
        - Formatting-only citation differences treated as matching
    """

    # TODO: default weights, make it changeable for users
    if weights is None:
        weights = {"semantic": 0.3, "citation": 0.4, "truth": 0.3}

    gold_answer = gold_answer or ""
    llm_answer  = llm_answer or ""
    question    = question or ""

    gold_cit = extract_citations(gold_answer)
    llm_cit  = extract_citations(llm_answer)
    q_cit    = extract_citations(question)

    # Citation similarity
    cit_gold_llm = citation_similarity(gold_cit, llm_cit)
    cit_q_llm    = citation_similarity(q_cit,  llm_cit)
    cit_q_gold   = citation_similarity(q_cit,  gold_cit)

    # Citation score selection
    if llm_binary == 0:
        cit_score = cit_gold_llm
    else:
        cit_score = max(
            cit_gold_llm,
            cit_q_llm * 0.9,
            (cit_q_llm + cit_q_gold) / 2
        )

    sem_score = semantic_similarity(
        remove_citations(gold_answer),
        remove_citations(llm_answer),
        cit_score
    )

    truth_score = float(gold_binary == llm_binary) if (
        gold_binary is not None and llm_binary is not None
    ) else 0.0

    q_gold_score = question_answer_similarity(question, gold_answer) if question else None
    q_llm_score  = question_answer_similarity(question, llm_answer)  if question else None
    q_ratio = (q_llm_score / q_gold_score) if (q_gold_score and q_gold_score > 0) else None

    q_contrib = 0.0
    if llm_binary == 0 and q_ratio is not None:
        q_contrib = max(min((q_ratio - 1.0) * 0.15, 0.05), -0.05)

    if llm_binary == 0:
        contextual_semantic = sem_score
    else:
        contextual_semantic = 0.6 * sem_score + 0.4 * (q_llm_score or 0)

    provisional = (
        weights["semantic"] * contextual_semantic +
        weights["citation"] * cit_score +
        weights["truth"]    * truth_score +
        q_contrib
    )

    final = provisional
    penalty_val = 0.0
    bonus_val   = 0.0

    def _digits_only(s: str) -> str:
        return re.sub(r'\D', '', normalize_citation_text(s))

    def _has_numeric_overlap(list1, list2):
        if not list1 or not list2:
            return False
        n1 = {_digits_only(x) for x in list1}
        n2 = {_digits_only(x) for x in list2}
        return bool(n1 & n2)

    exact_gold_overlap = _has_numeric_overlap(gold_cit, llm_cit)
    exact_q_overlap    = _has_numeric_overlap(q_cit,  llm_cit)

    # Title/section conflict
    def _title_section(x):
        m = re.findall(r"(\d+)\s*usc\.?\s*(\d+)", normalize_citation_text(x))
        return tuple(map(int, m[0])) if m else None

    def _title_conflict(gc, lc):
        g = [_title_section(c) for c in gc]
        l = [_title_section(c) for c in lc]
        g = [x for x in g if x]
        l = [x for x in l if x]
        for gx in g:
            for lx in l:
                if gx[0] == lx[0] and gx[1] != lx[1]:
                    return True
        return False

    title_conflict = _title_conflict(gold_cit, llm_cit)

    if truth_score == 1.0:

        # HIGH semantic -> presume “correct reasoning”
        strong_reasoning = sem_score >= 0.90

        # correct reasoning + citation close -> PASS
        if strong_reasoning and (cit_score >= 0.45 or exact_gold_overlap or exact_q_overlap):
            final = max(final, 0.85)

        # correct reasoning + extra citations -> PASS
        if strong_reasoning and not title_conflict:
            final = max(final, 0.85)

        # citation WRONG -> FAIL
        if title_conflict or cit_score < 0.45:
            final = min(final, 0.60)

    final = max(0.0, min(1.0, final))

    return {
        "final_score": final,
        "semantic_similarity": sem_score,
        "citation_similarity": cit_score,
        "truth_alignment": truth_score,
        "penalty": round(penalty_val, 4),
        "bonus": round(bonus_val, 4),
        "gold_citations": gold_cit,
        "llm_citations": llm_cit,
        "question_citations": q_cit,
        "q_gold_score": q_gold_score,
        "q_llm_score": q_llm_score,
        "q_ratio": q_ratio,
        "cit_gold_llm": cit_gold_llm,
        "cit_q_llm": cit_q_llm,
        "cit_q_gold": cit_q_gold,
        "exact_gold_overlap": exact_gold_overlap,
        "exact_q_overlap": exact_q_overlap,
        "title_conflict": title_conflict,
    }
