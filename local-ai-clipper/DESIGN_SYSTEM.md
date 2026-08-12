# DESIGN SYSTEM & UI FOUNDATIONS — LOCAL AI CLIPPER

## 1. Aesthetic Principles
- **Theme:** Sleek Dark Mode (Glassmorphism accents, high contrast typography, vibrant state indicators).
- **Typography:** Inter / Outfit font family stack with tabular figures for timestamps.
- **Micro-Animations:** Smooth 150ms cubic-bezier state transitions for progress bars and timeline scrubber.

## 2. Token Specification

### 2.1 Color Palette
```css
:root {
  /* Surfaces */
  --bg-app: #090d16;
  --bg-surface-1: #121824;
  --bg-surface-2: #1a2234;
  --bg-surface-glass: rgba(26, 34, 52, 0.75);

  /* Brand Accents */
  --primary-500: #6366f1;
  --primary-600: #4f46e5;
  --accent-cyan: #06b6d4;

  /* State Colors */
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --color-info: #3b82f6;

  /* Typography */
  --text-main: #f8fafc;
  --text-muted: #94a3b8;
  --text-dim: #64748b;

  /* Borders */
  --border-subtle: rgba(255, 255, 255, 0.08);
  --border-active: rgba(99, 102, 241, 0.4);
}
```

### 2.2 Typography Scale
- `Font Family:` `'Inter', -apple-system, BlinkMacSystemFont, sans-serif`
- `Display:` 28px / 1.2 line-height / SemiBold
- `Heading 1:` 20px / 1.3 line-height / SemiBold
- `Body Main:` 14px / 1.5 line-height / Regular
- `Caption / Code:` 12px / 1.4 line-height / Monospace ('JetBrains Mono', monospace)

## 3. Safe Zone Layout & Caption Preview Boundaries
For 9:16 vertical video overlays (1080x1920):
- **Top Safe Zone Clear Margin:** 280px (14.5%) reserved for platform status headers.
- **Bottom Safe Zone Clear Margin:** 380px (19.7%) reserved for platform caption / interaction buttons.
- **Horizontal Margins:** 60px left/right margins.
