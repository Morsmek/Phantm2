# PHANTM Mobile Interface Design Plan

PHANTM will be designed as a **portrait-first, one-handed mobile experience** that feels closer to a first-party iOS utility than a conventional launcher. The interface will use a dark spatial canvas, very low-visibility orbital structure, and precise Spectral Cyan interaction feedback so the user feels they are navigating a private phone-within-a-phone rather than moving through conventional screens.

| Design Area | PHANTM Decision |
|---|---|
| Primary orientation | Portrait only, optimised for 9:16 screens and thumb-reachable controls. |
| Interaction posture | One-handed use, with the central node and lower controls placed near the natural thumb zone. |
| Visual reference | The supplied frontend mockup defines the core look: Void Black radial grid, faint distant dots, centered orbital nest, Spectral Cyan glow, top transparent PHANTM header, Neutral context chip, and bottom navigation hint. |
| Platform feel | Mainstream iOS-inspired spacing, restrained animation, soft hierarchy, minimum 44pt touch targets, and safe-area-aware layout. |
| Data model | Local-first canvas state, nests, modules, captures, notes, timers, and exported JSON; no authentication or cloud sync for this build. |

## Screen List

| Screen | Route | Primary Content and Functionality |
|---|---|---|
| Onboarding | `/onboarding` | A seven-step walkthrough introduces PHANTM, the infinite canvas, the nest anatomy, hold-and-drag navigation, slot activation, customisation, and first nest creation. Each step uses a small animated or static canvas visual rather than dense instructional text. |
| Main Nest Setup | `/setup` | The user names the Main Nest, chooses an initial context accent, and assigns at least one module slot before entering the canvas. The form is intentionally short and thumb-friendly. |
| Canvas | `/` | The main screen shows the infinite canvas, top PHANTM brand bar, context chip, distant nest dots, central active nest, inner and outer rings, tappable slots, bottom instruction text, and compact bottom controls. |
| Nest Editor | `/nest/[id]/edit` | The user edits nest label, type, ring slots, module assignments, nest-link targets, and shareability options. The screen uses grouped cards and compact slot rows instead of complex diagrams. |
| Hidden Nest Gate | `/nest/[id]/unlock` | The user enters a password to reveal a hidden nest. The design uses Boundary Red as a restrained warning accent and returns safely to the canvas on cancel. |
| Notes Module | `/modules/notes` | A bottom sheet presents local notes, a quick composer, and an editor area for markdown/plain text. The canvas remains visible and dimmed behind the sheet. |
| Voice Module | `/modules/voice` | A bottom sheet presents recording controls, elapsed time, and a list of saved clips. If recording is unavailable on web, the UI explains the limitation without blocking other app features. |
| Quick Capture Module | `/modules/capture` | A bottom sheet offers one-tap text capture, a compact input, and a chronological local capture list. |
| Browser Module | `/modules/browser` | A bottom sheet lets the user enter a URL and open it through supported in-app browser behaviour. The app avoids external API dependencies. |
| Workflow Module | `/modules/workflows` | A bottom sheet shows local workflow sequences, step status, and a simple run/pause interaction. |
| Timer Module | `/modules/timer` | A bottom sheet presents Pomodoro/focus presets, countdown display, and start/pause/reset controls with Focus Amber highlights. |
| Settings | `/settings` | The settings screen provides preferences, onboarding reset, JSON export/import, local data management, and guidance about hidden and shareable nests. |

## Key User Flows

| Flow | Step-by-Step Interaction |
|---|---|
| First launch | User opens PHANTM, reads the onboarding steps, taps the final CTA, names the Main Nest, assigns a first slot, and lands on the main canvas. |
| Canvas navigation | User presses the central node, holds for approximately 300ms, receives visual feedback, drags in a direction, sees distant nests and a directional trail, then releases. If a nest is nearby, it snaps to center; otherwise, the canvas remains in transit. |
| Module opening | User taps a visible ring slot, the selected module opens as a bottom sheet, the canvas dims, and the user can dismiss the module with a close action or downward-feeling sheet control. |
| Nest editing | User opens the editor from canvas controls or settings, changes ring slot assignments, saves, and returns to the updated nest layout. |
| Hidden nest access | User approaches or selects a hidden nest, sees the password gate, enters the password, and then the hidden nest becomes available in the current session. |
| Share/export | User opens Settings or Nest Editor, exports a nest JSON configuration, copies the generated text, or imports a valid JSON configuration into the local canvas. |

## Color Choices

| Token | Hex | Usage |
|---|---:|---|
| Void Black | `#05070A` | Edge-to-edge canvas background and default app atmosphere. |
| Surface Deep | `#0E1417` | Sheet and card surfaces inspired by the provided frontend. |
| Surface Container | `#1A2123` | Elevated cards, editor sections, and inactive module panels. |
| Phantom Ink | `#9BA6B2` | Secondary labels, ring traces, inactive controls, and captions. |
| Spectral Cyan | `#39D5FF` | Default active nest accent, slot glow, central node pulse, and selected navigation icon. |
| Work Blue | `#4F8CFF` | Work context accent. |
| Personal Violet | `#A77BFF` | Personal context accent. |
| Focus Amber | `#F6B73C` | Timer, focus state, and interval signals. |
| Travel Mint | `#36D6A1` | Travel state and directional trail. |
| Boundary Red | `#FF5C7A` | Hidden nest locks, destructive actions, and failed unlock attempts. |
| Canvas Grid | `#0D1117` | Subtle radial-grid dot pattern. |

## Layout Rules

The canvas screen will be full-bleed, with the **PHANTM** brand and context chip floating at the top inside safe-area padding. The central nest occupies the middle of the screen with an inner ring around 180 logical pixels and an outer ring around 320 logical pixels on standard mobile previews, scaling down on smaller screens. The bottom instruction area sits above the home indicator and uses short instructional copy such as **“Hold center · drag to navigate”** so the main UI stays quiet.

| Component | Layout Treatment |
|---|---|
| Top brand bar | Transparent, fixed within safe area, left brand mark and wordmark, right context pill. |
| Active nest | Centered, with low-opacity rings and Spectral Cyan active glow. |
| Slot controls | Circular 44–48pt touch targets placed on orbital positions. Labels appear only when helpful to reduce visual noise. |
| Module sheets | Bottom sheets occupy roughly 55–75% of height depending on content, with rounded top corners and dimmed canvas background. |
| Editor/settings | Safe-area screen containers with grouped rounded cards and large, readable text. |

## Implementation Notes

The supplied frontend reference will be translated into React Native primitives rather than web-only CSS. The radial grid will be approximated with repeated canvas markers or SVG, the orbital rings will use `react-native-svg`, and material-style icons will use the Expo vector icon set already available in the scaffold. The app will prioritise core flow completion and deterministic local data handling before adding visual polish.
