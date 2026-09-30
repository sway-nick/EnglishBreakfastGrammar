"""Adaptation Generation Rules & Guidelines (TASK-011H).

Universal English Test Platform
Defines the core principles, generation instructions, priority hierarchy,
and high-risk mutation safeguards for content adaptation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


# Canonical Generation Instruction for all AI Models and Prompts
SYSTEM_GENERATION_INSTRUCTION = (
    "Preserve the source correct answer whenever possible. Prefer changing the situation "
    "and vocabulary around the grammar target rather than changing the grammatical form "
    "that determines the answer."
)

# Adaptation Priority Hierarchy (1-8)
ADAPTATION_PRIORITIES = [
    "1. Preserve the same correct answer whenever reasonably possible.",
    "2. Change context, names, objects, places, situations, and non-target vocabulary.",
    "3. Preserve the exact grammatical mechanism being tested.",
    "4. Preserve response_model.",
    "5. Preserve number of gaps/options.",
    "6. Avoid unnecessary grammatical mutations.",
    "7. Avoid one-to-one lexical substitution that leaves the whole sentence structurally identical.",
    "8. Do not force an answer change merely to make the text look different.",
]

# 13 High-Risk Grammatical Mutations that threaten answer validity
HIGH_RISK_MUTATIONS = {
    "gender": "Changing subject/object gender when pronouns, possessives, or agreement depend on it.",
    "singular_plural": "Changing grammatical number (singular ↔ plural, this ↔ these, child ↔ children).",
    "grammatical_person": "Mutating 1st/2nd/3rd person (I ↔ they, we ↔ he).",
    "subject": "Altering subject entity in a way that shifts person, number, or animacy.",
    "pronoun": "Changing pronoun references or cases (he ↔ they, me ↔ us, him ↔ her).",
    "possessive": "Shifting possessive adjectives or pronouns (his ↔ her ↔ their ↔ its).",
    "determiner": "Altering demonstratives or quantifiers (this ↔ these, that ↔ those, much ↔ many).",
    "article": "Changing article environments (a/an ↔ some ↔ the ↔ zero article).",
    "countability": "Switching countable nouns to uncountable or vice-versa (milk, advice, furniture).",
    "tense_aspect": "Shifting primary tense/aspect (present simple ↔ past simple, continuous ↔ perfect).",
    "auxiliary": "Changing auxiliary requirements (do/does, is/are, has/have, modal auxiliaries).",
    "verb_agreement": "Altering subject-verb agreement balance (singular subject with plural verb).",
    "comparative_superlative": "Switching degrees of comparison or morphological types (-er/-est ↔ more/most).",
}

# Quality Rule Definition
QUALITY_RULE = {
    "goal": "Natural English with identical educational objective and identical correct-answer logic, NOT maximum textual difference.",
    "requirements": [
        "Independent wording and context.",
        "Same educational objective and CEFR difficulty.",
        "Same correct-answer logic.",
        "Natural, idiomatic English phrasing.",
    ],
}


def build_adaptation_prompt(
    question_id: str,
    response_model: str,
    source_text: str,
    source_options: Optional[List[Dict[str, Any]]] = None,
    source_gaps: Optional[List[Dict[str, Any]]] = None,
    lesson_title: str = "",
    cefr_level: str = "",
    grammar_target: str = "",
) -> Dict[str, Any]:
    """Construct an adaptation prompt payload adhering to TASK-011H principles."""
    return {
        "instruction": SYSTEM_GENERATION_INSTRUCTION,
        "priorities": ADAPTATION_PRIORITIES,
        "context": {
            "question_id": question_id,
            "response_model": response_model,
            "lesson_title": lesson_title,
            "cefr_level": cefr_level,
            "grammar_target": grammar_target,
        },
        "source": {
            "text": source_text,
            "options": source_options or [],
            "gaps": source_gaps or [],
        },
        "constraints": [
            f"Preserve response_model: '{response_model}'.",
            "Preserve the exact correct answer(s) whenever reasonably possible.",
            "Do NOT mutate singular/plural, pronouns, tense, or gender unless strictly necessary.",
            "Change characters, settings, objects, and narrative scenarios to ensure original authorship.",
        ],
    }
