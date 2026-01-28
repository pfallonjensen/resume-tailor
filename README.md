# Resume Tailor

A Claude Code skill that tailors your resume to job descriptions **without hallucinating experience you don't have**.

## The Problem

Resume tailoring tools (including AI) often "improve" your resume by adding impressive-sounding skills, inflated metrics, or experiences you never had. This is both unethical and dangerous - recruiters and hiring managers will catch it.

## The Solution

This skill uses a **hybrid architecture**:

| Layer | Tool | What It Does |
|-------|------|-------------|
| **Deterministic** | Python | Extract keywords, count characters, validate edits |
| **Reasoning** | Claude | Propose minimal edits, apply tone preferences |

The key innovation: **every word in a proposed edit must exist in your bullet corpus**. If you haven't done it (or at least written about it), the skill won't claim you have.

## Quick Start

```bash
# 1. Set up your profile (see SETUP.md)

# 2. Run the skill with a job description
/resume-tailor

# 3. Follow the prompts to:
#    - Analyze keyword gaps
#    - Choose which gaps to address
#    - Review proposed edits
#    - Generate tailored resume
```

## Folder Structure

```
Career/
├── README.md           # You are here
├── SETUP.md            # Setup instructions for new users
├── CONTRIBUTING.md     # How to improve the skill
├── SHARING.md          # How to share with others
│
├── users/              # User profiles and data
│   ├── _template/      # Template for new users
│   │   ├── profile.md
│   │   ├── bullet-corpus.txt
│   │   └── current-resume.txt
│   │
│   └── [your-name]/    # Your profile
│       ├── profile.md
│       ├── bullet-corpus.txt
│       ├── current-resume.txt
│       └── job-applications/
│           └── [company-jd].txt
│
├── skill/              # The skill code
│   ├── README.md       # Technical documentation
│   ├── resume-tailor.py
│   └── skill.md
│
├── reference/          # Original instruction sets (read-only)
│   ├── README.md       # Guide to reference materials
│   ├── kb-instructions/
│   ├── example-lists/
│   ├── industry-terms/
│   └── jd-examples/
│
└── archive/            # Old resume versions
```

## How It Works

### 1. Gap Analysis (Python)
Extracts keywords from the job description, parses your resume into sections (summary, career highlights, experience bullets), and shows per-section keyword coverage.

### 2. Edit Proposals (Claude)
For each gap you want to address, Claude identifies the best section to modify and proposes minimal edits that:
- Add the keyword in the right place (positioning keywords → summary, achievements → highlights, evidence → bullets)
- Preserve all your metrics
- Stay within section-appropriate character limits
- Use ONLY words from your bullet corpus

### 3. Validation (Python)
Every proposed edit is validated:
- Character count within limits
- All metrics preserved
- No hallucinated words
- No invented company names or technologies

### 4. User Review
You see the original bullet, proposed edit, source reference from your corpus, and validation status. You approve, reject, or request alternatives.

## Key Concepts

**Bullet Corpus**: Your master file of every bullet variation you've ever written. This is the source of truth for what you can claim.

**Profile**: Your tone preferences, anti-patterns to avoid, and verified metrics. Makes edits sound like you wrote them.

**Gap Analysis**: Shows which JD keywords are missing from your resume, prioritized by importance.

**Character Limits**: Section-specific limits ensure proper formatting:
- Summary tagline: 60-100 chars (short, punchy)
- Summary body: 300-500 chars (2-4 sentences)
- Career highlights: 150-250 chars each
- Experience bullets: 80-116 (one-line) or 175-235 (two-line)

## Next Steps

1. **New user?** Start with [SETUP.md](SETUP.md)
2. **Want to share this?** See [SHARING.md](SHARING.md)
3. **Want to improve the skill?** See [CONTRIBUTING.md](CONTRIBUTING.md)
4. **Curious about the code?** Read [skill/README.md](skill/README.md)
5. **Learning from the reference materials?** Check [reference/README.md](reference/README.md)
