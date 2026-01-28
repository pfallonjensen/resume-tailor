---
name: resume-tailor
description: Tailor resume bullets to job descriptions without hallucinating. Uses Python for deterministic processing and Claude for reasoning.
---

# Resume Tailor Skill

Tailors your resume to specific job descriptions by:
1. Extracting keywords from the JD (Python)
2. Finding gaps between JD keywords and your resume (Python)
3. Proposing edits to summary, highlights, and experience sections (Claude)
4. Validating edits against your bullet corpus to prevent hallucination (Python)

## File Locations

Default user: `fallon-jensen` (change via `--profile` flag)

| File | Path |
|------|------|
| **User Folder** | `Career/users/fallon-jensen/` |
| **Corpus** | `Career/users/fallon-jensen/bullet-corpus.txt` |
| **Resume** | `Career/users/fallon-jensen/current-resume.txt` |
| **Profile** | `Career/users/fallon-jensen/profile.md` |
| **JDs** | `Career/users/fallon-jensen/job-applications/` |
| **Script** | `Career/skill/resume-tailor.py` |
| **Reference** | `Career/reference/` (original instruction sets) |
| **Scratchpad** | Use the session scratchpad for intermediate JSON files |

## Profile System

Each user has their own folder under `Career/users/` containing:
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
1. Read the active profile (default: `users/fallon-jensen/profile.md`)
2. Apply tone preferences to proposed wording
3. Check anti-patterns list before suggesting phrases
4. Reference verified metrics table when possible

**To use a different profile:**
```
/resume-tailor --profile scott-smith
```
This loads `Career/users/scott-smith/` files instead of the default.

**To create a new profile:**
1. Copy `Career/users/_template/` to `Career/users/[name]/`
2. Fill in `profile.md` with preferences
3. Build `bullet-corpus.txt` with all bullet variations
4. Add `current-resume.txt` (plain text)
5. See `Career/SETUP.md` for detailed instructions

## Resume Sections

The skill parses resumes into three sections, each with its own character limits and keyword placement strategy:

### Section Types

| Section | Character Limits | Parsing |
|---------|------------------|---------|
| **Summary Tagline** | 60-100 chars | First content line with `\|` separator |
| **Summary Body** | 300-500 chars | Paragraph after tagline |
| **Career Highlights** | 150-250 chars each | Bulleted items with `Label:` format |
| **Experience Bullets** | 80-116 (1-line), 175-235 (2-line) | Bulleted items under companies |

### Where to Add Keywords

Different keywords belong in different sections:

| Keyword Type | Best Section | Why | Example |
|--------------|--------------|-----|---------|
| Domain/industry | Summary tagline | Positioning | "Enterprise AI" |
| Core capabilities | Summary body | Capabilities overview | "data-driven product leadership" |
| Leadership scope | Summary body | Director+ positioning | "led PM teams", "scaled organizations" |
| Signature achievement | Career Highlights | Top-of-resume impact | "Drove $59M AI revenue" |
| Specific evidence | Experience bullets | Detailed proof | "Increased NPS 47% through..." |

### Decision Framework for Claude

**Before proposing an edit, ask:**
1. Is this keyword about WHO they are (positioning)? → Summary
2. Is this a top-3 career achievement? → Career Highlights
3. Is this detailed evidence of capability? → Experience bullets
4. Could reordering existing items help? → Consider resequencing before editing text

## Workflow

### Step 1: Preprocess the JD

Run the preprocessing script to extract keywords and analyze gaps:

```bash
python3 "/Users/fallonjensen/Obsidian Vault/Career/skill/resume-tailor.py" preprocess \
  --jd "<path_to_jd>" \
  --resume "/Users/fallonjensen/Obsidian Vault/Career/users/fallon-jensen/current-resume.txt" \
  --corpus "/Users/fallonjensen/Obsidian Vault/Career/users/fallon-jensen/bullet-corpus.txt" \
  --output "<scratchpad>/gap_analysis.json"
```

This produces:
- Extracted keywords with categories and importance
- Gap analysis showing which keywords are missing
- Parsed bullets with character counts

### Step 2: Review Gap Analysis with User

Present the gap analysis to the user:
1. Show summary stats (total keywords, explicit matches, missing)
2. Show section breakdown (what's in summary vs highlights vs experience)
3. List missing PRIMARY keywords first
4. List missing SECONDARY keywords
5. Ask user which gaps to prioritize

### Step 3: Propose Edits by Section

**First, load the active profile** (default: `Career/users/fallon-jensen/profile.md`):
- Read tone & voice preferences
- Note anti-patterns to avoid
- Check verified metrics for reference

#### Step 3a: Summary Section Edits

For keywords that fit positioning (domain, capabilities, leadership):

1. **Tagline edits**: Can this keyword strengthen the positioning? Keep to 60-100 chars.
   - Example: "Product Strategy & AI" → "Enterprise Product Strategy & AI"
2. **Body edits**: Does the keyword describe a core capability?
   - Example: Add "data-driven" or "platform" to the positioning paragraph

#### Step 3b: Career Highlights Edits

For keywords that represent major achievements:

1. **Reorder first**: Would moving an existing highlight up address the gap?
2. **Edit second**: Can an existing highlight be modified to add the keyword?
3. **New highlight last**: Only if corpus strongly supports adding a new highlight

**Character limit**: 150-250 chars per highlight

#### Step 3c: Experience Bullet Edits

For keywords that need specific evidence:

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

Create a JSON file with proposed edits. Include `section_type` for proper validation:

```json
[
  {
    "section_type": "summary_tagline",
    "id": "summary_tagline",
    "original": "Product Strategy & AI | Leading product teams...",
    "proposed": "Enterprise Product Strategy & AI | Leading product teams...",
    "keyword_added": "enterprise",
    "source_reference": "Found in corpus: 'enterprise AI adoption'"
  },
  {
    "section_type": "highlight",
    "id": "highlight_0",
    "original": "AI/ML Leadership: Led team of 8 ML engineers...",
    "proposed": "Enterprise AI Leadership: Led team of 8 ML engineers...",
    "keyword_added": "enterprise",
    "source_reference": "Found in corpus: 'enterprise AI platform'"
  },
  {
    "section_type": "bullet",
    "id": "logmein_staff_pm_2",
    "original": "Drove $59M in revenue by productizing 8 ML models in NLP, Computer Vision, and Recommenders.",
    "proposed": "Drove $59M in revenue by productizing 8 ML models in NLP, Computer Vision, and Recommenders, scaling enterprise AI adoption.",
    "keyword_added": "scaling",
    "source_reference": "Line in corpus: 'scaling enterprise adoption'"
  }
]
```

**Valid section_type values:** `summary_tagline`, `summary_body`, `highlight`, `bullet`

### Step 4: Validate Edits

Run validation on proposed edits:

```bash
python3 "/Users/fallonjensen/Obsidian Vault/Career/skill/resume-tailor.py" validate \
  --edits "<scratchpad>/proposed_edits.json" \
  --corpus "/Users/fallonjensen/Obsidian Vault/Career/users/fallon-jensen/bullet-corpus.txt" \
  --output "<scratchpad>/validated_edits.json"
```

This checks (using appropriate limits for each section type):
- Character limits (section-specific)
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
3. Offer to save to a new file (e.g., `Resume-Fallon-Jensen-Impel.txt`)

## Character Limit Guidelines

| Section | Range | Guidance |
|---------|-------|----------|
| **Summary tagline** | 60-100 chars | Short, punchy positioning |
| **Summary body** | 300-500 chars | 2-4 sentences overview |
| **Career highlights** | 150-250 chars | Each highlight item |
| **Experience (1-line)** | 80-116 chars | Preferred for clarity |
| **Experience (awkward)** | 117-174 chars | Adjust up or down |
| **Experience (2-line)** | 175-235 chars | OK for complex achievements |
| **Experience (over)** | 236+ chars | Must trim |

## Quick Command

For a new JD, user can say:
- `/resume-tailor` - Starts the full workflow
- `/resume-tailor gaps <jd_path>` - Just shows gap analysis
- `/resume-tailor validate` - Re-runs validation on current edits

## Example Session

```
User: /resume-tailor

Claude: I'll help you tailor your resume. What job description should I use?

User: Use the Impel VP Product AI Platform JD

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
- `Career/README.md` - Overview and quick start
- `Career/SETUP.md` - Setup instructions for new users
- `Career/CONTRIBUTING.md` - How to improve the skill
- `Career/skill/README.md` - Technical documentation
- `Career/reference/README.md` - Guide to original instruction sets
