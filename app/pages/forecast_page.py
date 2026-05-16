"""
CLIMAIA – Forecast Page
AI-powered prediction interface for extreme climate events.
"""

import customtkinter as ctk
from app.theme import Colors, Fonts, Spacing
from app.components import (SectionHeader, ActionButton, LabeledEntry,
                             LabeledOptionMenu, ConsoleBox, StatusBadge)


class ForecastPage(ctk.CTkFrame):
    """Forecasting / Prediction page."""

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
        ctk.CTkLabel(scroll, text="Previsão com IA", font=Fonts.HERO,
                     text_color=Colors.TEXT_PRIMARY, anchor="w").pack(
                         fill="x")
        ctk.CTkLabel(scroll,
                     text="Utilize os modelos treinados para prever eventos climáticos extremos",
                     font=Fonts.BODY, text_color=Colors.TEXT_MUTED,
                     anchor="w").pack(fill="x", pady=(4, Spacing.XL))

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

        self.model_status_frame = ctk.CTkFrame(left_inner, fg_color="transparent")
        self.model_status_frame.pack(fill="x", pady=(0, Spacing.MD))

        ctk.CTkLabel(self.model_status_frame, text="Status:",
                     font=Fonts.SMALL, text_color=Colors.TEXT_SECONDARY).pack(
                         side="left")
        self.model_badge = StatusBadge(self.model_status_frame, status="idle",
                                        text="NÃO TREINADO")
        self.model_badge.pack(side="left", padx=(Spacing.SM, 0))

        # Training button
        ActionButton(left_inner, text="Treinar Modelo", icon="⚙️",
                     color=Colors.ACCENT_WARM,
                     hover_color="#d97706",
                     command=self._train_model, width=200).pack(anchor="w")

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

        results_card = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD,
                                     corner_radius=Spacing.CORNER,
                                     border_width=1, border_color=Colors.BORDER,
                                     height=350)
        results_card.pack(fill="x", pady=(0, Spacing.XL))
        results_card.pack_propagate(False)

        # Placeholder
        placeholder = ctk.CTkFrame(results_card, fg_color="transparent")
        placeholder.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(placeholder, text="🤖", font=(Fonts.FAMILY, 48),
                     text_color=Colors.TEXT_DISABLED).pack()
        ctk.CTkLabel(placeholder,
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

        self.forecast_status = StatusBadge(actions, status="idle",
                                            text="AGUARDANDO")
        self.forecast_status.pack(side="left", padx=(Spacing.MD, 0))

        # ── Console ───────────────────────────────────────────────────────
        SectionHeader(scroll, title="Log de Previsão").pack(
            fill="x", pady=(Spacing.MD, Spacing.SM))

        self.console = ConsoleBox(scroll, height=150)
        self.console.pack(fill="x")

    def _train_model(self):
        model = self.model_select.get()
        self.console.log(f"Tentando treinar modelo: {model}")
        self.console.log("⏳ Motor de treinamento ainda não implementado.")
        self.console.log("   Será desenvolvido após a integração dos dados reais.")
        self.model_badge.set_status("warning", "PENDENTE")

    def _run_forecast(self):
        horizon = self.horizon.get()
        target = self.target_var.get()
        confidence = self.confidence.get()

        self.console.log(f"Configuração da previsão:")
        self.console.log(f"  Modelo: {self.model_select.get()}")
        self.console.log(f"  Horizonte: {horizon}")
        self.console.log(f"  Variável: {target}")
        self.console.log(f"  Confiança: {confidence}%")
        self.console.log("")
        self.console.log("⏳ Motor de previsão ainda não implementado.")
        self.forecast_status.set_status("warning", "NÃO IMPLEMENTADO")
