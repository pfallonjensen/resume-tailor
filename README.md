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
# 1. Clone this repo
git clone https://github.com/YOUR_USERNAME/resume-tailor.git

# 2. Set up your profile (see SETUP.md)
cp -r users/_template users/your-name

# 3. Install the skill in Claude Code
cp skill/* ~/.claude/skills/resume-tailor/

# 4. Fill in your data (corpus, resume, profile)

# 5. Run the skill
/resume-tailor
```

## Folder Structure

```
resume-tailor/
├── README.md           # You are here
├── SETUP.md            # Setup instructions
├── CONTRIBUTING.md     # How to improve the skill
│
├── users/              # User profiles and data
│   └── _template/      # Copy this to create your profile
│       ├── profile.md
│       ├── bullet-corpus.txt
│       └── current-resume.txt
│
├── skill/              # The skill code
│   ├── README.md       # Technical documentation
│   ├── resume-tailor.py
│   └── skill.md
│
└── reference/          # Original instruction sets (learning resource)
    ├── README.md
    ├── kb-instructions/
    ├── example-lists/
    ├── industry-terms/
    └── jd-examples/
```

## How It Works

### 1. Gap Analysis (Python)
Extracts keywords from the job description, categorizes them, and compares against your current resume to find missing keywords.

### 2. Edit Proposals (Claude)
For each gap you want to address, Claude proposes minimal edits that:
- Add the keyword naturally
- Preserve all your metrics
- Stay within character limits
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

**Character Limits**: One-line bullets (80-116 chars) are preferred. Two-line (175-235 chars) are acceptable. The "awkward zone" (117-174 chars) should be adjusted up or down.

## Contributing

Found a bug? Have an improvement? See [CONTRIBUTING.md](CONTRIBUTING.md).

Ideas welcome:
- Better keyword extraction patterns
- New industry term lists
- Improved validation rules
- Documentation improvements

## License

MIT - Use it, share it, improve it.

## Credits

Built with [Claude Code](https://claude.ai/claude-code). Original instruction design based on ChatGPT custom GPT experiments (see `reference/` folder).
