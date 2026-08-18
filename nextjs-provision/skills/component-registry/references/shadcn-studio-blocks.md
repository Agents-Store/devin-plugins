# shadcn studio Block Catalog

Pre-built UI blocks (800+) available via the `@ss-blocks` registry. Blocks are complete sections ready to drop into pages.

Install any block (namespaced address — CLI v4 has no `--registry` flag):
```bash
npx shadcn@latest add @ss-blocks/[name]
```

Full pre-built pages now live in the separate `@ss-pages` registry:
```bash
npx shadcn@latest add @ss-pages/feature-page-01
```

## Marketing Blocks

### Hero Sections (50+)

Full-width landing page hero sections with various layouts:
- **Centered text** with CTA buttons and optional image/video
- **Split layout** with text on one side, image/illustration on other
- **Full-screen background** image or video with overlay text
- **Animated** variants with motion effects
- **With form** embedded (email signup, search)
- **With social proof** (logos, testimonials, stats)
- **With gradient** background effects
- **Dark/light** theme variants

### Feature Sections (40+)

Showcase product features and capabilities:
- **Icon grid** (2x2, 3x3, 4x4) with descriptions
- **Alternating rows** (image left/right with text)
- **Card grid** with hover effects
- **Comparison table** (features vs competitors)
- **Bento grid** layout (mixed sizes)
- **With illustrations** or screenshots
- **Tab-based** feature showcase
- **Accordion-based** feature list

### Pricing (30+)

Pricing display components:
- **Card layout** (2-4 tiers side by side)
- **With toggle** (monthly/annual)
- **Highlighted tier** (recommended)
- **Feature comparison table**
- **Enterprise contact** variant
- **With FAQ section**
- **Compact list** style

### Testimonials (20+)

Customer testimonials and social proof:
- **Quote cards** (single, grid)
- **Carousel/slider** with auto-play
- **With avatar and role**
- **Star rating** variants
- **Video testimonial** placeholder
- **Social media style** quotes
- **Logo wall** with testimonials

### CTA Sections (20+)

Call-to-action blocks:
- **Centered text** with buttons
- **With email input** (newsletter signup)
- **Split layout** with image
- **With countdown timer**
- **Floating/sticky** CTA bar
- **With background pattern**

### Navigation (30+)

Header and navigation components:
- **Simple navbar** with logo and links
- **With dropdown menus**
- **Mega menu** with columns
- **With search bar**
- **Mobile responsive** (hamburger menu)
- **With CTA button** (sign up / login)
- **Transparent/overlay** for hero sections
- **Sticky/fixed** header
- **With notification badge**

### Footers (20+)

Page footer sections:
- **Multi-column** link layout
- **With newsletter signup**
- **With social media icons**
- **Simple centered** variant
- **With sitemap structure**
- **Dark background** variants
- **With logo and copyright**

## Dashboard Blocks (100+)

### Dashboard Shells

Complete dashboard layouts:
- **Sidebar + main content** layout
- **Top nav + content** layout
- **With breadcrumb** navigation
- **Collapsible sidebar** variants
- **With command palette** (Cmd+K)

### Stat Cards

Key metric display:
- **Simple number** with label
- **With trend indicator** (up/down arrow, percentage)
- **With sparkline chart**
- **Icon + number** layout
- **Comparison** (current vs previous period)
- **Progress ring** variant

### Chart Blocks

Data visualization:
- **Line chart** (single, multi-series)
- **Bar chart** (vertical, horizontal, stacked)
- **Area chart** (filled, gradient)
- **Pie/Donut chart**
- **With legend and tooltip**
- **Responsive container**

### Data Tables

Advanced table blocks:
- **With toolbar** (search, filter, view toggle)
- **With row actions** (edit, delete, view)
- **With column sorting**
- **With faceted filters**
- **With pagination**
- **With row selection** (batch actions)
- **Expandable rows**
- **With export button**

### Sidebar Navigation

Dashboard sidebar variants:
- **With icons** and labels
- **Grouped sections**
- **Collapsible to icon-only**
- **With user profile** at bottom
- **With search**
- **Nested items** (expandable)

### Widget Blocks

Dashboard widgets:
- **Activity feed** (timeline)
- **Recent items** list
- **Quick actions** grid
- **Calendar widget**
- **Task list** with checkboxes
- **Notification panel**

## Form Blocks (40+)

### Authentication

Login and signup forms:
- **Login** (email/password, with social providers)
- **Signup** (with name, email, password, confirm)
- **Forgot password** flow
- **OTP/code verification**
- **Two-factor authentication**
- **Magic link** login

### Multi-Step Forms

Complex form flows:
- **Wizard** with step indicator
- **Tab-based** sections
- **With progress bar**
- **With summary/review** step
- **Conditional steps** (branching logic)

### Settings Forms

Application settings:
- **Profile settings** (avatar, name, bio)
- **Account settings** (email, password, delete)
- **Notification preferences** (toggles)
- **Theme/appearance** settings
- **API keys** management

### Contact / Feedback

User communication:
- **Contact form** (name, email, message)
- **Feedback form** (with rating)
- **Bug report** form
- **Survey/questionnaire** layout

## eCommerce Blocks (100+)

### Product Display

Product presentation:
- **Product card** (image, title, price, rating)
- **Product grid** (2, 3, 4 columns)
- **Product list** (horizontal layout)
- **Product detail** page sections
- **Quick view** modal
- **Image gallery** with thumbnails
- **With size/color selectors**

### Shopping Cart

Cart and checkout:
- **Cart drawer** (slide-out panel)
- **Cart page** with item list
- **Order summary** (totals, tax, shipping)
- **Checkout form** (address, payment)
- **Empty cart** state

### Product Categories

Category navigation:
- **Category cards** with image
- **Category list** with count
- **Breadcrumb** trail
- **Filter sidebar** (price, color, size, rating)

### Reviews

Customer reviews:
- **Review list** with rating
- **Write review** form
- **Rating summary** (bar chart)
- **Verified purchase** badge

## Authentication Blocks (20+)

Complete auth page layouts:
- **Centered card** login/signup
- **Split screen** (form + image/branding)
- **Full-width** minimal login
- **With social provider** buttons (Google, GitHub, etc.)
- **With terms and privacy** links
- **Branded** with logo and tagline

## Bento Grid Blocks

Mixed-size grid layouts:
- **Feature showcase** bento
- **Portfolio/gallery** bento
- **Stats + features** combination
- **With animations** on scroll
- **Responsive** breakpoints

## How Blocks Are Installed

1. Block files are placed in `src/components/shadcn-studio/blocks/[block-name]/`
2. Move to your preferred location: `src/components/blocks/[block-name]/`
3. Block data (if any) goes to `src/app/[block-name]/`
4. Update imports to match your project structure
5. Customize content, colors, and layout with Tailwind classes
