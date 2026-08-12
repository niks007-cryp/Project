"""
Deterministic Candidate Feature Extractor for Content Intelligence Engine.
"""

import re
from typing import List, Set
from clipper.domain.models import ClipCandidate, CandidateFeatureVector


HOOK_KEYWORDS: Set[str] = {"why", "how", "what", "secret", "never", "always", "best", "worst", "stop", "ever"}
CURIOSITY_KEYWORDS: Set[str] = {"hidden", "secret", "nobody", "truth", "discover", "reason", "mystery", "actual"}
EMOTION_KEYWORDS: Set[str] = {"amazing", "incredible", "crazy", "shocking", "unbelievable", "worst", "insane", "love", "hate"}
PAYOFF_KEYWORDS: Set[str] = {"finally", "result", "turns out", "so", "therefore", "conclusion", "lesson"}
DEPENDENT_PRONOUNS: Set[str] = {"he", "she", "they", "this", "that", "these", "those", "also", "and"}


class FeatureExtractor:
    """Computes deterministic candidate feature metrics from text and timing."""

    @classmethod
    def extract_features(cls, candidate: ClipCandidate) -> CandidateFeatureVector:
        text = candidate.text.strip().lower()
        words = re.findall(r"\w+", text)
        word_count = len(words)

        if word_count == 0:
            return CandidateFeatureVector()

        duration = max(candidate.duration_seconds, 1.0)
        wps = word_count / duration

        # 1. Hook Strength
        first_5 = words[:5]
        hook_hits = sum(1 for w in first_5 if w in HOOK_KEYWORDS)
        has_q_mark = "?" in candidate.text[:50]
        hook_strength = min(1.0, 0.3 + (hook_hits * 0.25) + (0.3 if has_q_mark else 0.0))

        # 2. Curiosity Gap
        curiosity_hits = sum(1 for w in words if w in CURIOSITY_KEYWORDS)
        curiosity_gap = min(1.0, 0.2 + (curiosity_hits * 0.3))

        # 3. Emotional Intensity
        emotion_hits = sum(1 for w in words if w in EMOTION_KEYWORDS)
        has_excl = "!" in candidate.text
        emotional_intensity = min(1.0, 0.2 + (emotion_hits * 0.25) + (0.2 if has_excl else 0.0))

        # 4. Information Value (Lexical Diversity)
        unique_ratio = len(set(words)) / word_count
        information_value = round(min(1.0, 0.3 + (unique_ratio * 0.7)), 4)

        # 5. Story Completeness
        payoff_hits = sum(1 for w in words if w in PAYOFF_KEYWORDS)
        has_period_at_end = candidate.text.strip()[-1:] in [".", "!", "?"]
        story_completeness = min(1.0, 0.4 + (payoff_hits * 0.2) + (0.3 if has_period_at_end else 0.0))

        # 6. Pacing Quality (Optimal ~2.0 to 3.5 words/sec)
        if 1.8 <= wps <= 3.5:
            pacing_quality = 0.9
        elif 1.2 <= wps < 1.8 or 3.5 < wps <= 4.5:
            pacing_quality = 0.6
        else:
            pacing_quality = 0.3

        # 7. Context Independence (Penalty if starting with dependent pronoun)
        first_word = words[0] if words else ""
        context_indep = 0.4 if first_word in DEPENDENT_PRONOUNS else 0.95

        # 8. Repetition Penalty
        bigrams = list(zip(words[:-1], words[1:]))
        bigram_count = len(bigrams)
        unique_bigrams = len(set(bigrams))
        rep_ratio = (1.0 - (unique_bigrams / bigram_count)) if bigram_count > 0 else 0.0
        repetition_penalty = round(min(1.0, rep_ratio * 2.0), 4)

        return CandidateFeatureVector(
            hook_strength=round(hook_strength, 4),
            curiosity_gap=round(curiosity_gap, 4),
            emotional_intensity=round(emotional_intensity, 4),
            information_value=information_value,
            story_completeness=round(story_completeness, 4),
            novelty=round(unique_ratio, 4),
            payoff=round(min(1.0, 0.3 + (payoff_hits * 0.35)), 4),
            pacing_quality=round(pacing_quality, 4),
            context_independence=round(context_indep, 4),
            repetition_penalty=repetition_penalty,
        )
