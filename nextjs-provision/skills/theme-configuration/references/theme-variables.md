# CSS Variable Reference

Complete reference for shadcn/ui theme CSS custom properties.

## Variable Categories

### Background & Text

| Variable | Purpose | Typical Light | Typical Dark |
|----------|---------|---------------|--------------|
| `--background` | Page background | `oklch(1 0 0)` (white) | `oklch(0.145 0 0)` (near-black) |
| `--foreground` | Default text color | `oklch(0.145 0 0)` | `oklch(0.985 0 0)` |

### Primary Colors

| Variable | Purpose | Usage |
|----------|---------|-------|
| `--primary` | Primary action color | Buttons, links, active states |
| `--primary-foreground` | Text on primary backgrounds | Button text, badge text |

### Secondary Colors

| Variable | Purpose | Usage |
|----------|---------|-------|
| `--secondary` | Secondary action color | Secondary buttons, less prominent actions |
| `--secondary-foreground` | Text on secondary backgrounds | Secondary button text |

### Destructive Colors

| Variable | Purpose | Usage |
|----------|---------|-------|
| `--destructive` | Error/danger color | Delete buttons, error messages |
| `--destructive-foreground` | Text on destructive backgrounds | Error button text |

### Muted Colors

| Variable | Purpose | Usage |
|----------|---------|-------|
| `--muted` | Subtle background | Muted sections, disabled areas |
| `--muted-foreground` | Subtle text | Placeholder text, secondary labels |

### Accent Colors

| Variable | Purpose | Usage |
|----------|---------|-------|
| `--accent` | Highlight/accent | Hover states, selected items |
| `--accent-foreground` | Text on accent backgrounds | Hover text |

### Card & Popover

| Variable | Purpose | Usage |
|----------|---------|-------|
| `--card` | Card background | Card containers |
| `--card-foreground` | Card text | Text inside cards |
| `--popover` | Popover/dropdown background | Menus, tooltips, dialogs |
| `--popover-foreground` | Popover text | Text in popovers |

### Borders & Inputs

| Variable | Purpose | Usage |
|----------|---------|-------|
| `--border` | Default border color | Card borders, dividers |
| `--input` | Input border color | Form input borders |
| `--ring` | Focus ring color | Focus indicators on interactive elements |

### Layout

| Variable | Purpose | Usage |
|----------|---------|-------|
| `--radius` | Border radius | Applied to all components (default `0.625rem`) |

### Chart Colors

| Variable | Purpose |
|----------|---------|
| `--chart-1` | First chart color (series 1) |
| `--chart-2` | Second chart color (series 2) |
| `--chart-3` | Third chart color (series 3) |
| `--chart-4` | Fourth chart color (series 4) |
| `--chart-5` | Fifth chart color (series 5) |

### Sidebar Colors (if using sidebar component)

| Variable | Purpose |
|----------|---------|
| `--sidebar` | Sidebar background (formerly `--sidebar-background`) |
| `--sidebar-foreground` | Sidebar text |
| `--sidebar-primary` | Active sidebar item |
| `--sidebar-primary-foreground` | Active item text |
| `--sidebar-accent` | Hover sidebar item |
| `--sidebar-accent-foreground` | Hover item text |
| `--sidebar-border` | Sidebar borders |
| `--sidebar-ring` | Sidebar focus ring |

## OKLCH Format

All color values are complete OKLCH colors, referenced directly:

```css
/* Correct: */
--primary: oklch(0.205 0 0);

/* Legacy pattern (older projects only): */
--primary: 240 5.9% 10%; /* raw HSL triple */
```

Components reference them with `var()`:
```css
.button {
  background-color: var(--primary);
  color: var(--primary-foreground);
}
```

The `hsl(var(--primary))` wrapper is the **legacy pattern** — it only works with projects still using raw HSL triples. New inits emit OKLCH plus a `@theme inline` block that maps the variables to Tailwind utilities.

## Color Token Hierarchy

```
Background (page) → Card (container) → Popover (overlay)
     ↓                    ↓                    ↓
 Foreground          Card-foreground      Popover-foreground

Primary → Used for main CTAs, active navigation, links
Secondary → Used for secondary actions, less emphasis
Muted → Used for disabled, subtle backgrounds, placeholder text
Accent → Used for hover states, highlights
Destructive → Used for errors, deletions, warnings

Border → Dividers, card edges, separators
Input → Form field borders (often same as border)
Ring → Focus indicators (often matches primary)
```

## Base Colors

The `baseColor` options in `components.json` are now: **neutral | stone | zinc | mauve | olive | mist | taupe** (`slate` and `gray` are gone).

### Neutral (Default)
```css
:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --primary: oklch(0.205 0 0);
  --secondary: oklch(0.97 0 0);
  --muted: oklch(0.97 0 0);
  --accent: oklch(0.97 0 0);
  --destructive: oklch(0.577 0.245 27.325);
  --border: oklch(0.922 0 0);
  --radius: 0.625rem;
}
```

For the other base colors (stone, zinc, mauve, olive, mist, taupe) and the 8 style presets (Vega, Nova, Maia, Lyra, Mira, Luma, Rhea, Sera), generate the exact variable block with the visual builder at https://ui.shadcn.com/create and apply it with `shadcn apply <preset-code> --only theme`.

## Creating Custom Colors

### Hex to OKLCH Conversion

To convert brand colors to OKLCH for CSS variables (use a converter such as https://oklch.com):

| Hex | OKLCH | Variable Assignment |
|-----|-------|---------------------|
| `#000000` | `oklch(0 0 0)` | Pure black |
| `#ffffff` | `oklch(1 0 0)` | Pure white |
| `#3b82f6` | `oklch(0.623 0.214 259.8)` | Blue |
| `#ef4444` | `oklch(0.637 0.237 25.3)` | Red |
| `#22c55e` | `oklch(0.723 0.192 149.6)` | Green |
| `#f59e0b` | `oklch(0.769 0.188 70.1)` | Amber |
| `#8b5cf6` | `oklch(0.606 0.25 292.7)` | Violet |

### Contrast Guidelines

For accessibility, ensure sufficient contrast between background and foreground pairs:

| Pair | Minimum Contrast (WCAG AA) |
|------|---------------------------|
| `--background` / `--foreground` | 4.5:1 for normal text |
| `--primary` / `--primary-foreground` | 4.5:1 for button text |
| `--card` / `--card-foreground` | 4.5:1 for card text |
| `--muted` / `--muted-foreground` | 3:1 for large text/UI |
| `--destructive` / `--destructive-foreground` | 4.5:1 for error text |

### Generating a Color Scale

For a primary color of `oklch(0.62 0.21 260)` (blue), vary the lightness channel:

```css
/* Lighter variants */
--primary-50: oklch(0.97 0.02 260);
--primary-100: oklch(0.93 0.04 260);
--primary-200: oklch(0.85 0.08 260);
--primary-300: oklch(0.75 0.13 260);

/* Base */
--primary: oklch(0.62 0.21 260);

/* Darker variants */
--primary-600: oklch(0.55 0.21 260);
--primary-700: oklch(0.47 0.19 260);
--primary-800: oklch(0.4 0.16 260);
--primary-900: oklch(0.32 0.13 260);
```

Note: shadcn/ui's default theme system uses a simpler two-tone approach (primary + primary-foreground) rather than full color scales. Extend with custom variables only if your design requires it.
