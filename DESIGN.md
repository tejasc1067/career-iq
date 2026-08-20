---
version: 1.0.0
name: CareerIQ Design System
description: >-
  Original design system for CareerIQ, an AI-powered career intelligence
  product. Product-first, not marketing-first: a calm cool-neutral canvas,
  one scarce teal brand accent, hairline-and-lift depth instead of heavy
  shadow, and a 14px dense UI body paired with a 16px reading measure for
  resume surfaces. Optimized for resume viewing and editing, diff review of
  AI suggestions, dashboards, job lists, match scoring, and roadmaps.
  Every token is defined as a semantic role in both light and dark themes and
  maps to Tailwind CSS custom properties and shadcn/ui variables.
  Fonts are open source. Status colors and chart colors are separate systems.

meta:
  audience: authenticated product surfaces (app shell), not marketing pages
  themes: [light, dark]
  font-licensing: open-source only (SIL OFL)
  contrast-target: WCAG 2.2 AA (4.5:1 text, 3:1 large text and UI boundaries)
  base-unit: 4px
  default-theme: system

# ---------------------------------------------------------------------------
# COLOR — semantic roles. No component may reference a raw hex value.
# Raw ramps exist only so the semantic roles below have something to point at.
# ---------------------------------------------------------------------------

palette:
  # Brand ramp — "Meridian" teal. CareerIQ's single chromatic accent.
  brand:
    "50":  "#eff9f8"
    "100": "#d5f0ed"
    "200": "#abe1dc"
    "300": "#78cbc5"
    "400": "#47ada7"
    "500": "#2b908b"
    "600": "#1d7370"
    "700": "#1a5c5a"
    "800": "#174a49"
    "900": "#153d3c"
  # Neutral ramp — cool slate-tinted. Never pure black, never pure gray.
  neutral:
    "0":   "#ffffff"
    "25":  "#fafbfb"
    "50":  "#f4f6f6"
    "100": "#eaeeee"
    "200": "#e5e9e9"
    "300": "#cdd4d4"
    "400": "#a3adad"
    "500": "#7d8888"
    "600": "#5f6b6b"
    "700": "#3a4444"
    "800": "#232b2e"
    "850": "#1b2225"
    "900": "#141a1c"
    "950": "#0c1012"
    ink:   "#101616"
  # Status ramp — reserved for state. Never used for categories or series.
  status:
    success:      "#1a7f52"
    success-dark: "#3fbf85"
    warning:      "#9a6b08"
    warning-dark: "#e0b64a"
    danger:       "#a3282f"
    danger-dark:  "#f0868c"
    info:         "#1c5f9e"
    info-dark:    "#63b0ec"

colors-light:
  # Surfaces
  canvas:            "#f4f6f6"   # app background behind panels
  canvas-subtle:     "#fafbfb"
  surface:           "#ffffff"   # cards, panels, sheets
  surface-sunken:    "#f4f6f6"   # inset wells, code blocks, table zebra
  surface-raised:    "#ffffff"   # popovers, dropdowns, modals
  surface-hover:     "#eaeeee"
  surface-active:    "#e5e9e9"
  # Borders
  hairline:          "#e5e9e9"   # default 1px border
  hairline-subtle:   "#eaeeee"   # internal dividers
  hairline-strong:   "#cdd4d4"   # inputs, emphasis borders, focus-adjacent
  # Text
  ink:               "#101616"   # 18.3:1 on surface
  ink-secondary:     "#3a4444"   # 9.9:1
  ink-muted:         "#5f6b6b"   # 5.5:1 — smallest AA-safe body role
  ink-subtle:        "#7d8888"   # 3.7:1 — LARGE TEXT / NON-ESSENTIAL ONLY
  ink-disabled:      "#a3adad"   # decorative, exempt from AA
  ink-inverse:       "#ffffff"
  # Brand
  brand:             "#1d7370"   # 5.6:1 on surface, 5.6:1 white-on-brand
  brand-hover:       "#1a5c5a"
  brand-active:      "#174a49"
  brand-subtle:      "#eff9f8"   # tinted fill for selected rows, soft badges
  brand-subtle-hover:"#d5f0ed"
  brand-border:      "#abe1dc"
  brand-ink:         "#174a49"   # brand-colored text on brand-subtle fill
  on-brand:          "#ffffff"
  # Focus
  focus-ring:        "#1d7370"
  focus-ring-offset: "#ffffff"
  # Status — fg is text/icon, subtle is fill, border is 1px
  success:           "#1a7f52"
  success-subtle:    "#ebf7f1"
  success-border:    "#b3ddc8"
  warning:           "#9a6b08"
  warning-subtle:    "#fdf5e4"
  warning-border:    "#e8d3a0"
  danger:            "#a3282f"
  danger-subtle:     "#fdeeee"
  danger-border:     "#f0c4c4"
  info:              "#1c5f9e"
  info-subtle:       "#edf4fb"
  info-border:       "#bcd6ee"
  # AI provenance — proposed/unreviewed content. See section 20.
  ai-accent:         "#6153ad"
  ai-subtle:         "#f2f0fb"
  ai-border:         "#cdc6ec"
  ai-ink:            "#463c80"
  # Diff surfaces — see section 19
  diff-add-bg:       "#eaf6f0"
  diff-add-ink:      "#155f3e"
  diff-add-gutter:   "#1a7f52"
  diff-remove-bg:    "#fceeef"
  diff-remove-ink:   "#7f2026"
  diff-remove-gutter:"#a3282f"
  diff-context-ink:  "#5f6b6b"
  # Overlay
  overlay:           "rgba(16,22,22,0.40)"

colors-dark:
  canvas:            "#0c1012"
  canvas-subtle:     "#0c1012"
  surface:           "#141a1c"
  surface-sunken:    "#0c1012"
  surface-raised:    "#1b2225"
  surface-hover:     "#1b2225"
  surface-active:    "#232b2e"
  hairline:          "#2c3538"
  hairline-subtle:   "#232b2e"
  hairline-strong:   "#3d4749"
  ink:               "#eef2f2"   # 17.0:1 on canvas
  ink-secondary:     "#c3cccc"   # 11.6:1
  ink-muted:         "#98a3a3"   # 7.4:1
  ink-subtle:        "#788484"   # 4.4:1 on canvas — small non-essential text
  ink-disabled:      "#596465"
  ink-inverse:       "#0c1012"
  brand:             "#4fbdb5"   # 8.5:1 on canvas
  brand-hover:       "#78cbc5"
  brand-active:      "#abe1dc"
  brand-subtle:      "#12312f"
  brand-subtle-hover:"#173f3d"
  brand-border:      "#245a56"
  brand-ink:         "#8fd8d1"
  on-brand:          "#08201f"
  focus-ring:        "#4fbdb5"
  focus-ring-offset: "#0c1012"
  success:           "#3fbf85"
  success-subtle:    "#0f2c20"
  success-border:    "#1f5a41"
  warning:           "#e0b64a"
  warning-subtle:    "#2e2410"
  warning-border:    "#5c4a1c"
  danger:            "#f0868c"
  danger-subtle:     "#2f1518"
  danger-border:     "#63292e"
  info:              "#63b0ec"
  info-subtle:       "#0f2231"
  info-border:       "#1f4763"
  ai-accent:         "#9b8ce6"
  ai-subtle:         "#1c1830"
  ai-border:         "#3a3162"
  ai-ink:            "#c3b9f4"
  diff-add-bg:       "#0f2c20"
  diff-add-ink:      "#8fdcb4"
  diff-add-gutter:   "#3fbf85"
  diff-remove-bg:    "#2f1518"
  diff-remove-ink:   "#f2aeb2"
  diff-remove-gutter:"#f0868c"
  diff-context-ink:  "#98a3a3"
  overlay:           "rgba(0,0,0,0.60)"

# ---------------------------------------------------------------------------
# CHART COLORS — a separate system from status. See section 17.
# The categorical set deliberately contains no green and no red, so a series
# is never mistaken for a pass/fail signal.
# ---------------------------------------------------------------------------

charts-light:
  categorical:
    "1": "#1d7370"  # teal      (primary series — matches brand)
    "2": "#2e669e"  # blue
    "3": "#6153ad"  # violet
    "4": "#9c4a86"  # magenta
    "5": "#a75440"  # copper
    "6": "#8f6c1f"  # ochre
    "7": "#6b7a24"  # olive
    "8": "#5a6b78"  # slate
  sequential: ["#d5f0ed", "#abe1dc", "#78cbc5", "#47ada7", "#2b908b", "#1d7370"]
  diverging:  ["#a75440", "#c4886f", "#e0bdac", "#e8eaea", "#a9cfcb", "#5da8a1", "#1d7370"]
  grid:       "#e5e9e9"
  axis:       "#7d8888"
  axis-label: "#5f6b6b"
  reference:  "#a3adad"
  track:      "#eaeeee"

charts-dark:
  categorical:
    "1": "#4fbdb5"
    "2": "#6ba6de"
    "3": "#9b8ce6"
    "4": "#d987c1"
    "5": "#e08d76"
    "6": "#cfa947"
    "7": "#a8bb52"
    "8": "#94a6b4"
  sequential: ["#153d3c", "#1a5c5a", "#2b908b", "#47ada7", "#78cbc5", "#abe1dc"]
  diverging:  ["#e08d76", "#c07a63", "#8a6154", "#3a4444", "#3d7d76", "#4fbdb5", "#8fd8d1"]
  grid:       "#232b2e"
  axis:       "#788484"
  axis-label: "#98a3a3"
  reference:  "#596465"
  track:      "#232b2e"

# Match-score bands. Neutral-to-brand intensity ramp — NOT red-to-green.
# A weak match is not an error, so it must not read as one.
score-bands-light:
  low:       { range: "0-39",   fill: "#eaeeee", ink: "#5f6b6b", accent: "#a3adad" }
  fair:      { range: "40-59",  fill: "#fdf5e4", ink: "#7a5406", accent: "#c79a2a" }
  good:      { range: "60-74",  fill: "#eff9f8", ink: "#1a5c5a", accent: "#47ada7" }
  strong:    { range: "75-89",  fill: "#d5f0ed", ink: "#174a49", accent: "#1d7370" }
  excellent: { range: "90-100", fill: "#abe1dc", ink: "#153d3c", accent: "#174a49" }
score-bands-dark:
  low:       { range: "0-39",   fill: "#232b2e", ink: "#98a3a3", accent: "#596465" }
  fair:      { range: "40-59",  fill: "#2e2410", ink: "#e0b64a", accent: "#cfa947" }
  good:      { range: "60-74",  fill: "#12312f", ink: "#8fd8d1", accent: "#2b908b" }
  strong:    { range: "75-89",  fill: "#173f3d", ink: "#abe1dc", accent: "#4fbdb5" }
  excellent: { range: "90-100", fill: "#245a56", ink: "#eff9f8", accent: "#78cbc5" }

# ---------------------------------------------------------------------------
# TYPOGRAPHY — open fonts only.
# ---------------------------------------------------------------------------

fonts:
  sans:     "Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif"
  mono:     "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
  document: "var(--font-sans)"   # resume rendering surface; template-overridable
  features-global: "'cv05' 1, 'cv11' 1"   # Inter: single-story a, disambiguated l
  features-numeric: "'tnum' 1, 'zero' 1"  # applied per-element on any figure
  weights: [400, 500, 600]                # 600 is the display ceiling

typography:
  display-lg:   { size: 32px, weight: 600, lineHeight: 1.18, letterSpacing: -0.6px }
  display-md:   { size: 28px, weight: 600, lineHeight: 1.20, letterSpacing: -0.5px }
  heading-xl:   { size: 24px, weight: 600, lineHeight: 1.25, letterSpacing: -0.4px }
  heading-lg:   { size: 20px, weight: 600, lineHeight: 1.30, letterSpacing: -0.3px }
  heading-md:   { size: 18px, weight: 600, lineHeight: 1.35, letterSpacing: -0.2px }
  heading-sm:   { size: 16px, weight: 600, lineHeight: 1.40, letterSpacing: -0.1px }
  body-lg:      { size: 16px, weight: 400, lineHeight: 1.60, letterSpacing: 0 }
  body:         { size: 14px, weight: 400, lineHeight: 1.55, letterSpacing: 0 }
  body-medium:  { size: 14px, weight: 500, lineHeight: 1.55, letterSpacing: 0 }
  body-sm:      { size: 13px, weight: 400, lineHeight: 1.50, letterSpacing: 0 }
  label:        { size: 13px, weight: 500, lineHeight: 1.40, letterSpacing: 0 }
  label-sm:     { size: 12px, weight: 500, lineHeight: 1.35, letterSpacing: 0 }
  caption:      { size: 12px, weight: 400, lineHeight: 1.45, letterSpacing: 0 }
  micro:        { size: 11px, weight: 400, lineHeight: 1.40, letterSpacing: 0 }
  eyebrow:      { size: 11px, weight: 600, lineHeight: 1.30, letterSpacing: 0.6px, transform: uppercase }
  button:       { size: 14px, weight: 500, lineHeight: 1.20, letterSpacing: 0 }
  button-sm:    { size: 13px, weight: 500, lineHeight: 1.20, letterSpacing: 0 }
  numeric:      { size: 14px, weight: 500, lineHeight: 1.40, features: tnum }
  numeric-lg:   { size: 20px, weight: 600, lineHeight: 1.25, features: tnum, letterSpacing: -0.3px }
  metric:       { size: 32px, weight: 600, lineHeight: 1.10, features: tnum, letterSpacing: -0.8px }
  metric-xl:    { size: 44px, weight: 600, lineHeight: 1.05, features: tnum, letterSpacing: -1.4px }
  mono:         { size: 13px, weight: 400, lineHeight: 1.55, letterSpacing: 0 }
  # Resume document surface — reading measure, not UI density
  doc-name:     { size: 22px, weight: 600, lineHeight: 1.25, letterSpacing: -0.3px }
  doc-heading:  { size: 13px, weight: 600, lineHeight: 1.35, letterSpacing: 0.5px, transform: uppercase }
  doc-role:     { size: 14px, weight: 600, lineHeight: 1.40 }
  doc-body:     { size: 14px, weight: 400, lineHeight: 1.60 }
  doc-meta:     { size: 12px, weight: 400, lineHeight: 1.45 }

# ---------------------------------------------------------------------------
# SPACING — 4px base. Keys are Tailwind-compatible so there is no
# translation layer between this document and the utility classes.
# ---------------------------------------------------------------------------

spacing:
  "0":    0px
  px:     1px
  "0.5":  2px
  "1":    4px
  "1.5":  6px
  "2":    8px
  "2.5":  10px
  "3":    12px
  "4":    16px
  "5":    20px
  "6":    24px
  "8":    32px
  "10":   40px
  "12":   48px
  "16":   64px
  "20":   80px
  "24":   96px

layout:
  app-max-width:        1440px
  content-max-width:    1120px
  reading-max-width:    72ch     # resume + AI explanation prose
  sidebar-width:        264px
  sidebar-collapsed:    64px
  topbar-height:        56px
  subnav-height:        44px
  inspector-width:      360px    # right-hand AI/detail panel
  gutter-desktop:       24px
  gutter-mobile:        16px
  panel-padding:        20px
  panel-padding-dense:  12px
  row-height:           44px     # table + list default
  row-height-dense:     36px

rounded:
  none: 0px
  xs:   4px
  sm:   6px
  md:   8px      # buttons, inputs, badges-square — the system default
  lg:   12px     # cards, panels
  xl:   16px     # modals, sheets, resume page chrome
  "2xl": 20px
  full: 9999px   # avatars, pills, score rings, status dots

elevation-light:
  e0: { shadow: none, border: "1px solid {colors.hairline}" }
  e1: { shadow: "0 1px 2px rgba(16,22,22,0.04)", border: "1px solid {colors.hairline}" }
  e2: { shadow: "0 1px 2px rgba(16,22,22,0.04), 0 2px 6px rgba(16,22,22,0.05)", border: "1px solid {colors.hairline}" }
  e3: { shadow: "0 2px 4px rgba(16,22,22,0.04), 0 8px 16px -4px rgba(16,22,22,0.06)", border: "1px solid {colors.hairline}" }
  e4: { shadow: "0 4px 8px -2px rgba(16,22,22,0.05), 0 16px 32px -8px rgba(16,22,22,0.10)", border: "1px solid {colors.hairline}" }

elevation-dark:
  e0: { surface: "{colors.surface}",        shadow: none, border: "1px solid {colors.hairline}" }
  e1: { surface: "{colors.surface}",        shadow: none, border: "1px solid {colors.hairline}" }
  e2: { surface: "{colors.surface-raised}", shadow: none, border: "1px solid {colors.hairline}" }
  e3: { surface: "{colors.surface-raised}", shadow: "0 8px 24px rgba(0,0,0,0.45)", border: "1px solid {colors.hairline-strong}" }
  e4: { surface: "{colors.surface-active}", shadow: "0 16px 40px rgba(0,0,0,0.55)", border: "1px solid {colors.hairline-strong}" }

focus:
  ring-width:  2px
  ring-offset: 2px
  ring-color:  "{colors.focus-ring}"
  selector:    ":focus-visible"
  inset-variant: "0 0 0 2px {colors.focus-ring} inset"   # for table cells and rows

motion:
  duration-instant: 0ms
  duration-fast:    120ms
  duration-base:    180ms
  duration-slow:    240ms
  duration-slower:  320ms
  ease-standard:    "cubic-bezier(0.2, 0, 0, 1)"
  ease-enter:       "cubic-bezier(0.16, 1, 0.3, 1)"
  ease-exit:        "cubic-bezier(0.4, 0, 1, 1)"
  ease-linear:      "linear"
  reduced-motion:   "all transitions collapse to 0ms except opacity, which collapses to 120ms"

breakpoints:
  sm:   640px
  md:   768px
  lg:   1024px
  xl:   1280px
  "2xl": 1536px

z-index:
  base:      0
  sticky:    10
  sidebar:   20
  topbar:    30
  dropdown:  40
  overlay:   50
  modal:     60
  toast:     70
  tooltip:   80

# ---------------------------------------------------------------------------
# COMPONENTS
# ---------------------------------------------------------------------------

components:
  button-primary:
    background: "{colors.brand}"
    text: "{colors.on-brand}"
    typography: "{typography.button}"
    rounded: "{rounded.md}"
    padding: "8px 14px"
    minHeight: 36px
    minHeightTouch: 44px
    hover: "{colors.brand-hover}"
    active: "{colors.brand-active}"
    disabled: { background: "{colors.surface-active}", text: "{colors.ink-disabled}" }
  button-secondary:
    background: "{colors.surface}"
    text: "{colors.ink}"
    border: "1px solid {colors.hairline-strong}"
    typography: "{typography.button}"
    rounded: "{rounded.md}"
    padding: "8px 14px"
    hover: "{colors.surface-hover}"
  button-ghost:
    background: transparent
    text: "{colors.ink-secondary}"
    typography: "{typography.button}"
    rounded: "{rounded.md}"
    padding: "8px 12px"
    hover: "{colors.surface-hover}"
  button-destructive:
    background: "{colors.danger}"
    text: "#ffffff"
    typography: "{typography.button}"
    rounded: "{rounded.md}"
    padding: "8px 14px"
  button-icon:
    background: transparent
    text: "{colors.ink-muted}"
    rounded: "{rounded.md}"
    size: 36px
    sizeTouch: 44px
    iconSize: 16px
  text-input:
    background: "{colors.surface}"
    text: "{colors.ink}"
    placeholder: "{colors.ink-subtle}"
    border: "1px solid {colors.hairline-strong}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: "8px 12px"
    height: 36px
    heightTouch: 44px
    focus: { border: "1px solid {colors.brand}", ring: "{focus.ring-width} {colors.focus-ring}" }
    invalid: { border: "1px solid {colors.danger}" }
  textarea:
    inherits: text-input
    minHeight: 96px
    padding: "10px 12px"
  select-trigger:
    inherits: text-input
    chevron: "{colors.ink-muted}"
  checkbox:
    size: 16px
    rounded: "{rounded.xs}"
    border: "1px solid {colors.hairline-strong}"
    checked: { background: "{colors.brand}", mark: "{colors.on-brand}" }
    hitArea: 44px
  switch:
    track: { width: 36px, height: 20px, rounded: "{rounded.full}", off: "{colors.hairline-strong}", on: "{colors.brand}" }
    thumb: { size: 16px, color: "#ffffff" }
  card:
    background: "{colors.surface}"
    rounded: "{rounded.lg}"
    padding: "{layout.panel-padding}"
    elevation: e1
  card-interactive:
    inherits: card
    hover: { background: "{colors.surface-hover}", elevation: e2 }
    selected: { border: "1px solid {colors.brand-border}", background: "{colors.brand-subtle}" }
  panel-header:
    typography: "{typography.heading-md}"
    padding: "14px {layout.panel-padding}"
    border-bottom: "1px solid {colors.hairline-subtle}"
  sidebar:
    background: "{colors.canvas-subtle}"
    border-right: "1px solid {colors.hairline}"
    width: "{layout.sidebar-width}"
    padding: "12px 8px"
  sidebar-item:
    text: "{colors.ink-secondary}"
    typography: "{typography.body-medium}"
    rounded: "{rounded.md}"
    padding: "8px 10px"
    height: 36px
    iconSize: 16px
    hover: "{colors.surface-hover}"
  sidebar-item-active:
    background: "{colors.brand-subtle}"
    text: "{colors.brand-ink}"
    indicator: "3px {colors.brand} left bar"
  sidebar-section-label:
    typography: "{typography.eyebrow}"
    text: "{colors.ink-subtle}"
    padding: "12px 10px 4px"
  topbar:
    background: "{colors.surface}"
    border-bottom: "1px solid {colors.hairline}"
    height: "{layout.topbar-height}"
    padding: "0 16px"
  table-header-cell:
    background: "{colors.surface-sunken}"
    text: "{colors.ink-muted}"
    typography: "{typography.label-sm}"
    padding: "8px 12px"
    border-bottom: "1px solid {colors.hairline}"
  table-cell:
    text: "{colors.ink}"
    typography: "{typography.body}"
    padding: "10px 12px"
    border-bottom: "1px solid {colors.hairline-subtle}"
    height: "{layout.row-height}"
  table-cell-numeric:
    inherits: table-cell
    typography: "{typography.numeric}"
    align: right
  table-row-hover:
    background: "{colors.surface-hover}"
  table-row-selected:
    background: "{colors.brand-subtle}"
  badge-neutral:
    background: "{colors.surface-sunken}"
    text: "{colors.ink-secondary}"
    typography: "{typography.label-sm}"
    rounded: "{rounded.sm}"
    padding: "2px 8px"
  badge-success: { background: "{colors.success-subtle}", text: "{colors.success}", border: "1px solid {colors.success-border}", inherits: badge-neutral }
  badge-warning: { background: "{colors.warning-subtle}", text: "{colors.warning}", border: "1px solid {colors.warning-border}", inherits: badge-neutral }
  badge-danger:  { background: "{colors.danger-subtle}",  text: "{colors.danger}",  border: "1px solid {colors.danger-border}",  inherits: badge-neutral }
  badge-info:    { background: "{colors.info-subtle}",    text: "{colors.info}",    border: "1px solid {colors.info-border}",    inherits: badge-neutral }
  badge-brand:   { background: "{colors.brand-subtle}",   text: "{colors.brand-ink}", border: "1px solid {colors.brand-border}", inherits: badge-neutral }
  badge-ai:      { background: "{colors.ai-subtle}",      text: "{colors.ai-ink}",  border: "1px solid {colors.ai-border}",      inherits: badge-neutral }
  status-dot:
    size: 8px
    rounded: "{rounded.full}"
    pairedLabel: required
  progress-linear:
    track: "{charts.track}"
    fill: "{colors.brand}"
    height: 6px
    rounded: "{rounded.full}"
  progress-ring:
    size: 64px
    stroke: 6px
    track: "{charts.track}"
    fill: "score band accent"
    label: "{typography.numeric-lg}"
  score-ring:
    inherits: progress-ring
    size: 88px
    stroke: 8px
    label: "{typography.metric}"
    caption: "{typography.label-sm}"
  resume-page:
    background: "{colors.surface}"
    rounded: "{rounded.xl}"
    padding: "48px 56px"
    elevation: e2
    maxWidth: 816px
    typography: "{typography.doc-body}"
  diff-line-add:
    background: "{colors.diff-add-bg}"
    text: "{colors.diff-add-ink}"
    gutter: "3px {colors.diff-add-gutter} left bar"
    padding: "4px 12px"
    typography: "{typography.doc-body}"
  diff-line-remove:
    background: "{colors.diff-remove-bg}"
    text: "{colors.diff-remove-ink}"
    gutter: "3px {colors.diff-remove-gutter} left bar"
    padding: "4px 12px"
    decoration: line-through
  diff-line-context:
    background: transparent
    text: "{colors.diff-context-ink}"
    padding: "4px 12px"
  suggestion-card:
    background: "{colors.surface}"
    border: "1px solid {colors.ai-border}"
    accent: "3px {colors.ai-accent} left bar"
    rounded: "{rounded.lg}"
    padding: "16px"
    elevation: e1
  suggestion-rationale:
    background: "{colors.ai-subtle}"
    text: "{colors.ai-ink}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.md}"
    padding: "10px 12px"
  job-card:
    inherits: card-interactive
    padding: "16px"
    rounded: "{rounded.lg}"
    titleTypography: "{typography.heading-sm}"
    metaTypography: "{typography.body-sm}"
  roadmap-node:
    background: "{colors.surface}"
    border: "1px solid {colors.hairline}"
    rounded: "{rounded.lg}"
    padding: "14px 16px"
    connector: "2px {colors.hairline-strong}"
    states:
      done:     { accent: "{colors.success}", icon: check }
      current:  { accent: "{colors.brand}",   border: "1px solid {colors.brand-border}", background: "{colors.brand-subtle}" }
      upcoming: { accent: "{colors.ink-subtle}" }
  skeleton:
    background: "{colors.surface-sunken}"
    shimmer: "{colors.surface-hover}"
    rounded: "{rounded.sm}"
    duration: 1400ms
  empty-state:
    background: transparent
    titleTypography: "{typography.heading-md}"
    bodyTypography: "{typography.body}"
    bodyColor: "{colors.ink-muted}"
    maxWidth: 42ch
    padding: "48px 24px"
  error-inline:
    background: "{colors.danger-subtle}"
    border: "1px solid {colors.danger-border}"
    text: "{colors.danger}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.md}"
    padding: "10px 12px"
  toast:
    background: "{colors.surface-raised}"
    rounded: "{rounded.lg}"
    padding: "12px 14px"
    elevation: e4
    typography: "{typography.body}"
  modal:
    background: "{colors.surface-raised}"
    rounded: "{rounded.xl}"
    padding: "24px"
    elevation: e4
    maxWidth: 560px
    overlay: "{colors.overlay}"
  tooltip:
    background: "{colors.ink}"
    text: "{colors.ink-inverse}"
    typography: "{typography.caption}"
    rounded: "{rounded.sm}"
    padding: "6px 8px"
---

# CareerIQ Design System

> This document is the authority on how CareerIQ looks and behaves visually.
> It describes an **original** CareerIQ identity. It is not derived from, and
> must not reproduce, any third-party brand's colors, fonts, wordmarks, or
> naming. The `awesome-design-md` collection in this workspace was read as
> structural research only — for how a design document should be organised,
> not for what CareerIQ should look like.
>
> **Scope:** authenticated product surfaces. CareerIQ is a tool people work
> inside for long sessions, not a page they scroll once. Every decision below
> optimises for sustained reading, dense data, and reviewable AI output.

---

## 1. Design Philosophy

CareerIQ handles the single most personal document most people own. The
interface has to earn trust before it earns admiration. Five principles, in
priority order — when two conflict, the earlier one wins.

**1. Legibility before expression.** A resume, a match score, a salary band,
a skill gap: all of it is information the user will act on. Type contrast,
alignment, and numeric clarity outrank every decorative instinct.

**2. Calm by subtraction.** One chromatic accent — Meridian teal. Everything
else is a calibrated cool-neutral ladder. Color in CareerIQ always *means*
something: brand action, status, data series, or AI provenance. There is no
decorative color. No gradient meshes, no atmospheric washes, no illustration
system. A career-decision tool that shouts is a career-decision tool nobody
trusts.

**3. Depth by hairline, not by shadow.** Surfaces separate through 1px
hairlines and one-step surface lifts. Shadows appear only where something
genuinely floats above the page: popovers, modals, toasts, and the resume
page. In dark mode shadows do almost nothing, so depth there is carried
entirely by the surface ladder.

**4. AI is a guest with a name tag.** Every machine-generated element is
visually attributable, always reviewable, and never silently applied. AI
content uses its own provenance color and its own surface treatment so that
"what the user wrote" and "what the model proposed" are never confusable —
this is a product-integrity requirement, not a stylistic preference.

**5. Density is a feature, and it is adjustable.** Default row height 44px,
default UI body 14px. A dense mode drops rows to 36px for power users
scanning long job or diff lists. Reading surfaces (resume body, AI rationale)
move up to 16px/1.6 and cap at a 72ch measure — density and readability are
separate problems and get separate settings.

**Tone in one line:** an instrument panel, not a poster.

### Anti-patterns

- Do not add a second brand accent. Requests for "a bit more color" are
  answered with the chart palette or the status palette, both of which
  already carry meaning.
- Do not use gradients as surfaces. A gradient is permitted only inside a
  data visualisation (sequential scale) or the score ring arc.
- Do not use pill-shaped buttons. CareerIQ buttons are 8px rectangles;
  `{rounded.full}` is for avatars, status dots, score rings, and filter chips
  only.
- Do not raise display weight past 600. Weight is the loudest typographic
  lever and this product does not shout.
- Do not communicate anything with color alone. Every status color pairs with
  an icon, a label, or both.
- Do not put marketing patterns (hero bands, testimonial cards, pricing
  tables, logo walls) into the app shell. Those belong to a separate public
  site system, out of scope here.

---

## 2. Color System

Three independent color systems that never borrow from each other:

| System | Owns | Tokens |
|---|---|---|
| **Brand** | Identity, primary action, selection, focus | `brand`, `brand-hover`, `brand-active`, `brand-subtle`, `brand-border`, `brand-ink`, `on-brand` |
| **Status** | State and outcome | `success`, `warning`, `danger`, `info` + `-subtle` / `-border` each |
| **Data** | Series, categories, magnitude | `charts.categorical.1–8`, `charts.sequential`, `charts.diverging` |

Plus one narrow fourth system: **AI provenance** (`ai-accent`, `ai-subtle`,
`ai-border`, `ai-ink`) — a violet that exists solely to mark
machine-generated, not-yet-approved content. It is never used for status and
never used for a chart series.

### Brand accent — Meridian teal

`#1d7370` in light mode, `#4fbdb5` in dark. Teal reads as considered and
clinical rather than urgent — it is neither the corporate-blue default nor a
warning-adjacent warm hue, and it stays clearly distinct from the green that
means "success" and the red that means "problem". That separation matters in
a product where a screen can simultaneously show a brand-colored primary
action, a green passed check, and a red validation error.

Scarcity rule: at most **one** filled brand-colored element per viewport
region. In practice that is the single primary action of the current view.
Selection states, active nav, and focus rings use brand at low intensity
(`brand-subtle` fill, `brand` 1px border or 3px indicator), not a full fill.

### Semantic roles, not raw values

Components reference roles (`{colors.ink-muted}`), never ramps
(`{palette.neutral.600}`) and never hex. The ramps in the frontmatter exist
only to give the roles values. This is what makes the dark theme a
token swap instead of a rewrite.

### Text color roles and where each is allowed

| Role | Light contrast on `surface` | Allowed for |
|---|---|---|
| `ink` | 18.3:1 | Headings, primary body, table values, resume content |
| `ink-secondary` | 9.9:1 | Secondary body, nav labels, panel subtitles |
| `ink-muted` | 5.5:1 | Helper text, captions, table headers, axis labels |
| `ink-subtle` | 3.7:1 | **Large text (≥18.66px) or non-essential only** — eyebrows, watermark-style metadata. Never for anything the user must read to act. |
| `ink-disabled` | — | Disabled control text only (exempt from AA by WCAG 1.4.3) |

`ink-subtle` failing AA at body size is deliberate and documented rather than
quietly shipped: it exists for de-emphasis at large sizes. Any reviewer who
finds it on 13px essential copy should treat that as a bug.

### Status color pairs

Each status has a three-token set: `X` (text and icon), `X-subtle`
(background fill), `X-border` (1px). Never render status text directly on
`canvas` in a large filled block; use the subtle fill so the badge or banner
reads as a contained object.

| Status | Light | Contrast on white | Meaning in CareerIQ |
|---|---|---|---|
| `success` | `#1a7f52` | 5.0:1 | Change applied, requirement met, verified section |
| `warning` | `#9a6b08` | 4.7:1 | Weak or thin content, missing evidence, expiring item |
| `danger` | `#a3282f` | 7.2:1 | Validation failure, destructive action, unsupported claim |
| `info` | `#1c5f9e` | 6.6:1 | Neutral system notice, tips, parsing notes |

### Contrast verification

Every value above was computed against its intended background, not eyeballed.
The obligation is standing: any new color token must ship with its measured
ratio against the surfaces it will sit on, and the pair must clear 4.5:1 for
text, 3:1 for large text and for UI-component boundaries.

---

## 3. Light Mode

Light mode is the default and the primary design target — resume work is
document work, and documents read as paper.

The canvas is **not white**. `canvas` is `#f4f6f6`, a cool near-white, and
panels sit on top of it in pure `#ffffff`. This inversion of the common
"white page, gray cards" pattern gives every card an edge without a shadow,
and makes the resume page — the only pure-white full-bleed surface — read as
the document it is.

Surface ladder, lightest object on top:

| Token | Value | Use |
|---|---|---|
| `canvas` | `#f4f6f6` | App background behind everything |
| `canvas-subtle` | `#fafbfb` | Sidebar, secondary rails |
| `surface` | `#ffffff` | Cards, panels, table bodies, resume page |
| `surface-sunken` | `#f4f6f6` | Table headers, code blocks, inset wells, chart tracks |
| `surface-raised` | `#ffffff` | Popovers, dropdowns, modals (separated by shadow, not tone) |
| `surface-hover` | `#eaeeee` | Row and item hover |
| `surface-active` | `#e5e9e9` | Pressed state |

Hairlines do the structural work: `hairline` `#e5e9e9` for card and table
borders, `hairline-subtle` `#eaeeee` for internal row dividers,
`hairline-strong` `#cdd4d4` for input borders — inputs need a 3:1 boundary
against their surface to satisfy WCAG 1.4.11, so they get the stronger line.

---

## 4. Dark Mode

Dark mode is a first-class theme, not a filter. Three rules distinguish it
from an inverted light theme:

**1. Depth comes from the surface ladder, not shadow.** `canvas` `#0c1012` →
`surface` `#141a1c` → `surface-raised` `#1b2225` → `surface-active` `#232b2e`.
Shadows are retained only on `e3`/`e4` (modals, toasts, dropdowns) where a
real occlusion cue is needed.

**2. Ink and brand are re-derived, not lightened.** The dark brand token is
`#4fbdb5` — a lighter, less saturated Meridian that reaches 8.5:1 on canvas.
Reusing the light brand `#1d7370` on a dark canvas would give ~2.4:1 and fail.
Text on the dark brand fill is `on-brand` `#08201f`, a near-black — a light
accent carries dark type.

**3. Status and chart colors get their own dark set.** Dark-mode status hues
are desaturated and lightened (`success` `#3fbf85`, `danger` `#f0868c`), and
the `-subtle` fills become deep tints of the same hue rather than pale ones.
The diverging chart scale is re-anchored on `#3a4444` instead of a light
neutral so its midpoint reads as "neutral" and not "missing data".

Canvas is `#0c1012`, not `#000000`. True black against a bright accent
produces halation on OLED panels and makes long reading sessions harder;
a slightly lifted near-black with a cool cast is calmer.

**Implementation:** the `dark` class on `<html>`, `next-themes` for the
toggle, `system` as the default. Both themes must be defined at all times —
a component that reads correctly in one theme and not the other is unfinished.

---

## 5. Typography

**Inter** (SIL OFL, variable) for everything in the UI. **JetBrains Mono**
(SIL OFL) for code, IDs, keyboard hints, and raw parsed text. Two families,
both open, both loaded through `next/font/local` or `next/font/google` with
`display: swap` and subsetting. No third family, and no proprietary or
brand-licensed face at any point.

Global feature settings: `font-feature-settings: 'cv05' 1, 'cv11' 1` on
`body` — Inter's single-story `a` and disambiguated `l`, which measurably
helps at 13–14px. Weights are limited to 400 / 500 / 600; **600 is the
ceiling**, in every size, forever.

### Scale

The scale is built for a product, so it starts dense and tops out early. The
largest role is 44px (`metric-xl`, used for a single hero number), and the
largest *text* role is 32px. There is no 64px or 80px tier because CareerIQ
has no marketing hero.

Default UI body is **14px / 1.55**. Reading surfaces — resume body, AI
rationale, long-form explanations — step up to **16px / 1.6** and are capped
at a 72ch measure.

See `typography:` in the frontmatter for the full table of 24 roles.

### Numerals

Any figure the user might compare against another figure gets
`font-feature-settings: 'tnum' 1, 'zero' 1`: match scores, salary ranges,
years of experience, ATS scores, percentages, counts, dates in tables.
Tabular figures keep columns aligned and stop digits from shifting when a
number updates during streaming — a live-updating proportional number is
visibly unstable. The `numeric`, `numeric-lg`, `metric`, and `metric-xl`
roles have this built in; apply it explicitly anywhere else numerals appear
in a comparable context.

### Tracking

Negative letter-spacing scales with size: `-1.4px` at 44px down to `0` at
14px and below. Never positive, with one exception — `eyebrow` at `+0.6px`,
because uppercase 11px needs the air.

### Casing

Sentence case for everything: headings, buttons, labels, table headers, menu
items. Uppercase appears only in the `eyebrow` and `doc-heading` roles.
Sentence case is faster to read and less shouty, which is the whole brief.

---

## 6. Spacing Scale

4px base unit. The token keys are deliberately identical to Tailwind's
numeric spacing keys (`1` = 4px, `2` = 8px, `4` = 16px, `6` = 24px …) so
there is no mapping layer between this document and the class names — the
design system and the utility framework speak one language.

Applied rhythm:

| Context | Value |
|---|---|
| Icon-to-label gap | `2` (8px) |
| Form field vertical gap | `4` (16px) |
| Label to its control | `1.5` (6px) |
| Panel interior padding | `5` (20px), or `3` (12px) dense |
| Card interior padding | `4`–`5` (16–20px) |
| Gap between sibling cards | `4` (16px) |
| Section gap inside a page | `6`–`8` (24–32px) |
| Page top padding | `6` (24px) |
| Resume page interior | `12` × `14` (48px × 56px) |

**Interior tight, exterior generous.** Inside a card, related elements sit at
8px; the gap between cards is 16–24px. Inverting this — loose interiors,
tight exteriors — is the most common way a dense product UI stops feeling
grouped.

Vertical rhythm on dense surfaces snaps to 4px so that a 44px row, a 36px
control, and a 20px line box all land on the same grid.

---

## 7. Layout and Grid

### App shell

```
┌───────────────────────────────────────────────────────────────┐
│ Topbar  56px — breadcrumb · search · theme · account          │
├──────────┬──────────────────────────────────┬─────────────────┤
│ Sidebar  │  Content                          │  Inspector     │
│ 264px    │  max 1120px, gutters 24px         │  360px          │
│          │                                   │  (optional)     │
│ nav      │  ┌─ panel ─────────────────────┐  │  AI panel,      │
│ sections │  │                             │  │  job detail,    │
│          │  └─────────────────────────────┘  │  diff review    │
└──────────┴──────────────────────────────────┴─────────────────┘
```

- **Sidebar** 264px, collapsible to 64px icon rail. State persists per user.
- **Topbar** 56px, sticky, `surface` with a bottom hairline.
- **Content** max 1120px centred, 24px desktop gutters, 16px mobile.
- **Inspector** 360px right panel — the home of AI suggestions, job detail,
  and diff review. On `lg` and below it becomes a sheet over the content.
- **Reading measure** 72ch cap on resume body and any prose block, regardless
  of how wide the container gets.

### Grid patterns per surface

| Surface | Desktop | Tablet (`md`) | Mobile (`<md`) |
|---|---|---|---|
| Dashboard metric row | 4-up | 2-up | 1-up |
| Dashboard panels | 12-col, panels span 4/6/8/12 | 6-col | 1-col |
| Job list + detail | list 1-col + inspector | list, detail as sheet | list, detail as full page |
| Resume viewer | document + inspector | document, inspector as sheet | document only, inspector via tab |
| Resume comparison | 2-col side-by-side | 2-col, narrowed | stacked with a version switcher |
| Roadmap | horizontal timeline | horizontal, scrollable | vertical stepper |
| Settings / forms | single column, 640px max | same | same |

Forms never exceed a single column at 640px. Two-column forms save vertical
space and cost accuracy; on a product where the input is someone's career
history, accuracy wins.

---

## 8. Border Radius

| Token | Value | Applied to |
|---|---|---|
| `xs` | 4px | Checkboxes, tag chips, tight inline chrome |
| `sm` | 6px | Badges, small inputs, code blocks, skeleton bars |
| `md` | 8px | **Buttons, inputs, selects, menu items** — the system default |
| `lg` | 12px | Cards, panels, suggestion cards, job cards, roadmap nodes |
| `xl` | 16px | Modals, sheets, resume page chrome |
| `2xl` | 20px | Full-bleed feature panels (rare) |
| `full` | 9999px | Avatars, status dots, score rings, progress tracks, filter chips |

8px buttons are a deliberate identity choice. Pills read as marketing CTAs;
rectangles read as tools. The one place `full` touches an interactive control
is the filter chip row, where the pill shape usefully signals "removable".

Nesting rule: an inner radius is at least 2px smaller than the container it
sits in, so corners stay concentric. A 12px card holds 8px controls; a 16px
modal holds 12px cards.

---

## 9. Surface and Elevation

Five levels. The number climbs only when an element genuinely occludes what
is beneath it.

| Level | Light treatment | Dark treatment | Use |
|---|---|---|---|
| `e0` | Hairline, no shadow | Hairline on `surface` | Table containers, inline wells, flat groupings |
| `e1` | Hairline + `0 1px 2px` at 4% | Hairline on `surface`, no shadow | Default card, job card, suggestion card |
| `e2` | Hairline + two-offset stack | `surface-raised`, no shadow | Hovered card, resume page, active panel |
| `e3` | Hairline + soft 16px stack | `surface-raised` + `0 8px 24px` at 45% | Dropdowns, popovers, comboboxes |
| `e4` | Hairline + 32px stack | `surface-active` + `0 16px 40px` at 55% | Modals, sheets, toasts |

Shadows are **stacked from small offsets at low opacity**, never one large
blur — a single heavy drop-shadow makes a calm interface look like a
prototype. Every shadowed element also keeps its 1px hairline so the edge
stays crisp on both themes.

Hover lifts an element by at most one level, and only for genuinely clickable
cards. Rows, table cells, and nav items respond with a background change
(`surface-hover`), never with a shadow.

---

## 10. Buttons

Five variants. One `primary` per view.

| Variant | Fill | Text | Border | Use |
|---|---|---|---|---|
| `primary` | `brand` | `on-brand` | — | The single most important action on screen |
| `secondary` | `surface` | `ink` | 1px `hairline-strong` | Alternative actions, cancel, "Reject" |
| `ghost` | transparent | `ink-secondary` | — | Toolbar and row-level actions |
| `destructive` | `danger` | `#ffffff` | — | Delete resume, discard version |
| `link` | transparent | `brand` | — | Inline navigation inside prose |

Geometry: `{rounded.md}` 8px, `8px 14px` padding, 36px height at desktop
density, **44px minimum on touch viewports** (via increased vertical padding —
the visual height grows, the type size does not). Icon-only buttons are 36px
square desktop / 44px touch with a 16px glyph.

Sizes: `sm` 32px (dense tables, inline row actions), `md` 36px (default),
`lg` 44px (empty-state and modal primary actions).

States, all five defined for every variant: rest, hover, active/pressed,
focus-visible, disabled, plus `loading`. Loading replaces the leading icon
with a spinner, keeps the label, and locks the button width so the layout
does not shift. Disabled uses `surface-active` fill with `ink-disabled` text
and `cursor: not-allowed`; it never relies on opacity alone.

**Destructive actions are never the primary button in a dialog by default.**
The destructive confirm sits as `destructive`, the safe action as `secondary`,
and the safe action holds initial focus.

---

## 11. Inputs and Forms

Every field is a labelled triplet: visible label above, control, then either
help text or an error message below. Placeholder text is never a label —
placeholders vanish on input and are invisible to some assistive tech.

| Part | Spec |
|---|---|
| Label | `{typography.label}` 13px/500, `ink-secondary`, 6px above control |
| Control | 36px desktop / 44px touch, `{rounded.md}`, 1px `hairline-strong`, `body` 14px |
| Help text | `{typography.caption}` 12px, `ink-muted`, 6px below |
| Error | `{typography.caption}` 12px, `danger`, with a 12px alert icon, replaces help text |
| Required | `*` in `danger` after the label, plus `aria-required` |
| Optional | the word "Optional" in `ink-subtle` after the label |

Focus: 1px border switches to `brand` **and** a 2px `focus-ring` at 2px
offset appears. Both, not one — the border change alone is too quiet at 1px,
and the ring alone loses the field boundary.

Validation is **on blur, then on submit** — never on every keystroke. Live
per-character validation on a work-history field reads as nagging. Once a
field has errored, it re-validates on input so the error clears as soon as
it is fixed.

Error summary: on failed submit, a `danger` banner at the top of the form
lists the failing fields as in-page anchor links, focus moves to the banner,
and each field is marked `aria-invalid` with `aria-describedby` pointing at
its message.

Resume-specific field behaviour:

- **Date ranges** use two month/year selects plus a "Present" checkbox, not
  free text. Parsing ambiguity in dates is a top source of bad resume data.
- **Bullet fields** are textareas with a live character counter that turns
  `warning` past the recommended length and `danger` past the hard limit.
  The counter is `aria-live="polite"` and announces only at threshold
  crossings, not on every character.
- **Skill entry** is a token input: typing plus Enter commits a chip;
  Backspace on empty removes the last chip; each chip has a 44px-hit-area
  remove control with an accessible name of "Remove <skill>".
- **Autosave** shows a `caption`-sized status in the form footer: "Saving…" →
  "Saved 14:32". Autosave never fires while a field holds focus.

---

## 12. Cards

Cards are containers, not decoration. `surface` fill, `{rounded.lg}` 12px,
1px `hairline`, 16–20px padding, `e1`.

Anatomy, top to bottom: optional eyebrow, title (`heading-sm` or
`heading-md`), optional metadata row (`body-sm`, `ink-muted`), body, and an
action row pinned to the bottom of the card so buttons align across a row of
cards of unequal height.

Variants:

- **Static** — grouping only, no hover response, no pointer cursor.
- **Interactive** — the whole card is a link or button. Hover moves to
  `surface-hover` and `e2`; the accessible name comes from the title, and the
  entire card is one tab stop, not a card containing three tab stops.
- **Selected** — `brand-subtle` fill, 1px `brand-border`, and either a check
  affordance or `aria-selected`. Selection is not signalled by color alone.
- **Metric** — a dashboard tile: `eyebrow` label, `metric` (32px, tabular)
  value, and a delta line where a directional arrow icon carries the sign and
  `success`/`danger` carries the sentiment. The arrow is mandatory; the color
  is the redundancy, not the message.

Cards never nest more than one level. A card inside a card inside a panel is
a sign the page needs sections, not more containers.

---

## 13. Navigation and Sidebar

### Sidebar

`canvas-subtle` fill, 264px, right hairline, `12px 8px` padding. Items are
36px tall, `{rounded.md}`, with a 16px leading icon and a `body-medium` label.

Sections match the six product capabilities, each with an `eyebrow` group
label in `ink-subtle`:

```
OVERVIEW      Dashboard · Career profile
RESUME        My resumes · Analysis · Improvements
OPPORTUNITY   Job discovery · Matches · Saved
PLAN          Career transition · Roadmap
```

Active state: `brand-subtle` fill, `brand-ink` text, and a 3px `brand` bar on
the left edge. Three signals — fill, text color, and indicator — so the
active item survives both color-blindness and a low-contrast display. The
active item also carries `aria-current="page"`.

Collapsed rail: 64px, icons only, labels as tooltips after a 500ms delay,
with the section grouping preserved as hairline dividers. The collapse
toggle is a persistent 44px control at the sidebar footer.

### Topbar

56px, `surface`, bottom hairline, sticky. Left: breadcrumb trail
(`body-sm`, `ink-muted`, current page in `ink`). Centre: global search,
opening a command palette on `⌘K` / `Ctrl+K`. Right: theme toggle, help,
account menu. Nothing else earns a slot here.

### Secondary navigation

Within a section, tabs are an underline set — 44px tall, `body-medium`, a 2px
`brand` bottom border on the active tab, `ink-muted` when inactive. Underline
tabs, not pill tabs, so they read as navigation rather than as filters. Filter
chips — which *are* pills — remain visually distinct from tabs for exactly
this reason.

### Mobile

Below `md`, the sidebar becomes a slide-over sheet behind a 44px hamburger,
and the four most-used destinations appear in a bottom tab bar with a 56px
height plus safe-area inset.

---

## 14. Tables

Tables carry job lists, skill gaps, resume version history, and match
breakdowns. They are the highest-density surface in the product.

| Part | Spec |
|---|---|
| Container | `surface`, `{rounded.lg}`, 1px `hairline`, `overflow: hidden` |
| Header cell | `surface-sunken`, `label-sm` 12px/500, `ink-muted`, `8px 12px`, sentence case |
| Body cell | `body` 14px, `ink`, `10px 12px`, 44px row (36px dense) |
| Row divider | 1px `hairline-subtle` |
| Row hover | `surface-hover` |
| Row selected | `brand-subtle` |
| Numeric cell | right-aligned, `numeric` role with tabular figures |

Rules:

- **Numbers right-align, text left-aligns, and numbers use tabular figures.**
  A column of scores that does not align vertically is a column nobody can
  compare.
- **Sticky header** on any table that scrolls. Sticky first column on any
  table that scrolls horizontally.
- **Sorting** is a `<button>` inside the `<th>` with an arrow icon and
  `aria-sort` on the header. Sort state is never icon-hover-only.
- **Row actions** live in a trailing column, revealed on row hover *and*
  always present for keyboard focus — hover-only actions are inaccessible.
- **Overflow** never truncates a value the user needs. Long text wraps to two
  lines and clamps; the full value is available in a tooltip and in the
  detail view.
- **Mobile:** below `md`, tables become stacked cards with label-value pairs.
  A horizontally scrolling table on a phone is a table nobody reads. The one
  exception is a genuine comparison matrix, which keeps horizontal scroll with
  a sticky first column and a visible scroll affordance.
- **Empty and loading** states are per section 25 and 26 — a table never
  renders as a bare header row with nothing under it.

---

## 15. Badges and Status Indicators

Two shapes, distinct jobs.

**Badge** — `{rounded.sm}` 6px, `label-sm` 12px/500, `2px 8px` padding, made
of a `-subtle` fill, a `-border` hairline, and the status color as text.
Variants: `neutral`, `brand`, `success`, `warning`, `danger`, `info`, `ai`.

**Status dot** — 8px `full` circle, always immediately followed by a text
label. A bare colored dot is never sufficient.

CareerIQ's status vocabulary:

| Label | Variant | Meaning |
|---|---|---|
| Verified | `success` | Content the user has confirmed |
| Needs review | `warning` | Thin, vague, or unquantified content |
| Unsupported | `danger` | A claim with no basis in user-provided data |
| AI suggested | `ai` | Machine-generated, not yet accepted |
| Draft | `neutral` | Unpublished resume version |
| Active | `brand` | Resume currently used for matching |
| Applied | `success` | Job application submitted |
| Expired | `neutral` | Posting no longer open |

`Unsupported` is load-bearing for product integrity, not cosmetic. It marks
content that has drifted from what the user actually supplied, and it is the
one badge that must never be suppressed to make a screen look cleaner.

Every badge carries text. Icon-only status is permitted only in a dense table
cell, and then only with an `aria-label` and a tooltip.

---

## 16. Progress Indicators

Four forms, each with a defined purpose:

**Linear bar** — a 6px `full` track in `charts.track` with a `brand` fill.
Determinate progress: profile completeness, upload progress, section
completion. Always paired with a percentage or an "n of m" label.

**Ring** — 64px, 6px stroke. A single score in a compact space: a job card's
match score, a section score. The arc uses the score band accent (section
23), not flat brand, so the ring's color carries magnitude.

**Score ring, large** — 88px, 8px stroke, `metric` value in the centre with a
`label-sm` caption under it. One per view: the headline score of the current
resume or match.

**Stepper** — for multi-step flows (resume upload → parse → review →
confirm). Completed steps show a `success` check, the current step shows a
`brand` fill, upcoming steps show an `ink-subtle` outline. The current step is
also announced with `aria-current="step"`.

Indeterminate work uses skeletons (section 25), not spinners, wherever the
final shape of the content is known. Spinners are for actions inside a
button, where the shape of the result is not a layout.

Long AI operations (analysis, generation) show **stage labels, not a fake
percentage**: "Parsing resume" → "Extracting skills" → "Matching against
role". An invented progress bar for a non-deterministic operation is a lie
the interface tells, and users notice when it stalls at 90%.

---

## 17. Charts and Data Visualization

Chart color is a **separate system** from status color. A chart series is a
category, not a state.

### Categorical palette

Eight colors: teal, blue, violet, magenta, copper, ochre, olive, slate. The
set deliberately excludes green and red so that a data series is never misread
as a pass/fail signal on a screen that also carries real `success` and
`danger` states.

Series 1 is `charts.categorical.1`, which equals the brand teal — so a
single-series chart reads as brand-native without any extra decision.

Rules:

- **Five series maximum** in a legend-based chart. Beyond five, group the
  tail into "Other" or switch to a small-multiples layout. Eight colors exist
  for the rare wide case, not as a target.
- **Order is fixed.** Series index determines color; colors are never
  reassigned between renders of the same chart, and never re-sorted by value.
- **Never encode by color alone.** Line charts get distinct markers, bar
  charts get direct labels where space allows, and every chart has an
  accessible table equivalent (visually hidden, or behind a "View as table"
  toggle).
- **Sequential scale** (single-hue teal, 6 steps) for magnitude: skill
  coverage heatmaps, demand intensity.
- **Diverging scale** (copper ↔ neutral ↔ teal, 7 steps) for
  above/below-target: skill gap versus a role's requirement. The neutral
  midpoint is `#e8eaea` light / `#3a4444` dark and must be visually distinct
  from the "no data" treatment, which is a hatched or `surface-sunken` cell
  with an explicit "No data" label.

### Chart chrome

Grid lines `charts.grid` at 1px, horizontal only. Axis line `charts.axis`.
Axis labels `caption` 12px in `charts.axis-label`. No chart borders, no
background fills, no 3D, no drop shadows on data marks, no pie charts beyond
two slices (a donut with a single percentage is a ring, and belongs to
section 16).

Tooltips: `e3` elevation, `surface-raised`, values in `numeric` with tabular
figures, keyboard-reachable via arrow keys across data points.

### CareerIQ chart forms

| Data | Form |
|---|---|
| Skill coverage vs target role | Horizontal bars, diverging scale, sorted by gap size |
| Match score breakdown | Horizontal stacked bar, one segment per dimension |
| Salary range vs market | Range bar with a market band and a user marker |
| Career trajectory | Stepped timeline, not a line chart — careers move in discrete steps |
| Skill demand over time | Sparkline in table rows; full line chart in detail |
| Resume score history | Line chart with version markers |

---

## 18. Resume Viewer

The resume is the product's centre of gravity. Its viewer is the one surface
allowed to look like a document rather than an application.

**Page:** `surface` white fill, `{rounded.xl}` 16px, `e2`, 816px max width
(US Letter at 96dpi), `48px 56px` interior padding. It sits on `canvas` with
24px of surrounding gutter so the page edge is unmistakable. In dark mode the
page **stays light** by default — a resume is a document destined for print
and PDF, and showing it inverted misrepresents the artefact. A "match app
theme" toggle exists for users who prefer it, and it is off by default.

**Document typography** is a separate token set (`doc-*`) from the UI:
`doc-name` 22px/600 for the person's name, `doc-heading` 13px/600 uppercase
with `+0.5px` tracking for section headings, `doc-role` 14px/600 for job
titles, `doc-body` 14px/1.6 for content, `doc-meta` 12px for dates and
locations. The document never inherits UI type scale — mixing the two makes
the resume look like a form.

**Viewer chrome** lives outside the page, never on it: a toolbar above with
zoom (50–200%), page navigation, version selector, and a download action. A
section outline rail on the left jumps to sections and highlights the section
in view.

**Section interaction:** hovering a section reveals a `ghost` action cluster
in the outer gutter — never overlaying the document text. Clicking a section
selects it (`brand-border` 1px outline, 2px offset from the text) and loads
its analysis into the inspector.

**Annotations** are margin markers, not inline highlights: a small dot in the
gutter, colored by severity, expanding to a note on click. Inline highlighting
of resume text is reserved exclusively for diff view, so highlight always
means "this text changed" and nothing else.

**Print and export** use a dedicated print stylesheet: chrome hidden,
annotations hidden, `#000` on `#fff`, no rounded corners, no shadow, exact
page geometry. What the user sees at 100% zoom is what the PDF contains.

---

## 19. Resume Comparison UI

Comparison answers one question: what changed, and where did it come from?

**Layout.** Side-by-side at `xl` and above — two 816px-max panes at whatever
scale fits, scroll-locked together, with a version label above each pane
(`Original · v3` / `Proposed · AI improvements`). At `lg` and below, an inline
unified diff replaces side-by-side; a "compare" toggle switches between
unified and side-by-side wherever both fit.

**Diff treatment.**

| Kind | Background | Text | Gutter | Extra |
|---|---|---|---|---|
| Added | `diff-add-bg` | `diff-add-ink` | 3px `diff-add-gutter` bar | `+` marker |
| Removed | `diff-remove-bg` | `diff-remove-ink` | 3px `diff-remove-gutter` bar | `−` marker, line-through |
| Unchanged | none | `diff-context-ink` | none | — |
| Moved | `brand-subtle` | `brand-ink` | 3px `brand` bar | `↕` marker + destination hint |

Colour is never the only signal: every changed line carries a gutter bar and
a `+` / `−` / `↕` marker, so the diff survives greyscale printing and
colour-blind viewing. Word-level highlighting within a changed line uses a
slightly stronger tint of the same diff color, plus an underline.

**Navigation.** A change counter in the toolbar ("4 of 12 changes") with
previous/next controls bound to `j`/`k` and to the arrow keys. Each jump moves
focus, not just scroll, so keyboard and screen-reader users track position.

**Granularity toggle:** section / paragraph / word. Word-level is not the
default — for resume review, paragraph-level is what the user actually
evaluates.

**Version history** is a left rail listing versions with timestamp, origin
(`Manual edit` / `AI improvement` / `Import`), and a change count. Any two
versions can be selected for comparison. Versions are immutable; "revert"
creates a new version rather than deleting history.

---

## 20. AI Suggestion UI

This section encodes a product rule, not a preference: **CareerIQ never
fabricates resume content, and AI output is always attributable and always
reviewable.** The visual system is how that rule becomes visible.

**Provenance color.** AI-generated, not-yet-accepted content uses the AI
violet set (`ai-accent`, `ai-subtle`, `ai-border`, `ai-ink`) — deliberately
not brand teal, so "the product's action" and "the model's proposal" are
never the same color. Once a suggestion is accepted, the content becomes
ordinary user content and **loses the AI treatment entirely**. Accepted
content is the user's, and the interface says so by dropping the marker.

**Suggestion card anatomy:**

```
┌─ 3px ai-accent left bar ──────────────────────────────┐
│ [AI suggested]  Clarity · Impact              ⋯       │  eyebrow row
│                                                        │
│ Current                                                │  label-sm, ink-muted
│ Responsible for the reporting pipeline.                │  diff-remove treatment
│                                                        │
│ Proposed                                               │
│ Rebuilt the reporting pipeline, cutting refresh        │  diff-add treatment
│ time from 40 to 6 minutes.                             │
│                                                        │
│ ┌ Why this change ─────────────────────────────────┐   │  ai-subtle well
│ │ Quantifies an outcome you already listed in your │   │  body-sm, ai-ink
│ │ 2023 project notes. No new claims introduced.    │   │
│ └──────────────────────────────────────────────────┘   │
│                                                        │
│ Source: your project notes, Mar 2023      [Reject][Apply]
└────────────────────────────────────────────────────────┘
```

Four elements are **mandatory** on every suggestion:

1. **Category** — what kind of improvement (Clarity, Impact, Relevance,
   Structure, Keywords). Sets the user's expectation before they read.
2. **Rationale** — the "Why this change" well. Plain language, no jargon,
   capped at two sentences.
3. **Provenance** — which user-provided input the suggestion draws on. If a
   suggestion cannot name a source, it must render the `Unsupported` badge
   and default to Reject.
4. **Explicit accept and reject controls.** There is no auto-apply, no "apply
   all" without a confirmation step that lists every change, and no silent
   background rewrite.

**Grouping.** Suggestions group by resume section, with a per-section count
and a collapse control. Within a section they are ordered by expected impact,
labelled `High` / `Medium` / `Low` as `badge-neutral`, not by a numeric score
the model cannot honestly calibrate.

**Streaming.** While a suggestion streams in, the card shows a skeleton for
the proposed text and an `aria-live="polite"` region announcing "Generating
suggestion 3 of 8". The accept control stays disabled until the suggestion is
complete — an accept on a half-generated line is a data integrity bug.

**Empty result** is a success state, not a failure: "No changes suggested for
this section — it already reads clearly." Never an error, never an empty box.

---

## 21. Apply / Reject Change UI

The accept surface is the highest-consequence interaction in the product, so
it gets the strictest rules.

**Per-suggestion controls.** `Apply` is a `primary` button, `Reject` is
`secondary`, placed bottom-right of the suggestion card in that order.
`Reject` is never `destructive` red — rejecting a suggestion is a normal,
encouraged action and must not look like a warning.

**Feedback on apply.** The change animates into the resume (180ms fade, no
motion for reduced-motion users), the suggestion card collapses to a one-line
`success` receipt — "Applied · Undo" — and the undo affordance stays available
for the remainder of the session. Nothing about applying a change is
irreversible.

**Bulk apply.** `Apply all` opens a confirmation sheet that lists every
pending change as a compact diff with individual checkboxes, all checked by
default, with a count in the confirm button ("Apply 7 changes"). The user can
uncheck any line before confirming. There is no single-click path from
"suggestions exist" to "resume rewritten".

**Rejection capture.** Rejecting offers an optional single-tap reason chip
row (Not accurate · Not relevant · Wrong tone · Overstated). Optional, one
tap, dismissible — never a required modal.

**Pending state.** A resume with unreviewed suggestions shows a persistent
`ai`-variant status strip at the top of the viewer: "7 suggestions awaiting
your review", with `Review` and `Dismiss all` actions. Unreviewed AI content
is never rendered as though it were already part of the resume.

**Guarantee, stated in the interface.** The review header carries one line of
copy: "Nothing is added to your resume until you approve it." That sentence
is part of the design, not decoration.

---

## 22. Job Cards

The unit of the discovery surface. `card-interactive`, `{rounded.lg}` 12px,
16px padding, `e1`, whole card is one tab stop and one link.

```
┌──────────────────────────────────────────────────────────┐
│ ⬡  Senior Data Engineer                        ╭────╮    │
│    Company · Remote (EU)                       │ 87 │    │  score ring 64px
│                                                ╰────╯    │
│    €85k – €105k · Full-time · Posted 3d ago              │  body-sm, tabular
│                                                          │
│    [Python] [Airflow] [dbt] [+4]                         │  matched skill chips
│    ✓ 9 of 11 requirements met                            │  success, body-sm
│                                                          │
│    [Save]  [View match breakdown]                        │
└──────────────────────────────────────────────────────────┘
```

Rules:

- **Title is the loudest element** (`heading-sm` 16px/600). Company, location,
  and salary are `body-sm` in `ink-muted`.
- **Salary and dates use tabular figures**, so a scanned list stays aligned.
- **Matched skill chips show matches first**, capped at four visible with a
  `+n` overflow chip. Chips use `badge-brand` when matched from the user's
  resume and `badge-neutral` when unmatched — the distinction is the point.
- **Score ring** top-right, 64px, band-colored per section 23. Every card in a
  list shows a score or explicitly shows "Not scored"; a blank corner is
  ambiguous.
- **Card states:** default, hover (`surface-hover` + `e2`), visited (title in
  `ink-secondary`), saved (`Save` becomes filled with a `brand` icon),
  applied (`success` badge, card fill moves to `surface-sunken`), expired
  (`ink-muted` text, `Expired` neutral badge, actions removed).
- **List density** is a user setting: comfortable (the layout above) or
  compact (single 44px row, title + company + score, no chips).

Never render a job card without a source and a posted date. A job the user
cannot locate or date is not usable information.

---

## 23. Job Matching Score UI

A match score is an estimate. The interface's job is to show its basis, not to
project false precision.

**Bands** — a neutral-to-brand intensity ramp, not red-to-green:

| Band | Range | Label | Accent |
|---|---|---|---|
| Low | 0–39 | Limited match | `ink-subtle` neutral |
| Fair | 40–59 | Partial match | ochre |
| Good | 60–74 | Good match | teal 400 |
| Strong | 75–89 | Strong match | teal 600 |
| Excellent | 90–100 | Excellent match | teal 800 |

Red-to-green is wrong here. A 30% match is not an error or a failure — it is
a job that does not fit, and a red score implies the user did something wrong.
The neutral-to-brand ramp says "less relevant" instead of "bad".

**Presentation rules:**

- The score is **always an integer with a band label**. `87 · Strong match`.
  Never a bare number, never a decimal — a decimal implies precision the model
  does not have.
- **The breakdown is one click away, always.** A score with no visible basis
  is not trustworthy. The breakdown is a horizontal stacked bar plus a
  dimension table: Skills, Experience, Seniority, Domain, Location, each with
  its own sub-score, weight, and a one-line explanation.
- **Gaps are actionable.** Every unmet requirement lists what is missing and
  links to the roadmap surface: "Missing: Kubernetes · Add to roadmap".
- **Weights are visible and, where supported, adjustable.** If the user cares
  more about location than seniority, the score should reflect that, and the
  interface should show that it did.
- **Confidence is stated when it is low.** Where inputs are thin (a sparse
  resume, a vague posting), the score carries a `warning` `Low confidence`
  badge and a reason, instead of quietly presenting a fragile number as a
  firm one.

---

## 24. Career Roadmap UI

A roadmap is a sequence of steps between the user's current position and a
target role. It is rendered as a timeline of nodes, not a Gantt chart —
careers are ordered, not scheduled to the day.

**Desktop:** horizontal timeline, left to right, with a 2px `hairline-strong`
connector. Nodes are 12px-radius cards on the line, grouped into phases
(Now · 3 months · 6 months · 12 months) with `eyebrow` phase labels above.

**Mobile and `md` and below:** vertical stepper, same node content, connector
running down the left gutter at 2px.

**Node states:**

| State | Treatment |
|---|---|
| Done | `success` check icon, `ink-muted` title, `hairline` border |
| Current | `brand-subtle` fill, 1px `brand-border`, `brand` accent dot, `aria-current="step"` |
| Upcoming | `surface` fill, `hairline` border, `ink-subtle` accent |
| Blocked | `warning` icon plus an explicit prerequisite line: "Needs: SQL fundamentals" |

**Node content:** a type badge (Skill · Certification · Project · Experience),
a title, an effort estimate (`numeric`, e.g. "~20 hrs"), and the gap it closes
("Closes: Kubernetes gap for Senior Platform Engineer"). Every node states the
gap it closes — a step with no stated purpose is a to-do item, not a roadmap.

**Progress:** a linear bar at the top of the surface with an "n of m steps
complete" label and, where the data supports it, a projected readiness date
that is explicitly labelled as an estimate.

**Branching:** where a roadmap forks (two viable target roles), the fork
renders as two parallel tracks with a shared prefix, each track labelled with
its target and its own score. Never a single flattened list that hides the
choice.

**No fabricated milestones.** Every node traces to either a gap identified
from user-provided data or an explicit user addition. A generated roadmap
carries the `AI suggested` badge on each generated node until the user
accepts the plan, following the same accept/reject flow as section 21.

---

## 25. Loading and Skeleton States

Every asynchronous surface has a designed loading state. A blank panel is not
a loading state.

**Skeletons** are the default. `surface-sunken` fill, `{rounded.sm}`, with a
1400ms shimmer sweeping to `surface-hover`. The skeleton must mirror the real
layout — same block count, same widths, same row heights — so that content
arriving does not reflow the page. Text skeletons vary width (100% / 85% /
60%) so a paragraph placeholder reads as prose rather than as a solid block.

| Surface | Loading treatment |
|---|---|
| Dashboard | Metric tiles as 4 skeleton cards; charts as a skeleton block at the chart's exact height |
| Job list | 5 skeleton job cards at full height |
| Table | Header renders immediately; 8 skeleton rows at 44px |
| Resume viewer | Page chrome renders; content as skeleton text blocks in document rhythm |
| AI suggestions | Card frame with category badge visible; proposed text as skeleton |
| Score ring | Track at full opacity, arc absent, centre shows an em dash |

**Spinners** appear in exactly two places: inside a button during a submit,
and as a 16px inline indicator next to a background operation's label. A
full-page spinner is never correct in this product.

**Streaming AI output** renders progressively into its final container with no
layout shift — the container is sized before text arrives. A subtle caret
marks the insertion point. `aria-live="polite"` announces start and completion,
not every token.

**Staged progress for long operations**, per section 16: named stages, no
invented percentage.

**Thresholds.** Under 200ms: no indicator at all, since a flash of skeleton is
worse than a brief wait. 200ms–10s: skeleton or spinner. Over 10s: staged
progress plus a cancel affordance. Optimistic UI applies to saves and
toggles — reflect the change immediately, reconcile on response, and revert
with a `danger` toast if it fails.

---

## 26. Empty States

Every list, table, chart, and panel has a designed empty state. Empty states
are the product's best teaching moment, so they carry an action.

Anatomy: a 40px line icon in `ink-subtle`, a `heading-md` title, one or two
`body` lines in `ink-muted` capped at 42ch, and a single primary action. 48px
vertical padding, centred, no illustration system, no decorative artwork.

Four distinct kinds, which are not interchangeable:

**1. First use — nothing exists yet.** Explain the value, give the one action
that starts the flow.
> *No resumes yet* — Upload a resume to get your career profile, match scores,
> and improvement suggestions. **[Upload resume]**

**2. No results — the user filtered too far.** Never say "no data"; say what
was searched and offer a way back.
> *No jobs match these filters* — Try widening the location radius or removing
> the seniority filter. **[Clear filters]** · 3 filters active

**3. Cleared — the user finished the work.** This is a success state and
should feel like one.
> *No suggestions pending* — You've reviewed every suggestion for this
> resume. **[Run a new analysis]**

**4. Not applicable — the feature needs a prerequisite.** Name the
prerequisite and link to it.
> *Match scores need a target role* — Pick a role you're aiming for and
> CareerIQ will score every job against it. **[Choose target role]**

Empty states never use `danger` or `warning` color. An empty list is not an
error. Charts with no data show their axes and a centred "No data for this
period" label so the user can see the chart exists and is simply unpopulated.

---

## 27. Error States

Errors are placed at the smallest scope that contains the problem, and every
error names a next action.

| Scope | Treatment |
|---|---|
| **Field** | `danger` border, 12px `danger` message with an alert icon beneath the field, `aria-invalid`, `aria-describedby` |
| **Form** | `danger-subtle` banner at the top listing failing fields as anchor links; focus moves to the banner on submit |
| **Section / panel** | Inline `danger-subtle` block inside the panel frame, with **Retry**. The rest of the page stays interactive |
| **Page** | Centred error state: title, cause in plain language, Retry and a route back. Shell (topbar + sidebar) stays rendered |
| **Transient** | Toast, `e4`, auto-dismiss at 6s, with an action where one exists. Never for errors requiring a decision |
| **Destructive confirm** | Modal naming the exact object ("Delete resume *Senior Data Engineer v3*?"), consequence stated, safe action focused |

Rules:

- **Never show a raw exception, stack trace, or status code as the primary
  message.** A technical detail line is permitted, collapsed, under a
  "Details" disclosure for support purposes.
- **Every error names a cause and an action.** "Something went wrong" without
  a next step is not an acceptable message.
- **Partial failure degrades, it does not blank the page.** If job matching
  fails but the resume loaded, show the resume and an error only in the match
  panel.
- **Local-first failure modes get their own copy.** CareerIQ runs against a
  local model, so "the model is not running", "the model is still loading",
  and "the request timed out" are three different messages with three
  different actions (start it, wait with a staged indicator, retry or reduce
  scope). A generic network error would be wrong for all three.
- **Never lose user input on error.** Form state survives a failed submit,
  and unsaved resume edits survive a failed save with an explicit "Unsaved
  changes — retry" affordance.
- **Errors are announced.** `role="alert"` on the message so assistive tech
  reads it without the user hunting for it.

---

## 28. Accessibility Requirements

These are requirements, not aspirations. Target: **WCAG 2.2 Level AA**.

**Contrast.** 4.5:1 for body text, 3:1 for text ≥18.66px or ≥14px bold, 3:1
for UI component boundaries and meaningful graphics (WCAG 1.4.11). Every
token in this document was computed, and the measured ratios are recorded in
sections 2–4. `ink-subtle` (3.7:1 light) is restricted to large or
non-essential text and that restriction is enforced in review.

**Focus.** A visible focus indicator on every interactive element, using
`:focus-visible` — 2px `focus-ring` with 2px offset. `outline: none` without a
replacement indicator is prohibited. Table rows and cells use the inset ring
variant so the indicator is not clipped by `overflow: hidden`. Focus order
follows visual order. Modals, sheets, and the command palette trap focus and
restore it to the trigger on close. A skip-to-content link is the first tab
stop on every page.

**Touch targets.** 44×44px minimum on touch viewports (WCAG 2.5.8 asks 24px;
CareerIQ sets 44px). Where a control renders visually smaller — a 16px
checkbox, a 12px chip remove — its hit area is expanded with padding or a
pseudo-element to reach 44px. Adjacent targets keep 8px of separation.

**Colour independence.** No information conveyed by colour alone. Status
carries an icon or a label. Diffs carry gutter bars and `+`/`−` markers. Chart
series carry markers, direct labels, or a table equivalent. Every screen must
survive a greyscale screenshot with no loss of meaning — this is the review
test.

**Semantics and keyboard.** Native elements first: `<button>`, `<a>`,
`<table>`, `<label>`, `<fieldset>`. ARIA only where no native element exists.
Every flow is completable by keyboard alone. Documented shortcuts: `⌘K`
command palette, `j`/`k` next/previous item, `/` focus search, `Esc` close,
`⌘S` save. All shortcuts are listed in a help dialog and none conflict with
assistive-technology bindings.

**Screen readers.** One `<h1>` per page and a heading hierarchy with no
skipped levels. Landmark regions (`banner`, `navigation`, `main`,
`complementary`). Live regions: `polite` for autosave, streaming AI, and
progress; `assertive` reserved for errors that block the user. Tables use
`<caption>`, `scope`, and `aria-sort`. Icon-only controls always carry an
accessible name. Decorative icons are `aria-hidden`.

**Motion.** `prefers-reduced-motion: reduce` is honoured everywhere — see
section 30.

**Forms.** Every input has a programmatically associated `<label>`.
Placeholders are never labels. Errors are announced, associated, and
persistent. Autocomplete attributes are set on personal-data fields
(`name`, `email`, `tel`, `address-level2`) — resume forms collect exactly the
data browser autofill is designed for.

**Zoom and reflow.** Usable at 200% zoom and at a 320px viewport width with no
horizontal scrolling (WCAG 1.4.10). Type sizes are `rem`-based so browser font
settings are respected.

**Testing floor.** `eslint-plugin-jsx-a11y` in CI, `axe` assertions in
component tests, and a manual keyboard-only pass on every new flow. Automated
tools catch roughly a third of real issues; the keyboard pass is not optional.

---

## 29. Responsive Behavior

Tailwind's default breakpoints, unmodified: `sm` 640, `md` 768, `lg` 1024,
`xl` 1280, `2xl` 1536.

| Breakpoint | App shell | Content |
|---|---|---|
| `< sm` (mobile) | Sidebar as sheet; bottom tab bar; topbar 56px | Single column, 16px gutters. Tables → cards. Roadmap → vertical stepper. Diff → unified. Inspector → full page |
| `sm–md` | Same as mobile, wider gutters | 2-up metric tiles |
| `md–lg` (tablet) | Sidebar as icon rail, expandable | 2-up cards, 6-col panel grid. Inspector → sheet. Side-by-side comparison unavailable |
| `lg–xl` (laptop) | Sidebar expanded 264px | 3-up cards, 12-col grid, inspector inline at 320px |
| `xl–2xl` (desktop) | Full shell | 4-up metric tiles, inspector 360px, side-by-side comparison available |
| `≥ 2xl` | Full shell | Content stays capped at 1120px and centres; extra width goes to gutters, never to line length |

**Type scaling.** `metric-xl` 44 → 32px, `display-lg` 32 → 24px, `heading-xl`
24 → 20px below `md`. Body sizes never scale down — 14px is the floor and
reading surfaces stay at 16px on every viewport.

**Density.** Touch viewports force the comfortable density: 44px rows and
44px controls regardless of the user's density preference. Dense mode is a
pointer-input feature.

**Collapsing order** — what goes first as width decreases:
1. Decorative and secondary metadata columns
2. The inspector panel (→ sheet → full page)
3. Multi-column grids (4 → 2 → 1)
4. The sidebar (expanded → rail → sheet)
5. Table layout (columns → stacked cards)

**Never collapsed away:** the primary action of a view, the match score, any
`Unsupported` or `Needs review` badge, and the accept/reject controls on a
pending AI change. Integrity signals survive every breakpoint.

**Resume viewer** is the one surface that keeps horizontal scroll on mobile,
because a resume's line breaks are part of the artefact. It opens at
fit-to-width with pinch-zoom enabled, and a "reflow to mobile reading view"
toggle offers a linearised, non-authoritative reading mode that is clearly
labelled as not the printed layout.

---

## 30. Motion and Animation Guidelines

Motion in CareerIQ explains a state change. It never announces itself.

| Duration | Value | Use |
|---|---|---|
| `fast` | 120ms | Hover, focus ring, button press, tooltip |
| `base` | 180ms | Dropdowns, accordions, applying a suggestion, badge changes |
| `slow` | 240ms | Sheets, modals, inspector open/close |
| `slower` | 320ms | Full-page and route transitions (rare) |

Easings: `ease-standard` `cubic-bezier(0.2,0,0,1)` for most movement,
`ease-enter` `cubic-bezier(0.16,1,0.3,1)` for entrances, `ease-exit`
`cubic-bezier(0.4,0,1,1)` for exits. Exits run at 80% of their entrance
duration — leaving should feel quicker than arriving.

**Animate only** `transform` and `opacity`. Never `width`, `height`, `top`, or
`left` — layout-triggering animation janks on the dense surfaces where it
would be most visible. Skeleton shimmer moves a `transform`-based gradient.

**Permitted:**
- Entrances: 4–8px translate plus opacity fade, never scale beyond 0.98→1
- Sheets and drawers: slide from their edge
- Accordions: `grid-template-rows` or measured height with opacity
- Suggestion applied: 180ms cross-fade of the changed text plus a brief
  `success` gutter flash
- Score ring: arc sweeps once on first paint over 400ms `ease-out`, then never
  re-animates on re-render
- Number changes: no rolling-digit animation — the value swaps. Tabular
  figures make a swap read as an update rather than a glitch

**Prohibited:** parallax, scroll-jacking, autoplaying loops outside skeletons,
bounce and elastic easings, staggered list entrances longer than 200ms total,
attention-seeking pulses on anything other than a genuine alert, and any
motion on the resume document surface itself.

**Reduced motion.** Under `prefers-reduced-motion: reduce`, all transforms and
transitions collapse to 0ms; opacity transitions are retained at 120ms so
state changes remain perceptible. Skeleton shimmer becomes a static fill. The
score ring paints its final arc directly. Auto-dismiss timings are unchanged —
reduced motion is not reduced time. Implement as one global override plus a
`useReducedMotion` hook for JS-driven animation; never re-implement the check
per component.

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

---

## Implementation: Next.js, Tailwind CSS, shadcn/ui

### Layering

```
DESIGN.md  (this file — the authority)
   ↓  hand-transcribed once
app/globals.css   @theme + :root / .dark custom properties
   ↓  consumed as utility classes
Tailwind utilities  bg-surface, text-ink-muted, rounded-lg, gap-4
   ↓  and as component variables
shadcn/ui components  --primary, --border, --ring, --radius
```

Tokens are defined **once**, as CSS custom properties in `globals.css`. No
token is duplicated in `tailwind.config`, in a TypeScript constants file, or
inline in a component. A second definition is a second source of truth.

### shadcn/ui variable mapping

shadcn components read a fixed set of variables. Map CareerIQ roles onto them
rather than fighting the convention:

| shadcn variable | Light | Dark |
|---|---|---|
| `--background` | `canvas` `#f4f6f6` | `canvas` `#0c1012` |
| `--foreground` | `ink` `#101616` | `ink` `#eef2f2` |
| `--card` | `surface` `#ffffff` | `surface` `#141a1c` |
| `--card-foreground` | `ink` | `ink` |
| `--popover` | `surface-raised` `#ffffff` | `surface-raised` `#1b2225` |
| `--popover-foreground` | `ink` | `ink` |
| `--primary` | `brand` `#1d7370` | `brand` `#4fbdb5` |
| `--primary-foreground` | `on-brand` `#ffffff` | `on-brand` `#08201f` |
| `--secondary` | `surface-sunken` `#f4f6f6` | `surface-active` `#232b2e` |
| `--secondary-foreground` | `ink-secondary` | `ink-secondary` |
| `--muted` | `surface-sunken` | `surface-hover` `#1b2225` |
| `--muted-foreground` | `ink-muted` `#5f6b6b` | `ink-muted` `#98a3a3` |
| `--accent` | `brand-subtle` `#eff9f8` | `brand-subtle` `#12312f` |
| `--accent-foreground` | `brand-ink` `#174a49` | `brand-ink` `#8fd8d1` |
| `--destructive` | `danger` `#a3282f` | `danger` `#f0868c` |
| `--destructive-foreground` | `#ffffff` | `#0c1012` |
| `--border` | `hairline` `#e5e9e9` | `hairline` `#2c3538` |
| `--input` | `hairline-strong` `#cdd4d4` | `hairline-strong` `#3d4749` |
| `--ring` | `focus-ring` `#1d7370` | `focus-ring` `#4fbdb5` |
| `--radius` | `0.5rem` (8px) | `0.5rem` |
| `--chart-1` … `--chart-5` | `charts.categorical.1–5` | dark categorical `1–5` |
| `--sidebar` | `canvas-subtle` `#fafbfb` | `surface` `#141a1c` |
| `--sidebar-foreground` | `ink-secondary` | `ink-secondary` |
| `--sidebar-primary` | `brand` | `brand` |
| `--sidebar-accent` | `brand-subtle` | `brand-subtle` |
| `--sidebar-border` | `hairline` | `hairline` |
| `--sidebar-ring` | `focus-ring` | `focus-ring` |

Note that `--input` maps to `hairline-strong`, not `hairline`: form controls
need a 3:1 boundary to satisfy WCAG 1.4.11, and the default hairline does not
reach it.

CareerIQ-only tokens with no shadcn equivalent — `charts.categorical.6–8`,
the sequential and diverging scales, all `score-bands-*`, the `ai-*` set, the
`diff-*` set, `ink-subtle`, `hairline-subtle`, `surface-sunken` — are declared
in the same block under a `--cq-` prefix and exposed to Tailwind through
`@theme inline`.

### globals.css shape

```css
:root {
  /* shadcn contract */
  --background: #f4f6f6;
  --foreground: #101616;
  --primary:    #1d7370;
  /* … */
  --radius: 0.5rem;

  /* CareerIQ extensions */
  --cq-surface-sunken: #f4f6f6;
  --cq-ink-subtle:     #7d8888;
  --cq-ai-accent:      #6153ad;
  --cq-diff-add-bg:    #eaf6f0;
  --cq-chart-6:        #8f6c1f;
  /* … */
}

.dark { /* every token above, redefined — none omitted */ }

@theme inline {
  --color-surface-sunken: var(--cq-surface-sunken);
  --color-ink-subtle:     var(--cq-ink-subtle);
  --color-ai-accent:      var(--cq-ai-accent);
  /* … generates bg-surface-sunken, text-ink-subtle, border-ai-accent */
}
```

Spacing needs no configuration: this document's spacing keys are already
Tailwind's. Radius maps through `--radius`, which shadcn derives `sm`/`md`/
`lg`/`xl` from.

### Fonts

`next/font` with `variable: '--font-sans'` (Inter) and `--font-mono`
(JetBrains Mono), applied on `<html>`. `font-feature-settings: 'cv05' 1,
'cv11' 1` on `body`; a `.tabular` utility applies `'tnum' 1, 'zero' 1` for
numeric contexts. Self-host both faces so the app stays local-first and makes
no third-party font requests at runtime — this is a privacy requirement, not
just a performance one.

### Theming

`next-themes` with `attribute="class"`, `defaultTheme="system"`, and
`disableTransitionOnChange` so the theme swap does not animate every token at
once. Server components render theme-neutral markup; only the toggle is a
client component.

### Component conventions

- shadcn/ui primitives are the base. Restyle by editing the copied component's
  variants — never by adding a competing wrapper.
- Variants via `class-variance-authority`, matching the variant names in this
  document (`primary`, `secondary`, `ghost`, `destructive`, `link`).
- No inline hex values in components, ever. A hex in a `.tsx` file is a
  design-system bug.
- Every component ships its loading, empty, and error states in the same PR as
  its success state. A component with only a success state is not done.

---

## Known Gaps and Assumptions to Review

These are open, and each needs a decision. They are recorded here rather than
resolved silently.

1. **The Meridian teal accent is an original choice, not a validated brand
   decision.** Values are contrast-verified but not tested with users, and
   there is no logo or wordmark yet. A future brand mark could shift the hue.
2. **Inter and JetBrains Mono are defaults, not requirements.** Both are SIL
   OFL and self-hostable. If a distinct typographic voice is wanted later, the
   display tier can move to another open face without touching the scale.
3. **The resume document renders light in dark mode by default.** This assumes
   users think of a resume as a printable artefact. If usage shows otherwise,
   the toggle default flips — the tokens already support both.
4. **Score bands are 5 fixed ranges at 0/40/60/75/90.** These thresholds are
   placeholders until the matching model's score distribution is known; if
   real scores cluster in 60–80, the bands are miscalibrated and must move.
   The visual ramp does not need to change, only the numbers.
5. **Chart forms in section 17 are proposals.** They assume specific data
   shapes from the backend (per-dimension sub-scores, time-series demand) that
   do not exist yet.
6. **Density as a user setting** adds real complexity to every dense
   component. If the audience turns out to be uniformly non-power-users, ship
   comfortable-only and drop the setting.
7. **A print stylesheet for the resume is specified but not detailed.** Exact
   page geometry, margin handling, and multi-page breaks need a dedicated pass
   once a resume template model exists.
8. **No illustration or icon set is chosen.** The spec assumes a single 16/20/
   40px line-icon family (Lucide is the shadcn default and is MIT-licensed).
   Confirm before any icon work begins.
9. **Contrast ratios were computed against the intended surfaces only.** Any
   new token, and any existing token used on an unlisted background, must be
   re-measured. This is an ongoing obligation, not a one-time audit.
10. **`awesome-design-md` must not be committed to this repository.** It is a
    separate git checkout inside the project directory; committing it would
    embed another repository and ship 5MB of third-party design documents
    inside CareerIQ. Move it outside the project root or add it to
    `.gitignore` before the first commit.

---

*CareerIQ Design System v1.0.0 — original work. Contains no third-party brand
colors, fonts, wordmarks, or visual identity.*
