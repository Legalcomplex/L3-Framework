# How the L3-Framework Calculates Scores 🧮

> A simple guide to understanding how this Legal LLM Evaluation Framework grades AI responses

Imagine you're a teacher grading a student's law exam. You have the **correct answer** (gold answer) and the **student's answer** (LLM answer). This framework is like a super-smart grading system that checks multiple things.

---

## 📋 Table of Contents

- [Step 1: The True/False Check (Truth Gate)](#step-1-the-truefalse-check-truth-gate)
- [Step 2: Three Main Scores](#step-2-three-main-scores-when-both-say-false)
- [Step 3: The Final Formula](#step-3-the-final-formula)
- [Step 4: Bonus Rules & Penalties](#step-4-bonus-rules--penalties)
- [Step 5: Pass or Fail?](#step-5-pass-or-fail)
- [Real Examples](#real-examples)
- [Summary](#summary-think-of-it-like-a-report-card-)

---

## Step 1: The True/False Check (Truth Gate)

Every answer starts with **True** or **False**. This is the first and most important check:

| Gold Answer | LLM Answer | What Happens |
|:-----------:|:----------:|:-------------|
| ✅ True | ✅ True | **PASS!** Score = 1.0 (They agreed it's true) |
| ❌ False | ❌ False | 🔍 **Keep checking...** (Need to verify the explanation) |
| ✅ True | ❌ False | **FAIL!** Score = 0.0 (They disagree) |
| ❌ False | ✅ True | **FAIL!** Score = 0.0 (They disagree) |

### Why does this matter?

If you ask *"Is the sky blue?"* and one says True and one says False, they clearly disagree - no need to check further!

But if **BOTH** say False (like *"Is it legal to steal?"* - both correctly say False), we need to check if their **explanations** match.

---

## Step 2: Three Main Scores (When Both Say False)

When both answers are False, the system calculates three things:

### 🧠 1. Semantic Similarity (30% of score)

**"Do the explanations mean the same thing?"**

This uses AI (a legal-trained model called [Legal-BERT](https://huggingface.co/nlpaueb/legal-bert-base-uncased)) to understand the *meaning* of both answers. It's like asking: *"Are they saying the same thing, even if they use different words?"*

> **Example:**
> - **Gold:** "This violates the Fourth Amendment protection against searches"
> - **LLM:** "The Fourth Amendment prohibits this type of search"
> - **Result:** High similarity! ✅ They mean the same thing.

---

### 📚 2. Citation Similarity (40% of score)

**"Did they cite the same laws?"**

Legal answers need to reference specific laws. The system extracts citations like:

```
42 U.S.C. § 1983      (a US federal law)
29 U.S.C. § 621       (another US law)
Clean Air Act         (environmental law)
Regulation (EU) 2016/679   (EU law - GDPR)
```

Then it checks: Did the LLM cite the **same laws** as the gold answer?

> **Example:**
> - **Gold cites:** `42 U.S.C. § 12112`
> - **LLM cites:** `42 U.S.C. § 12112`
> - **Result:** Perfect match! ✅

---

### ⚖️ 3. Truth Alignment (30% of score)

**"Did they give the same True/False answer?"**

| Scenario | Score |
|:---------|:-----:|
| Both said True | 1.0 |
| Both said False | 1.0 |
| They disagree | 0.0 |

---

## Step 3: The Final Formula

```
Final Score = (0.3 × Semantic) + (0.4 × Citation) + (0.3 × Truth)
```

### 📊 Example Calculation

| Component | Value |
|:----------|:-----:|
| Semantic Similarity | 0.85 |
| Citation Similarity | 0.90 |
| Truth Alignment | 1.0 (both said False) |

```
Final = (0.3 × 0.85) + (0.4 × 0.90) + (0.3 × 1.0)
      = 0.255 + 0.36 + 0.30
      = 0.915 ✅ PASS!
```

---

## Step 4: Bonus Rules & Penalties

### 🎁 Bonuses (Score goes UP)

| Condition | Effect |
|:----------|:-------|
| Strong reasoning (semantic > 90%) AND correct citations | Bump score to at least 0.85 |
| Strong reasoning AND no title conflicts | Bump score to at least 0.85 |

### 🚫 Penalties (Score goes DOWN)

| Condition | Effect |
|:----------|:-------|
| **Title Conflict** - Same law book, wrong section (e.g., gold says `§ 1983` but LLM says `§ 1985`) | Score capped at 0.60 |
| **Parroting** - LLM just repeats the question instead of answering | Score reduced |
| **Poor citations** - Citation score < 0.45 | Score capped at 0.60 |

---

## Step 5: Pass or Fail?

```
┌─────────────────────────────────────┐
│         Threshold: 0.85             │
├─────────────────────────────────────┤
│  Score ≥ 0.85  →  ✅ PASS           │
│  Score < 0.85  →  ❌ FAIL           │
└─────────────────────────────────────┘
```

---

## Real Examples

### Example 1: Both Say True (Quick Pass)

**Question:** *"Does the ADA require employers to provide accommodations?"*

| Answer | Response |
|:-------|:---------|
| **Gold** | "True. Under 42 U.S.C. § 12112, the ADA requires reasonable accommodations..." |
| **LLM** | "True. Yes, the ADA under 42 U.S.C. § 12112 mandates accommodations..." |

| Check | Result |
|:------|:-------|
| Truth Gate | Both True → **Score = 1.0, PASS!** ✅ |

> The system stops here because they both said True - no need to check further!

---

### Example 2: Both Say False (Full Analysis)

**Question:** *"Is warrantless home search legal?"*

| Answer | Response |
|:-------|:---------|
| **Gold** | "False. The Fourth Amendment prohibits this under 42 U.S.C. § 1983..." |
| **LLM** | "False. The Fourth Amendment requires warrants per Payton v. New York..." |

| Check | Score | Notes |
|:------|:-----:|:------|
| Truth Gate | — | Both False → Keep checking... |
| Semantic | ~0.88 | Similar meaning ✅ |
| Citation | ~0.70 | Different citations but related |
| Truth | 1.0 | Both said False ✅ |
| **Final** | **~0.85** | **PASS!** ✅ |

---

## Summary: Think of it Like a Report Card 📝

| Category | Weight | What It Checks |
|:---------|:------:|:---------------|
| 🎯 **Truth Alignment** | 30% | Did they give the same True/False answer? |
| 🧠 **Semantic Similarity** | 30% | Do the explanations mean the same thing? |
| 📚 **Citation Similarity** | 40% | Did they cite the same laws? |

---

<div align="center">

### 🏆 Pass = 85% or higher!

</div>

---

## Quick Reference: Supported Citation Formats

The framework can extract and compare citations from multiple jurisdictions:

| Jurisdiction | Example Citations |
|:-------------|:------------------|
| 🇺🇸 **US Federal** | `42 U.S.C. § 1983`, `29 U.S.C. § 621`, `Pub. L. 117-347` |
| 🇺🇸 **US Regulations** | `40 C.F.R. § 122.1` |
| 🇬🇧 **UK Acts** | `Human Rights Act 1998`, `S.I. 2024/123` |
| 🇬🇧 **UK Cases** | `Smith v. Jones`, `[2024] UKSC 1` |
| 🇪🇺 **EU Law** | `Regulation (EU) 2016/679`, `Directive 2000/31/EC`, `Article 8 TFEU` |

---

## Learn More

- 📖 [Main README](./README.md) - Full documentation
- 🎮 [Streamlit App](./app.py) - Interactive evaluation interface
- 📊 [Sample Data](./sample_data.csv) - Example legal questions

---

<div align="center">

**Built with ❤️ for Legal AI Evaluation**

[Report Issue](https://github.com/Legalcomplex/L3-Framework/issues) · [Contribute](https://github.com/Legalcomplex/L3-Framework/pulls)

</div>
