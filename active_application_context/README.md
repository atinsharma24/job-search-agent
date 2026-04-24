# Active Application Context

This directory stores the minimal runtime state for standard application runs.

## Standard Loop

1. Read `background_agent_state.json`.
2. Process the current job packet only.
3. If `stack_match >= 0.70`, apply immediately with fast-path tailoring.
4. If `stack_match < 0.70`, log `skip`.
5. If blocked, log `blocked`.
6. Update state and tracker, then terminate.

## Deferred Context

- Interview libraries
- session status logs
- historical run summaries

Do not load deferred context during standard application runs.
