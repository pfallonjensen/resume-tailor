# Resume Tailor - Technical Documentation

How the skill code works, for anyone who wants to modify or understand it.

> **Note for Fallon's vault**: The "live" skill files are at `.claude/skills/resume-tailor/`. This folder (`Career/skill/`) is a copy for documentation and sharing. If you modify the skill, update both locations.

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

#### `parse_resume(resume_text) -> ParsedResume`
Parses resume into structured sections: summary, career highlights, and experience bullets.

```python
# Returns ParsedResume dataclass:
{
    "summary": {
        "tagline": "Product Strategy & Innovation | Leading...",
        "tagline_char_count": 86,
        "body": "With 15 years in product strategy...",
        "body_char_count": 483
    },
    "highlights": [
        {
            "id": "highlight_0",
            "label": "AI/ML & Product Innovation:",
            "text": "Spearheaded the productization of 12 ML models...",
            "full_text": "AI/ML & Product Innovation: Spearheaded...",
            "char_count": 189,
            "metrics": ["$59M"]
        },
        ...
    ],
    "experience_bullets": [
        {
            "id": "code_and_theory_0",
            "company": "Code and Theory",
            "text": "Generated $23M+ in revenue...",
            "char_count": 94,
            "metrics": ["$23M+", "12"]
        },
        ...
    ]
}
```

**Logic:**
1. Split into sections by headers (CAREER HIGHLIGHTS, PROFESSIONAL IMPACT/EXPERIENCE)
2. Parse summary: tagline (first line with | separator) and body paragraph
3. Parse highlights: labeled bullets (Label: description format)
4. Parse experience: company headers and bullet points
5. Count characters and extract metrics for each item

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

#### `validate_edit(original, proposed, corpus, section_type='bullet') -> tuple[list, bool]`
Validates a proposed edit against anti-hallucination rules with section-appropriate limits.

```python
# Parameters:
#   original: str - Original text
#   proposed: str - Proposed replacement
#   corpus: set[str] - Words from bullet corpus
#   section_type: str - One of: 'summary_tagline', 'summary_body', 'highlight', 'bullet'

# Returns tuple of (warnings_list, passed_bool):
(['CHAR_EXCEEDED: Tagline 120 chars exceeds max (100)'], False)
```

**Validation Rules:**

| Rule | Check | Failure Mode |
|------|-------|--------------|
| Character limits | Section-specific (see CHAR_LIMITS) | `CHAR_EXCEEDED` or `CHAR_AWKWARD` |
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
    'summary_tagline': (60, 100),      # Short, punchy positioning
    'summary_body': (300, 500),        # 2-4 sentences overview
    'highlight': (150, 250),           # Career highlights
    'bullet_one_line': (80, 116),      # Ideal for experience
    'bullet_two_line': (175, 235),     # Acceptable for complex achievements
    'bullet_awkward': (117, 174),      # Adjust up or down
}
```

The `validate_edit()` function accepts a `section_type` parameter to apply the appropriate limits.

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
  --resume users/fallon-jensen/current-resume.txt \
  --corpus users/fallon-jensen/bullet-corpus.txt \
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
