"""
similarity_evaluator.py
Originality and similarity evaluation engine for content adaptation.

Universal English Test Platform
Implements the metrics and threshold rules defined in docs/TASK-010B_ADAPTATION_SPEC.md (Section 6),
calibrated under TASK-011E for short, formulaic grammar items.

METRICS & THRESHOLDS:
1. N-gram Shingle Overlap (N >= 3) [Primary Rejection Signal]
   - Verbatim sequence of >= 3 consecutive non-target content words detected
   -> forbidden_shingle_detected = True -> REJECTED (Unconditional)

2. Jaccard Token Similarity [Primary Originality Signal]
   - Jaccard <= 0.40        -> PASS (VALIDATED)
   - 0.40 < Jaccard <= 0.50 -> REVIEW_REQUIRED
   - Jaccard > 0.50         -> REJECTED (Unconditional)

3. Normalized Levenshtein Similarity [Secondary Diagnostic Signal]
   - Dialogue scaffolding, quotation marks, formatting instructions, and redundant
     punctuation are normalized/stripped prior to Levenshtein calculation.
   - For standard text (len >= 40 chars after normalization):
     Levenshtein >= 0.45 -> REVIEW_REQUIRED.
   - For very short text (len < 40 chars after normalization):
     Levenshtein similarity MUST NOT by itself cause REVIEW_REQUIRED.
     Levenshtein contributes to REVIEW_REQUIRED only when combined with another
     meaningful similarity signal (e.g. elevated Jaccard token similarity >= 0.25).
"""

from typing import Dict, Any, List, Set, Tuple, Optional, Iterable
import re


# Regular expressions for tokens and structural extraction
PLACEHOLDER_REGEX = re.compile(r"\{\{gap_?\d*\}\}|_{2,}", re.IGNORECASE)
LEADING_NUMBER_REGEX = re.compile(r"^\s*\d+[\.\)]?\s*")
WORD_REGEX = re.compile(r"[a-zA-Z0-9]+(?:'[a-zA-Z0-9]+)?")

# Non-semantic dialogue scaffolding, instruction, and punctuation regexes
DIALOGUE_SPEAKER_REGEX = re.compile(r"(?i)\b(?:speaker\s*\d+|person\s*[a-z]|[a-z])\s*:\s*")
QUOTE_REGEX = re.compile(r"['\"‘’“”`]")
FORMATTING_INSTRUCTION_REGEX = re.compile(
    r"(?i)\(?\b(?:choose|identify|select|circle|fill|complete)\s+(?:two|three|one|\d+)?\s*(?:correct|valid)?\s*(?:answers?|responses?|options?)?\)?",
)
REDUNDANT_PUNCT_REGEX = re.compile(r"[⇒→\-><—–_~\|]+")


def normalize_text_for_comparison(text: str) -> str:
    """
    Normalizes sentence text before Levenshtein edit distance calculation:
    1. Strips leading question numbers (e.g. '1. ', '10 ')
    2. Strips gap placeholders and blanks ('{{gap_1}}', '_____')
    3. Strips formatting-only instruction prompts (e.g. 'Choose TWO correct answers')
    4. Strips non-semantic dialogue speaker labels (e.g. 'A:', 'B:', 'Speaker 1:')
    5. Strips quotation marks ('', "", ``, etc.)
    6. Strips redundant transformation punctuation and arrows ('⇒', '->', '---')
    7. Cleans dangling punctuation and collapses multiple spaces
    """
    if not text:
        return ""
    t = LEADING_NUMBER_REGEX.sub("", text)
    t = PLACEHOLDER_REGEX.sub(" ", t)
    t = FORMATTING_INSTRUCTION_REGEX.sub(" ", t)
    t = DIALOGUE_SPEAKER_REGEX.sub(" ", t)
    t = QUOTE_REGEX.sub("", t)
    t = REDUNDANT_PUNCT_REGEX.sub(" ", t)
    t = re.sub(r"[\s.,:;?!]+", " ", t).strip()
    return t


def extract_non_target_tokens(
    text: str,
    target_tokens: Optional[Iterable[str]] = None
) -> List[str]:
    """
    Cleans text by removing leading numbering, gap placeholders, punctuation,
    and optional target grammar tokens. Returns list of lowercased tokens.
    """
    if not text:
        return []

    # 1. Strip leading question numbering (e.g. '1 ', '10. ')
    cleaned = LEADING_NUMBER_REGEX.sub("", text)

    # 2. Remove gap placeholders (e.g. '{{gap_1}}', '{{gap1}}', '_____')
    cleaned = PLACEHOLDER_REGEX.sub(" ", cleaned)

    # 3. Strip formatting-only instruction prompts
    cleaned = FORMATTING_INSTRUCTION_REGEX.sub(" ", cleaned)

    # 4. Extract words (handles alphanumeric and internal contractions)
    raw_tokens = WORD_REGEX.findall(cleaned.lower())

    # 5. Filter target tokens if provided
    targets: Set[str] = set()
    if target_tokens:
        for t in target_tokens:
            targets.update(WORD_REGEX.findall(str(t).lower()))

    if targets:
        return [tok for tok in raw_tokens if tok not in targets]
    return raw_tokens


def compute_jaccard_similarity(tokens_a: List[str], tokens_b: List[str]) -> float:
    """
    Calculates Jaccard token similarity: |A ∩ B| / |A ∪ B|.
    Returns 0.0 if both token sets are empty.
    """
    set_a = set(tokens_a)
    set_b = set(tokens_b)

    union = set_a.union(set_b)
    if not union:
        return 0.0

    intersection = set_a.intersection(set_b)
    return round(len(intersection) / len(union), 4)


def extract_shingles(tokens: List[str], n: int = 3) -> List[Tuple[str, ...]]:
    """Generates consecutive n-grams from a list of tokens."""
    if len(tokens) < n:
        return []
    return [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def compute_shingle_overlap(
    tokens_source: List[str],
    tokens_adapted: List[str],
    n: int = 3
) -> Tuple[float, List[str]]:
    """
    Finds verbatim sequences of length >= n shared between source and adapted tokens.
    Returns (overlap_ratio, list_of_matching_shingles).
    """
    shingles_src = extract_shingles(tokens_source, n)
    shingles_adapt = extract_shingles(tokens_adapted, n)

    if not shingles_src:
        return 0.0, []

    src_set = set(shingles_src)
    adapt_set = set(shingles_adapt)

    matching = sorted(src_set.intersection(adapt_set))
    matching_strings = [" ".join(sh) for sh in matching]

    overlap_ratio = round(len(matching) / len(src_set), 4)
    return overlap_ratio, matching_strings


def compute_levenshtein_distance(s1: str, s2: str) -> int:
    """Computes standard Levenshtein edit distance using two rows."""
    if s1 == s2:
        return 0
    if len(s1) == 0:
        return len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1] + [0] * len(s2)
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (0 if c1 == c2 else 1)
            current_row[j + 1] = min(insertions, deletions, substitutions)
        previous_row = current_row

    return previous_row[len(s2)]


def compute_levenshtein_similarity(s1: str, s2: str) -> float:
    """
    Computes normalized Levenshtein similarity: 1.0 - (distance / max(len(s1), len(s2))).
    Returns 1.0 if both empty or identical; 0.0 if entirely different.
    """
    s1_clean = " ".join(s1.split()).lower()
    s2_clean = " ".join(s2.split()).lower()

    if s1_clean == s2_clean:
        return 1.0 if s1_clean != "" else 0.0

    max_len = max(len(s1_clean), len(s2_clean))
    if max_len == 0:
        return 0.0

    dist = compute_levenshtein_distance(s1_clean, s2_clean)
    similarity = 1.0 - (dist / max_len)
    return max(0.0, round(similarity, 4))


def evaluate_similarity(
    source_text: str,
    adapted_text: str,
    target_tokens: Optional[Iterable[str]] = None
) -> Dict[str, Any]:
    """
    Evaluates similarity between source and adapted text according to TASK-010B & TASK-011E specs.

    Calibration rules (TASK-011E):
    - Primary rejection signals: forbidden 3+ word shingle, Jaccard > 0.50.
    - Non-semantic dialogue scaffolding, quotes, instructions, and redundant symbols
      are normalized prior to Levenshtein calculation.
    - For text < 40 chars after normalization, Levenshtein >= 0.45 alone does NOT cause REVIEW_REQUIRED;
      it contributes to review only when combined with elevated token similarity (Jaccard >= 0.25).
    - For standard text (>= 40 chars), Levenshtein >= 0.45 triggers REVIEW_REQUIRED.

    Returns structured dict:
    - jaccard_similarity: float
    - shingle_overlap: float
    - levenshtein_similarity: float
    - forbidden_shingle_detected: bool
    - matching_shingles: List[str]
    - originality_status: 'VALIDATED' | 'REVIEW_REQUIRED' | 'REJECTED'
    - reasons: List[str]
    - source_tokens: List[str]
    - adapted_tokens: List[str]
    - normalized_source: str
    - normalized_adapted: str
    - is_short_text: bool
    """
    src_norm_str = normalize_text_for_comparison(source_text)
    adp_norm_str = normalize_text_for_comparison(adapted_text)

    tokens_src = extract_non_target_tokens(source_text, target_tokens)
    tokens_adp = extract_non_target_tokens(adapted_text, target_tokens)

    # 1. Exact / empty text handling
    if not source_text or not adapted_text:
        return {
            "jaccard_similarity": 1.0 if source_text == adapted_text else 0.0,
            "shingle_overlap": 1.0 if source_text == adapted_text else 0.0,
            "levenshtein_similarity": 1.0 if source_text == adapted_text else 0.0,
            "forbidden_shingle_detected": False,
            "matching_shingles": [],
            "originality_status": "REJECTED",
            "reasons": ["Empty source or adapted text provided."],
            "source_tokens": tokens_src,
            "adapted_tokens": tokens_adp,
            "normalized_source": src_norm_str,
            "normalized_adapted": adp_norm_str,
            "is_short_text": True,
        }

    if src_norm_str.lower() == adp_norm_str.lower():
        return {
            "jaccard_similarity": 1.0,
            "shingle_overlap": 1.0,
            "levenshtein_similarity": 1.0,
            "forbidden_shingle_detected": True if len(tokens_src) >= 3 else False,
            "matching_shingles": [" ".join(tokens_src[:3])] if len(tokens_src) >= 3 else [],
            "originality_status": "REJECTED",
            "reasons": ["Identical text: adapted sentence is unchanged from source after normalization."],
            "source_tokens": tokens_src,
            "adapted_tokens": tokens_adp,
            "normalized_source": src_norm_str,
            "normalized_adapted": adp_norm_str,
            "is_short_text": len(src_norm_str) < 40,
        }

    # 2. Compute metrics
    jaccard = compute_jaccard_similarity(tokens_src, tokens_adp)
    shingle_ratio, matching_shingles = compute_shingle_overlap(tokens_src, tokens_adp, n=3)
    lev_sim = compute_levenshtein_similarity(src_norm_str, adp_norm_str)

    forbidden_shingle = len(matching_shingles) > 0

    reasons: List[str] = []
    status = "VALIDATED"

    # Determine whether text qualifies as short (less than 40 chars after normalization)
    norm_len = min(len(src_norm_str), len(adp_norm_str))
    max_norm_len = max(len(src_norm_str), len(adp_norm_str))
    is_short = norm_len < 40

    # 3. Apply Calibrated Threshold Rules (TASK-011E)
    # Check A: Verbatim 3+ word non-target sequence (Primary Rejection Signal)
    if forbidden_shingle:
        status = "REJECTED"
        reasons.append(
            f"Forbidden verbatim 3+ word shingle detected: '{matching_shingles[0]}'"
            + (f" (+{len(matching_shingles) - 1} more)" if len(matching_shingles) > 1 else "")
        )

    # Check B: Jaccard Token Similarity (Primary Originality Signal)
    if jaccard > 0.50:
        status = "REJECTED"
        reasons.append(
            f"Jaccard token similarity ({jaccard:.4f}) exceeds rejection threshold (> 0.50)."
        )
    elif 0.40 < jaccard <= 0.50:
        if status != "REJECTED":
            status = "REVIEW_REQUIRED"
        reasons.append(
            f"Jaccard token similarity ({jaccard:.4f}) is in review zone (0.40 < J <= 0.50)."
        )

    # Check C: Levenshtein Distance (Secondary Diagnostic Signal)
    if status != "REJECTED":
        if not is_short:
            # Standard text (length >= 40 chars)
            if lev_sim >= 0.45:
                status = "REVIEW_REQUIRED"
                reasons.append(
                    f"Normalized Levenshtein similarity ({lev_sim:.4f}) exceeds threshold (< 0.45) on standard text (len={max_norm_len})."
                )
        else:
            # Very short text (< 40 chars after normalization):
            # Levenshtein >= 0.45 MUST NOT by itself cause REVIEW_REQUIRED.
            # Triggers REVIEW_REQUIRED only when combined with elevated token similarity (Jaccard >= 0.25).
            if lev_sim >= 0.45 and jaccard >= 0.25:
                status = "REVIEW_REQUIRED"
                reasons.append(
                    f"Short text (len={norm_len} < 40): combined elevated Levenshtein ({lev_sim:.4f} >= 0.45) and token similarity ({jaccard:.4f} >= 0.25)."
                )
            elif lev_sim >= 0.45:
                reasons.append(
                    f"Short text (len={norm_len} < 40): Levenshtein similarity ({lev_sim:.4f} >= 0.45) exempted due to low token similarity ({jaccard:.4f} < 0.25) and absence of verbatim shingles."
                )

    # Check D: Clean pass confirmation
    if status == "VALIDATED":
        reasons.append(
            "Passes all originality thresholds (Jaccard <= 0.40, Levenshtein calibrated, 0 forbidden shingles)."
        )

    return {
        "jaccard_similarity": jaccard,
        "shingle_overlap": shingle_ratio,
        "levenshtein_similarity": lev_sim,
        "forbidden_shingle_detected": forbidden_shingle,
        "matching_shingles": matching_shingles,
        "originality_status": status,
        "reasons": reasons,
        "source_tokens": tokens_src,
        "adapted_tokens": tokens_adp,
        "normalized_source": src_norm_str,
        "normalized_adapted": adp_norm_str,
        "is_short_text": is_short,
    }
