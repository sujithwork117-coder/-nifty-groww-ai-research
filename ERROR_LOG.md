# Error Log

Runtime failures from bounded experiments are appended to `data/agent_state/errors.jsonl`. Errors are re-raised after being recorded so a caller cannot mistake a failed experiment for a valid result.

## Current Known Issues

- Ekalayava stop-loss remains undefined by the canonical strategy definition.
- Out-of-sample evidence is insufficient for accepting strategy modifications.
- 2026-09-23: autonomous demo stopped before planning because `RESEARCH_LLM_PROVIDER` and `RESEARCH_LLM_API_KEY` were missing. This is a configuration block, not a research result; no fallback response was generated.