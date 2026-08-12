# CANDIDATE SCORING ENGINE SPECIFICATION — LOCAL AI CLIPPER

## 1. Feature Metrics
- **Hook Strength (20%):** Evaluates early keyword presence and question marks.
- **Curiosity Gap (15%):** Measures information gap keywords ("secret", "hidden", "truth").
- **Story Completeness (15%):** Evaluates payoff words and end punctuation.
- **Information Value (15%):** Evaluates lexical diversity (unique words / total words).
- **Emotional Intensity (10%):** Measures high-energy emotional vocabulary.
- **Pacing Quality (10%):** Optimal speech rate (1.8 - 3.5 words/sec).
- **Context Independence (10%):** Penalizes initial dependent pronouns ("he", "this", "that").
- **Novelty (5%):** Measures distinct vocabulary ratio.
- **Repetition Penalty:** Subtracts points for repeated n-grams.

## 2. Score Formula
$$\text{Composite Score} = \sum (\text{Feature}_i \times \text{Weight}_i) - \text{Repetition Penalty}$$
Scaled between 0.0 and 100.0.
