# Resume Tailor Reference Materials

Archive of the original ChatGPT custom GPT instruction sets and examples from the 2024 job search.

**Source**: `OneDrive/2024 Job Search/cGPT/`
**Copied**: 2026-01-27

## Purpose

These files document the original approach to resume tailoring using ChatGPT custom GPTs. They're preserved as reference for:
- Understanding the design decisions
- Extracting useful patterns for future improvements
- Example lists that can inform Claude's reasoning

## Folder Structure

```
reference/
├── kb-instructions/          # Knowledge base instruction sets
│   ├── KB 1 - Anti_Hallucination*     # Core anti-hallucination rules
│   ├── KB 2 - Keyword_Integration*    # Keyword prioritization
│   ├── KB 3A - Character Limit*       # Character constraints
│   ├── KB 3B - Minimal Changes*       # Edit principles
│   ├── KB 3C - Multi-Sentence*        # Flow handling
│   ├── KB 4 - Verification*           # Verification examples
│   └── KB Simplification Rules*       # Core component rules
│
├── example-lists/            # Few-shot learning examples
│   ├── Bullet Tailoring Positive*     # Good edit examples
│   ├── Bullet Tailoring Negative*     # Bad edit examples (what to avoid)
│   └── Bullet Tailoring GRAY*         # Edge cases / judgment calls
│
├── industry-terms/           # Keyword vocabularies
│   ├── cGPT Bullet Point Industry Terms*
│   └── cGPT Keyword_Industry_Concepts*
│
├── jd-examples/              # 10 example JD keyword extractions
│   └── cGPT Keyword Extraction JD Example [1-10]*
│
├── cGPT All Bullets.*        # Full bullet corpus (original)
├── cGPT Resume Bullets MASTER.*
├── Resume_Baseline.*         # Original baseline resume
└── chatgpt-memory-context.txt  # Session priming context
```

## Key Insights from Original System

**What worked well:**
- Anti-hallucination focus (KB 1)
- Example-based learning (positive/negative/gray lists)
- Character limit constraints
- Verification log concept

**What the new skill improves:**
- Code-enforced validation (not just instructions)
- Profile system for multiple users
- Deterministic keyword extraction
- Programmatic character counting

## How to Use These

**For improving the skill:**
- Read the example lists for patterns
- Reference KB files for edge cases
- Use industry terms to expand keyword detection

**For other users:**
- Example lists show what good/bad edits look like
- KB files explain the reasoning behind rules
- JD examples show expected extraction outputs
