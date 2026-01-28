# Contributing & Improving the Skill

Ideas for making the Resume Tailor better, from quick wins to ambitious experiments.

## Architecture Overview

Understanding what lives where helps you know what to change:

```
┌─────────────────────────────────────────────────────────┐
│                    Claude Code Skill                     │
│  (.claude/skills/resume-tailor/skill.md)                │
│  - Workflow instructions for Claude                      │
│  - Anti-hallucination rules (enforced by Claude)        │
│  - Profile system integration                            │
└─────────────────────────────────────────────────────────┘
                          │
                          │ calls
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Python Script                         │
│  (skill/resume-tailor.py)                        │
│  - Keyword extraction (deterministic)                    │
│  - Gap analysis (deterministic)                          │
│  - Edit validation (code-enforced)                       │
│  - Character counting (exact)                            │
└─────────────────────────────────────────────────────────┘
                          │
                          │ reads
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    User Data                             │
│  (users/your-name/)                              │
│  - bullet-corpus.txt (ground truth)                      │
│  - current-resume.txt (baseline)                         │
│  - profile.md (tone/style preferences)                   │
└─────────────────────────────────────────────────────────┘
```

## Quick Wins (< 30 minutes each)

### 1. Add Industry Keywords
The Python script has a `KEYWORD_PATTERNS` dict. Add patterns for your industry:

```python
# In resume-tailor.py
KEYWORD_PATTERNS = {
    'ai_ml': ['machine learning', 'AI', 'LLM', 'neural network', ...],
    'your_domain': ['term1', 'term2', ...],  # Add your domain
}
```

### 2. Expand Anti-Patterns
Add phrases to avoid in your profile's anti-patterns table:

```markdown
| Instead of... | Use... | Why |
|---------------|--------|-----|
| "leverage" | "use" | Corporate jargon |
| "synergy" | specific collaboration | Meaningless |
```

### 3. Improve Keyword Categories
The `categorize_keyword()` function determines PRIMARY vs SECONDARY importance. Adjust weights for your target roles.

### 4. Add More Example JDs
The `reference/jd-examples/` folder has 10 keyword extraction examples. Add more from your target companies to improve pattern recognition.

## Medium Improvements (1-2 hours)

### 5. Semantic Matching (v2)
Currently, gap analysis uses exact string matching. Add semantic similarity:

```python
# Potential approach using sentence-transformers
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def semantic_match(keyword, resume_text, threshold=0.7):
    keyword_emb = model.encode(keyword)
    # Compare to resume sections...
```

**Trade-off**: Adds dependency, slower, but catches paraphrased matches.

### 6. ATS Simulation
Modern ATS systems weight keywords by:
- Position in document (earlier = more weight)
- Section (Skills > Experience > Summary for technical terms)
- Frequency (diminishing returns after 2-3 mentions)

Add scoring that simulates this.

### 7. Bullet Quality Scoring
Add heuristics for bullet quality:
- Starts with strong verb? (+1)
- Has quantified metric? (+2)
- Under 120 chars? (+1)
- "Responsible for" detected? (-2)

### 8. Multi-Resume Support
Allow generating multiple resume versions optimized for different role types from the same corpus.

## Ambitious Experiments (Half-day+)

### 9. Learning from Outcomes
Track which tailored resumes got interviews. Use this to improve:
- Which keywords actually matter
- Which edit styles work
- Optimal resume length by industry

### 10. Company-Specific Optimization
Scrape company careers pages, press releases, and annual reports to extract their specific vocabulary. Tailor to match their language.

### 11. Cover Letter Generation
Extend the skill to generate cover letters that:
- Reference specific JD requirements
- Map to corpus achievements
- Apply the same anti-hallucination rules

### 12. Interview Prep Mode
Use the corpus to generate STAR stories for behavioral interviews based on gaps the resume tailoring revealed.

## Reference Materials

The `reference/` folder contains the original ChatGPT instruction sets. Useful patterns:

| File | What to Extract |
|------|-----------------|
| `kb-instructions/KB 1 - Anti_Hallucination*` | Core hallucination prevention rules |
| `example-lists/Bullet Tailoring Positive*` | Good edit examples |
| `example-lists/Bullet Tailoring Negative*` | What NOT to do |
| `example-lists/Bullet Tailoring GRAY*` | Edge cases requiring judgment |
| `kb-instructions/KB 4 - Verification*` | Verification log patterns |
| `industry-terms/*` | Keyword vocabularies by domain |

## Code Style

When modifying `resume-tailor.py`:

1. **Keep deterministic logic in Python** - Don't add "fuzzy" matching that could vary between runs
2. **Keep reasoning in Claude** - Edit proposals, tone application, judgment calls
3. **Fail loud** - Validation should clearly flag issues, not silently accept bad edits
4. **Test with edge cases** - Very short bullets, very long bullets, bullets with special characters

## Testing Changes

After making changes:

```bash
# Test preprocessing
python resume-tailor.py preprocess \
  --jd path/to/test-jd.txt \
  --resume path/to/resume.txt \
  --corpus path/to/corpus.txt \
  --output /tmp/gap_analysis.json

# Test validation (create a test edits file)
python resume-tailor.py validate \
  --edits /tmp/proposed_edits.json \
  --corpus path/to/corpus.txt \
  --output /tmp/validated.json
```

## Sharing Improvements

If you make the skill better:

1. Document what you changed and why
2. Test with at least 3 different JDs
3. Share the specific files changed
4. Note any new dependencies

The skill lives in Claude Code, so there's no formal PR process - just share your improved versions with others who might benefit.
