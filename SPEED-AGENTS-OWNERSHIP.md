# Speed Agents Ownership & Workflow

## Overview
This document tracks file ownership and handoff protocols for the W0rm-Gpt speed agents workflow.

## Ownership Split

### User (Product Feel)
**Focus:** UI polish, chat feel, window seamless & fun

**Owned Files:**
- [`ui/main_window.py`](ui/main_window.py) - Main application window, chat interface, user interactions
- [`ui/responsive_layout.py`](ui/responsive_layout.py) - Responsive layout manager, adaptive sizing, smooth transitions
- [`ui/animated_widgets.py`](ui/animated_widgets.py) - Animated widgets, typing indicators, visual feedback

**Responsibilities:**
- Spacing and visual polish
- Drawer motion and animations
- Card sizing and layout
- Narrow-window behavior
- Overall user experience feel

---

### Kilo (Performance & Inline Tools)
**Focus:** Speed, responsiveness, inline capability plumbing

**Owned Files:**
- [`kai_capabilities.py`](kai_capabilities.py) - Core capabilities module (code analysis, file ops, command execution)
- [`ui/capabilities_integration.py`](ui/capabilities_integration.py) - UI integration for capabilities
- [`ui/quick_actions.py`](ui/quick_actions.py) - Quick actions, slash commands, smart suggestions

**Responsibilities:**
- Making scans/capabilities feel instant
- Performance optimization
- Inline tool integration
- Command processing speed
- Capability response time

---

## Collaboration Rules

### 1. Strict File Ownership
- **DO NOT** edit files owned by the other agent
- If you need changes in another agent's files, request it via handoff note
- Conflicts are resolved by the owning agent

### 2. Shared Lane: Visual QA
After each pass, **both agents** run the real app and check:
- [ ] Spacing consistency
- [ ] Drawer motion smoothness
- [ ] Card sizing appropriateness
- [ ] Narrow-window behavior (< 800px)
- [ ] Overall feel and responsiveness

### 3. Handoff Protocol
After completing a pass, create a handoff note in [`HANDOFF-NOTES.md`](HANDOFF-NOTES.md) with:
- What was changed
- What to test
- Any issues found
- Next steps for the other agent

---

## Current Status

### Last Handoff
- **Date:** 2026-03-27
- **Agent:** System (initial setup)
- **Changes:** Established ownership split and workflow
- **Test Notes:** Verify all files are accessible and ownership is clear

### Pending Work
- [ ] User: Initial UI polish pass
- [ ] Kilo: Performance optimization pass
- [ ] Both: Visual QA after each pass

---

## Quick Reference

| File | Owner | Purpose |
|------|-------|---------|
| `ui/main_window.py` | User | Main window, chat interface |
| `ui/responsive_layout.py` | User | Responsive layout, adaptive sizing |
| `ui/animated_widgets.py` | User | Animations, visual feedback |
| `kai_capabilities.py` | Kilo | Core capabilities, performance |
| `ui/capabilities_integration.py` | Kilo | Capability UI integration |
| `ui/quick_actions.py` | Kilo | Quick actions, commands |

---

## Cross-Ownership Dependencies

### Known Dependencies
- [`ui/main_window.py`](ui/main_window.py) (User) imports from [`ui/quick_actions.py`](ui/quick_actions.py) (Kilo)
  - Classes imported: `SlashCommandMenu`, `SmartSuggestions`, `QuickReply`, `WorkspaceContextBar`, `CommandProcessor`
  - **Impact:** User's UI changes may need to coordinate with Kilo's quick_actions API

### Coordination Protocol
When modifying interfaces in cross-owned files:
1. Announce changes in handoff note
2. Provide migration path if API changes
3. Test integration after both passes

## Notes
- This is a living document - update after each handoff
- Keep handoff notes concise and actionable
- Always test the actual window between passes
- Focus on making the app feel instant and seamless
