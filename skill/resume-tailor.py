#!/usr/bin/env python3
"""
resume-tailor.py - Deterministic preprocessing and validation for resume tailoring

This script handles:
1. Keyword extraction from job descriptions
2. Gap analysis between JD keywords and resume content
3. Validation of proposed edits against the bullet corpus (anti-hallucination)

Usage:
    python resume-tailor.py preprocess --jd <jd_path> --resume <resume_path> --corpus <corpus_path> --output <output_path>
    python resume-tailor.py validate --edits <edits_json> --corpus <corpus_path> --output <output_path>
"""

import argparse
import json
import re
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import List, Set, Dict, Optional, Tuple

# ============================================================================
# CONFIGURATION
# ============================================================================

# Character limits for bullets
CHAR_LIMIT_ONE_LINE = (80, 116)
CHAR_LIMIT_TWO_LINE = (175, 235)
CHAR_LIMIT_AWKWARD = (117, 174)  # Should be adjusted up or down

# Common PM/tech keywords to look for
INDUSTRY_TERMS = {
    # Strategy & Leadership
    "product strategy", "product vision", "roadmap", "strategic", "vision",
    "go-to-market", "gtm", "product-led growth", "plg", "north star",
    "okrs", "kpis", "metrics", "product-market fit", "pmf",

    # AI/ML
    "ai", "ml", "machine learning", "artificial intelligence", "deep learning",
    "nlp", "natural language processing", "llm", "large language model",
    "genai", "generative ai", "agentic", "autonomous", "intelligent",
    "recommendation", "recommender", "predictive", "computer vision",

    # Product Management
    "product management", "product lifecycle", "0-1", "zero-to-one",
    "discovery", "validation", "mvp", "iteration", "experimentation",
    "a/b testing", "ab testing", "hypothesis", "user research",
    "customer discovery", "customer-centric", "user-centric",
    "design thinking", "jtbd", "jobs to be done",

    # Growth & Metrics
    "growth", "acquisition", "retention", "engagement", "conversion",
    "arr", "revenue", "arpu", "ltv", "cltv", "churn", "nps",
    "adoption", "activation", "onboarding", "funnel",

    # Technical
    "saas", "b2b", "b2c", "b2b2c", "platform", "api", "integration",
    "data-driven", "analytics", "data strategy", "scalable", "scale",

    # Leadership & Team
    "cross-functional", "stakeholder", "executive", "leadership",
    "team management", "mentorship", "coaching", "collaboration",
    "high-performing", "building teams", "scaling teams",

    # Methodologies
    "agile", "scrum", "lean", "kanban", "sprint", "velocity",

    # Domains
    "fintech", "healthtech", "automotive", "enterprise", "consumer",
    "e-commerce", "ecommerce", "web3", "blockchain",
}

# Stopwords to ignore in validation
STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
    'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'must', 'that', 'which', 'who',
    'this', 'these', 'those', 'it', 'its', 'i', 'my', 'our', 'we', 'they',
    'their', 'your', 'up', 'out', 'into', 'over', 'under', 'through',
    'during', 'before', 'after', 'above', 'below', 'between', 'among',
    'while', 'when', 'where', 'how', 'what', 'why', 'all', 'each', 'every',
    'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'not',
    'only', 'same', 'so', 'than', 'too', 'very', 'just', 'also', 'now',
    'new', 'first', 'last', 'long', 'great', 'little', 'own', 'well',
    'back', 'way', 'even', 'still', 'here', 'there', 'then', 'can', 'any',
    'about', 'across', 'within', 'including', 'led', 'leading', 'using',
}

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Keyword:
    term: str
    category: str  # skill, responsibility, tool, outcome, methodology, domain
    importance: str  # primary, secondary
    source_context: str  # snippet from JD where it appeared

@dataclass
class Bullet:
    id: str
    text: str
    char_count: int
    company: str
    metrics: List[str] = field(default_factory=list)

@dataclass
class GapAnalysis:
    keyword: str
    category: str
    importance: str
    status: str  # explicit, missing
    match_locations: List[str] = field(default_factory=list)

@dataclass
class ValidationResult:
    bullet_id: str
    original: str
    proposed: str
    keyword_added: str
    char_count: int
    warnings: List[str] = field(default_factory=list)
    passed: bool = True

# ============================================================================
# KEYWORD EXTRACTION
# ============================================================================

def extract_keywords(jd_text: str) -> List[Keyword]:
    """Extract keywords from job description using pattern matching."""
    keywords = []
    jd_lower = jd_text.lower()
    seen_terms = set()

    # Find industry terms
    for term in INDUSTRY_TERMS:
        if term in jd_lower and term not in seen_terms:
            # Find context (surrounding text)
            idx = jd_lower.find(term)
            start = max(0, idx - 50)
            end = min(len(jd_lower), idx + len(term) + 50)
            context = jd_text[start:end].strip()

            # Determine importance based on section
            importance = "primary"
            if "preferred" in jd_lower[max(0,idx-100):idx].lower():
                importance = "secondary"
            if "nice to have" in jd_lower[max(0,idx-100):idx].lower():
                importance = "secondary"

            keywords.append(Keyword(
                term=term,
                category=categorize_keyword(term),
                importance=importance,
                source_context=context
            ))
            seen_terms.add(term)

    # Extract years of experience requirements
    exp_matches = re.findall(r'(\d+)\+?\s*years?\s+(?:of\s+)?experience', jd_lower)
    for years in exp_matches:
        keywords.append(Keyword(
            term=f"{years}+ years experience",
            category="qualification",
            importance="primary",
            source_context=f"Requires {years}+ years of experience"
        ))

    return keywords

def categorize_keyword(term: str) -> str:
    """Categorize keyword by type."""
    strategy = {"product strategy", "product vision", "roadmap", "strategic", "vision",
                "go-to-market", "gtm", "north star", "product-market fit", "pmf"}
    ai_ml = {"ai", "ml", "machine learning", "artificial intelligence", "deep learning",
             "nlp", "natural language processing", "llm", "large language model",
             "genai", "generative ai", "agentic", "autonomous", "intelligent",
             "recommendation", "recommender", "predictive", "computer vision"}
    outcomes = {"growth", "acquisition", "retention", "engagement", "conversion",
                "arr", "revenue", "arpu", "ltv", "cltv", "churn", "nps",
                "adoption", "activation"}
    methodology = {"agile", "scrum", "lean", "kanban", "design thinking",
                   "a/b testing", "ab testing", "experimentation", "jtbd"}
    leadership = {"cross-functional", "stakeholder", "executive", "leadership",
                  "team management", "mentorship", "coaching", "collaboration",
                  "high-performing", "building teams", "scaling teams"}
    domain = {"fintech", "healthtech", "automotive", "enterprise", "consumer",
              "e-commerce", "ecommerce", "web3", "blockchain", "saas", "b2b", "b2c"}

    if term in strategy:
        return "strategy"
    elif term in ai_ml:
        return "ai_ml"
    elif term in outcomes:
        return "outcome"
    elif term in methodology:
        return "methodology"
    elif term in leadership:
        return "leadership"
    elif term in domain:
        return "domain"
    else:
        return "skill"

# ============================================================================
# RESUME PARSING
# ============================================================================

def parse_resume(resume_text: str) -> List[Bullet]:
    """Parse resume into structured bullets."""
    bullets = []
    lines = resume_text.split('\n')
    current_company = "unknown"
    bullet_count = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect company headers (heuristic: contains date range)
        if re.search(r'(19|20)\d{2}\s*[-–]\s*(19|20)?\d{2}|Present', line):
            # Extract company name (usually before the date)
            parts = re.split(r'\t|\s{2,}', line)
            if parts:
                current_company = parts[0].strip()[:30]  # Truncate for ID
            continue

        # Detect bullet points
        if line.startswith('•') or line.startswith('-') or line.startswith('	•'):
            bullet_text = re.sub(r'^[•\-\t\s]+', '', line).strip()
            if len(bullet_text) < 20:  # Skip very short lines
                continue

            # Extract metrics
            metrics = re.findall(r'\$[\d.,]+[MBK]?|\d+%|\d+x|\d+\+', bullet_text)

            # Create clean company name for ID
            company_clean = re.sub(r'[^a-zA-Z0-9]', '_', current_company.lower())[:20]
            bullet_id = f"{company_clean}_{bullet_count}"
            bullet_count += 1

            bullets.append(Bullet(
                id=bullet_id,
                text=bullet_text,
                char_count=len(bullet_text),
                company=current_company,
                metrics=metrics
            ))

    return bullets

# ============================================================================
# GAP ANALYSIS
# ============================================================================

def find_explicit_matches(keyword: str, text: str) -> List[str]:
    """Find all explicit matches of a keyword in text."""
    matches = []
    text_lower = text.lower()
    keyword_lower = keyword.lower()

    # Direct match
    if keyword_lower in text_lower:
        # Find the line containing the match
        for line in text.split('\n'):
            if keyword_lower in line.lower():
                matches.append(line.strip()[:100])

    return matches

def compute_gap_analysis(keywords: List[Keyword], resume_text: str, corpus_text: str) -> List[GapAnalysis]:
    """Determine which keywords are covered or missing."""
    gaps = []

    # Combine resume and corpus for matching
    combined_text = resume_text + "\n" + corpus_text

    for kw in keywords:
        matches = find_explicit_matches(kw.term, combined_text)

        status = "explicit" if matches else "missing"

        gaps.append(GapAnalysis(
            keyword=kw.term,
            category=kw.category,
            importance=kw.importance,
            status=status,
            match_locations=matches[:3]  # Limit to 3 examples
        ))

    return gaps

# ============================================================================
# VALIDATION
# ============================================================================

def load_corpus_words(corpus_path: str) -> Set[str]:
    """Load all words from the bullet corpus."""
    with open(corpus_path, 'r') as f:
        text = f.read().lower()

    # Extract all words (keep hyphenated terms together)
    words = set(re.findall(r'\b[\w-]+\b', text))
    return words

def extract_metrics(text: str) -> Set[str]:
    """Extract all metrics from text."""
    return set(re.findall(r'\$[\d.,]+[MBK]?|\d+%|\d+x|\d+\+', text))

def validate_edit(original: str, proposed: str, corpus_words: Set[str]) -> Tuple[List[str], bool]:
    """Validate a proposed edit against anti-hallucination rules."""
    warnings = []
    passed = True
    char_count = len(proposed)

    # Check 1: Character limits
    if CHAR_LIMIT_AWKWARD[0] <= char_count <= CHAR_LIMIT_AWKWARD[1]:
        warnings.append(f"CHAR_AWKWARD: {char_count} chars is in awkward range (117-174). Adjust to one-line or two-line.")
    elif char_count > CHAR_LIMIT_TWO_LINE[1]:
        warnings.append(f"CHAR_EXCEEDED: {char_count} chars exceeds max ({CHAR_LIMIT_TWO_LINE[1]})")
        passed = False
    elif char_count < CHAR_LIMIT_ONE_LINE[0]:
        warnings.append(f"CHAR_SHORT: {char_count} chars below minimum ({CHAR_LIMIT_ONE_LINE[0]})")

    # Check 2: All significant words exist in corpus
    original_words = set(re.findall(r'\b[\w-]+\b', original.lower()))
    proposed_words = set(re.findall(r'\b[\w-]+\b', proposed.lower()))
    new_words = proposed_words - original_words - STOPWORDS

    hallucination_words = []
    for word in new_words:
        # Skip numbers and very short words
        if word.isdigit() or len(word) <= 2:
            continue
        if word not in corpus_words:
            hallucination_words.append(word)

    if hallucination_words:
        warnings.append(f"HALLUCINATION_RISK: Words not in corpus: {hallucination_words}")
        passed = False

    # Check 3: Metrics preserved
    original_metrics = extract_metrics(original)
    proposed_metrics = extract_metrics(proposed)
    lost_metrics = original_metrics - proposed_metrics

    if lost_metrics:
        warnings.append(f"METRICS_LOST: {list(lost_metrics)}")
        passed = False

    # Check 4: No new capitalized words (potential hallucinated proper nouns)
    original_caps = set(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', original))
    proposed_caps = set(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', proposed))
    new_caps = proposed_caps - original_caps

    for cap in new_caps:
        cap_lower = cap.lower()
        if cap_lower not in corpus_words and cap_lower.replace(' ', '-') not in corpus_words:
            warnings.append(f"NEW_PROPER_NOUN: '{cap}' - verify this exists in your experience")

    return warnings, passed

def run_validation(edits_path: str, corpus_path: str) -> List[ValidationResult]:
    """Validate all proposed edits."""
    with open(edits_path, 'r') as f:
        edits = json.load(f)

    corpus_words = load_corpus_words(corpus_path)
    results = []

    for edit in edits:
        warnings, passed = validate_edit(
            edit['original'],
            edit['proposed'],
            corpus_words
        )

        results.append(ValidationResult(
            bullet_id=edit.get('bullet_id', 'unknown'),
            original=edit['original'],
            proposed=edit['proposed'],
            keyword_added=edit.get('keyword_added', ''),
            char_count=len(edit['proposed']),
            warnings=warnings,
            passed=passed
        ))

    return results

# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Resume tailoring preprocessing and validation')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Preprocess command
    preprocess = subparsers.add_parser('preprocess', help='Extract keywords and analyze gaps')
    preprocess.add_argument('--jd', required=True, help='Path to job description')
    preprocess.add_argument('--resume', required=True, help='Path to resume')
    preprocess.add_argument('--corpus', required=True, help='Path to bullet corpus')
    preprocess.add_argument('--output', required=True, help='Output JSON path')

    # Validate command
    validate = subparsers.add_parser('validate', help='Validate proposed edits')
    validate.add_argument('--edits', required=True, help='Path to proposed edits JSON')
    validate.add_argument('--corpus', required=True, help='Path to bullet corpus')
    validate.add_argument('--output', required=True, help='Output JSON path')

    args = parser.parse_args()

    if args.command == 'preprocess':
        # Load inputs
        with open(args.jd, 'r') as f:
            jd_text = f.read()
        with open(args.resume, 'r') as f:
            resume_text = f.read()
        with open(args.corpus, 'r') as f:
            corpus_text = f.read()

        # Process
        keywords = extract_keywords(jd_text)
        bullets = parse_resume(resume_text)
        gaps = compute_gap_analysis(keywords, resume_text, corpus_text)

        # Sort gaps: missing primary first, then missing secondary, then explicit
        def gap_sort_key(g):
            status_order = {'missing': 0, 'explicit': 1}
            importance_order = {'primary': 0, 'secondary': 1}
            return (status_order.get(g.status, 2), importance_order.get(g.importance, 2))

        gaps.sort(key=gap_sort_key)

        # Output
        output = {
            'jd_file': args.jd,
            'resume_file': args.resume,
            'keywords': [asdict(k) for k in keywords],
            'bullets': [asdict(b) for b in bullets],
            'gaps': [asdict(g) for g in gaps],
            'summary': {
                'total_keywords': len(keywords),
                'explicit_matches': len([g for g in gaps if g.status == 'explicit']),
                'missing': len([g for g in gaps if g.status == 'missing']),
                'missing_primary': len([g for g in gaps if g.status == 'missing' and g.importance == 'primary']),
                'missing_secondary': len([g for g in gaps if g.status == 'missing' and g.importance == 'secondary']),
                'total_bullets': len(bullets),
            }
        }

        with open(args.output, 'w') as f:
            json.dump(output, f, indent=2)

        # Print summary
        print(f"\n{'='*60}")
        print("GAP ANALYSIS COMPLETE")
        print(f"{'='*60}")
        print(f"Keywords found: {output['summary']['total_keywords']}")
        print(f"  - Explicit in resume: {output['summary']['explicit_matches']}")
        print(f"  - Missing: {output['summary']['missing']} ({output['summary']['missing_primary']} primary)")
        print(f"Bullets parsed: {output['summary']['total_bullets']}")
        print(f"\nOutput written to: {args.output}")
        print(f"{'='*60}\n")

        # Print missing keywords
        print("MISSING KEYWORDS (prioritized):")
        for g in gaps:
            if g.status == 'missing':
                print(f"  [{g.importance.upper()}] {g.keyword} ({g.category})")

    elif args.command == 'validate':
        results = run_validation(args.edits, args.corpus)

        output = {
            'results': [asdict(r) for r in results],
            'summary': {
                'total': len(results),
                'passed': len([r for r in results if r.passed]),
                'failed': len([r for r in results if not r.passed]),
                'warnings': sum(len(r.warnings) for r in results),
            }
        }

        with open(args.output, 'w') as f:
            json.dump(output, f, indent=2)

        # Print summary
        print(f"\n{'='*60}")
        print("VALIDATION COMPLETE")
        print(f"{'='*60}")
        print(f"Total edits: {output['summary']['total']}")
        print(f"  - Passed: {output['summary']['passed']}")
        print(f"  - Failed: {output['summary']['failed']}")
        print(f"  - Total warnings: {output['summary']['warnings']}")
        print(f"\nOutput written to: {args.output}")
        print(f"{'='*60}\n")

        # Print failures
        for r in results:
            if not r.passed:
                print(f"\nFAILED: {r.bullet_id}")
                for w in r.warnings:
                    print(f"  - {w}")

if __name__ == '__main__':
    main()
