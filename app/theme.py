"""
CLIMAIA Design System & Theme
Defines colors, fonts and style constants for the entire application.
"""

# ─── Color Palette ────────────────────────────────────────────────────────────
class Colors:
    # Base backgrounds (dark mode)
    BG_DARKEST     = "#0a0e17"
    BG_DARK        = "#0f1422"
    BG_CARD        = "#151b2e"
    BG_CARD_HOVER  = "#1a2238"
    BG_INPUT       = "#111827"
    BG_SIDEBAR     = "#0c1019"

    # Accent & brand colors
    PRIMARY        = "#6366f1"     # Indigo-500
    PRIMARY_HOVER  = "#818cf8"     # Indigo-400
    PRIMARY_DARK   = "#4f46e5"     # Indigo-600
    PRIMARY_GLOW   = "#6366f120"   # Subtle glow

    SECONDARY      = "#06b6d4"     # Cyan-500
    SECONDARY_HOVER = "#22d3ee"    # Cyan-400

    ACCENT_WARM    = "#f59e0b"     # Amber-500
    ACCENT_ROSE    = "#f43f5e"     # Rose-500
    ACCENT_EMERALD = "#10b981"     # Emerald-500
    ACCENT_VIOLET  = "#8b5cf6"     # Violet-500

    # Status colors
    SUCCESS        = "#10b981"
    WARNING        = "#f59e0b"
    DANGER         = "#ef4444"
    INFO           = "#3b82f6"

    # Text colors
    TEXT_PRIMARY   = "#f1f5f9"
    TEXT_SECONDARY = "#94a3b8"
    TEXT_MUTED     = "#64748b"
    TEXT_DISABLED  = "#475569"

    # Borders
    BORDER         = "#1e293b"
    BORDER_LIGHT   = "#334155"
    BORDER_FOCUS   = "#6366f1"

    # Chart palette (for matplotlib)
    CHART_PALETTE  = [
        "#6366f1", "#06b6d4", "#10b981", "#f59e0b",
        "#f43f5e", "#8b5cf6", "#ec4899", "#14b8a6",
    ]
    CHART_BG       = "#0f1422"
    CHART_GRID     = "#1e293b"
    CHART_TEXT     = "#94a3b8"


# ─── Typography ───────────────────────────────────────────────────────────────
class Fonts:
    FAMILY         = "Segoe UI"
    FAMILY_MONO    = "Consolas"

    # Sizes
    SIZE_HERO      = 28
    SIZE_H1        = 22
    SIZE_H2        = 18
    SIZE_H3        = 15
    SIZE_BODY      = 13
    SIZE_SMALL     = 11
    SIZE_TINY      = 10

    # Tuples ready to use
    HERO           = (FAMILY, SIZE_HERO, "bold")
    H1             = (FAMILY, SIZE_H1, "bold")
    H2             = (FAMILY, SIZE_H2, "bold")
    H3             = (FAMILY, SIZE_H3, "bold")
    BODY           = (FAMILY, SIZE_BODY)
    BODY_BOLD      = (FAMILY, SIZE_BODY, "bold")
    SMALL          = (FAMILY, SIZE_SMALL)
    SMALL_BOLD     = (FAMILY, SIZE_SMALL, "bold")
    TINY           = (FAMILY, SIZE_TINY)
    MONO           = (FAMILY_MONO, SIZE_BODY)
    MONO_SMALL     = (FAMILY_MONO, SIZE_SMALL)


# ─── Spacing & Sizing ────────────────────────────────────────────────────────
class Spacing:
    XS  = 4
    SM  = 8
    MD  = 12
    LG  = 16
    XL  = 24
    XXL = 32

    CARD_PAD   = 20
    SIDEBAR_W  = 260
    CORNER     = 12
    CORNER_SM  = 8
