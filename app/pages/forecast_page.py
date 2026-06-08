import threading
import os
import json
import pickle
import numpy as np
import pandas as pd
import customtkinter as ctk
from datetime import datetime
from app.theme import Colors, Fonts, Spacing
from app.components import (SectionHeader, ActionButton, LabeledEntry,
                             LabeledOptionMenu, ConsoleBox, StatusBadge)
from src.models.forecaster import ClimaiaForecaster
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure



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

        # Determine available models based on TensorFlow availability
        from src.models.forecaster import is_tensorflow_available
        if is_tensorflow_available():
            model_options = ["LSTM (Redes Neurais)", "XGBoost (Gradient Boosting)",
                             "Ensemble (LSTM + XGBoost)"]
            default_model = "LSTM (Redes Neurais)"
        else:
            model_options = ["XGBoost (Gradient Boosting)"]
            default_model = "XGBoost (Gradient Boosting)"

        self.model_select = LabeledOptionMenu(
            left_inner, label="Modelo",
            values=model_options,
            default=default_model)
        self.model_select.pack(fill="x", pady=(0, Spacing.MD))

        # Show TF warning if unavailable
        if not is_tensorflow_available():
            tf_warn = ctk.CTkLabel(
                left_inner,
                text="⚠️ TensorFlow indisponível — apenas XGBoost disponível",
                font=Fonts.TINY, text_color=Colors.ACCENT_WARM, anchor="w")
            tf_warn.pack(fill="x", pady=(0, Spacing.SM))

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

        # Load pre-trained model button
        btn_row_load = ctk.CTkFrame(left_inner, fg_color="transparent")
        btn_row_load.pack(fill="x", pady=(Spacing.SM, 0))

        ActionButton(btn_row_load, text="Carregar Modelo Treinado", icon="📦",
                     color=Colors.ACCENT_EMERALD,
                     hover_color="#059669",
                     command=self._load_pretrained_model, width=260).pack(
                         side="left")

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
        """Train model — validates prerequisites and runs training in a background thread."""
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
        model_name = model.split(" (")[0]  # "LSTM", "XGBoost", "Ensemble"

        self.model_badge.set_status("running", "TREINANDO...")
        self.console.log("━" * 50)
        self.console.log(f"⚙️ Iniciando treinamento do modelo: {model_name}")
        self.console.log(f"  Épocas configuradas: {epochs}")

        # Choose DataFrame (Treated preferred)
        df = state.get("treated_df") if state.get("treated_df") is not None else state.get("raw_df")
        target = self.target_var.get()
        
        # Get variable list
        config = state.get("analysis_config", {})
        variables = config.get("variables", [])
        
        if target == "Todas":
            target = variables[0] if variables else df.columns[1]  # Fallback

        # Check date column
        date_col = state.get("csv_date_col", "Auto-detectar")
        if date_col == "Auto-detectar":
            possible = [c for c in df.columns if any(x in c.lower() for x in ["date", "time", "timestamp", "data_hora", "data"])]
            date_col = possible[0] if possible else None

        # Start background training thread
        threading.Thread(
            target=self._run_training_thread,
            args=(df, target, date_col, model_name, epochs),
            daemon=True
        ).start()

    def _run_training_thread(self, df, target, date_col, model_name, epochs):
        """Background thread execution for training."""
        state = self.app.app_state
        try:
            forecaster = ClimaiaForecaster(model_type=model_name, epochs=epochs)
            
            # Simple wrapper to write logs to our console box safely from thread
            def log_fn(msg):
                self.app.after(0, lambda: self.console.log(msg))

            forecaster.train(df, target, date_col, log_fn)

            # Update UI on main thread upon success
            def on_success():
                state["model_trained"] = True
                state["model_type"] = model_name
                state["forecaster"] = forecaster
                state["forecast_target"] = target
                state["forecast_date_col"] = date_col
                
                self.model_badge.set_status("ready", f"TREINADO ({model_name})")
                self.check_labels["model"].configure(text="✅")
                self.console.log(f"\n🎉 Modelo {model_name} treinado com sucesso para prever '{target}'!")
                self.console.log("━" * 50)
                
                # Refresh page state
                self._refresh_state()

            self.app.after(0, on_success)

        except Exception as e:
            def on_failure():
                self.model_badge.set_status("error", "FALHA")
                self.console.log(f"\n❌ ERRO durante o treinamento: {e}")
                self.console.log("━" * 50)
            self.app.after(0, on_failure)

    def _reset_model(self):
        """Reset model training state."""
        if not self.app:
            return

        self.app.app_state["model_trained"] = False
        self.app.app_state["model_type"] = None
        self.app.app_state["forecaster"] = None
        self.app.app_state["forecast_target"] = None
        self.app.app_state["forecast_results"] = None
        
        self.model_badge.set_status("idle", "NÃO TREINADO")
        self.check_labels["model"].configure(text="❌")
        self.forecast_status.set_status("idle", "AGUARDANDO")

        # Restore results card placeholder
        for widget in self.results_card.winfo_children():
            widget.destroy()
            
        self.results_placeholder = ctk.CTkFrame(self.results_card, fg_color="transparent")
        self.results_placeholder.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(self.results_placeholder, text="🤖", font=(Fonts.FAMILY, 48),
                     text_color=Colors.TEXT_DISABLED).pack()
        ctk.CTkLabel(self.results_placeholder,
                     text="Treine o modelo e execute uma previsão para ver os resultados",
                     font=Fonts.BODY, text_color=Colors.TEXT_DISABLED).pack(pady=(Spacing.SM, 0))

        self.console.log("🔄 Estado do modelo resetado.")
        self.app.log("Estado do modelo de previsão resetado")

        # Update banner
        self.prereq_icon.configure(text="ℹ️")
        self.prereq_text.configure(
            text="Pré-requisitos para previsão:",
            text_color=Colors.TEXT_MUTED)

    def _run_forecast(self):
        """Execute forecast — validates all prerequisites and plots prediction."""
        if not self.app:
            return

        state = self.app.app_state

        # ── Validation ────────────────────────────────────────────────────
        errors = []
        if not self.app.has_data("any"):
            errors.append("Nenhum dado carregado")
        if not state.get("analysis_ran"):
            errors.append("Análise estatística não executada")
        if not state.get("model_trained") or "forecaster" not in state:
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
        
        # Determine current dataset
        df = state.get("treated_df") if state.get("treated_df") is not None else state.get("raw_df")
        
        # Dynamic target selection for pre-trained models
        ui_target = self.target_var.get()
        pretrained = state.get("pretrained_models")
        
        if pretrained and ui_target in pretrained:
            pm = pretrained[ui_target]
            from src.models.forecaster import ClimaiaForecaster
            forecaster = ClimaiaForecaster(model_type="XGBoost", epochs=0)
            forecaster.xgb_model = pm['xgb']
            forecaster.lstm_model = pm.get('lstm')
            forecaster.scaler_X = pm['scaler_X']
            forecaster.scaler_y = pm['scaler_y']
            forecaster.feature_cols = pm['config']['feature_cols']
            forecaster.steps_in_day = pm['config'].get('steps_per_day', 288)
            state["forecaster"] = forecaster
            state["forecast_target"] = ui_target
            target = ui_target
        else:
            target = state.get("forecast_target")
            forecaster = state.get("forecaster")

        model_type = state.get("model_type", "N/A")
        date_col = state.get("forecast_date_col")
        
        # Fallback for date_col if missing
        if not date_col or date_col == "Auto-detectar":
            if df is not None:
                possible = [c for c in df.columns if any(x in c.lower() for x in ["date", "time", "timestamp", "data_hora", "data"])]
                date_col = possible[0] if possible else None

        self.forecast_status.set_status("running", "EXECUTANDO...")
        self.console.log("━" * 50)
        self.console.log("▶️ Iniciando previsão de eventos extremos...")
        self.console.log(f"  🧠 Modelo: {model_type}")
        self.console.log(f"  Target: {target}")
        self.console.log(f"  ⏱️  Horizonte: {horizon}")
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

        try:
            # Execute prediction
            pred_df = forecaster.predict(df, target, date_col, hours, confidence_val)
            state["forecast_results"] = pred_df

            # Output stats
            mean_pred = pred_df['Prediction'].mean()
            max_pred = pred_df['Prediction'].max()
            self.console.log(f"\n📊 Previsão gerada com sucesso:")
            self.console.log(f"  - Pontos previstos: {len(pred_df)}")
            self.console.log(f"  - Valor médio previsto: {mean_pred:.2f}")
            self.console.log(f"  - Valor máximo previsto: {max_pred:.2f}")
            
            # Plot the prediction
            self._plot_predictions(df, target, date_col, pred_df)
            
            self.forecast_status.set_status("ready", "CONCLUÍDA")
            self.console.log("\n🎉 Previsão concluída! O gráfico de projeção foi renderizado acima.")
            self.console.log("━" * 50)

        except Exception as e:
            self.console.log(f"\n❌ ERRO durante a previsão: {e}")
            self.console.log("━" * 50)
            self.forecast_status.set_status("error", "FALHA")

        self.app.log(f"Previsão executada: {model_type} | {target} | {horizon} | {confidence_val}% confiança")

    def _plot_predictions(self, historical_df, target, date_col, pred_df):
        """Render prediction line chart with confidence bands in self.results_card."""
        for widget in self.results_card.winfo_children():
            widget.destroy()

        fig = Figure(figsize=(7, 3.2), facecolor=Colors.BG_CARD)
        ax = fig.add_subplot(111)
        ax.set_facecolor(Colors.BG_CARD)

        # Plot historical data (last 50 points for context)
        hist_size = min(50, len(historical_df))
        hist_slice = historical_df.iloc[-hist_size:].copy()
        
        # Prepare historical index
        if date_col and date_col in hist_slice.columns:
            hist_x = pd.to_datetime(hist_slice[date_col])
        else:
            hist_x = np.arange(-hist_size, 0)
            
        hist_y = hist_slice[target].values

        # Prepare forecast index
        if date_col and date_col in historical_df.columns:
            try:
                pred_x = pd.to_datetime(pred_df['Date'])
            except Exception:
                pred_x = np.arange(0, len(pred_df))
        else:
            pred_x = np.arange(0, len(pred_df))

        # Helper to convert HEX colors to RGB
        def hex_to_rgb(hex_str):
            h = hex_str.lstrip('#')
            return tuple(int(h[i:i+2], 16)/255.0 for i in (0, 2, 4))

        color_hist = hex_to_rgb(Colors.TEXT_MUTED)
        color_pred = hex_to_rgb(Colors.ACCENT_VIOLET)
        
        # Plot lines
        ax.plot(hist_x, hist_y, color=color_hist, label='Histórico', linewidth=1.5, alpha=0.8)
        ax.plot(pred_x, pred_df['Prediction'].values, color=color_pred, label='Previsão (IA)', linewidth=2.0)
        
        # Plot confidence intervals
        ax.fill_between(pred_x, pred_df['Lower'].values, pred_df['Upper'].values, 
                        color=color_pred, alpha=0.15, label='Intervalo de Confiança')

        ax.set_title(f"Projeção Temporal de {target}", color=Colors.TEXT_PRIMARY, fontsize=10, pad=8)
        ax.tick_params(colors=Colors.TEXT_MUTED, labelsize=8)
        ax.grid(True, color=Colors.BORDER, linestyle='--', alpha=0.3)
        
        # Format labels nicely if they are datetimes
        if date_col and date_col in historical_df.columns:
            fig.autofmt_xdate()
            
        for spine in ax.spines.values():
            spine.set_color(Colors.BORDER)
            spine.set_alpha(0.5)

        leg = ax.legend(facecolor=Colors.BG_DARKEST, edgecolor=Colors.BORDER, labelcolor=Colors.TEXT_SECONDARY, fontsize=8)
        leg.get_frame().set_alpha(0.8)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.results_card)
        canvas.draw()
        canvas.get_tkwidget().pack(fill="both", expand=True, padx=Spacing.MD, pady=Spacing.MD)

    def _load_pretrained_model(self):
        """Load a pre-trained model from data/models_trained/ directory."""
        if not self.app:
            return

        import sys
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
        models_dir = os.path.join(base_path, "data", "models_trained")

        if not os.path.isdir(models_dir):
            self.console.log("━" * 50)
            self.console.log("❌ Pasta de modelos não encontrada.")
            self.console.log(f"   Esperado: {models_dir}")
            self.console.log("   → Execute train_model.py primeiro para gerar os modelos.")
            self.console.log("━" * 50)
            return

        # Detect available trained models
        config_files = sorted([f for f in os.listdir(models_dir) if f.startswith('config_') and f.endswith('.json')])

        if not config_files:
            self.console.log("❌ Nenhum modelo treinado encontrado na pasta.")
            return

        # Extract variable names
        available_vars = []
        for cf in config_files:
            var_name = cf.replace('config_', '').replace('.json', '')
            xgb_path = os.path.join(models_dir, f"xgboost_{var_name}.pkl")
            if os.path.exists(xgb_path):
                available_vars.append(var_name)

        if not available_vars:
            self.console.log("❌ Nenhum modelo completo encontrado (faltam arquivos .pkl).")
            return

        self.console.log("━" * 50)
        self.console.log("📦 Modelos pré-treinados encontrados:")

        loaded_models = {}
        for var_name in available_vars:
            try:
                # Load config
                config_path = os.path.join(models_dir, f"config_{var_name}.json")
                with open(config_path, 'r') as f:
                    config = json.load(f)

                # Load XGBoost
                xgb_path = os.path.join(models_dir, f"xgboost_{var_name}.pkl")
                with open(xgb_path, 'rb') as f:
                    xgb_model = pickle.load(f)

                # Load scalers
                scalers_path = os.path.join(models_dir, f"scalers_{var_name}.pkl")
                with open(scalers_path, 'rb') as f:
                    scalers = pickle.load(f)

                # Load LSTM (optional — requires TensorFlow)
                lstm_model = None
                lstm_path = os.path.join(models_dir, f"lstm_{var_name}.keras")
                if os.path.exists(lstm_path):
                    try:
                        from src.models.forecaster import is_tensorflow_available
                        if is_tensorflow_available():
                            from tensorflow.keras.models import load_model
                            lstm_model = load_model(lstm_path)
                        else:
                            self.console.log(f"    ⚠️ TensorFlow indisponível — LSTM de '{var_name}' ignorado (XGBoost será usado).")
                    except Exception:
                        pass

                loaded_models[var_name] = {
                    'config': config,
                    'xgb': xgb_model,
                    'lstm': lstm_model,
                    'scaler_X': scalers['scaler_X'],
                    'scaler_y': scalers['scaler_y'],
                }

                trained_at = config.get('trained_at', 'N/A')[:19]
                has_lstm = '✅' if lstm_model else '❌'
                self.console.log(f"  ✅ {var_name}: XGBoost ✅ | LSTM {has_lstm} | Treinado em {trained_at}")

            except Exception as e:
                self.console.log(f"  ⚠️ {var_name}: erro ao carregar — {e}")

        if not loaded_models:
            self.console.log("❌ Não foi possível carregar nenhum modelo.")
            return

        # Store in app state
        state = self.app.app_state
        state["pretrained_models"] = loaded_models
        state["model_trained"] = True
        state["model_type"] = "Pré-treinado"

        # Create a wrapper forecaster for the first variable
        first_var = available_vars[0]
        forecaster = ClimaiaForecaster(model_type="XGBoost", epochs=0)
        forecaster.xgb_model = loaded_models[first_var]['xgb']
        forecaster.lstm_model = loaded_models[first_var].get('lstm')
        forecaster.scaler_X = loaded_models[first_var]['scaler_X']
        forecaster.scaler_y = loaded_models[first_var]['scaler_y']
        forecaster.feature_cols = loaded_models[first_var]['config']['feature_cols']
        forecaster.steps_in_day = loaded_models[first_var]['config'].get('steps_per_day', 288)
        state["forecaster"] = forecaster
        state["forecast_target"] = first_var

        # Update UI
        self.model_badge.set_status("ready", f"PRÉ-TREINADO ({len(loaded_models)} vars)")
        self.check_labels["model"].configure(text="✅")

        # Update target variable dropdown with available vars
        var_options = available_vars + ["Todas"]
        self.target_var.option.configure(values=var_options)
        self.target_var.option.set(first_var)

        # Skip analysis prerequisite for pre-trained models
        self.check_labels["analysis"].configure(text="✅")
        state["analysis_ran"] = True

        self.console.log(f"\n🎉 {len(loaded_models)} modelo(s) carregado(s) com sucesso!")
        self.console.log("   Agora você pode executar previsões diretamente.")
        self.console.log("━" * 50)

        self.app.log(f"Modelos pré-treinados carregados: {', '.join(available_vars)}")

