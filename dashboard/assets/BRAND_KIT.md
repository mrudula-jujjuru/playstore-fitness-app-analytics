# FitScope Analytics — Brand Kit

Use this exact spec to make the Power BI dashboard visually match the
Streamlit dashboard. Both should look like the same product.

---

## Logo
File: `dashboard/assets/logo.png` (also `logo.svg` for scaling)
Usage: Top-left of every dashboard page/screen, ~48-64px height.

## Name
**FitScope Analytics** — use as the dashboard title everywhere (browser
tab, Power BI report title, README screenshots caption).

## Color Palette

| Role | Hex | Usage |
|---|---|---|
| Primary (Deep Teal) | `#1B4B43` | Headers, primary bars/charts, hero background |
| Primary Dark | `#143630` | Gradient end, hero background depth |
| Accent — Risk/Warning (Coral) | `#FF6B5C` | At-Risk segment, warning banners, negative indicators |
| Accent — Trust/Premium (Gold) | `#E8B923` | Trusted/Premium segment, positive highlights, badge border |
| Growth-Stage teal | `#2E8B7F` | Freemium Growth-Stage segment |
| Utility teal (light) | `#8FBFA8` | Free Utility segment |
| Neutral purple | `#6B4E9E` | Premium Paid Outliers segment |
| Background | `#FAFAF8` | Page/canvas background |
| Card/Panel background | `#FFFFFF` | KPI cards, chart panels |
| Muted text | `#6B7280` | Secondary text, captions, labels |
| Border | `#E5E7EB` | Card borders, dividers |

**Segment color mapping (use consistently in every chart, both tools):**
- Trusted Market Leaders → `#1B4B43` (deep teal)
- Freemium Growth-Stage → `#2E8B7F` (mid teal)
- Free Utility → `#8FBFA8` (light teal)
- Neglected but Functional → `#E8B923` (gold)
- At-Risk / Underperforming → `#FF6B5C` (coral)
- Premium Paid Outliers → `#6B4E9E` (purple)

## Typography

- **Headers:** Poppins (Semi-Bold/Bold) — Google Font, free to use in
  Power BI via "Poppins" if installed system-wide, or substitute
  **Segoe UI Semibold** (Power BI's closest built-in equivalent) if
  Poppins isn't available on your machine.
- **Body/data text:** Inter — substitute **Segoe UI** in Power BI if
  Inter isn't installed.

## Layout Principles (apply to both dashboards)

1. **Hero/header band** at the top: logo + title + one-line business
   framing, on a dark teal gradient background (matches the Streamlit
   `.hero` CSS class).
2. **KPI cards row** directly under the header: 4 cards — Total Apps,
   Avg Rating, Avg Installs, % At-Risk Apps. White cards, subtle border,
   muted gray labels.
3. **Charts use segment colors consistently** — the same 6 colors above,
   in the same order, in every chart across both tools. This is the most
   important consistency rule — a recruiter flipping between the two
   dashboards should immediately recognize "Trusted Market Leaders" as
   the same teal in both.
4. **Risk banner** — when At-Risk apps are present in a filtered view,
   show a coral-accented warning banner (light coral background
   `#FFF1EF`, coral left border, coral warning icon).

## Power BI Setup Steps to Match This Theme

1. In Power BI Desktop: **View → Themes → Browse for themes** → create a
   custom JSON theme using the hex codes above (Power BI supports
   importing a `.json` theme file — see `powerbi_theme.json` in this
   folder).
2. Set report background to `#FAFAF8`, card backgrounds to `#FFFFFF`.
3. Use the `cluster_name` field to color every chart, and manually set
   each category's color in the visual's "Format" pane → Data colors to
   match the segment color mapping above exactly.
4. Add the logo image (`logo.png`) as an Image visual in the top-left of
   the report canvas, next to a Text Box titled "FitScope Analytics" in
   Segoe UI Semibold, colored `#1B4B43`.
