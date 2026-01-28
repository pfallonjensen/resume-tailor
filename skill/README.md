# Resume Tailor - Technical Documentation

How the skill code works, for anyone who wants to modify or understand it.



## Files

| File | Purpose |
|------|---------|
| `resume-tailor.py` | Python script for deterministic processing |
| `skill.md` | Claude Code skill definition (workflow instructions) |

## Python Script Architecture

### CLI Commands

```bash
# Preprocess: Extract keywords and analyze gaps
python3 resume-tailor.py preprocess \
  --jd <jd_path> \
  --resume <resume_path> \
  --corpus <corpus_path> \
  --output <output_json>

# Validate: Check proposed edits against rules
python3 resume-tailor.py validate \
  --edits <edits_json> \
  --corpus <corpus_path> \
  --output <output_json>
```

### Core Functions

#### `extract_keywords(jd_text) -> list[dict]`
Extracts and categorizes keywords from job description text.

```python
# Returns:
[
    {
        "keyword": "machine learning",
        "category": "ai_ml",
        "importance": "PRIMARY",
        "context": "3+ years of machine learning experience"
    },
    ...
]
```

**Logic:**
1. Normalize text (lowercase, strip special chars)
2. Match against `KEYWORD_PATTERNS` dictionary
3. Extract context (surrounding sentence)
4. Categorize importance based on position and frequency

#### `parse_resume(resume_text) -> list[dict]`
Parses resume into structured bullets with metadata.

```python
# Returns:
[
    {
        "id": "company_role_1",
        "company": "LogMeIn",
        "role": "Staff PM",
        "text": "Drove $59M in revenue...",
        "char_count": 94,
        "metrics": ["$59M", "8"]
    },
    ...
]
```

**Logic:**
1. Split by section headers (EXPERIENCE, EDUCATION, etc.)
2. Identify company/role headers
3. Extract bullet points
4. Count characters and extract metrics (numbers, percentages, dollar amounts)

#### `compute_gap_analysis(keywords, resume) -> dict`
Compares JD keywords against resume to find gaps.

```python
# Returns:
{
    "total_keywords": 28,
    "explicit_matches": 24,
    "missing": [
        {
            "keyword": "agentic",
            "category": "ai_ml",
            "importance": "PRIMARY",
            "closest_match": "autonomous",  # if any partial match
            "match_score": 0.0
        },
        ...
    ],
    "match_details": [...]
}
```

**Logic:**
1. For each keyword, search resume text (exact match, case-insensitive)
2. Track which section matched (summary, experience, skills)
3. Calculate overall coverage percentage
4. Sort missing by importance

#### `validate_edit(original, proposed, corpus) -> dict`
Validates a proposed bullet edit against anti-hallucination rules.

```python
# Returns:
{
    "valid": false,
    "warnings": ["CHAR_LIMIT_EXCEEDED", "HALLUCINATION_RISK"],
    "details": {
        "char_count": 156,
        "char_limit": "AWKWARD_ZONE",
        "missing_words": ["lifecycle"],
        "metrics_check": {
            "original": ["$59M", "8"],
            "proposed": ["$59M", "8"],
            "preserved": true
        }
    }
}
```

**Validation Rules:**

| Rule | Check | Failure Mode |
|------|-------|--------------|
| Character limits | 80-116 (one-line), 175-235 (two-line) | `CHAR_LIMIT_EXCEEDED` |
| Metrics preserved | All numbers from original exist in proposed | `METRICS_LOST` |
| No hallucination | Every word exists in corpus | `HALLUCINATION_RISK` |
| No new proper nouns | Company/tech names must be in corpus | `NEW_PROPER_NOUN` |

### Key Data Structures

#### `KEYWORD_PATTERNS`
Dictionary mapping categories to keyword lists:

```python
KEYWORD_PATTERNS = {
    'ai_ml': [
        'machine learning', 'ML', 'artificial intelligence', 'AI',
        'deep learning', 'neural network', 'LLM', 'NLP', 'computer vision',
        'agentic', 'autonomous', 'generative AI', ...
    ],
    'leadership': [
        'led', 'managed', 'built', 'scaled', 'mentored', 'cross-functional',
        'high-performing', 'director', 'VP', 'executive', ...
    ],
    'outcome': [
        'revenue', 'ARR', 'growth', 'retention', 'engagement',
        'conversion', 'efficiency', 'ROI', ...
    ],
    'skill': [
        'strategy', 'roadmap', 'prioritization', 'stakeholder',
        'data-driven', 'experimentation', 'platform', 'portfolio', ...
    ],
    'domain': [
        # Industry-specific terms
    ]
}
```

#### Character Limit Constants

```python
CHAR_LIMITS = {
    'ONE_LINE': (80, 116),      # Ideal
    'AWKWARD': (117, 174),      # Adjust up or down
    'TWO_LINE': (175, 235),     # Acceptable
    'OVER': (236, float('inf')) # Must trim
}
```

## Skill Definition (skill.md)

The skill.md file tells Claude how to orchestrate the workflow.

### Key Sections

1. **File Locations** - Where to find corpus, resume, JDs
2. **Profile System** - How to load user preferences
3. **Workflow** - 6-step process from preprocessing to final output
4. **Anti-Hallucination Rules** - Critical checklist Claude must follow
5. **Output Formats** - JSON structures for proposed edits

### Claude's Role vs Python's Role

| Task | Handled By | Why |
|------|-----------|-----|
| Keyword extraction | Python | Deterministic, reproducible |
| Gap analysis | Python | Exact matching, no judgment |
| Character counting | Python | Must be exact |
| Propose edits | **Claude** | Requires reasoning about context |
| Apply tone preferences | **Claude** | Requires understanding nuance |
| Validation | Python | Code-enforced rules |
| User interaction | **Claude** | Natural language understanding |

### Anti-Hallucination Enforcement

The skill.md includes this critical checklist:

```markdown
**BEFORE proposing any edit, verify:**
- [ ] Every new word exists somewhere in `bullet-corpus.txt`
- [ ] All metrics from original bullet are preserved
- [ ] No new company names, technologies, or achievements invented
- [ ] Character count is within limits

**If you cannot find corpus support for adding a keyword:**
- Mark it as UNSUPPORTED
- Explain why
- Do NOT propose an edit
```

## Extending the Code

### Adding a New Keyword Category

1. Add to `KEYWORD_PATTERNS`:
```python
'new_category': ['term1', 'term2', ...]
```

2. Update `categorize_importance()` if the category should affect PRIMARY/SECONDARY weighting.

### Adding a New Validation Rule

1. Add check in `validate_edit()`:
```python
# Check for new rule
if some_condition(proposed):
    warnings.append('NEW_RULE_VIOLATION')
```

2. Document the rule in skill.md under Anti-Hallucination Rules.

### Supporting a New Resume Format

1. Add parsing logic in `parse_resume()`:
```python
def parse_resume(text, format='standard'):
    if format == 'functional':
        return _parse_functional_resume(text)
    # ...
```

## Testing

### Unit Test Examples

```python
def test_keyword_extraction():
    jd = "Looking for 5+ years of machine learning experience..."
    keywords = extract_keywords(jd)
    assert any(k['keyword'] == 'machine learning' for k in keywords)
    assert keywords[0]['importance'] == 'PRIMARY'

def test_validation_catches_hallucination():
    original = "Built ML pipeline"
    proposed = "Built enterprise ML pipeline with kubernetes orchestration"
    corpus = "Built ML pipeline. enterprise systems."

    result = validate_edit(original, proposed, corpus)
    assert 'HALLUCINATION_RISK' in result['warnings']
    assert 'kubernetes' in result['details']['missing_words']
```

### Integration Test

```bash
# Full workflow test
python3 resume-tailor.py preprocess \
  --jd reference/jd-examples/example-1.txt \
  --resume users/<your-name>/current-resume.txt \
  --corpus users/<your-name>/bullet-corpus.txt \
  --output /tmp/test_gap.json

# Verify output
cat /tmp/test_gap.json | python -m json.tool
```

## Dependencies

- Python 3.8+
- Standard library only (no external packages for v1)
- Optional: `sentence-transformers` for semantic matching (v2)

## Performance

- Preprocessing: ~100ms for typical JD + resume
- Validation: ~10ms per edit
- No API calls (all local processing)
