"""
CLIMAIA – Comparison Page
Side-by-side comparison of extreme event detection between raw and treated data.
"""

import customtkinter as ctk
from app.theme import Colors, Fonts, Spacing
from app.components import SectionHeader, ActionButton, StatCard, ConsoleBox


class ComparisonPage(ctk.CTkFrame):
    """Raw vs Treated data comparison page."""

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
        ctk.CTkLabel(scroll, text="Comparação Bruto vs Tratado",
                     font=Fonts.HERO, text_color=Colors.TEXT_PRIMARY,
                     anchor="w").pack(fill="x")
        ctk.CTkLabel(scroll,
                     text="Análise comparativa da integridade dos dados após tratamento",
                     font=Fonts.BODY, text_color=Colors.TEXT_MUTED,
                     anchor="w").pack(fill="x", pady=(4, Spacing.XL))

        # ── Comparison Stats ──────────────────────────────────────────────
        stats_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, Spacing.XL))
        stats_frame.columnconfigure((0, 1, 2, 3), weight=1, uniform="cstat")

        self.card_total_raw = StatCard(
            stats_frame, icon="📄", label="Eventos (Bruto)",
            value="—", accent=Colors.PRIMARY)
        self.card_total_raw.grid(row=0, column=0, padx=(0, Spacing.MD),
                                  sticky="nsew")

        self.card_total_treated = StatCard(
            stats_frame, icon="✨", label="Eventos (Tratado)",
            value="—", accent=Colors.SECONDARY)
        self.card_total_treated.grid(row=0, column=1, padx=(0, Spacing.MD),
                                      sticky="nsew")

        self.card_created = StatCard(
            stats_frame, icon="🆕", label="Eventos Criados",
            value="—", accent=Colors.WARNING)
        self.card_created.grid(row=0, column=2, padx=(0, Spacing.MD),
                                sticky="nsew")

        self.card_suppressed = StatCard(
            stats_frame, icon="🚫", label="Eventos Suprimidos",
            value="—", accent=Colors.DANGER)
        self.card_suppressed.grid(row=0, column=3, sticky="nsew")

        # ── Comparison Detail Table ───────────────────────────────────────
        SectionHeader(scroll, title="Diagnóstico Detalhado",
                      subtitle="Resultado da sobreposição de eventos entre os dois datasets").pack(
                          fill="x", pady=(0, Spacing.MD))

        detail_card = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD,
                                    corner_radius=Spacing.CORNER,
                                    border_width=1, border_color=Colors.BORDER)
        detail_card.pack(fill="x", pady=(0, Spacing.XL))

        # Table header
        header_row = ctk.CTkFrame(detail_card, fg_color=Colors.BG_DARKEST,
                                   corner_radius=0)
        header_row.pack(fill="x", padx=1, pady=(1, 0))

        columns = ["Variável", "Eventos Brutos", "Eventos Tratados",
                    "Coincidentes", "Criados", "Suprimidos", "Concordância"]
        for i, col in enumerate(columns):
            ctk.CTkLabel(header_row, text=col, font=Fonts.SMALL_BOLD,
                         text_color=Colors.TEXT_MUTED, anchor="center",
                         width=130).pack(side="left", padx=2, pady=Spacing.SM)

        # Placeholder rows
        self.table_frame = ctk.CTkFrame(detail_card, fg_color="transparent")
        self.table_frame.pack(fill="x", padx=1, pady=(0, 1))

        placeholder_vars = ["Velocidade do Vento", "Temperatura",
                            "Radiação Solar"]
        for var in placeholder_vars:
            row = ctk.CTkFrame(self.table_frame, fg_color="transparent",
                               height=36)
            row.pack(fill="x")

            vals = [var, "—", "—", "—", "—", "—", "—"]
            for val in vals:
                ctk.CTkLabel(row, text=val, font=Fonts.SMALL,
                             text_color=Colors.TEXT_SECONDARY,
                             anchor="center", width=130).pack(
                                 side="left", padx=2, pady=4)

        # ── Chart Placeholder ─────────────────────────────────────────────
        SectionHeader(scroll, title="Visualização Gráfica",
                      subtitle="Gráficos comparativos serão exibidos após a análise").pack(
                          fill="x", pady=(0, Spacing.MD))

        chart_card = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD,
                                   corner_radius=Spacing.CORNER,
                                   border_width=1, border_color=Colors.BORDER,
                                   height=300)
        chart_card.pack(fill="x", pady=(0, Spacing.XL))
        chart_card.pack_propagate(False)

        # Placeholder content
        placeholder = ctk.CTkFrame(chart_card, fg_color="transparent")
        placeholder.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(placeholder, text="📊", font=(Fonts.FAMILY, 48),
                     text_color=Colors.TEXT_DISABLED).pack()
        ctk.CTkLabel(placeholder,
                     text="Execute a análise para gerar os gráficos comparativos",
                     font=Fonts.BODY, text_color=Colors.TEXT_DISABLED).pack(
                         pady=(Spacing.SM, 0))

        # ── Actions ───────────────────────────────────────────────────────
        actions = ctk.CTkFrame(scroll, fg_color="transparent")
        actions.pack(fill="x", pady=(0, Spacing.MD))

        ActionButton(actions, text="Executar Comparação", icon="🔄",
                     color=Colors.ACCENT_EMERALD,
                     command=self._run_comparison, width=220).pack(side="left")

        ActionButton(actions, text="Exportar Relatório", icon="📋",
                     color=Colors.PRIMARY,
                     command=self._export_report, width=200).pack(
                         side="left", padx=(Spacing.MD, 0))

        # ── Console ───────────────────────────────────────────────────────
        SectionHeader(scroll, title="Log de Comparação").pack(
            fill="x", pady=(Spacing.MD, Spacing.SM))

        self.console = ConsoleBox(scroll, height=150)
        self.console.pack(fill="x")

    def _run_comparison(self):
        self.console.log("⏳ Motor de comparação ainda não implementado.")
        self.console.log("   Será integrado após o desenvolvimento do motor estatístico.")

    def _export_report(self):
        self.console.log("⏳ Exportação de relatório será implementada com o motor de comparação.")
