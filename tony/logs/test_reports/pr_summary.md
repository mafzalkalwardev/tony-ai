# PR Summary Draft

## Git Status
```text
M .gitignore
 M README.md
 M config/permissions.json
 M config/settings.json
 M docs/COMMANDS.md
 M docs/ROADMAP.md
 M docs/SAFETY.md
 M requirements.txt
 M tony/app.py
 M tony/core/agent.py
 M tony/core/command_parser.py
 M tony/core/memory.py
 M tony/core/ollama_client.py
 M tony/core/planner.py
 M tony/core/safety.py
 M tony/core/task_runner.py
 M tony/tools/browser_tool.py
 M tony/ui/main_window.py
 M tony/ui/styles.qss
 M tony/voice/stt.py
 M tony/voice/tts.py
 M tony/voice/wake_word.py
?? .github/
?? CHANGELOG.md
?? VERSION
?? assets/
?? docs/ACTION_RECORDER.md
?? docs/BUSINESS_OPERATOR.md
?? docs/CODING_WORKFLOWS.md
?? docs/GITHUB_OPERATOR.md
?? docs/LAPTOP_OPERATOR.md
?? docs/LIVE_VOICE.md
?? docs/RELEASE.md
?? docs/TEACH_MODE.md
?? docs/TESTING.md
?? docs/VISION_MODE.md
?? docs/WORKFLOW_MEMORY.md
?? docs/screenshots/
?? scripts/
?? tests/conftest.py
?? tests/test_action_recorder_safety.py
?? tests/test_assistant_brain.py
?? tests/test_business_tool.py
?? tests/test_command_normalizer.py
?? tests/test_git_tool.py
?? tests/test_github_operator.py
?? tests/test_github_operator_safety.py
?? tests/test_intent_router.py
?? tests/test_laptop_operator_safety.py
?? tests/test_live_voice_safety.py
?? tests/test_memory.py
?? tests/test_observe_mode_safety.py
?? tests/test_project_detector.py
?? tests/test_prompt_generator.py
?? tests/test_reply_builder.py
?? tests/test_screen_context.py
?? tests/test_screen_recorder_safety.py
?? tests/test_smoke_launch.py
?? tests/test_ui_imports.py
?? tests/test_vision_safety.py
?? tests/test_voice_command_pipeline.py
?? tests/test_voice_runtime.py
?? tests/test_voice_safety.py
?? tests/test_voice_setup.py
?? tests/test_wake_engine.py
?? tests/test_wake_word.py
?? tests/test_workflow_engine.py
?? tests/test_workflow_memory.py
?? tests/test_workflow_teacher.py
?? tests/test_workspace.py
?? tony/core/approval_manager.py
?? tony/core/assistant_brain.py
?? tony/core/business_memory.py
?? tony/core/command_normalizer.py
?? tony/core/context_manager.py
?? tony/core/intent_router.py
?? tony/core/live_state.py
?? tony/core/logging_config.py
?? tony/core/observation_manager.py
?? tony/core/project_detector.py
?? tony/core/project_profile.py
?? tony/core/reply_builder.py
?? tony/core/screen_context.py
?? tony/core/skill_registry.py
?? tony/core/workflow_engine.py
?? tony/core/workflow_memory.py
?? tony/core/workspace.py
?? tony/logs/test_reports/
?? tony/logs/voice/
?? tony/tools/action_recorder.py
?? tony/tools/app_tool.py
?? tony/tools/business_tool.py
?? tony/tools/code_analyzer.py
?? tony/tools/github_operator.py
?? tony/tools/macro_player.py
?? tony/tools/project_tool.py
?? tony/tools/prompt_generator.py
?? tony/tools/repo_analyzer.py
?? tony/tools/report_generator.py
?? tony/tools/screen_recorder.py
?? tony/tools/screenshot_tool.py
?? tony/tools/task_planner.py
?? tony/tools/vision_tool.py
?? tony/tools/window_tool.py
?? tony/tools/workflow_player.py
?? tony/tools/workflow_teacher.py
?? tony/voice/audio_waveform.py
?? tony/voice/live_listener.py
?? tony/voice/vad.py
?? tony/voice/voice_setup.py
?? tony/voice/wake_engine.py
```

## Diff Stat
```text
.gitignore                  |   3 +-
 README.md                   | 205 +++++++++++++++++-----
 config/permissions.json     |   5 +-
 config/settings.json        |  56 ++++++
 docs/COMMANDS.md            |  92 ++++++++++
 docs/ROADMAP.md             |  49 ++++--
 docs/SAFETY.md              | 136 +++++++++++++++
 requirements.txt            |  10 ++
 tony/app.py                 |  14 +-
 tony/core/agent.py          | 373 ++++++++++++++++++++++++++++++++++++---
 tony/core/command_parser.py | 172 +++++++++++++++++-
 tony/core/memory.py         | 135 +++++++++++++-
 tony/core/ollama_client.py  |   6 +-
 tony/core/planner.py        |  42 ++++-
 tony/core/safety.py         |  86 ++++++++-
 tony/core/task_runner.py    | 119 ++++++++++++-
 tony/tools/browser_tool.py  |  35 +++-
 tony/ui/main_window.py      | 415 +++++++++++++++++++++++++++++++++++---------
 tony/ui/styles.qss          | 103 ++++++++---
 tony/voice/stt.py           |  69 ++++++--
 tony/voice/tts.py           |  17 +-
 tony/voice/wake_word.py     |  22 +++
 22 files changed, 1938 insertions(+), 226 deletions(-)
```

## Changelog
# Changelog

## [1.0.0] - Initial Tony AI Release

- Voice-first assistant UI
- Text command support
- Wake phrase architecture
- Safety approval system
- Git/project tools
- Local memory/logging
- Vision, Observe, Teach, and workflow memory foundations
- Testing framework
- README/docs polish


## Validation
- Run `python -m pytest tests` before opening the PR.