# Speed Agents Workflow

## Quick Start

This project uses a **speed agents** workflow to parallelize development between two agents:

- **User** (you): Product feel, UI polish, chat experience
- **Kilo** (AI): Performance, responsiveness, inline capability plumbing

## File Ownership

### User's Files (UI/Feel)
- [`ui/main_window.py`](ui/main_window.py) - Main window, chat interface
- [`ui/responsive_layout.py`](ui/responsive_layout.py) - Responsive layout, adaptive sizing
- [`ui/animated_widgets.py`](ui/animated_widgets.py) - Animations, visual feedback

### Kilo's Files (Performance/Tools)
- [`kai_capabilities.py`](kai_capabilities.py) - Core capabilities, performance
- [`ui/capabilities_integration.py`](ui/capabilities_integration.py) - Capability UI integration
- [`ui/quick_actions.py`](ui/quick_actions.py) - Quick actions, commands

## Workflow

### 1. Work in Parallel
- Each agent only edits their owned files
- No conflicts, no merge issues
- Maximum velocity

### 2. Handoff After Each Pass
After completing work, create a handoff note in [`HANDOFF-NOTES.md`](HANDOFF-NOTES.md):

```markdown
### [Date] - [Agent] - [Pass #]
**Changes Made:**
- What you changed

**What to Test:**
- What the other agent should verify

**Issues Found:**
- Any problems discovered

**Next Steps for [Other Agent]:**
- What needs to happen next

**Visual QA Checklist:**
- [ ] Spacing consistency
- [ ] Drawer motion smoothness
- [ ] Card sizing appropriateness
- [ ] Narrow-window behavior (< 800px)
- [ ] Overall feel and responsiveness
```

### 3. Visual QA Together
After each pass, **both agents** run the real app and check:
- Spacing and visual polish
- Drawer motion and animations
- Card sizing and layout
- Narrow-window behavior (< 800px)
- Overall feel and responsiveness

## Key Documents

| Document | Purpose |
|----------|---------|
| [`SPEED-AGENTS-OWNERSHIP.md`](SPEED-AGENTS-OWNERSHIP.md) | File ownership, rules, dependencies |
| [`HANDOFF-NOTES.md`](HANDOFF-NOTES.md) | Pass history and handoff tracking |
| [`SPEED-AGENTS-README.md`](SPEED-AGENTS-README.md) | This file - workflow overview |

## Cross-Ownership Dependencies

**Important:** [`ui/main_window.py`](ui/main_window.py) (User) imports from [`ui/quick_actions.py`](ui/quick_actions.py) (Kilo):
- `SlashCommandMenu`
- `SmartSuggestions`
- `QuickReply`
- `WorkspaceContextBar`
- `CommandProcessor`

**Coordination:** If Kilo changes the API in `quick_actions.py`, announce in handoff note and provide migration path.

## Focus Areas

### User: Product Feel
- Spacing and visual polish
- Drawer motion and animations
- Card sizing and layout
- Narrow-window behavior
- Overall user experience

### Kilo: Performance & Tools
- Making scans/capabilities feel instant
- Performance optimization
- Inline tool integration
- Command processing speed
- Capability response time

## Getting Started

1. **User:** Start with UI polish pass on your files
2. **Kilo:** Start with performance optimization on your files
3. **Both:** Run visual QA after each pass
4. **Both:** Create handoff notes in [`HANDOFF-NOTES.md`](HANDOFF-NOTES.md)

## Rules

1. **Strict file ownership** - Don't edit files you don't own
2. **Handoff after every pass** - Document what you did and what to test
3. **Visual QA together** - Run the actual app between passes
4. **Focus on your lane** - User = feel, Kilo = speed
5. **Communicate changes** - Especially cross-ownership dependencies

## Goal

Make the app feel **instant** and **seamless** through parallel, focused development.
