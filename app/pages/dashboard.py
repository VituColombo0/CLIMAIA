"""
CLIMAIA – Dashboard Page
Overview with stat cards, recent activity and quick actions.
"""

import customtkinter as ctk
from app.theme import Colors, Fonts, Spacing
from app.components import StatCard, SectionHeader, ActionButton, ConsoleBox, StatusBadge


class DashboardPage(ctk.CTkFrame):
    """Main dashboard / home screen."""

    def __init__(self, master, app_ref=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app_ref
        self._build_ui()
        self._refresh_state()

    def _build_ui(self):
        # ── Scrollable container ──────────────────────────────────────────
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                         scrollbar_button_color=Colors.BORDER,
                                         scrollbar_button_hover_color=Colors.BORDER_LIGHT)
        scroll.pack(fill="both", expand=True)

        # ── Welcome header ────────────────────────────────────────────────
        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, Spacing.XL))

        ctk.CTkLabel(header, text="Dashboard", font=Fonts.HERO,
                     text_color=Colors.TEXT_PRIMARY, anchor="w").pack(
                         fill="x")
        ctk.CTkLabel(header, text="Visão geral do sistema de análise climática",
                     font=Fonts.BODY, text_color=Colors.TEXT_MUTED,
                     anchor="w").pack(fill="x", pady=(4, 0))

        # ── Stat cards row ────────────────────────────────────────────────
        cards_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        cards_frame.pack(fill="x", pady=(0, Spacing.XL))
        cards_frame.columnconfigure((0, 1, 2, 3), weight=1, uniform="card")

        self.card_datasets = StatCard(
            cards_frame, icon="📁", label="Datasets Carregados",
            value="0", accent=Colors.PRIMARY)
        self.card_datasets.grid(row=0, column=0, padx=(0, Spacing.MD),
                                 sticky="nsew")

        self.card_records = StatCard(
            cards_frame, icon="📊", label="Total de Registros",
            value="0", accent=Colors.ACCENT_WARM)
        self.card_records.grid(row=0, column=1, padx=(0, Spacing.MD),
                               sticky="nsew")

        self.card_accuracy = StatCard(
            cards_frame, icon="🎯", label="Concordância B/T",
            value="—%", accent=Colors.ACCENT_EMERALD)
        self.card_accuracy.grid(row=0, column=2, padx=(0, Spacing.MD),
                                 sticky="nsew")

        self.card_model = StatCard(
            cards_frame, icon="🧠", label="Status do Modelo",
            value="Offline", accent=Colors.ACCENT_ROSE)
        self.card_model.grid(row=0, column=3, sticky="nsew")

        # ── Quick Actions ─────────────────────────────────────────────────
        SectionHeader(scroll, title="Ações Rápidas",
                      subtitle="Acesse as funcionalidades principais").pack(
                          fill="x", pady=(0, Spacing.MD))

        actions = ctk.CTkFrame(scroll, fg_color="transparent")
        actions.pack(fill="x", pady=(0, Spacing.XL))

        quick_buttons = [
            ("📂", "Carregar Dados", Colors.PRIMARY, lambda: self._nav("data")),
            ("🔬", "Nova Análise", Colors.SECONDARY, lambda: self._nav("analysis")),
            ("📊", "Ver Comparação", Colors.ACCENT_EMERALD, lambda: self._nav("comparison")),
            ("🤖", "Previsão IA", Colors.ACCENT_VIOLET, lambda: self._nav("forecast")),
        ]
        for i, (icon, text, color, cmd) in enumerate(quick_buttons):
            btn = ActionButton(actions, text=text, icon=icon, color=color,
                               hover_color=color, command=cmd, width=200)
            btn.pack(side="left", padx=(0, Spacing.MD))

        # ── System Status ─────────────────────────────────────────────────
        SectionHeader(scroll, title="Status do Sistema",
                      subtitle="Informações sobre o estado atual").pack(
                          fill="x", pady=(0, Spacing.MD))

        status_frame = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD,
                                     corner_radius=Spacing.CORNER,
                                     border_width=1,
                                     border_color=Colors.BORDER)
        status_frame.pack(fill="x", pady=(0, Spacing.XL))

        status_items = [
            ("Motor Estatístico (EVT/Gumbel)", "idle", "AGUARDANDO"),
            ("Modelo LSTM", "idle", "NÃO TREINADO"),
            ("Modelo XGBoost", "idle", "NÃO TREINADO"),
            ("Dados Brutos", "idle", "NÃO CARREGADOS"),
            ("Dados Tratados", "idle", "NÃO CARREGADOS"),
        ]

        self.status_badges = {}
        for i, (name, status, text) in enumerate(status_items):
            row = ctk.CTkFrame(status_frame, fg_color="transparent")
            row.pack(fill="x", padx=Spacing.CARD_PAD,
                     pady=(Spacing.MD if i == 0 else 4,
                           Spacing.MD if i == len(status_items) - 1 else 4))

            ctk.CTkLabel(row, text=name, font=Fonts.BODY,
                         text_color=Colors.TEXT_SECONDARY, anchor="w").pack(
                             side="left")

            badge = StatusBadge(row, status=status, text=text)
            badge.pack(side="right")
            self.status_badges[name] = badge

        # ── Console ───────────────────────────────────────────────────────
        SectionHeader(scroll, title="Console",
                      subtitle="Log de atividades do sistema").pack(
                          fill="x", pady=(0, Spacing.MD))

        self.console = ConsoleBox(scroll, height=150)
        self.console.pack(fill="x")

    def _nav(self, page: str):
        if self.app:
            self.app.navigate(page)

    def _refresh_state(self):
        """Refresh all dashboard elements from the current app state."""
        if not self.app:
            self.console.log("CLIMAIA v1.0 inicializado com sucesso.")
            self.console.log("Aguardando carregamento de dados...")
            return

        state = self.app.app_state

        # ── Update stat cards ─────────────────────────────────────────────
        dataset_count = self.app.count_loaded_datasets()
        self.card_datasets.set_value(str(dataset_count))

        total_records = self.app.get_total_records()
        self.card_records.set_value(f"{total_records:,}" if total_records > 0 else "0")

        # Accuracy from comparison
        if state.get("comparison_ran") and state.get("comparison_results"):
            results = state["comparison_results"]
            acc = results.get("overall_agreement")
            if acc is not None:
                self.card_accuracy.set_value(f"{acc:.1f}%")

        # Model status
        if state.get("model_trained"):
            model_type = state.get("model_type", "IA")
            self.card_model.set_value(f"✅ {model_type}")
        else:
            self.card_model.set_value("Offline")

        # ── Update status badges ──────────────────────────────────────────
        # Raw data status
        if state.get("raw_df") is not None:
            raw_rows = len(state["raw_df"])
            self.status_badges["Dados Brutos"].set_status(
                "ready", f"CARREGADO ({raw_rows:,} linhas)")
        else:
            self.status_badges["Dados Brutos"].set_status("idle", "NÃO CARREGADOS")

        # Treated data status
        if state.get("treated_df") is not None:
            treated_rows = len(state["treated_df"])
            self.status_badges["Dados Tratados"].set_status(
                "ready", f"CARREGADO ({treated_rows:,} linhas)")
        else:
            self.status_badges["Dados Tratados"].set_status("idle", "NÃO CARREGADOS")

        # Analysis engine status
        if state.get("analysis_ran"):
            self.status_badges["Motor Estatístico (EVT/Gumbel)"].set_status(
                "ready", "ANÁLISE CONCLUÍDA")
        else:
            self.status_badges["Motor Estatístico (EVT/Gumbel)"].set_status(
                "idle", "AGUARDANDO")

        # Model statuses
        if state.get("model_trained"):
            model = state.get("model_type", "")
            if "LSTM" in model or "Ensemble" in model:
                self.status_badges["Modelo LSTM"].set_status("ready", "TREINADO")
            if "XGBoost" in model or "Ensemble" in model:
                self.status_badges["Modelo XGBoost"].set_status("ready", "TREINADO")
        else:
            self.status_badges["Modelo LSTM"].set_status("idle", "NÃO TREINADO")
            self.status_badges["Modelo XGBoost"].set_status("idle", "NÃO TREINADO")

        # ── Replay log messages ───────────────────────────────────────────
        log_messages = self.app.get_log_messages()
        if log_messages:
            # Show the last 20 messages
            for msg in log_messages[-20:]:
                self.console.log(msg)
        else:
            self.console.log("CLIMAIA v1.0 inicializado com sucesso.")
            self.console.log("Aguardando carregamento de dados...")

    def update_stats(self, datasets=None, events=None, accuracy=None,
                     model_status=None):
        if datasets is not None:
            self.card_datasets.set_value(str(datasets))
        if events is not None:
            self.card_records.set_value(str(events))
        if accuracy is not None:
            self.card_accuracy.set_value(f"{accuracy:.1f}%")
        if model_status is not None:
            self.card_model.set_value(model_status)
