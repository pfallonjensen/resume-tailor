---
name: resume-tailor
description: Tailor resume bullets to job descriptions without hallucinating. Uses Python for deterministic processing and Claude for reasoning.
---

# Resume Tailor Skill

Tailors your resume to specific job descriptions by:
1. Extracting keywords from the JD (Python)
2. Finding gaps between JD keywords and your resume (Python)
3. Proposing minimal bullet edits to incorporate missing keywords (Claude)
4. Validating edits against your bullet corpus to prevent hallucination (Python)

## File Locations

**IMPORTANT**: Update these paths to match your installation.

| File | Path |
|------|------|
| **User Folder** | `<YOUR_PATH>/users/<your-name>/` |
| **Corpus** | `<YOUR_PATH>/users/<your-name>/bullet-corpus.txt` |
| **Resume** | `<YOUR_PATH>/users/<your-name>/current-resume.txt` |
| **Profile** | `<YOUR_PATH>/users/<your-name>/profile.md` |
| **JDs** | `<YOUR_PATH>/users/<your-name>/job-applications/` |
| **Script** | `<YOUR_PATH>/skill/resume-tailor.py` |
| **Scratchpad** | Use the session scratchpad for intermediate JSON files |

## Profile System

Each user has their own folder under `users/` containing:
- `profile.md` - Tone, style, and positioning guidance
- `bullet-corpus.txt` - Ground truth for anti-hallucination
- `current-resume.txt` - Baseline resume to tailor
- `job-applications/` - JD files organized by company

**What profiles contain:**
- Quick context paragraph (for priming sessions)
- Positioning (USP, target roles)
- Tone & voice preferences
- Anti-patterns (phrases to avoid)
- Resume formatting preferences
- Verified metrics with sources

**When proposing edits, Claude should:**
1. Read the active profile
2. Apply tone preferences to proposed wording
3. Check anti-patterns list before suggesting phrases
4. Reference verified metrics table when possible

**To use a different profile:**
```
/resume-tailor --profile other-name
```
This loads `users/other-name/` files instead of the default.

**To create a new profile:**
1. Copy `users/_template/` to `users/[name]/`
2. Fill in `profile.md` with preferences
3. Build `bullet-corpus.txt` with all bullet variations
4. Add `current-resume.txt` (plain text)
5. See `SETUP.md` for detailed instructions

## Workflow

### Step 1: Preprocess the JD

Run the preprocessing script to extract keywords and analyze gaps:

```bash
python3 "<YOUR_PATH>/skill/resume-tailor.py" preprocess \
  --jd "<path_to_jd>" \
  --resume "<YOUR_PATH>/users/<your-name>/current-resume.txt" \
  --corpus "<YOUR_PATH>/users/<your-name>/bullet-corpus.txt" \
  --output "<scratchpad>/gap_analysis.json"
```

This produces:
- Extracted keywords with categories and importance
- Gap analysis showing which keywords are missing
- Parsed bullets with character counts

### Step 2: Review Gap Analysis with User

Present the gap analysis to the user:
1. Show summary stats (total keywords, explicit matches, missing)
2. List missing PRIMARY keywords first
3. List missing SECONDARY keywords
4. Ask user which gaps to prioritize

### Step 3: Propose Edits (Claude's Role)

**First, load the active profile**:
- Read tone & voice preferences
- Note anti-patterns to avoid
- Check verified metrics for reference

For each missing keyword the user wants to address:

1. **Read the bullet corpus** to find supporting text
2. **Identify the best bullet to modify** (most thematically related)
3. **Apply profile preferences** when wording the edit
4. **Propose a minimal edit** that:
   - Adds the keyword naturally
   - Preserves all metrics (numbers, percentages, dollar amounts)
   - Stays within character limits (80-116 for one-line, 175-235 for two-line)
   - Uses ONLY words that exist in the corpus

#### CRITICAL: Anti-Hallucination Rules

**BEFORE proposing any edit, verify:**
- [ ] Every new word exists somewhere in `bullet-corpus.txt`
- [ ] All metrics from original bullet are preserved
- [ ] No new company names, technologies, or achievements invented
- [ ] Character count is within limits

**If you cannot find corpus support for adding a keyword:**
- Mark it as UNSUPPORTED
- Explain why
- Do NOT propose an edit

#### Output Format for Proposed Edits

Create a JSON file with proposed edits:

```json
[
  {
    "bullet_id": "company_role_2",
    "original": "Drove $59M in revenue by productizing 8 ML models in NLP, Computer Vision, and Recommenders.",
    "proposed": "Drove $59M in revenue by productizing 8 ML models in NLP, Computer Vision, and Recommenders, scaling enterprise AI adoption.",
    "keyword_added": "scaling",
    "source_reference": "Line in corpus: 'scaling enterprise adoption'"
  }
]
```

### Step 4: Validate Edits

Run validation on proposed edits:

```bash
python3 "<YOUR_PATH>/skill/resume-tailor.py" validate \
  --edits "<scratchpad>/proposed_edits.json" \
  --corpus "<YOUR_PATH>/users/<your-name>/bullet-corpus.txt" \
  --output "<scratchpad>/validated_edits.json"
```

This checks:
- Character limits
- Metrics preserved
- No hallucinated words
- No new proper nouns

### Step 5: Present Results to User

For each edit, show:
1. **Original bullet**
2. **Proposed edit** (with changes highlighted)
3. **Keyword added**
4. **Source reference** from corpus
5. **Validation status** (PASSED or warnings)
6. **Character count** with limit assessment

User can: **Accept** | **Reject** | **Request Alternative**

### Step 6: Generate Final Resume

After user approves edits:
1. Apply accepted edits to resume
2. Show final resume with highlighted changes
3. Offer to save to a new file (e.g., `tailored-resume-companyname.txt`)

## Character Limit Guidelines

| Type | Range | Guidance |
|------|-------|----------|
| One-line | 80-116 chars | Preferred for clarity |
| Awkward | 117-174 chars | Adjust up or down |
| Two-line | 175-235 chars | OK for complex achievements |
| Over | 236+ chars | Must trim |

## Quick Command

For a new JD, user can say:
- `/resume-tailor` - Starts the full workflow
- `/resume-tailor gaps <jd_path>` - Just shows gap analysis
- `/resume-tailor validate` - Re-runs validation on current edits

## Example Session

```
User: /resume-tailor

Claude: I'll help you tailor your resume. What job description should I use?

User: Use the Acme Corp VP Product JD

Claude: Running gap analysis...
[Runs preprocessing script]

Found 18 keywords, 12 explicit matches, 6 missing.

Missing PRIMARY keywords:
- agentic (ai_ml) - Not found in resume
- automotive (domain) - Not found in resume
- high-performing (leadership) - Not found in resume

Missing SECONDARY keywords:
- commercial metrics (outcome)
- platform (skill)
- portfolio (skill)

Which gaps would you like me to address?

User: Focus on agentic and high-performing

Claude: [Searches corpus, proposes edits, runs validation, presents results]
```

## Maintenance

When you complete work on a job application:
1. Add any new bullet variations to your `bullet-corpus.txt`
2. Save the tailored resume to `job-applications/[company]/tailored-resume.txt`
3. Keep the JD file in the same folder for reference

## Documentation

For more details, see:
- `README.md` - Overview and quick start
- `SETUP.md` - Setup instructions for new users
- `CONTRIBUTING.md` - How to improve the skill
- `skill/README.md` - Technical documentation
- `reference/README.md` - Guide to original instruction sets
