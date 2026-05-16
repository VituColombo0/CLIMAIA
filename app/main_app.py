"""
CLIMAIA – Main Application Shell
Sidebar navigation + page router for the desktop application.
"""

import customtkinter as ctk
from app.theme import Colors, Fonts, Spacing
from app.components import NavItem
from app.pages.dashboard import DashboardPage
from app.pages.data_page import DataPage
from app.pages.analysis_page import AnalysisPage
from app.pages.comparison_page import ComparisonPage
from app.pages.forecast_page import ForecastPage
from app.pages.settings_page import SettingsPage


class CLIMAIAApp(ctk.CTk):
    """Root application window with sidebar navigation."""

    APP_TITLE = "CLIMAIA"
    APP_VERSION = "1.0.0-alpha"
    MIN_WIDTH = 1200
    MIN_HEIGHT = 750

    NAV_ITEMS = [
        ("dashboard",  "🏠", "Dashboard"),
        ("data",       "📁", "Dados"),
        ("analysis",   "🔬", "Análise"),
        ("comparison", "📊", "Comparação"),
        ("forecast",   "🤖", "Previsão IA"),
        ("settings",   "⚙️", "Configurações"),
    ]

    def __init__(self):
        super().__init__()

        # ── Window setup ──────────────────────────────────────────────────
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title(f"{self.APP_TITLE}  •  Climate AI Analysis")
        self.geometry("1400x850")
        self.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.configure(fg_color=Colors.BG_DARK)

        # ── Shared application state ──────────────────────────────────────
        self.state = {
            "raw_df": None,
            "treated_df": None,
            "raw_path": None,
            "treated_path": None,
            "analysis_results": None,
            "comparison_results": None,
        }

        self._current_page = None
        self._nav_buttons = {}
        self._pages = {}

        # ── Build layout ──────────────────────────────────────────────────
        self._build_sidebar()
        self._build_content_area()

        # ── Show dashboard ────────────────────────────────────────────────
        self.navigate("dashboard")

    # ──────────────────────────────────────────────────────────────────────
    # Sidebar
    # ──────────────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, fg_color=Colors.BG_SIDEBAR,
                                     width=Spacing.SIDEBAR_W,
                                     corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # ── Logo / Brand ──────────────────────────────────────────────────
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent",
                                    height=80)
        brand_frame.pack(fill="x", padx=Spacing.LG, pady=(Spacing.XL, Spacing.SM))
        brand_frame.pack_propagate(False)

        # Logo icon
        logo_row = ctk.CTkFrame(brand_frame, fg_color="transparent")
        logo_row.pack(fill="x")

        ctk.CTkLabel(logo_row, text="🌩️", font=(Fonts.FAMILY, 28)).pack(
            side="left")

        title_col = ctk.CTkFrame(logo_row, fg_color="transparent")
        title_col.pack(side="left", padx=(Spacing.SM, 0))

        ctk.CTkLabel(title_col, text="CLIMAIA", font=Fonts.H1,
                     text_color=Colors.TEXT_PRIMARY, anchor="w").pack(
                         fill="x")
        ctk.CTkLabel(title_col, text="Climate AI Analysis",
                     font=Fonts.TINY,
                     text_color=Colors.TEXT_MUTED, anchor="w").pack(fill="x")

        # ── Divider ──────────────────────────────────────────────────────
        divider = ctk.CTkFrame(self.sidebar, fg_color=Colors.BORDER,
                                height=1)
        divider.pack(fill="x", padx=Spacing.LG, pady=(Spacing.SM, Spacing.LG))

        # ── Navigation label ─────────────────────────────────────────────
        ctk.CTkLabel(self.sidebar, text="  NAVEGAÇÃO", font=Fonts.TINY,
                     text_color=Colors.TEXT_DISABLED, anchor="w").pack(
                         fill="x", padx=Spacing.LG, pady=(0, Spacing.SM))

        # ── Navigation buttons ────────────────────────────────────────────
        for key, icon, text in self.NAV_ITEMS:
            btn = NavItem(self.sidebar, icon=icon, text=text,
                          command=lambda k=key: self.navigate(k))
            btn.pack(fill="x", padx=Spacing.MD, pady=2)
            self._nav_buttons[key] = btn

        # ── Bottom spacer + version ───────────────────────────────────────
        spacer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        # Divider
        ctk.CTkFrame(self.sidebar, fg_color=Colors.BORDER,
                      height=1).pack(fill="x", padx=Spacing.LG,
                                      pady=(0, Spacing.MD))

        # Version info
        bottom = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.LG))

        ctk.CTkLabel(bottom, text=f"v{self.APP_VERSION}", font=Fonts.TINY,
                     text_color=Colors.TEXT_DISABLED, anchor="w").pack(
                         fill="x")
        ctk.CTkLabel(bottom, text="© 2026 Victor V. Colombo",
                     font=Fonts.TINY, text_color=Colors.TEXT_DISABLED,
                     anchor="w").pack(fill="x")

    # ──────────────────────────────────────────────────────────────────────
    # Content area
    # ──────────────────────────────────────────────────────────────────────
    def _build_content_area(self):
        self.content = ctk.CTkFrame(self, fg_color=Colors.BG_DARK,
                                     corner_radius=0)
        self.content.pack(side="right", fill="both", expand=True)

        # Inner padding
        self.page_container = ctk.CTkFrame(self.content,
                                            fg_color="transparent")
        self.page_container.pack(fill="both", expand=True,
                                  padx=Spacing.XXL, pady=Spacing.XL)

    # ──────────────────────────────────────────────────────────────────────
    # Navigation
    # ──────────────────────────────────────────────────────────────────────
    def navigate(self, page_key: str):
        """Switch the active page."""
        if page_key == self._current_page:
            return

        # Update nav button styles
        for key, btn in self._nav_buttons.items():
            btn.set_active(key == page_key)

        # Destroy current page
        for widget in self.page_container.winfo_children():
            widget.destroy()

        # Create page (lazy instantiation)
        page_classes = {
            "dashboard":  DashboardPage,
            "data":       DataPage,
            "analysis":   AnalysisPage,
            "comparison": ComparisonPage,
            "forecast":   ForecastPage,
            "settings":   SettingsPage,
        }

        page_cls = page_classes.get(page_key)
        if page_cls:
            page = page_cls(self.page_container, app_ref=self)
            page.pack(fill="both", expand=True)

        self._current_page = page_key

    # ──────────────────────────────────────────────────────────────────────
    # Shared utilities
    # ──────────────────────────────────────────────────────────────────────
    def log(self, message: str):
        """Log a message to the dashboard console if available."""
        # Navigate to dashboard won't work well here, so just print
        print(f"[CLIMAIA] {message}")
