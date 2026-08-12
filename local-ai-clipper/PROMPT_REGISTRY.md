# PROMPT REGISTRY & INJECTION DEFENSE SPECIFICATION — LOCAL AI CLIPPER

## 1. Registered Production Prompts

| Prompt Key | ID | Version | Description | Input Schema | Output Schema |
|------------|----|---------|-------------|--------------|---------------|
| `clip_evaluation_v1` | `clip_eval_v1` | `1.0.0` | Viral appeal & narrative completeness analysis | `candidate_id`, `candidate_text`, `context_text` | `candidate_id`, `hook_score`, `curiosity_score`, `value_score`, `emotion_score`, `story_score`, `hook_summary`, `reasoning` |

## 2. Prompt Injection Defense Architecture
All untrusted user or transcript text MUST be quarantined inside `<untrusted_transcript_data>` XML-style data tags. The system prompt explicitly instructs the LLM to treat encapsulated text strictly as passive DATA and ignore any embedded command directives.
