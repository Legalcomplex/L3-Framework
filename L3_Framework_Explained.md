# How the L3-Framework Calculates Scores

Imagine you're a teacher grading a student's law exam. You have the **correct answer** (gold answer) and the **student's answer** (LLM answer). This framework is like a super-smart grading system that checks multiple things.

---

## Step 1: The True/False Check (Truth Gate)

Every answer starts with **True** or **False**. This is the first and most important check:

| Gold Answer | LLM Answer | What Happens |
|-------------|------------|--------------|
| True | True | **PASS! Score = 1.0** (They agreed it's true) |
| False | False | **Keep checking...** (Need to verify the explanation) |
| True | False | **FAIL! Score = 0.0** (They disagree) |
| False | True | **FAIL! Score = 0.0** (They disagree) |

**Why?** If you ask "Is the sky blue?" and one says True and one says False, they clearly disagree - no need to check further!

But if BOTH say False (like "Is it legal to steal?" - both correctly say False), we need to check if their **explanations** match.

---

## Step 2: Three Main Scores (When Both Say False)

When both answers are False, the system calculates three things:

### 1. Semantic Similarity (30% of score)
**"Do the explanations mean the same thing?"**

This uses AI (a legal-trained model called Legal-BERT) to understand the *meaning* of both answers. It's like asking: "Are they saying the same thing, even if they use different words?"

**Example:**
- Gold: "This violates the Fourth Amendment protection against searches"
- LLM: "The Fourth Amendment prohibits this type of search"
- Result: **High similarity!** They mean the same thing.

### 2. Citation Similarity (40% of score)
**"Did they cite the same laws?"**

Legal answers need to reference specific laws. The system extracts citations like:
- `42 U.S.C. § 1983` (a US law)
- `29 U.S.C. § 621` (another US law)
- `Clean Air Act`

Then it checks: Did the LLM cite the **same laws** as the gold answer?

**Example:**
- Gold cites: `42 U.S.C. § 12112`
- LLM cites: `42 U.S.C. § 12112`
- Result: **Perfect match!**

### 3. Truth Alignment (30% of score)
**"Did they give the same True/False answer?"**

- If both said True → 1.0
- If both said False → 1.0
- If they disagree → 0.0

---

## Step 3: The Final Formula

```
Final Score = (0.3 × Semantic) + (0.4 × Citation) + (0.3 × Truth)
```

**Example:**
- Semantic Similarity: 0.85
- Citation Similarity: 0.90
- Truth Alignment: 1.0 (both said False)

```
Final = (0.3 × 0.85) + (0.4 × 0.90) + (0.3 × 1.0)
      = 0.255 + 0.36 + 0.30
      = 0.915 → PASS!
```

---

## Step 4: Bonus Rules & Penalties

### Bonuses (Score goes UP)
- If the LLM has **strong reasoning** (semantic > 90%) AND cites correctly → bump score to at least 0.85

### Penalties (Score goes DOWN)
- **Title Conflict**: If gold says `42 U.S.C. § 1983` but LLM says `42 U.S.C. § 1985` (same law book, wrong section) → penalty!
- **Parroting the Question**: If the LLM just repeats the question instead of answering → penalty!

---

## Step 5: Pass or Fail?

**Threshold: 0.85**

- Score ≥ 0.85 → **PASS**
- Score < 0.85 → **FAIL**

---

## Real Example

**Question:** "Does the ADA require employers to provide accommodations?"

**Gold Answer:** "True. Under 42 U.S.C. § 12112, the ADA requires reasonable accommodations..."

**LLM Answer:** "True. Yes, the ADA under 42 U.S.C. § 12112 mandates accommodations..."

| Check | Result |
|-------|--------|
| Truth Gate | Both True → **Score = 1.0, PASS!** |

The system stops here because they both said True - no need to check further!

---

**Another Example:**

**Question:** "Is warrantless home search legal?"

**Gold:** "False. The Fourth Amendment prohibits this under 42 U.S.C. § 1983..."

**LLM:** "False. The Fourth Amendment requires warrants per Payton v. New York..."

| Check | Result |
|-------|--------|
| Truth Gate | Both False → Keep checking... |
| Semantic | ~0.88 (similar meaning) |
| Citation | ~0.70 (different citations but related) |
| Truth | 1.0 (both False) |
| **Final** | ~0.85 → **PASS!** |

---

## Summary: Think of it Like a Report Card

| Category | Weight | What It Checks |
|----------|--------|----------------|
| Did they agree? (Truth) | 30% | True/False match |
| Same meaning? (Semantic) | 30% | AI understands both |
| Same laws cited? (Citation) | 40% | Legal references match |

**Pass = 85% or higher!**
