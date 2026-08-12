"""
Unit Tests for WER Evaluator.
"""

from clipper.core.transcription.wer_evaluator import WEREvaluator


def test_wer_evaluator_exact_match():
    ref = "The quick brown fox jumps over the lazy dog."
    hyp = "The quick brown fox jumps over the lazy dog."

    res = WEREvaluator.evaluate(ref, hyp)
    assert res["wer"] == 0.0
    assert res["edit_distance"] == 0
    assert res["ref_word_count"] == 9


def test_wer_evaluator_substitutions_and_deletions():
    ref = "Welcome to the local AI video clipping platform."
    hyp = "Welcome to the local video clipping platform."

    res = WEREvaluator.evaluate(ref, hyp)
    assert res["wer"] > 0.0
    assert res["edit_distance"] == 1  # Deletion of 'AI'
    assert res["ref_word_count"] == 8
