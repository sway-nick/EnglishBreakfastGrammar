from __future__ import annotations

from dataclasses import dataclass, field


# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class OptionData:
    option_id: str
    order:     int
    text:      str


@dataclass
class GapData:
    gap_id:         str
    gap_order:      int
    input_control:  str           # "select" | "text"
    options:        list[OptionData] = field(default_factory=list)
    already_filled: bool = False  # True if correct_answer already set


@dataclass
class QuestionData:
    question_id:    str
    order:          int
    response_model: str           # "gap" | "single_choice"
    content:        str
    gaps:           list[GapData]     = field(default_factory=list)
    options:        list[OptionData]  = field(default_factory=list)


@dataclass
class ExerciseBatch:
    lesson_title:    str
    lesson_id:       str
    exercise_id:     str
    exercise_title:  str
    instruction:     str
    example_source:  str | None
    example_target:  str | None
    questions:       list[QuestionData] = field(default_factory=list)

    def is_complete(self) -> bool:
        """
        Returns True only if every gap has a valid correct_answer
        and every select/single_choice option has is_correct set.
        Used for Q-P2: skip already-filled batches.
        """
        for q in self.questions:
            for gap in q.gaps:
                if not gap.already_filled:
                    return False
        return True


@dataclass
class ValidatedGap:
    gap_id:           str
    correct_answer:   str
    accepted_answers: list[str]   # full list including correct_answer


@dataclass
class ValidatedOption:
    option_id:  str
    is_correct: bool


@dataclass
class ValidatedQuestion:
    question_id: str
    gaps:        list[ValidatedGap]
    options:     list[ValidatedOption]


@dataclass
class ValidationResult:
    exercise_id: str
    ok:          bool
    questions:   list[ValidatedQuestion] = field(default_factory=list)
    errors:      list[str]               = field(default_factory=list)
