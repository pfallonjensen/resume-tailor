# Setup Guide

Get the Resume Tailor skill working for yourself in ~20 minutes.

## Prerequisites

- **Claude Code** installed and working
- **Python 3.8+** (for the validation scripts)
- Your resume in any format (Word, PDF, plain text)
- At least one job description you want to tailor for

## Step 1: Create Your User Folder

```bash
# Copy the template to create your profile
cp -r users/_template users/your-name
```

Replace `your-name` with your actual name (lowercase, hyphenated).

## Step 2: Fill Out Your Profile

Edit `users/your-name/profile.md`:

### Quick Context (Required)
Write a 2-3 sentence summary of who you are professionally. This primes Claude sessions.

```markdown
## Quick Context
I'm [Name], a [role] with [X years] experience in [domains].
I've [key achievement] and [key achievement].
My tone is [adjectives] - I [preference] and [preference].
```

### Positioning (Required)
- What's your unique selling proposition?
- What roles are you targeting?
- What makes you different from other candidates?

### Tone & Voice (Required)
- How do you write? (Formal? Casual? Somewhere in between?)
- What do you avoid? (Jargon? Passive voice? Certain words?)
- What's your philosophy on resume writing?

### Anti-Patterns Table (Recommended)
List phrases you hate seeing on resumes. Claude will avoid suggesting these.

```markdown
| Instead of... | Use... | Why |
|---------------|--------|-----|
| "proven track record" | specific metrics | Too generic |
| "passionate about" | demonstrated by [action] | Show don't tell |
```

### Verified Metrics (Recommended)
List your actual, verifiable achievements. Reference sources if possible.

```markdown
| Metric | Source | Notes |
|--------|--------|-------|
| $59M ARR | Investor deck | AI products at LogMeIn |
| 600+ experiments | Internal dashboard | A/B testing program |
```

## Step 3: Build Your Bullet Corpus

This is the most important file. Edit `users/your-name/bullet-corpus.txt`:

### What to Include
- Every resume bullet you've ever written (all variations)
- Rejected drafts (they contain useful vocabulary)
- Different phrasings of the same achievement
- Notes about projects that never made it to your resume

### Format

```text
## Company Name | Role | Dates

- Bullet variation 1 with specific metric
- Same bullet, different phrasing
- Another achievement with different emphasis

# Notes: context about this role that might be useful
# Rejected: phrasing I tried but didn't like
```

### Why This Matters
The anti-hallucination system only allows words that exist in your corpus. More variations = more vocabulary = better edits.

**Tip**: Export your LinkedIn profile, past resume versions, and performance reviews. Consolidate everything here.

## Step 4: Add Your Current Resume

Convert your resume to plain text and save as `users/your-name/current-resume.txt`:

```bash
# From Word doc on macOS:
textutil -convert txt resume.docx -output current-resume.txt

# Or manually copy/paste into the file
```

Keep the `.docx` version too (for reference): `current-resume.docx`

## Step 5: Add a Job Description

Save job descriptions to `users/your-name/job-applications/`:

```
job-applications/
├── impel-vp-product.txt
├── hubspot-gpm-ai.txt
└── stripe-director-product.txt
```

**Format**: Plain text. Copy the full JD including requirements, responsibilities, and "nice to haves."

## Step 6: Install the Skill (Claude Code)

If you're using Fallon's Obsidian vault, the skill is already installed at:
- `.claude/skills/resume-tailor/skill.md`
- `.claude/skills/resume-tailor/resume-tailor.py`
- `.claude/commands/resume-tailor.md`

If setting up elsewhere, copy these files to your Claude Code skill location.

## Step 7: Update File Paths

Edit `.claude/skills/resume-tailor/skill.md` to point to your files:

```markdown
## File Locations

- **Corpus**: `/path/to/users/your-name/bullet-corpus.txt`
- **Current Resume**: `/path/to/users/your-name/current-resume.txt`
- **JDs**: `/path/to/users/your-name/job-applications/*.txt`
```

Or use the `--profile` flag when running:
```bash
/resume-tailor --profile your-name
```

## Step 8: Test It

```bash
# Start a Claude Code session
claude

# Run the skill
> /resume-tailor

# Follow prompts to select a JD and review gaps
```

## Troubleshooting

### "Keyword not in corpus"
Your bullet corpus is missing vocabulary. Add more bullet variations that include the concept.

### "Character limit exceeded"
Proposed edit is too long. Ask for a shorter alternative or manually trim.

### "Metrics not preserved"
The edit lost a number from the original bullet. This is a validation failure - the edit won't be applied.

### "Hallucination risk detected"
A word in the proposed edit doesn't exist in your corpus. Either:
1. Add supporting text to your corpus (if you can legitimately claim it)
2. Reject the edit (if you can't claim it)

## Next Steps

- Read [CONTRIBUTING.md](CONTRIBUTING.md) to improve the skill
- Check [skill/README.md](skill/README.md) for technical details
- Review [reference/README.md](reference/README.md) for the original design thinking
