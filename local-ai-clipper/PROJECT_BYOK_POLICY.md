# PROJECT-WIDE BYOK & USER-CONTROLLED AI PROVIDER POLICY

**System:** Local-First Automated AI Video Clipping & Reframing Platform  
**Scope:** Applies retroactively to Floors 1–5 and prospectively to all future floors.

---

## Mandatory Architecture Rules

1. **User Owns API Configuration:** Zero hardcoded API keys or provider secrets in `.py`, `.ts`, `.json`, Dockerfiles, logs, manifests, or test fixtures.
2. **User-Controlled Provider Settings:** Configurable `Provider Name`, `API Key`, `Model`, and `Endpoint URL` without source code modification.
3. **Provider Abstraction:** `LLMProvider` interface hierarchy (`GeminiProvider`, `OpenAIProvider`, `OpenRouterProvider`, `LocalLLMProvider`, `MockLLMProvider`).
4. **User Decides Provider:** No silent paid external API calls. Unconfigured providers raise `EXTERNAL AI PROVIDER NOT CONFIGURED` and fall back to local processing.
5. **Secure API Key Storage:** Encrypted DPAPI / KeyVault protected storage on Windows. Keys never logged or serialized in plaintext.
6. **Key Masking:** Secrets formatted as `****************ABCD` in outputs and displays.
7. **Connection Validation:** `clipper provider test <name>` validates credentials with a minimal provider ping before pipeline run.
8. **No Secret Fallbacks:** Zero hidden developer keys or silent provider switching.
9. **Provenance Tracking:** Non-secret provider provenance (`provider_name`, `model_name`, `prompt_version`, `config_hash`) logged cleanly.
