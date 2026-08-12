"""
Word Error Rate (WER) Evaluator for Local AI Clipper.
"""

import re
import editdistance
from typing import Dict, Any, List


def normalize_text_for_wer(text: str) -> List[str]:
    """Normalizes text by removing punctuation and converting to lowercase word tokens."""
    clean = re.sub(r"[^\w\s]", "", text).lower().strip()
    return clean.split()


class WEREvaluator:
    """Calculates Word Error Rate (WER) metrics against reference ground-truth transcripts."""

    @classmethod
    def evaluate(cls, reference_text: str, hypothesis_text: str) -> Dict[str, Any]:
        ref_words = normalize_text_for_wer(reference_text)
        hyp_words = normalize_text_for_wer(hypothesis_text)

        if not ref_words:
            wer = 0.0 if not hyp_words else 1.0
            return {
                "wer": wer,
                "distance": len(hyp_words),
                "ref_word_count": 0,
                "hyp_word_count": len(hyp_words),
            }

        dist = editdistance.eval(ref_words, hyp_words)
        wer = round(dist / len(ref_words), 4)

        return {
            "wer": wer,
            "edit_distance": dist,
            "ref_word_count": len(ref_words),
            "hyp_word_count": len(hyp_words),
            "reference_text_sample": " ".join(ref_words[:10]),
            "hypothesis_text_sample": " ".join(hyp_words[:10]),
        }
