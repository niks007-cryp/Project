# FLOOR 6 LATENCY BUDGET & PERFORMANCE BENCHMARKS

## Real-Time Factor (RTF) Targets

$$\text{RTF} = \frac{\text{Render Execution Time (seconds)}}{\text{Clip Source Duration (seconds)}}$$

- **Target CPU RTF:** <= 0.5x (Renders 30s clip in <= 15s).
- **Target GPU RTF:** <= 0.15x (Renders 30s clip in <= 4.5s).

## Benchmarking Scenarios
1. **Short Clip:** 15 seconds (1080x1920 @ 30fps).
2. **Medium Clip:** 30 seconds (1080x1920 @ 30fps).
3. **Long Clip:** 60 seconds (1080x1920 @ 30fps).
