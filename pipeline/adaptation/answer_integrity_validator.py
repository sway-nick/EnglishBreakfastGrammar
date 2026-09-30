"""Answer Integrity & Grammatical Dependency Validator (TASK-011H).

Universal English Test Platform
Validates:
1. Preservation of the source correct answer whenever reasonably possible.
2. Detection of high-risk grammatical mutations (singular/plural, gender, pronoun, countability, etc.).
3. Semantic and syntactic validity of the correct answer within the adapted sentence context.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


UNCOUNTABLE_NOUNS = {
    "milk", "water", "tea", "coffee", "juice", "bread", "butter", "cheese",
    "information", "advice", "furniture", "luggage", "baggage", "homework",
    "money", "traffic", "weather", "music", "news", "equipment", "rice", "sugar"
}

MASCULINE_SUBJECTS = {
    "he", "john", "tom", "peter", "david", "jack", "michael", "george",
    "robert", "liam", "ethan", "brother", "father", "boy", "man", "uncle", "son"
}

FEMININE_SUBJECTS = {
    "she", "kate", "julia", "mary", "anna", "sarah", "emily", "sister",
    "mother", "girl", "woman", "aunt", "daughter"
}

PLURAL_PRONOUNS_AND_DEMONSTRATIVES = {
    "they", "them", "these", "those", "we", "us"
}

SINGULAR_PRONOUNS_AND_DEMONSTRATIVES = {
    "he", "she", "it", "this", "that", "him", "her"
}


@dataclass
class AnswerIntegrityResult:
    """Deterministic validation outcome for answer integrity and grammar dependencies."""
    is_valid: bool
    answer_preserved: bool
    source_correct_answers: List[str]
    adapted_correct_answers: List[str]
    is_answer_valid: bool
    high_risk_mutations: List[str] = field(default_factory=list)
    review_required: bool = False
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def normalize_token(s: str) -> str:
    """Normalize answer token for whitespace and punctuation tolerance."""
    if s is None:
        return ""
    s_clean = str(s).strip().lower().replace("’", "'").replace("‘", "'").replace("\ufffd", "'")
    cleaned = re.sub(r"[^\w\s'-]", "", s_clean)
    return " ".join(cleaned.split())


def detect_high_risk_mutations(
    source_text: str,
    adapted_text: str,
    source_answers: List[str],
    adapted_answers: List[str],
) -> List[str]:
    """Detect presence of dangerous mutations that can destabilize answer integrity."""
    mutations: List[str] = []
    s_norm = f" {normalize_token(source_text)} "
    a_norm = f" {normalize_token(adapted_text)} "

    # 1. Singular ↔ Plural mutations
    s_has_plural_subj = bool(re.search(r"\b(and\b|they\b|we\b|these\b|those\b|\w+s\s+(are|were|have))\b", s_norm))
    a_has_plural_subj = bool(re.search(r"\b(and\b|they\b|we\b|these\b|those\b|\w+s\s+(are|were|have))\b", a_norm))
    if s_has_plural_subj != a_has_plural_subj:
        mutations.append("singular_plural: Subject/demonstrative number shifted between singular and plural.")

    # 2. Gender mutations
    s_words = set(re.findall(r"\b[a-z]+\b", s_norm))
    a_words = set(re.findall(r"\b[a-z]+\b", a_norm))
    s_has_fem = bool(s_words & FEMININE_SUBJECTS)
    s_has_masc = bool(s_words & MASCULINE_SUBJECTS)
    a_has_fem = bool(a_words & FEMININE_SUBJECTS)
    a_has_masc = bool(a_words & MASCULINE_SUBJECTS)

    if (s_has_fem and a_has_masc and not a_has_fem) or (s_has_masc and a_has_fem and not a_has_masc):
        mutations.append("gender: Gender of primary person shifted.")

    # 3. Pronoun / Person mutations
    s_person = 1 if re.search(r"\b(i|me|my|mine|we|us|our)\b", s_norm) else (2 if "you" in s_norm else 3)
    a_person = 1 if re.search(r"\b(i|me|my|mine|we|us|our)\b", a_norm) else (2 if "you" in a_norm else 3)
    if s_person != a_person:
        mutations.append("pronoun: Grammatical person shifted (1st, 2nd, or 3rd person).")

    # 4. Countability / Article shifts
    s_has_uncount = any(f" {u} " in s_norm for u in UNCOUNTABLE_NOUNS)
    a_has_uncount = any(f" {u} " in a_norm for u in UNCOUNTABLE_NOUNS)
    if s_has_uncount != a_has_uncount:
        mutations.append("countability: Countable vs uncountable noun environment shifted.")

    return mutations


def verify_answer_syntactic_validity(
    adapted_text: str,
    correct_answers: List[str],
    response_model: str,
) -> Tuple[bool, List[str]]:
    """Verify that the adapted sentence independently makes the correct answer valid."""
    errors: List[str] = []
    text_lower = adapted_text.lower()

    for ans in correct_answers:
        ans_norm = normalize_token(ans)

        # 1. Article 'a' / 'an' before uncountable or plural noun
        if ans_norm in ("a", "an"):
            # Check what follows {{gap}} or the blank
            match = re.search(r"(\{\{gap_?\d*\}\}|_{2,})\s+([a-z]+)", text_lower)
            if match:
                next_word = match.group(2)
                if next_word in UNCOUNTABLE_NOUNS:
                    errors.append(f"Indefinite article '{ans}' is ungrammatical before uncountable noun '{next_word}'.")
                elif next_word.endswith("s") and next_word not in ("glass", "class", "bus", "pass"):
                    errors.append(f"Indefinite article '{ans}' is ungrammatical before plural noun '{next_word}'.")

        # 2. Subject-verb agreement clash with plural subjects
        # e.g., 'Tom and Jack is...' or 'The students has...'
        has_compound_or_plural = bool(re.search(r"\b([a-z]+\s+and\s+[a-z]+|they|these students|both)\b", text_lower))
        if has_compound_or_plural:
            if ans_norm in ("is", "was", "has", "does") or (ans_norm.endswith("s") and ans_norm not in ("is", "was", "has", "this", "us", "yes")):
                errors.append(f"Plural/compound subject conflicts with singular verb form '{ans}'.")

        # 3. Pronoun gender clash
        # e.g. male subject with 'her' / 'herself' in pronoun target
        words = set(re.findall(r"\b[a-z]+\b", text_lower))
        has_masc_subj = bool(words & MASCULINE_SUBJECTS)
        has_fem_subj = bool(words & FEMININE_SUBJECTS)
        if has_masc_subj and not has_fem_subj:
            if ans_norm in ("her", "hers", "herself"):
                errors.append(f"Masculine subject antecedent conflicts with feminine pronoun answer '{ans}'.")
        elif has_fem_subj and not has_masc_subj:
            if ans_norm in ("him", "his", "himself"):
                errors.append(f"Feminine subject antecedent conflicts with masculine pronoun answer '{ans}'.")

    return (len(errors) == 0, errors)


def validate_answer_integrity(
    source_item: Dict[str, Any],
    adapted_item: Dict[str, Any],
) -> AnswerIntegrityResult:
    """Perform rigorous Answer Integrity validation between source and adapted questions."""
    response_model = source_item.get("response_model", "single_choice")
    source_text = source_item.get("content") or source_item.get("text") or ""
    adapted_text = adapted_item.get("adapted_text") or adapted_item.get("text") or ""

    reasons: List[str] = []

    # 1. Extract source correct answers
    s_correct: List[str] = []
    if response_model in ("single_choice", "multiple_choice"):
        s_opts = source_item.get("options", [])
        s_correct = [str(o.get("text") or o.get("value")) for o in s_opts if o.get("is_correct")]
    elif response_model == "gap":
        s_gaps = source_item.get("gaps", [])
        for g in s_gaps:
            c_ans = g.get("correct_answer")
            if c_ans is not None:
                s_correct.append(str(c_ans))
            elif "options" in g:
                corr_opts = [str(o.get("text") or o.get("value")) for o in g["options"] if o.get("is_correct")]
                s_correct.extend(corr_opts)

    # 2. Extract adapted correct answers
    a_correct: List[str] = []
    if response_model in ("single_choice", "multiple_choice"):
        a_opts = adapted_item.get("options", [])
        a_correct = [str(o.get("adapted_text") or o.get("text") or o.get("value")) for o in a_opts if o.get("adapted_is_correct") or o.get("is_correct")]
    elif response_model == "gap":
        a_gaps = adapted_item.get("gaps", [])
        for g in a_gaps:
            c_ans = g.get("adapted_correct_answer") or g.get("correct_answer")
            if c_ans is not None:
                a_correct.append(str(c_ans))
            elif "options" in g:
                corr_opts = [str(o.get("adapted_text") or o.get("text") or o.get("value")) for o in g["options"] if o.get("adapted_is_correct") or o.get("is_correct")]
                a_correct.extend(corr_opts)

    # 3. Check answer preservation
    answer_preserved = False
    if response_model == "single_choice":
        s_norm = normalize_token(s_correct[0]) if s_correct else ""
        a_norm = normalize_token(a_correct[0]) if a_correct else ""
        answer_preserved = (s_norm == a_norm) and bool(s_norm)
    elif response_model == "multiple_choice":
        s_set = {normalize_token(x) for x in s_correct}
        a_set = {normalize_token(x) for x in a_correct}
        answer_preserved = (s_set == a_set) and bool(s_set)
    elif response_model == "gap":
        if len(s_correct) == len(a_correct) and s_correct:
            answer_preserved = all(normalize_token(s) == normalize_token(a) for s, a in zip(s_correct, a_correct))
        else:
            answer_preserved = False

    review_required = False
    if not answer_preserved:
        review_required = True
        reasons.append(
            f"Correct answer diverged from source: source={s_correct}, adapted={a_correct}. Flagged for review."
        )

    # 4. Check for high-risk mutations
    high_risk_mutations = detect_high_risk_mutations(source_text, adapted_text, s_correct, a_correct)
    if high_risk_mutations:
        reasons.extend(high_risk_mutations)

    # 5. Check semantic/syntactic validity of the answer in the adapted text
    is_answer_valid, validity_errors = verify_answer_syntactic_validity(adapted_text, a_correct, response_model)
    if not is_answer_valid:
        review_required = True
        reasons.extend(validity_errors)

    # Overall validity (syntactically valid + structural match)
    is_valid = is_answer_valid and len(s_correct) == len(a_correct)

    return AnswerIntegrityResult(
        is_valid=is_valid,
        answer_preserved=answer_preserved,
        source_correct_answers=s_correct,
        adapted_correct_answers=a_correct,
        is_answer_valid=is_answer_valid,
        high_risk_mutations=high_risk_mutations,
        review_required=review_required,
        reasons=reasons,
    )
