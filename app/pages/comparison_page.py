"""
CLIMAIA – Comparison Page
Side-by-side comparison of extreme event detection between raw and treated data.
"""

import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from app.theme import Colors, Fonts, Spacing
from app.components import SectionHeader, ActionButton, StatCard, ConsoleBox, StatusBadge


class ComparisonPage(ctk.CTkFrame):
    """Raw vs Treated data comparison page."""

    def __init__(self, master, app_ref=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app_ref
        self._build_ui()
        self._refresh_state()

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

        # ── Prerequisites Banner ──────────────────────────────────────────
        self.prereq_banner = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD,
                                           corner_radius=Spacing.CORNER,
                                           border_width=1,
                                           border_color=Colors.BORDER)
        self.prereq_banner.pack(fill="x", pady=(0, Spacing.XL))

        banner_inner = ctk.CTkFrame(self.prereq_banner, fg_color="transparent")
        banner_inner.pack(fill="x", padx=Spacing.CARD_PAD, pady=Spacing.MD)

        self.prereq_icon = ctk.CTkLabel(banner_inner, text="⚠️",
                                         font=(Fonts.FAMILY, 20))
        self.prereq_icon.pack(side="left")

        self.prereq_text = ctk.CTkLabel(
            banner_inner,
            text="Pré-requisitos: Carregue ambos os datasets e execute a análise primeiro.",
            font=Fonts.BODY, text_color=Colors.TEXT_MUTED, anchor="w")
        self.prereq_text.pack(side="left", padx=(Spacing.SM, 0), fill="x", expand=True)

        # Prerequisite checklist
        self.check_frame = ctk.CTkFrame(self.prereq_banner, fg_color="transparent")
        self.check_frame.pack(fill="x", padx=Spacing.CARD_PAD, pady=(0, Spacing.MD))

        self.check_labels = {}
        checks = [
            ("raw", "Dados Brutos carregados"),
            ("treated", "Dados Tratados carregados"),
            ("analysis", "Análise estatística executada"),
        ]
        for key, label in checks:
            row = ctk.CTkFrame(self.check_frame, fg_color="transparent")
            row.pack(fill="x", pady=1)
            icon_lbl = ctk.CTkLabel(row, text="❌", font=Fonts.SMALL, width=24)
            icon_lbl.pack(side="left")
            ctk.CTkLabel(row, text=label, font=Fonts.SMALL,
                         text_color=Colors.TEXT_SECONDARY).pack(side="left")
            self.check_labels[key] = icon_lbl

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

        # Table body (dynamic)
        self.table_frame = ctk.CTkFrame(detail_card, fg_color="transparent")
        self.table_frame.pack(fill="x", padx=1, pady=(0, 1))

        self._build_placeholder_rows()

        # ── Chart Placeholder ─────────────────────────────────────────────
        SectionHeader(scroll, title="Visualização Gráfica",
                      subtitle="Gráficos comparativos serão exibidos após a análise").pack(
                          fill="x", pady=(0, Spacing.MD))

        self.chart_card = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD,
                                   corner_radius=Spacing.CORNER,
                                   border_width=1, border_color=Colors.BORDER,
                                   height=300)
        self.chart_card.pack(fill="x", pady=(0, Spacing.XL))
        self.chart_card.pack_propagate(False)

        # Placeholder content
        placeholder = ctk.CTkFrame(self.chart_card, fg_color="transparent")
        placeholder.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(placeholder, text="📊", font=(Fonts.FAMILY, 48),
                     text_color=Colors.TEXT_DISABLED).pack()
        ctk.CTkLabel(placeholder,
                     text="Execute a comparação para gerar os gráficos",
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

        self.comparison_status = StatusBadge(actions, status="idle",
                                              text="AGUARDANDO")
        self.comparison_status.pack(side="left", padx=(Spacing.MD, 0))

        # ── Console ───────────────────────────────────────────────────────
        SectionHeader(scroll, title="Log de Comparação").pack(
            fill="x", pady=(Spacing.MD, Spacing.SM))

        self.console = ConsoleBox(scroll, height=150)
        self.console.pack(fill="x")

    def _build_placeholder_rows(self):
        """Build placeholder rows in the comparison table."""
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        vars_to_show = []
        if self.app and self.app.app_state.get("analysis_config"):
            vars_to_show = self.app.app_state["analysis_config"].get("variables", [])

        if not vars_to_show:
            vars_to_show = ["Velocidade do Vento", "Temperatura", "Radiação Solar"]

        for var in vars_to_show:
            row = ctk.CTkFrame(self.table_frame, fg_color="transparent",
                               height=36)
            row.pack(fill="x")

            vals = [var, "—", "—", "—", "—", "—", "—"]
            for val in vals:
                ctk.CTkLabel(row, text=val, font=Fonts.SMALL,
                             text_color=Colors.TEXT_SECONDARY,
                             anchor="center", width=130).pack(
                                 side="left", padx=2, pady=4)

    def _refresh_state(self):
        """Update prerequisite checks from app state."""
        if not self.app:
            return

        state = self.app.app_state
        all_ok = True

        # Check raw data
        if state.get("raw_df") is not None:
            self.check_labels["raw"].configure(text="✅")
        else:
            self.check_labels["raw"].configure(text="❌")
            all_ok = False

        # Check treated data
        if state.get("treated_df") is not None:
            self.check_labels["treated"].configure(text="✅")
        else:
            self.check_labels["treated"].configure(text="❌")
            all_ok = False

        # Check analysis ran
        if state.get("analysis_ran"):
            self.check_labels["analysis"].configure(text="✅")
        else:
            self.check_labels["analysis"].configure(text="❌")
            all_ok = False

        # Update banner style
        if all_ok:
            self.prereq_icon.configure(text="✅")
            self.prereq_text.configure(
                text="Todos os pré-requisitos atendidos. Pronto para executar a comparação.",
                text_color=Colors.ACCENT_EMERALD)
        else:
            self.prereq_icon.configure(text="⚠️")
            self.prereq_text.configure(
                text="Pré-requisitos pendentes:",
                text_color=Colors.ACCENT_WARM)

        # Update table with analysis variables
        self._build_placeholder_rows()

        # If comparison was already run, show status
        if state.get("comparison_ran"):
            self.comparison_status.set_status("ready", "CONCLUÍDA")

    def _run_comparison(self):
        """Execute comparison — validates all prerequisites first."""
        if not self.app:
            return

        state = self.app.app_state

        # ── Validation ────────────────────────────────────────────────────
        errors = []
        if state.get("raw_df") is None:
            errors.append("Dados Brutos não carregados")
        if state.get("treated_df") is None:
            errors.append("Dados Tratados não carregados")
        if not state.get("analysis_ran"):
            errors.append("Análise estatística não executada")

        if errors:
            self.console.log("━" * 50)
            self.console.log("❌ Não é possível executar a comparação:")
            for err in errors:
                self.console.log(f"   → {err}")
            self.console.log("")
            self.console.log("💡 Resolva os pré-requisitos e tente novamente:")
            if state.get("raw_df") is None or state.get("treated_df") is None:
                self.console.log("   1. Vá para a aba 'Dados' e carregue ambos os CSVs")
            if not state.get("analysis_ran"):
                self.console.log("   2. Vá para a aba 'Análise' e execute a detecção de eventos")
            self.console.log("━" * 50)
            self.comparison_status.set_status("error", "PRÉ-REQUISITOS")
            return

        # ── Execute comparison ────────────────────────────────────────────
        config = state.get("analysis_config", {})
        variables = config.get("variables", [])
        method = config.get("method", "N/A")

        self.comparison_status.set_status("running", "EXECUTANDO...")
        self.console.log("━" * 50)
        self.console.log("🔄 Iniciando comparação Bruto vs Tratado...")
        self.console.log(f"  Método utilizado: {method}")
        self.console.log(f"  Variáveis: {', '.join(variables)}")

        raw_df = state["raw_df"]
        treated_df = state["treated_df"]
        self.console.log(f"  Dataset Bruto: {len(raw_df):,} registros")
        self.console.log(f"  Dataset Tratado: {len(treated_df):,} registros")

        # Shape comparison
        if raw_df.shape != treated_df.shape:
            self.console.log(f"  ⚠️ Dimensões diferentes: Bruto {raw_df.shape} vs Tratado {treated_df.shape}")
        else:
            self.console.log(f"  ✅ Dimensões iguais: {raw_df.shape}")

        # Column comparison
        raw_cols = set(raw_df.columns)
        treated_cols = set(treated_df.columns)
        common_cols = raw_cols & treated_cols
        only_raw = raw_cols - treated_cols
        only_treated = treated_cols - raw_cols

        self.console.log(f"  Colunas em comum: {len(common_cols)}")
        if only_raw:
            self.console.log(f"  ⚠️ Apenas no Bruto: {', '.join(sorted(only_raw))}")
        if only_treated:
            self.console.log(f"  ⚠️ Apenas no Tratado: {', '.join(sorted(only_treated))}")

        self.console.log("")
        self.console.log("⏳ Motor de comparação de eventos será implementado na Fase 2.")
        self.console.log("   → Depende da implementação do motor estatístico na aba 'Análise'.")
        self.console.log("   → Quando pronto, esta aba exibirá: eventos suprimidos, criados e taxa de concordância.")
        self.console.log("━" * 50)

        # Mark as run
        state["comparison_ran"] = True
        self.comparison_status.set_status("warning", "FASE 2 PENDENTE")

        self.app.log("Comparação Bruto vs Tratado configurada — aguardando motor estatístico (Fase 2)")

    def _export_report(self):
        """Export comparison report as a text file."""
        if not self.app:
            return

        state = self.app.app_state

        if not state.get("comparison_ran"):
            self.console.log("❌ Execute a comparação antes de exportar o relatório.")
            return

        # Open save dialog
        filepath = filedialog.asksaveasfilename(
            title="Exportar Relatório de Comparação",
            defaultextension=".txt",
            filetypes=[
                ("Texto", "*.txt"),
                ("CSV", "*.csv"),
                ("Todos os arquivos", "*.*"),
            ],
            initialfile="CLIMAIA_Relatorio_Comparacao.txt")

        if not filepath:
            return

        try:
            config = state.get("analysis_config", {})
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("=" * 60 + "\n")
                f.write("CLIMAIA - Relatório de Comparação Bruto vs Tratado\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Data: {__import__('datetime').datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
                f.write(f"Método: {config.get('method', 'N/A')}\n")
                f.write(f"Limiar: {config.get('threshold', 'N/A')}%\n")
                f.write(f"Variáveis: {', '.join(config.get('variables', []))}\n\n")

                # Data summary
                raw_df = state.get("raw_df")
                treated_df = state.get("treated_df")
                if raw_df is not None:
                    f.write(f"Dataset Bruto: {len(raw_df):,} registros, {len(raw_df.columns)} colunas\n")
                if treated_df is not None:
                    f.write(f"Dataset Tratado: {len(treated_df):,} registros, {len(treated_df.columns)} colunas\n")

                f.write("\n" + "=" * 60 + "\n")
                f.write("NOTA: Motor de comparação será implementado na Fase 2.\n")
                f.write("Este relatório será preenchido com os resultados da detecção\n")
                f.write("de eventos extremos quando o motor estatístico estiver ativo.\n")
                f.write("=" * 60 + "\n")

            self.console.log(f"✅ Relatório exportado: {os.path.basename(filepath)}")
            self.app.log(f"Relatório de comparação exportado para: {filepath}")

        except Exception as e:
            self.console.log(f"❌ Erro ao exportar: {e}")
            messagebox.showerror("Erro ao Exportar", f"Não foi possível salvar o relatório:\n{e}")
