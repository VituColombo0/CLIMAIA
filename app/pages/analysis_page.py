"""
CLIMAIA – Analysis Page
Configure and run extreme event detection on loaded datasets.
"""

import customtkinter as ctk
from datetime import datetime
from app.theme import Colors, Fonts, Spacing
from app.components import (SectionHeader, ActionButton, LabeledEntry,
                             LabeledOptionMenu, ConsoleBox, StatusBadge)


class AnalysisPage(ctk.CTkFrame):
    """Analysis configuration and execution page."""

    def __init__(self, master, app_ref=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app_ref
        self._build_ui()

    def _build_ui(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                         scrollbar_button_color=Colors.BORDER,
                                         scrollbar_button_hover_color=Colors.BORDER_LIGHT)
        scroll.pack(fill="both", expand=True)

        # ── Header ────────────────────────────────────────────────────────
        ctk.CTkLabel(scroll, text="Análise de Eventos Extremos",
                     font=Fonts.HERO, text_color=Colors.TEXT_PRIMARY,
                     anchor="w").pack(fill="x")
        ctk.CTkLabel(scroll, text="Configure os parâmetros e execute a detecção estatística",
                     font=Fonts.BODY, text_color=Colors.TEXT_MUTED,
                     anchor="w").pack(fill="x", pady=(4, Spacing.XL))

        # ── Configuration Grid ────────────────────────────────────────────
        config_row = ctk.CTkFrame(scroll, fg_color="transparent")
        config_row.pack(fill="x", pady=(0, Spacing.XL))
        config_row.columnconfigure((0, 1), weight=1, uniform="config")

        # Left: Period selection
        left_card = ctk.CTkFrame(config_row, fg_color=Colors.BG_CARD,
                                  corner_radius=Spacing.CORNER,
                                  border_width=1, border_color=Colors.BORDER)
        left_card.grid(row=0, column=0, padx=(0, Spacing.MD), sticky="nsew")

        left_inner = ctk.CTkFrame(left_card, fg_color="transparent")
        left_inner.pack(fill="both", expand=True, padx=Spacing.CARD_PAD,
                        pady=Spacing.CARD_PAD)

        ctk.CTkLabel(left_inner, text="📅  Período de Análise", font=Fonts.H3,
                     text_color=Colors.TEXT_PRIMARY).pack(fill="x",
                         pady=(0, Spacing.MD))

        # Period preset
        self.period_preset = LabeledOptionMenu(
            left_inner, label="Período Predefinido",
            values=["Personalizado", "Último Mês", "Últimos 3 Meses",
                    "Últimos 6 Meses", "Último Ano", "Todo o Dataset"],
            default="Todo o Dataset",
            command=self._on_period_change)
        self.period_preset.pack(fill="x", pady=(0, Spacing.MD))

        # Custom date inputs
        self.custom_dates_frame = ctk.CTkFrame(left_inner, fg_color="transparent")
        self.custom_dates_frame.pack(fill="x", pady=(0, Spacing.MD))

        dates_row = ctk.CTkFrame(self.custom_dates_frame, fg_color="transparent")
        dates_row.pack(fill="x")
        dates_row.columnconfigure((0, 1), weight=1, uniform="date")

        self.date_start = LabeledEntry(dates_row, label="Data Início",
                                        placeholder="YYYY-MM-DD")
        self.date_start.grid(row=0, column=0, padx=(0, Spacing.SM), sticky="ew")

        self.date_end = LabeledEntry(dates_row, label="Data Fim",
                                      placeholder="YYYY-MM-DD")
        self.date_end.grid(row=0, column=1, sticky="ew")

        # Granularity
        self.granularity = LabeledOptionMenu(
            left_inner, label="Granularidade Temporal",
            values=["10 min", "Horária", "Diária", "Semanal", "Mensal"],
            default="Horária")
        self.granularity.pack(fill="x")

        # Right: Method selection
        right_card = ctk.CTkFrame(config_row, fg_color=Colors.BG_CARD,
                                   corner_radius=Spacing.CORNER,
                                   border_width=1, border_color=Colors.BORDER)
        right_card.grid(row=0, column=1, sticky="nsew")

        right_inner = ctk.CTkFrame(right_card, fg_color="transparent")
        right_inner.pack(fill="both", expand=True, padx=Spacing.CARD_PAD,
                         pady=Spacing.CARD_PAD)

        ctk.CTkLabel(right_inner, text="🔬  Método Estatístico", font=Fonts.H3,
                     text_color=Colors.TEXT_PRIMARY).pack(fill="x",
                         pady=(0, Spacing.MD))

        # Statistical method
        self.method = LabeledOptionMenu(
            right_inner, label="Método de Detecção",
            values=[
                "Percentil Adaptativo (P95/P99)",
                "Teoria de Valores Extremos (EVT)",
                "Distribuição de Gumbel",
                "Z-Score (Desvio Padrão)",
                "IQR (Interquartil Range)",
                "Todos os Métodos",
            ],
            default="Percentil Adaptativo (P95/P99)")
        self.method.pack(fill="x", pady=(0, Spacing.MD))

        # Threshold
        self.threshold = LabeledEntry(
            right_inner, label="Limiar de Sensibilidade (%)",
            placeholder="95")
        self.threshold.pack(fill="x", pady=(0, Spacing.MD))
        self.threshold.set("95")

        # Target datasets
        ctk.CTkLabel(right_inner, text="Aplicar Em", font=Fonts.SMALL_BOLD,
                     text_color=Colors.TEXT_SECONDARY, anchor="w").pack(
                         fill="x")

        check_frame = ctk.CTkFrame(right_inner, fg_color="transparent")
        check_frame.pack(fill="x", pady=(Spacing.XS, 0))

        self.apply_raw = ctk.CTkCheckBox(
            check_frame, text="Dados Brutos", font=Fonts.BODY,
            fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_HOVER,
            text_color=Colors.TEXT_PRIMARY,
            border_color=Colors.BORDER_LIGHT)
        self.apply_raw.pack(anchor="w", pady=2)
        self.apply_raw.select()

        self.apply_treated = ctk.CTkCheckBox(
            check_frame, text="Dados Tratados", font=Fonts.BODY,
            fg_color=Colors.SECONDARY, hover_color=Colors.SECONDARY_HOVER,
            text_color=Colors.TEXT_PRIMARY,
            border_color=Colors.BORDER_LIGHT)
        self.apply_treated.pack(anchor="w", pady=2)
        self.apply_treated.select()

        # ── Variable Selection ────────────────────────────────────────────
        SectionHeader(scroll, title="Variáveis para Análise",
                      subtitle="Selecione quais variáveis meteorológicas serão analisadas").pack(
                          fill="x", pady=(0, Spacing.MD))

        var_card = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD,
                                 corner_radius=Spacing.CORNER,
                                 border_width=1, border_color=Colors.BORDER)
        var_card.pack(fill="x", pady=(0, Spacing.XL))

        var_inner = ctk.CTkFrame(var_card, fg_color="transparent")
        var_inner.pack(fill="both", padx=Spacing.CARD_PAD,
                       pady=Spacing.CARD_PAD)

        self.var_checkboxes = {}
        default_vars = [
            ("Velocidade do Vento", True),
            ("Temperatura", True),
            ("Radiação Solar (POA)", True),
            ("Pressão Atmosférica", False),
            ("Umidade Relativa", False),
            ("Precipitação", False),
        ]

        var_grid = ctk.CTkFrame(var_inner, fg_color="transparent")
        var_grid.pack(fill="x")
        var_grid.columnconfigure((0, 1, 2), weight=1, uniform="var")

        for i, (name, default) in enumerate(default_vars):
            cb = ctk.CTkCheckBox(
                var_grid, text=name, font=Fonts.BODY,
                fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_HOVER,
                text_color=Colors.TEXT_PRIMARY,
                border_color=Colors.BORDER_LIGHT)
            cb.grid(row=i // 3, column=i % 3, sticky="w",
                    padx=Spacing.SM, pady=Spacing.XS)
            if default:
                cb.select()
            self.var_checkboxes[name] = cb

        # Info: auto-detect
        ctk.CTkLabel(var_inner,
                     text="💡 As variáveis serão detectadas automaticamente a partir das colunas do CSV carregado.",
                     font=Fonts.SMALL, text_color=Colors.TEXT_MUTED,
                     anchor="w").pack(fill="x", pady=(Spacing.MD, 0))

        # ── Run Analysis ──────────────────────────────────────────────────
        run_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        run_frame.pack(fill="x", pady=(0, Spacing.MD))

        ActionButton(run_frame, text="Executar Análise", icon="▶️",
                     color=Colors.ACCENT_EMERALD,
                     hover_color="#059669",
                     command=self._run_analysis, width=220).pack(side="left")

        self.run_status = StatusBadge(run_frame, status="idle",
                                       text="AGUARDANDO")
        self.run_status.pack(side="left", padx=(Spacing.MD, 0))

        # ── Console ───────────────────────────────────────────────────────
        SectionHeader(scroll, title="Log da Análise").pack(
            fill="x", pady=(Spacing.MD, Spacing.SM))

        self.console = ConsoleBox(scroll, height=180)
        self.console.pack(fill="x")

    def _on_period_change(self, value):
        """Handle period preset changes."""
        pass  # Date fields remain available for manual override

    def _run_analysis(self):
        """Execute the analysis pipeline (placeholder for now)."""
        # Validation
        has_raw = self.app and self.app.state.get("raw_df") is not None
        has_treated = self.app and self.app.state.get("treated_df") is not None
        want_raw = self.apply_raw.get()
        want_treated = self.apply_treated.get()

        if want_raw and not has_raw:
            self.console.log("ERRO: Dados brutos não carregados. Vá para a aba 'Dados' primeiro.")
            self.run_status.set_status("error", "SEM DADOS")
            return
        if want_treated and not has_treated:
            self.console.log("ERRO: Dados tratados não carregados. Vá para a aba 'Dados' primeiro.")
            self.run_status.set_status("error", "SEM DADOS")
            return

        # Get config
        method = self.method.get()
        threshold = self.threshold.get()
        granularity = self.granularity.get()
        period = self.period_preset.get()

        self.run_status.set_status("running", "EXECUTANDO...")
        self.console.log(f"Iniciando análise...")
        self.console.log(f"  Método: {method}")
        self.console.log(f"  Limiar: {threshold}%")
        self.console.log(f"  Granularidade: {granularity}")
        self.console.log(f"  Período: {period}")

        selected_vars = [name for name, cb in self.var_checkboxes.items() if cb.get()]
        self.console.log(f"  Variáveis: {', '.join(selected_vars)}")

        # Placeholder – this is where the statistical engine will be called
        self.console.log("")
        self.console.log("⏳ Motor estatístico ainda não implementado.")
        self.console.log("   O modelo será integrado na próxima fase do projeto.")
        self.run_status.set_status("warning", "NÃO IMPLEMENTADO")
