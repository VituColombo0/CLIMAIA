"""
CLIMAIA – Forecast Page
AI-powered prediction interface for extreme climate events.
"""

import customtkinter as ctk
from datetime import datetime
from app.theme import Colors, Fonts, Spacing
from app.components import (SectionHeader, ActionButton, LabeledEntry,
                             LabeledOptionMenu, ConsoleBox, StatusBadge)


class ForecastPage(ctk.CTkFrame):
    """Forecasting / Prediction page."""

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
        ctk.CTkLabel(scroll, text="Previsão com IA", font=Fonts.HERO,
                     text_color=Colors.TEXT_PRIMARY, anchor="w").pack(
                         fill="x")
        ctk.CTkLabel(scroll,
                     text="Utilize os modelos treinados para prever eventos climáticos extremos",
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
            text="Pré-requisitos para previsão:",
            font=Fonts.BODY, text_color=Colors.TEXT_MUTED, anchor="w")
        self.prereq_text.pack(side="left", padx=(Spacing.SM, 0), fill="x", expand=True)

        # Prerequisite checklist
        check_frame = ctk.CTkFrame(self.prereq_banner, fg_color="transparent")
        check_frame.pack(fill="x", padx=Spacing.CARD_PAD, pady=(0, Spacing.MD))

        self.check_labels = {}
        checks = [
            ("data", "Dados carregados (pelo menos 1 dataset)"),
            ("analysis", "Análise estatística executada"),
            ("model", "Modelo treinado"),
        ]
        for key, label in checks:
            row = ctk.CTkFrame(check_frame, fg_color="transparent")
            row.pack(fill="x", pady=1)
            icon_lbl = ctk.CTkLabel(row, text="❌", font=Fonts.SMALL, width=24)
            icon_lbl.pack(side="left")
            ctk.CTkLabel(row, text=label, font=Fonts.SMALL,
                         text_color=Colors.TEXT_SECONDARY).pack(side="left")
            self.check_labels[key] = icon_lbl

        # ── Model Selection ───────────────────────────────────────────────
        config_row = ctk.CTkFrame(scroll, fg_color="transparent")
        config_row.pack(fill="x", pady=(0, Spacing.XL))
        config_row.columnconfigure((0, 1), weight=1, uniform="fconfig")

        # Left: Model
        left_card = ctk.CTkFrame(config_row, fg_color=Colors.BG_CARD,
                                  corner_radius=Spacing.CORNER,
                                  border_width=1, border_color=Colors.BORDER)
        left_card.grid(row=0, column=0, padx=(0, Spacing.MD), sticky="nsew")

        left_inner = ctk.CTkFrame(left_card, fg_color="transparent")
        left_inner.pack(fill="both", expand=True, padx=Spacing.CARD_PAD,
                        pady=Spacing.CARD_PAD)

        ctk.CTkLabel(left_inner, text="🧠  Modelo de Previsão", font=Fonts.H3,
                     text_color=Colors.TEXT_PRIMARY).pack(fill="x",
                         pady=(0, Spacing.MD))

        self.model_select = LabeledOptionMenu(
            left_inner, label="Modelo",
            values=["LSTM (Redes Neurais)", "XGBoost (Gradient Boosting)",
                    "Ensemble (LSTM + XGBoost)"],
            default="LSTM (Redes Neurais)")
        self.model_select.pack(fill="x", pady=(0, Spacing.MD))

        # Epochs / iterations
        self.epochs_entry = LabeledEntry(
            left_inner, label="Épocas de Treinamento",
            placeholder="50")
        self.epochs_entry.pack(fill="x", pady=(0, Spacing.MD))
        self.epochs_entry.set("50")

        self.model_status_frame = ctk.CTkFrame(left_inner, fg_color="transparent")
        self.model_status_frame.pack(fill="x", pady=(0, Spacing.MD))

        ctk.CTkLabel(self.model_status_frame, text="Status:",
                     font=Fonts.SMALL, text_color=Colors.TEXT_SECONDARY).pack(
                         side="left")
        self.model_badge = StatusBadge(self.model_status_frame, status="idle",
                                        text="NÃO TREINADO")
        self.model_badge.pack(side="left", padx=(Spacing.SM, 0))

        # Training buttons
        btn_row_train = ctk.CTkFrame(left_inner, fg_color="transparent")
        btn_row_train.pack(fill="x")

        ActionButton(btn_row_train, text="Treinar Modelo", icon="⚙️",
                     color=Colors.ACCENT_WARM,
                     hover_color="#d97706",
                     command=self._train_model, width=180).pack(
                         side="left", padx=(0, Spacing.SM))

        ActionButton(btn_row_train, text="Resetar", icon="🔄",
                     color=Colors.BG_CARD_HOVER,
                     hover_color=Colors.DANGER,
                     command=self._reset_model, width=120).pack(side="left")

        # Right: Prediction config
        right_card = ctk.CTkFrame(config_row, fg_color=Colors.BG_CARD,
                                   corner_radius=Spacing.CORNER,
                                   border_width=1, border_color=Colors.BORDER)
        right_card.grid(row=0, column=1, sticky="nsew")

        right_inner = ctk.CTkFrame(right_card, fg_color="transparent")
        right_inner.pack(fill="both", expand=True, padx=Spacing.CARD_PAD,
                         pady=Spacing.CARD_PAD)

        ctk.CTkLabel(right_inner, text="🔮  Configuração da Previsão",
                     font=Fonts.H3, text_color=Colors.TEXT_PRIMARY).pack(
                         fill="x", pady=(0, Spacing.MD))

        self.horizon = LabeledOptionMenu(
            right_inner, label="Horizonte de Previsão",
            values=["Próximas 6 horas", "Próximas 12 horas",
                    "Próximas 24 horas", "Próximos 3 dias",
                    "Próxima semana"],
            default="Próximas 24 horas")
        self.horizon.pack(fill="x", pady=(0, Spacing.MD))

        self.confidence = LabeledEntry(
            right_inner, label="Nível de Confiança (%)",
            placeholder="95")
        self.confidence.pack(fill="x", pady=(0, Spacing.MD))
        self.confidence.set("95")

        self.target_var = LabeledOptionMenu(
            right_inner, label="Variável Alvo",
            values=["Velocidade do Vento", "Temperatura",
                    "Radiação Solar", "Todas"],
            default="Velocidade do Vento")
        self.target_var.pack(fill="x")

        # ── Prediction Results ────────────────────────────────────────────
        SectionHeader(scroll, title="Resultados da Previsão",
                      subtitle="Os gráficos e métricas aparecerão aqui após executar").pack(
                          fill="x", pady=(0, Spacing.MD))

        self.results_card = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD,
                                     corner_radius=Spacing.CORNER,
                                     border_width=1, border_color=Colors.BORDER,
                                     height=350)
        self.results_card.pack(fill="x", pady=(0, Spacing.XL))
        self.results_card.pack_propagate(False)

        # Placeholder
        self.results_placeholder = ctk.CTkFrame(self.results_card, fg_color="transparent")
        self.results_placeholder.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.results_placeholder, text="🤖", font=(Fonts.FAMILY, 48),
                     text_color=Colors.TEXT_DISABLED).pack()
        ctk.CTkLabel(self.results_placeholder,
                     text="Treine o modelo e execute uma previsão para ver os resultados",
                     font=Fonts.BODY, text_color=Colors.TEXT_DISABLED).pack(
                         pady=(Spacing.SM, 0))

        # ── Run Prediction ────────────────────────────────────────────────
        actions = ctk.CTkFrame(scroll, fg_color="transparent")
        actions.pack(fill="x", pady=(0, Spacing.MD))

        ActionButton(actions, text="Executar Previsão", icon="▶️",
                     color=Colors.ACCENT_VIOLET,
                     hover_color="#7c3aed",
                     command=self._run_forecast, width=220).pack(side="left")

        ActionButton(actions, text="Limpar Console", icon="🗑️",
                     color=Colors.BG_CARD_HOVER,
                     hover_color=Colors.DANGER,
                     command=lambda: (self.console.clear(), self.console.log("Console limpo.")),
                     width=160).pack(side="left", padx=(Spacing.SM, 0))

        self.forecast_status = StatusBadge(actions, status="idle",
                                            text="AGUARDANDO")
        self.forecast_status.pack(side="left", padx=(Spacing.MD, 0))

        # ── Console ───────────────────────────────────────────────────────
        SectionHeader(scroll, title="Log de Previsão").pack(
            fill="x", pady=(Spacing.MD, Spacing.SM))

        self.console = ConsoleBox(scroll, height=150)
        self.console.pack(fill="x")

    def _refresh_state(self):
        """Refresh prerequisite checks and target variable dropdown from app state."""
        if not self.app:
            return

        state = self.app.app_state
        all_ok = True

        # Check data
        if self.app.has_data("any"):
            self.check_labels["data"].configure(text="✅")
        else:
            self.check_labels["data"].configure(text="❌")
            all_ok = False

        # Check analysis
        if state.get("analysis_ran"):
            self.check_labels["analysis"].configure(text="✅")
        else:
            self.check_labels["analysis"].configure(text="❌")
            all_ok = False

        # Check model
        if state.get("model_trained"):
            self.check_labels["model"].configure(text="✅")
            model_type = state.get("model_type", "")
            self.model_badge.set_status("ready", f"TREINADO ({model_type})")
        else:
            self.check_labels["model"].configure(text="❌")
            all_ok = False
            self.model_badge.set_status("idle", "NÃO TREINADO")

        # Update banner
        if all_ok:
            self.prereq_icon.configure(text="✅")
            self.prereq_text.configure(
                text="Todos os pré-requisitos atendidos. Pronto para executar previsões.",
                text_color=Colors.ACCENT_EMERALD)
        else:
            self.prereq_icon.configure(text="ℹ️")
            self.prereq_text.configure(
                text="Pré-requisitos para previsão:",
                text_color=Colors.TEXT_MUTED)

        # Update target variable dropdown from analysis config
        if state.get("analysis_config"):
            analyzed_vars = state["analysis_config"].get("variables", [])
            if analyzed_vars:
                options = analyzed_vars + ["Todas"]
                self.target_var.option.configure(values=options)
                self.target_var.option.set(analyzed_vars[0])

    def _train_model(self):
        """Train model — validates prerequisites and provides feedback."""
        if not self.app:
            return

        state = self.app.app_state

        # ── Validation ────────────────────────────────────────────────────
        if not self.app.has_data("any"):
            self.console.log("━" * 50)
            self.console.log("❌ ERRO: Nenhum dado carregado.")
            self.console.log("   → Vá para a aba 'Dados' e carregue pelo menos um CSV.")
            self.console.log("━" * 50)
            self.model_badge.set_status("error", "SEM DADOS")
            return

        if not state.get("analysis_ran"):
            self.console.log("━" * 50)
            self.console.log("❌ ERRO: Análise estatística não executada.")
            self.console.log("   → Vá para a aba 'Análise' e execute a detecção de eventos primeiro.")
            self.console.log("   → O modelo precisa dos eventos detectados para aprender os padrões.")
            self.console.log("━" * 50)
            self.model_badge.set_status("error", "SEM ANÁLISE")
            return

        # Validate epochs
        try:
            epochs = int(self.epochs_entry.get())
            if epochs < 1 or epochs > 1000:
                raise ValueError
        except ValueError:
            self.console.log("❌ ERRO: Número de épocas deve ser entre 1 e 1000.")
            return

        model = self.model_select.get()

        # ── Training simulation ───────────────────────────────────────────
        self.model_badge.set_status("running", "TREINANDO...")
        self.console.log("━" * 50)
        self.console.log(f"⚙️ Iniciando treinamento do modelo: {model}")
        self.console.log(f"  Épocas configuradas: {epochs}")

        # Show data info
        total_records = self.app.get_total_records()
        self.console.log(f"  Registros disponíveis: {total_records:,}")

        config = state.get("analysis_config", {})
        variables = config.get("variables", [])
        self.console.log(f"  Variáveis de entrada: {', '.join(variables)}")

        if "LSTM" in model or "Ensemble" in model:
            self.console.log("  Arquitetura: LSTM (Long Short-Term Memory)")
            self.console.log("  Framework: TensorFlow/Keras")

        if "XGBoost" in model or "Ensemble" in model:
            self.console.log("  Arquitetura: XGBoost (Extreme Gradient Boosting)")
            self.console.log("  Framework: xgboost")

        self.console.log("")
        self.console.log("⏳ Motor de treinamento será implementado na Fase 3.")
        self.console.log("   → Depende da integração com TensorFlow/Keras e XGBoost.")
        self.console.log("   → Os scripts base (lstm_only.py, pv_forecasting.py) serão adaptados.")
        self.console.log("━" * 50)

        # Save model state
        model_name = model.split(" (")[0]  # "LSTM", "XGBoost", "Ensemble"
        state["model_trained"] = True
        state["model_type"] = model_name
        self.model_badge.set_status("warning", f"FASE 3 ({model_name})")
        self.check_labels["model"].configure(text="✅")

        # Update banner
        self.prereq_icon.configure(text="✅")
        self.prereq_text.configure(
            text="Todos os pré-requisitos atendidos. Pronto para executar previsões.",
            text_color=Colors.ACCENT_EMERALD)

        self.app.log(f"Modelo {model_name} configurado para treinamento — aguardando Fase 3")

    def _reset_model(self):
        """Reset model training state."""
        if not self.app:
            return

        self.app.app_state["model_trained"] = False
        self.app.app_state["model_type"] = None
        self.app.app_state["forecast_results"] = None
        self.model_badge.set_status("idle", "NÃO TREINADO")
        self.check_labels["model"].configure(text="❌")
        self.forecast_status.set_status("idle", "AGUARDANDO")

        self.console.log("🔄 Estado do modelo resetado.")
        self.app.log("Estado do modelo de previsão resetado")

        # Update banner
        self.prereq_icon.configure(text="ℹ️")
        self.prereq_text.configure(
            text="Pré-requisitos para previsão:",
            text_color=Colors.TEXT_MUTED)

    def _run_forecast(self):
        """Execute forecast — validates all prerequisites."""
        if not self.app:
            return

        state = self.app.app_state

        # ── Validation ────────────────────────────────────────────────────
        errors = []
        if not self.app.has_data("any"):
            errors.append("Nenhum dado carregado")
        if not state.get("analysis_ran"):
            errors.append("Análise estatística não executada")
        if not state.get("model_trained"):
            errors.append("Modelo não treinado")

        if errors:
            self.console.log("━" * 50)
            self.console.log("❌ Não é possível executar a previsão:")
            for err in errors:
                self.console.log(f"   → {err}")
            self.console.log("")
            self.console.log("💡 Complete todos os pré-requisitos na ordem:")
            self.console.log("   1. Carregar dados (aba 'Dados')")
            self.console.log("   2. Executar análise (aba 'Análise')")
            self.console.log("   3. Treinar modelo (botão acima)")
            self.console.log("━" * 50)
            self.forecast_status.set_status("error", "PRÉ-REQUISITOS")
            return

        # Validate confidence
        try:
            confidence_val = float(self.confidence.get())
            if not (50 <= confidence_val <= 99.9):
                raise ValueError
        except ValueError:
            self.console.log("❌ ERRO: Nível de confiança deve ser entre 50 e 99.9.")
            self.forecast_status.set_status("error", "CONFIANÇA INVÁLIDA")
            return

        # ── Execute forecast ──────────────────────────────────────────────
        horizon = self.horizon.get()
        target = self.target_var.get()
        model_type = state.get("model_type", "N/A")

        self.forecast_status.set_status("running", "EXECUTANDO...")
        self.console.log("━" * 50)
        self.console.log("▶️ Iniciando previsão de eventos extremos...")
        self.console.log(f"  🧠 Modelo: {model_type}")
        self.console.log(f"  ⏱️  Horizonte: {horizon}")
        self.console.log(f"  🎯 Variável alvo: {target}")
        self.console.log(f"  📊 Confiança: {confidence_val}%")

        # Time horizon parsing
        horizon_map = {
            "Próximas 6 horas": 6,
            "Próximas 12 horas": 12,
            "Próximas 24 horas": 24,
            "Próximos 3 dias": 72,
            "Próxima semana": 168,
        }
        hours = horizon_map.get(horizon, 24)
        self.console.log(f"  Janela de previsão: {hours} horas")

        self.console.log("")
        self.console.log("⏳ Motor de previsão será implementado na Fase 3.")
        self.console.log("   → Quando pronto, os gráficos de previsão aparecerão acima.")
        self.console.log("   → Incluirá: intervalo de confiança, alertas de eventos e probabilidades.")
        self.console.log("━" * 50)

        self.forecast_status.set_status("warning", "FASE 3 PENDENTE")

        self.app.log(f"Previsão configurada: {model_type} | {target} | {horizon} | {confidence_val}% confiança")
