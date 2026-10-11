# Universal UI Colour System & Design Consistency Rules

Whenever you design, build, modify, or improve a user interface, follow the colour system and design principles defined below.

## 1. Core Colour Palette

Use this warm, minimalist palette as the default visual foundation for dashboards, web applications, admin panels, analytics tools, and other UI projects.

**Neutral foundation**
- Canvas Grey: `#E1E1E1`
- Main Background: `#F8F8F8`
- Surface / Cards: `#FFFFFF`
- Muted Surface: `#EFEFEF`

**Typography**
- Primary Text: `#030202`
- Secondary Text: `#5C5B5A`
- Muted Text: `#949292`
- Disabled Text: `#B1B0AF`

**Borders**
- Standard Border: `#CACACA`
- Subtle Border: `#EFEFEF`

**Signature Coral Palette**
- Primary Accent: `#E1644A`
- Hover / Pressed Accent: `#B65541`
- Secondary Coral: `#C26653`
- Dusty Coral: `#D69383`
- Soft Coral: `#F0BBB0`
- Pale Coral: `#F4D7CF`
- Coral Tint: `#F8ECEA`

## 2. Colour Usage Rules

- Use soft white as the primary page background and white for cards, panels, and elevated surfaces.
- Use near-black for headings, important figures, and primary text.
- Use secondary and muted greys for descriptions, metadata, and supporting information.
- Use the signature coral for primary actions, active states, important highlights, and selected chart elements.
- Use lighter coral shades for subtle backgrounds, progress indicators, chart fills, and decorative accents.
- Use neutral borders and restrained shadows to separate elements without creating visual clutter.
- Avoid excessive colours, gradients, glowing effects, and unnecessary decoration.
- Never use the accent colour everywhere. Preserve its visual impact by applying it selectively.

## 3. Reusable Design Tokens

Define the palette centrally using CSS variables, theme tokens, or the equivalent supported by the project's existing technology stack.

Prefer semantic names such as:
- `background`
- `surface`
- `text-primary`
- `text-secondary`
- `border`
- `accent`
- `accent-hover`
- `accent-subtle`
- `focus-ring`

Components must reference these tokens rather than repeatedly hardcoding colour values.

Maintain one authoritative source of truth for the theme. Avoid duplicate definitions and inconsistent colour variations across pages or components.

## 4. Universal Design Principles

Apply the palette while respecting the project's purpose and existing design requirements.

- Maintain clear visual hierarchy, consistent spacing, alignment, and readable typography.
- Prefer clean layouts, generous whitespace, rounded corners, subtle borders, and restrained shadows.
- Keep buttons, forms, navigation, cards, tables, charts, dialogs, and interactive states visually consistent.
- Support responsive layouts across desktop, tablet, and mobile.
- Provide clear hover, focus, active, disabled, loading, success, warning, and error states where appropriate.
- Maintain accessibility and verify colour contrast against WCAG 2.2 AA requirements wherever applicable.
- Do not rely on colour alone to communicate important information.
- Do not sacrifice usability, readability, or accessibility to match the palette.

## 5. Adaptation Rules

This palette is a reusable default, not a restriction on the product's functionality or layout.

Before implementation:
1. Inspect the existing project, framework, design system, styling conventions, and component library.
2. Identify existing theme tokens and reusable UI components.
3. Preserve established project conventions and working functionality.
4. Determine where the palette fits naturally into the current interface.

If the project already has an explicitly defined brand identity or a different mandatory design system, respect that requirement and ask for clarification if the intended priority is unclear.

If the project has no established colour system, use this palette by default.

If additional semantic colours are required, introduce them sparingly, document their purpose, and ensure they work harmoniously with the existing palette.

Do not force the same layout, component structure, or colour proportions onto every project.

## 6. Implementation and Maintenance

When working with an existing codebase:
- Make changes consistent with its architecture and coding standards.
- Reuse existing components and styling utilities wherever practical.
- Avoid unnecessary dependencies, unrelated refactoring, or changes to application logic.
- Replace inconsistent colour definitions with shared tokens where appropriate.
- Verify the final result across relevant pages, components, responsive sizes, and interaction states.
- Run available checks and tests when practical.
- Document any significant design-system changes.

For a new project, establish the central colour tokens before implementing the main UI components.

## 7. Expected Outcome

The result should feel cohesive, modern, clean, professional, and easy to maintain.

The neutral foundation should dominate the interface. The coral palette should provide a recognizable visual identity and guide attention toward meaningful actions and information.

Apply these rules whenever you work on UI design or frontend styling, unless the project's explicit requirements say otherwise.