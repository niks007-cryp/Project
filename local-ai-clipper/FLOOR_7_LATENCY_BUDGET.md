# FLOOR 7 LATENCY BUDGET & BENCHMARK TARGETS

## Response Time Targets (Local Web API)

- **GET `/api/health`:** <= 10 ms
- **GET `/api/projects`:** <= 15 ms
- **GET `/api/jobs`:** <= 20 ms
- **POST `/api/providers/set` (BYOK):** <= 25 ms
- **POST `/api/providers/test`:** <= 500 ms (depends on provider network ping)
- **POST `/api/jobs/create`:** <= 30 ms
