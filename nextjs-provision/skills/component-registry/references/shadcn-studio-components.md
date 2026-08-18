# shadcn studio Component Catalog

Listing of shadcn studio component variants (1000+) available via the `@ss-components` registry.

Install any component (namespaced address — CLI v4 has no `--registry` flag):
```bash
npx shadcn@latest add @ss-components/[name]
```

## Accordion

Collapsible content sections with smooth animations.
- Default, bordered, separated styles
- Icon positions: left, right
- Multiple or single expand modes

## Alert

Inline notification messages for important information.
- Variants: default, destructive, warning, success, info
- With icon, title, description
- Dismissible variants

## Avatar

User profile images with fallback support.
- Sizes: xs, sm, md, lg, xl
- Shapes: circle, rounded square
- Group/stack variants for multiple avatars
- With status indicator (online, offline, busy)

## Badge

Status labels, tags, and category indicators.
- Variants: default, secondary, outline, destructive
- Sizes: sm, md, lg
- With icon, with close button
- Animated (pulse, bounce)

## Button

Action buttons with extensive variant options.
- Variants: default, secondary, outline, ghost, link, destructive
- Sizes: sm, default, lg, icon
- Loading state with spinner
- With icon (left, right)
- Group/toolbar layout
- Animated variants (hover effects, transitions)

## Calendar

Date display and selection component.
- Single date, date range, multiple dates
- With presets
- Month/year navigation
- Min/max date constraints
- Localization support

## Card

Flexible content containers.
- Default, bordered, shadow styles
- With image header
- Horizontal layout
- Interactive (hover effects)
- Pricing card variants
- Profile card variants
- Stats card variants

## Checkbox

Selection controls for multiple options.
- Default, with label, with description
- Indeterminate state
- Group/fieldset layout
- Card-style checkbox

## Collapsible

Show/hide content sections.
- Default expand/collapse
- With custom trigger
- Nested collapsibles

## Command

Search command palette (combobox/autocomplete).
- With search input
- Grouped items
- With icons
- Dialog-triggered command palette
- Keyboard shortcuts display

## Data Table

Advanced table with sorting, filtering, pagination.
- Column visibility toggle
- Row selection
- Sorting (single, multi-column)
- Filtering (text, faceted)
- Pagination controls
- Column resizing
- Expandable rows

## Date Picker

Date selection with calendar popup.
- Single date, date range
- With presets (today, tomorrow, next week)
- Time picker variant
- Date-time picker

## Dialog

Modal windows for focused interactions.
- Default, scrollable, full-screen
- With form content
- Nested dialogs
- Alert dialog variant (confirm/cancel)
- Sheet-style (slide from side)

## Dropdown Menu

Context menus and action menus.
- With icons, shortcuts, checkboxes, radio items
- Nested submenus
- With separator groups
- With labels

## Form

Form layouts with validation integration.
- React Hook Form + Zod integration
- Field variants: input, select, checkbox, radio, switch, textarea, date picker, combobox
- Inline and stacked layouts
- Multi-step forms
- Error states and messages

## Input

Text input fields.
- Default, with label, with description
- With icon (leading, trailing)
- With inline button
- Password with toggle visibility
- Search input
- File input
- Disabled, error states

## Label

Form field labels.
- Default, required indicator
- With tooltip help

## Navigation Menu

Site navigation with mega menu support.
- Horizontal navigation
- With icons, descriptions
- Mega menu with columns
- Mobile-responsive variants

## Pagination

Page navigation controls.
- Default (prev/next + page numbers)
- With page size selector
- Compact variant
- Infinite scroll trigger

## Popover

Floating content panels.
- Default, with arrow
- Positioned (top, bottom, left, right)
- With form content
- Trigger on hover or click

## Progress

Progress indicators.
- Linear progress bar
- Circular/radial progress
- With label and percentage
- Indeterminate/loading state

## Radio Group

Single selection controls.
- Default, card-style
- With description
- Horizontal and vertical layout
- With icons

## Resizable

Resizable panel layouts.
- Horizontal, vertical, grid
- With min/max constraints
- Nested panels
- Collapsible panels

## Scroll Area

Custom scrollbar container.
- Vertical, horizontal, both
- With scroll indicators
- Custom scrollbar styling

## Select

Dropdown selection.
- Default, searchable
- With groups
- With icons
- Multiple select
- Async loading options

## Separator

Visual dividers.
- Horizontal, vertical
- With label
- Dashed, dotted styles

## Sheet

Slide-over panels (drawers).
- Sides: top, bottom, left, right
- With close button
- With form content
- Sizes: sm, default, lg, full

## Sidebar

Application sidebar navigation.
- Collapsible (icon-only mode)
- With sections and groups
- With search
- Nested navigation
- Mobile drawer variant
- With user profile section

## Skeleton

Loading placeholder animations.
- Text lines, circles, rectangles
- Card skeleton
- Table skeleton
- Custom shapes

## Slider

Range input controls.
- Single value, range (two thumbs)
- With labels and value display
- Step increments
- Vertical orientation

## Switch

Toggle on/off controls.
- Default, with label
- With description
- Sizes: sm, md, lg
- Card-style switch

## Table

Data table component.
- With header, body, footer
- Striped rows
- Sortable columns
- Selectable rows
- Caption support

## Tabs

Tabbed content navigation.
- Default, underline, pills style
- With icons
- Vertical tabs
- Responsive (scrollable on mobile)
- With content panels

## Textarea

Multi-line text input.
- Default, with label
- Auto-resize
- Character counter
- With limit

## Toast / Sonner

Notification messages.
- Variants: default, success, error, warning, info
- With action button
- Positioned (top-right, bottom-right, etc.)
- Auto-dismiss with timer
- Stacking behavior

## Tooltip

Hover information popups.
- Default, with arrow
- Positioned (top, bottom, left, right)
- Rich content (not just text)
- Delay settings

## Toggle

Toggle buttons.
- Default, outline
- Single, group
- With icon
- Pressed state styling
