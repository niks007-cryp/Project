# FLOOR 4 EVALUATION & BENCHMARKING SPECIFICATION

## 1. Metrics & Formulas

### Precision@K
$$\text{Precision@K} = \frac{\text{Relevant Candidates in Top-K}}{K}$$

### Normalized Discounted Cumulative Gain (NDCG@K)
$$\text{DCG@K} = \sum_{i=1}^{K} \frac{rel_i}{\log_2(i + 1)}$$
$$\text{NDCG@K} = \frac{\text{DCG@K}}{\text{IDCG@K}}$$

### Pairwise Ranking Accuracy
$$\text{Pairwise Accuracy} = \frac{\text{Correctly Ordered Candidate Pairs}}{\text{Total Candidate Pairs}}$$

## 2. Evaluation Dataset Fixture
Ground-truth benchmark dataset stored at `tests/fixtures/candidate_benchmark.json` containing 10 transcripts with human-labeled candidate relevance scores (0 to 3 scale).
