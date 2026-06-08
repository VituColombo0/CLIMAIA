"""
CLIMAIA – Main Application Shell
Sidebar navigation + page router for the desktop application.
"""

import customtkinter as ctk
from datetime import datetime
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
        self.app_state = {
            # Data
            "raw_df": None,
            "treated_df": None,
            "raw_path": None,
            "treated_path": None,
            "raw_columns": [],
            "treated_columns": [],

            # Analysis results
            "analysis_results": None,
            "analysis_ran": False,
            "analysis_config": None,

            # Comparison results
            "comparison_results": None,
            "comparison_ran": False,

            # Forecast / Model
            "model_trained": False,
            "model_type": None,
            "forecast_results": None,

            # Settings
            "csv_separator": "Auto-detectar",
            "csv_encoding": "UTF-8",
            "csv_date_col": "Auto-detectar",
            "export_format": "CSV",
            "theme": "Escuro (Padrão)",
            "scale": "100%",
        }

        # ── Log message queue (cross-page communication) ──────────────────
        self._log_messages = []

        self._current_page = None
        self._current_page_widget = None
        self._nav_buttons = {}

        # ── Build layout ──────────────────────────────────────────────────
        self._build_sidebar()
        self._build_content_area()

        # ── Show dashboard ────────────────────────────────────────────────
        self.navigate("dashboard")

        # ── Pre-load default datasets ─────────────────────────────────────
        self._preload_data()

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
            self._current_page_widget = page

        self._current_page = page_key

    # ──────────────────────────────────────────────────────────────────────
    # Cross-page logging
    # ──────────────────────────────────────────────────────────────────────
    def log(self, message: str):
        """Log a message. Stored for dashboard replay and printed to stdout."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        self._log_messages.append(entry)
        print(f"[CLIMAIA] {entry}")

        # If the dashboard is currently visible, push the message live
        if (self._current_page == "dashboard"
                and self._current_page_widget
                and hasattr(self._current_page_widget, 'console')):
            self._current_page_widget.console.log(message)

    def get_log_messages(self) -> list:
        """Return all accumulated log messages."""
        return list(self._log_messages)

    # ──────────────────────────────────────────────────────────────────────
    # Data preload
    # ──────────────────────────────────────────────────────────────────────
    def _preload_data(self):
        """Automatically load default raw and treated datasets if they exist."""
        import os
        import pandas as pd
        import threading
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        raw_path = os.path.join(base_dir, "data", "raw", "dataset_bruto.csv")
        treated_path = os.path.join(base_dir, "data", "treated", "dataset_consolidado.csv")
        
        def load_thread():
            try:
                if os.path.exists(raw_path):
                    df_raw = pd.read_csv(raw_path, sep=';')
                    self.app_state["raw_df"] = df_raw
                    self.app_state["raw_path"] = raw_path
                    self.app_state["raw_columns"] = df_raw.columns.tolist()
                    self.log(f"Dados brutos carregados automaticamente: {os.path.basename(raw_path)}")
                
                if os.path.exists(treated_path):
                    df_treated = pd.read_csv(treated_path, sep=',')
                    self.app_state["treated_df"] = df_treated
                    self.app_state["treated_path"] = treated_path
                    self.app_state["treated_columns"] = df_treated.columns.tolist()
                    self.log(f"Dados tratados carregados automaticamente: {os.path.basename(treated_path)}")
                
                # If we're currently on the data page, force refresh (safely on main thread)
                if self._current_page == "data" and self._current_page_widget:
                    self.after(100, self._current_page_widget._restore_state)
            except Exception as e:
                self.log(f"Erro ao auto-carregar dados: {e}")

        threading.Thread(target=load_thread, daemon=True).start()

    # ──────────────────────────────────────────────────────────────────────
    # State helpers
    # ──────────────────────────────────────────────────────────────────────
    def has_data(self, dtype: str = "any") -> bool:
        """Check if data is loaded. dtype: 'raw', 'treated', 'any', 'both'."""
        has_raw = self.app_state.get("raw_df") is not None
        has_treated = self.app_state.get("treated_df") is not None
        if dtype == "raw":
            return has_raw
        elif dtype == "treated":
            return has_treated
        elif dtype == "both":
            return has_raw and has_treated
        else:  # any
            return has_raw or has_treated

    def get_data_columns(self) -> list:
        """Get the union of column names from loaded datasets."""
        cols = set()
        raw_df = self.app_state.get("raw_df")
        treated_df = self.app_state.get("treated_df")
        if raw_df is not None:
            cols.update(raw_df.columns.tolist())
        if treated_df is not None:
            cols.update(treated_df.columns.tolist())
        return sorted(list(cols))

    def get_numeric_columns(self) -> list:
        """Get numeric column names from loaded datasets."""
        cols = set()
        raw_df = self.app_state.get("raw_df")
        treated_df = self.app_state.get("treated_df")
        if raw_df is not None:
            cols.update(raw_df.select_dtypes(include="number").columns.tolist())
        if treated_df is not None:
            cols.update(treated_df.select_dtypes(include="number").columns.tolist())
        return sorted(list(cols))

    def count_loaded_datasets(self) -> int:
        """Count how many datasets are loaded (0, 1, or 2)."""
        count = 0
        if self.app_state.get("raw_df") is not None:
            count += 1
        if self.app_state.get("treated_df") is not None:
            count += 1
        return count

    def get_total_records(self) -> int:
        """Get total number of records across all loaded datasets."""
        total = 0
        raw_df = self.app_state.get("raw_df")
        treated_df = self.app_state.get("treated_df")
        if raw_df is not None:
            total += len(raw_df)
        if treated_df is not None:
            total += len(treated_df)
        return total

    def get_csv_read_kwargs(self) -> dict:
        """Build pandas read_csv kwargs from current settings."""
        kwargs = {}

        # Separator
        sep = self.app_state.get("csv_separator", "Auto-detectar")
        sep_map = {
            "Vírgula (,)": ",",
            "Ponto e Vírgula (;)": ";",
            "Tab": "\t",
        }
        if sep in sep_map:
            kwargs["sep"] = sep_map[sep]
        # else: let pandas auto-detect (default is ',')

        # Encoding
        enc = self.app_state.get("csv_encoding", "UTF-8")
        enc_map = {
            "UTF-8": "utf-8",
            "Latin-1 (ISO-8859-1)": "latin-1",
            "Windows-1252": "cp1252",
        }
        if enc in enc_map:
            kwargs["encoding"] = enc_map[enc]

        return kwargs
