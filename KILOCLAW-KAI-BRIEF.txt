# KiloClaw Brief: Understanding Kai

This file is the fastest way to understand the current Kai direction without reading the whole repo.

## What Kai Is

Kai is a PyQt5 desktop AI assistant built around a chat-first interface.

Current product direction:
- single-window experience
- one main conversation surface
- inline tools instead of extra panels
- responsive, warm, low-friction interaction
- project-aware help inside chat

This is no longer heading toward a multi-panel dashboard. The active goal is to make Kai feel like one smart teammate in one clear window.

## Where the Real App Lives

Primary working app root:
- `W0rm-Gpt-main/`

Key launch file:
- `main.py`

Important note:
- there is also a nested `W0rm-Gpt-main/W0rm-Gpt-main/` copy in this workspace tree
- the active files being edited for the current overhaul are under the top-level app root shown above
- before making edits, confirm you are in the same file path the latest handoff notes reference

## Core Architecture

Main UI flow:
- `main.py`: app bootstrap, splash/auth/main window flow
- `ui/main_window.py`: main chat window, message flow, history drawer, input, AI response handling
- `ui/quick_actions.py`: slash commands, smart suggestions, quick replies, project-radar chips, async capability workers
- `ui/code_block_widget.py`: message rendering, code blocks, inline tool-result cards
- `ui/responsive_layout.py`: quick-action bar, status bar, responsive helpers
- `ui/animated_widgets.py`: typing indicator and animation helpers

Project intelligence:
- `kai_capabilities.py`: code analysis, file operations, project scanning, related files, recent files, command execution
- `ui/capabilities_integration.py`: integration helpers for capability UI wiring

Persistence and session:
- `database/db_manager.py`: conversations and chat history
- `utils/session_manager.py`: auth/session state
- `utils/text_formatter.py`: AI/user text rendering styles

## Current UX Direction

The app has already been pushed toward:
- collapsible history instead of permanent sidebar behavior
- inline slash commands
- inline tool cards for project/file results
- quick replies and smart suggestions
- project-aware chips for focused, related, and recent files
- smoother typing and faster conversation restore

The next level is not "more features everywhere."
It is:
- better feel
- better responsiveness
- better inline context

## What Changed Recently

Recent completed passes:
- debounced composer suggestion updates
- skipped per-message animation during history restore
- added project-radar chips
- added `/related` and `/recent`
- moved heavy slash commands off the UI thread
- added lazy capability initialization
- updated handoff notes for ongoing passes

Heavy commands now running asynchronously:
- `/project`
- `/find`
- `/analyze`
- `/related`
- `/recent`

## Important Files To Read First

Read these in order:
1. `HANDOFF-NOTES.md`
2. `SPEED-AGENTS-OWNERSHIP.md`
3. `ui/main_window.py`
4. `ui/quick_actions.py`
5. `kai_capabilities.py`

Optional context:
- `NEXT-LEVEL-ROADMAP.md`
- `ENHANCEMENT-SUMMARY.md`
- `CAPABILITIES-README.md`

## Current Product Rules

Keep these true while editing:
- chat first, tools second
- avoid adding new permanent panels
- prefer inline cards, chips, and contextual actions
- small responsiveness wins matter
- every improvement should reduce friction, not add supervision overhead

If a change makes Kai feel more like a dashboard than a collaborator, it is probably the wrong direction.

## Good Next Tasks

Best next tasks right now:
- add inline loading feedback for async slash commands
- improve project-radar chip spacing and overflow behavior
- run live visual QA on narrow widths
- polish status bar language during background work
- keep making message rendering easier to scan

High-value small improvements:
- cleaner loading states
- calmer status text
- smoother transitions
- better spacing in chat cards
- smarter file-aware follow-up chips

## Ownership Guidance

If you are working in parallel with Codex:
- avoid overlapping edits in `ui/main_window.py` and `ui/quick_actions.py` unless coordinated
- use `HANDOFF-NOTES.md` after every meaningful pass
- keep changes small, shippable, and easy to verify

Suggested split:
- one agent on feel/UI polish
- one agent on performance/capability plumbing
- one agent on live visual QA

## How To Verify

Basic checks:
- run `python main.py`
- test slash commands in the chat window
- load an older conversation and watch restore behavior
- test `/project`, `/find`, `/analyze`, `/related`, `/recent`
- check project-radar chips after file-oriented actions

Regression checks:
- history drawer still opens smoothly
- input still feels fast
- no UI freeze on heavy commands
- tool cards still render correctly
- recent chats still load normally

## Bottom Line

Kai is a chat-first desktop teammate with growing project awareness.

The right way to improve it is:
- one small pass at a time
- always toward smoother feel
- always toward less clutter
- always toward more useful inline context
