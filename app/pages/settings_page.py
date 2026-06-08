"""
CLIMAIA – Settings Page
Application configuration, about info and data export options.
"""

import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from app.theme import Colors, Fonts, Spacing
from app.components import SectionHeader, ActionButton, LabeledOptionMenu, StatusBadge


class SettingsPage(ctk.CTkFrame):
    """Settings and about page."""

    def __init__(self, master, app_ref=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app_ref
        self._build_ui()
        self._restore_settings()

    def _build_ui(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                         scrollbar_button_color=Colors.BORDER,
                                         scrollbar_button_hover_color=Colors.BORDER_LIGHT)
        scroll.pack(fill="both", expand=True)

        # ── Header ────────────────────────────────────────────────────────
        ctk.CTkLabel(scroll, text="Configurações", font=Fonts.HERO,
                     text_color=Colors.TEXT_PRIMARY, anchor="w").pack(fill="x")
        ctk.CTkLabel(scroll, text="Preferências da aplicação e informações do projeto",
                     font=Fonts.BODY, text_color=Colors.TEXT_MUTED,
                     anchor="w").pack(fill="x", pady=(4, Spacing.XL))

        # ── Appearance ────────────────────────────────────────────────────
        SectionHeader(scroll, title="Aparência",
                      subtitle="Personalize a interface do CLIMAIA").pack(
                          fill="x", pady=(0, Spacing.MD))

        appear_card = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD,
                                    corner_radius=Spacing.CORNER,
                                    border_width=1, border_color=Colors.BORDER)
        appear_card.pack(fill="x", pady=(0, Spacing.XL))

        appear_inner = ctk.CTkFrame(appear_card, fg_color="transparent")
        appear_inner.pack(fill="both", padx=Spacing.CARD_PAD, pady=Spacing.CARD_PAD)

        self.theme_select = LabeledOptionMenu(
            appear_inner, label="Tema",
            values=["Escuro (Padrão)", "Claro", "Sistema"],
            default="Escuro (Padrão)",
            command=self._change_theme)
        self.theme_select.pack(fill="x", pady=(0, Spacing.MD))

        self.scale_select = LabeledOptionMenu(
            appear_inner, label="Escala da Interface",
            values=["80%", "90%", "100%", "110%", "120%"],
            default="100%",
            command=self._change_scale)
        self.scale_select.pack(fill="x")

        # ── Data Settings ─────────────────────────────────────────────────
        SectionHeader(scroll, title="Dados",
                      subtitle="Configurações de processamento de CSV").pack(
                          fill="x", pady=(0, Spacing.MD))

        data_card = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD,
                                  corner_radius=Spacing.CORNER,
                                  border_width=1, border_color=Colors.BORDER)
        data_card.pack(fill="x", pady=(0, Spacing.XL))

        data_inner = ctk.CTkFrame(data_card, fg_color="transparent")
        data_inner.pack(fill="both", padx=Spacing.CARD_PAD, pady=Spacing.CARD_PAD)

        self.date_col = LabeledOptionMenu(
            data_inner, label="Coluna de Data (padrão)",
            values=["Auto-detectar", "Date", "Datetime", "Timestamp",
                    "date", "datetime", "timestamp", "Data",
                    "data_hora", "data_hora_dt"],
            default="Auto-detectar",
            command=self._on_setting_change)
        self.date_col.pack(fill="x", pady=(0, Spacing.MD))

        self.separator = LabeledOptionMenu(
            data_inner, label="Separador CSV",
            values=["Auto-detectar", "Vírgula (,)", "Ponto e Vírgula (;)", "Tab"],
            default="Auto-detectar",
            command=self._on_setting_change)
        self.separator.pack(fill="x", pady=(0, Spacing.MD))

        self.encoding = LabeledOptionMenu(
            data_inner, label="Encoding",
            values=["UTF-8", "Latin-1 (ISO-8859-1)", "Windows-1252", "Auto-detectar"],
            default="UTF-8",
            command=self._on_setting_change)
        self.encoding.pack(fill="x", pady=(0, Spacing.MD))

        # Settings note
        ctk.CTkLabel(data_inner,
                     text="💡 Alterações serão aplicadas ao próximo carregamento de dados.",
                     font=Fonts.SMALL, text_color=Colors.TEXT_MUTED,
                     anchor="w").pack(fill="x")

        # ── Export ────────────────────────────────────────────────────────
        SectionHeader(scroll, title="Exportação",
                      subtitle="Opções de saída de dados e relatórios").pack(
                          fill="x", pady=(0, Spacing.MD))

        export_card = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD,
                                    corner_radius=Spacing.CORNER,
                                    border_width=1, border_color=Colors.BORDER)
        export_card.pack(fill="x", pady=(0, Spacing.XL))

        export_inner = ctk.CTkFrame(export_card, fg_color="transparent")
        export_inner.pack(fill="both", padx=Spacing.CARD_PAD, pady=Spacing.CARD_PAD)

        self.export_format = LabeledOptionMenu(
            export_inner, label="Formato de Exportação",
            values=["CSV", "Excel (.xlsx)", "JSON", "Parquet"],
            default="CSV",
            command=self._on_setting_change)
        self.export_format.pack(fill="x", pady=(0, Spacing.MD))

        # Data status summary
        self.export_status = ctk.CTkFrame(export_inner, fg_color="transparent")
        self.export_status.pack(fill="x", pady=(0, Spacing.MD))

        self.raw_export_status = ctk.CTkLabel(
            self.export_status, text="📄 Dados Brutos: Não carregados",
            font=Fonts.SMALL, text_color=Colors.TEXT_MUTED, anchor="w")
        self.raw_export_status.pack(fill="x", pady=1)

        self.treated_export_status = ctk.CTkLabel(
            self.export_status, text="✨ Dados Tratados: Não carregados",
            font=Fonts.SMALL, text_color=Colors.TEXT_MUTED, anchor="w")
        self.treated_export_status.pack(fill="x", pady=1)

        btn_row = ctk.CTkFrame(export_inner, fg_color="transparent")
        btn_row.pack(fill="x")

        ActionButton(btn_row, text="Exportar Dados Brutos", icon="📄",
                     color=Colors.PRIMARY, width=220,
                     command=lambda: self._export("raw")).pack(
                         side="left", padx=(0, Spacing.SM))

        ActionButton(btn_row, text="Exportar Dados Tratados", icon="✨",
                     color=Colors.SECONDARY, width=220,
                     command=lambda: self._export("treated")).pack(
                         side="left", padx=(0, Spacing.SM))

        ActionButton(btn_row, text="Exportar Ambos", icon="📦",
                     color=Colors.ACCENT_EMERALD, width=180,
                     command=lambda: self._export("both")).pack(side="left")

        # ── Reset Application ─────────────────────────────────────────────
        SectionHeader(scroll, title="Manutenção",
                      subtitle="Opções de reset e limpeza").pack(
                          fill="x", pady=(0, Spacing.MD))

        maint_card = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD,
                                   corner_radius=Spacing.CORNER,
                                   border_width=1, border_color=Colors.BORDER)
        maint_card.pack(fill="x", pady=(0, Spacing.XL))

        maint_inner = ctk.CTkFrame(maint_card, fg_color="transparent")
        maint_inner.pack(fill="both", padx=Spacing.CARD_PAD, pady=Spacing.CARD_PAD)

        ctk.CTkLabel(maint_inner,
                     text="⚠️ As ações abaixo irão limpar dados carregados e resultados.",
                     font=Fonts.SMALL, text_color=Colors.ACCENT_WARM,
                     anchor="w").pack(fill="x", pady=(0, Spacing.MD))

        reset_row = ctk.CTkFrame(maint_inner, fg_color="transparent")
        reset_row.pack(fill="x")

        ActionButton(reset_row, text="Limpar Dados", icon="🗑️",
                     color=Colors.BG_CARD_HOVER,
                     hover_color=Colors.DANGER,
                     command=self._clear_all_data, width=180).pack(
                         side="left", padx=(0, Spacing.SM))

        ActionButton(reset_row, text="Resetar Tudo", icon="⚠️",
                     color=Colors.DANGER,
                     hover_color="#b91c1c",
                     command=self._reset_all, width=180).pack(side="left")

        # ── About ─────────────────────────────────────────────────────────
        SectionHeader(scroll, title="Sobre o CLIMAIA").pack(
            fill="x", pady=(0, Spacing.MD))

        about_card = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD,
                                   corner_radius=Spacing.CORNER,
                                   border_width=1, border_color=Colors.BORDER)
        about_card.pack(fill="x")

        about_inner = ctk.CTkFrame(about_card, fg_color="transparent")
        about_inner.pack(fill="both", padx=Spacing.CARD_PAD, pady=Spacing.CARD_PAD)

        info_lines = [
            ("Versão", "1.0.0-alpha"),
            ("Desenvolvido por", "Victor Vieira Colombo"),
            ("Repositório", "github.com/VituColombo0/CLIMAIA"),
            ("Licença", "Privado"),
            ("Stack", "Python 3.12 • CustomTkinter • Pandas • NumPy • Matplotlib"),
            ("Modelos", "LSTM • XGBoost • EVT • Gumbel"),
        ]

        for label, value in info_lines:
            row = ctk.CTkFrame(about_inner, fg_color="transparent")
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(row, text=f"{label}:", font=Fonts.SMALL_BOLD,
                         text_color=Colors.TEXT_SECONDARY, width=160,
                         anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=value, font=Fonts.SMALL,
                         text_color=Colors.TEXT_PRIMARY, anchor="w").pack(
                             side="left")

    def _restore_settings(self):
        """Restore settings from app_state when page is loaded."""
        if not self.app:
            return

        state = self.app.app_state

        # Restore dropdowns from state
        if state.get("theme"):
            self.theme_select.set(state["theme"])
        if state.get("scale"):
            self.scale_select.set(state["scale"])
        if state.get("csv_separator"):
            self.separator.set(state["csv_separator"])
        if state.get("csv_encoding"):
            self.encoding.set(state["csv_encoding"])
        if state.get("csv_date_col"):
            self.date_col.set(state["csv_date_col"])
        if state.get("export_format"):
            self.export_format.set(state["export_format"])

        # Update export status
        self._update_export_status()

    def _on_setting_change(self, value=None):
        """Persist all current settings to app_state."""
        if not self.app:
            return

        self.app.app_state["csv_separator"] = self.separator.get()
        self.app.app_state["csv_encoding"] = self.encoding.get()
        self.app.app_state["csv_date_col"] = self.date_col.get()
        self.app.app_state["export_format"] = self.export_format.get()

    def _update_export_status(self):
        """Update the export status labels."""
        if not self.app:
            return

        raw_df = self.app.app_state.get("raw_df")
        treated_df = self.app.app_state.get("treated_df")

        if raw_df is not None:
            path = self.app.app_state.get("raw_path", "")
            name = os.path.basename(path) if path else "dados"
            self.raw_export_status.configure(
                text=f"📄 Dados Brutos: ✅ {name} ({len(raw_df):,} linhas)",
                text_color=Colors.ACCENT_EMERALD)
        else:
            self.raw_export_status.configure(
                text="📄 Dados Brutos: ❌ Não carregados",
                text_color=Colors.TEXT_MUTED)

        if treated_df is not None:
            path = self.app.app_state.get("treated_path", "")
            name = os.path.basename(path) if path else "dados"
            self.treated_export_status.configure(
                text=f"✨ Dados Tratados: ✅ {name} ({len(treated_df):,} linhas)",
                text_color=Colors.ACCENT_EMERALD)
        else:
            self.treated_export_status.configure(
                text="✨ Dados Tratados: ❌ Não carregados",
                text_color=Colors.TEXT_MUTED)

    def _change_theme(self, value):
        mapping = {
            "Escuro (Padrão)": "dark",
            "Claro": "light",
            "Sistema": "system",
        }
        ctk.set_appearance_mode(mapping.get(value, "dark"))
        if self.app:
            self.app.app_state["theme"] = value
            self.app.log(f"Tema alterado para: {value}")

    def _change_scale(self, value):
        scale_map = {
            "80%": 0.8, "90%": 0.9, "100%": 1.0,
            "110%": 1.1, "120%": 1.2,
        }
        ctk.set_widget_scaling(scale_map.get(value, 1.0))
        if self.app:
            self.app.app_state["scale"] = value
            self.app.log(f"Escala alterada para: {value}")

    def _export(self, dtype: str):
        """Export data using file save dialog with the selected format."""
        if not self.app:
            return

        state = self.app.app_state
        fmt = self.export_format.get()

        # Build list of DataFrames to export
        exports = []
        if dtype in ("raw", "both"):
            if state.get("raw_df") is not None:
                exports.append(("bruto", state["raw_df"]))
            else:
                messagebox.showwarning("Sem Dados",
                                       "Dados brutos não carregados. Carregue na aba 'Dados'.")
                if dtype == "raw":
                    return

        if dtype in ("treated", "both"):
            if state.get("treated_df") is not None:
                exports.append(("tratado", state["treated_df"]))
            else:
                messagebox.showwarning("Sem Dados",
                                       "Dados tratados não carregados. Carregue na aba 'Dados'.")
                if dtype == "treated":
                    return

        if not exports:
            messagebox.showwarning("Sem Dados",
                                   "Nenhum dado disponível para exportar.")
            return

        # File type mapping
        ext_map = {
            "CSV": (".csv", [("CSV", "*.csv")]),
            "Excel (.xlsx)": (".xlsx", [("Excel", "*.xlsx")]),
            "JSON": (".json", [("JSON", "*.json")]),
            "Parquet": (".parquet", [("Parquet", "*.parquet")]),
        }
        ext, ftypes = ext_map.get(fmt, (".csv", [("CSV", "*.csv")]))

        for label, df in exports:
            filepath = filedialog.asksaveasfilename(
                title=f"Exportar Dados {label.title()}",
                defaultextension=ext,
                filetypes=ftypes + [("Todos os arquivos", "*.*")],
                initialfile=f"CLIMAIA_dados_{label}{ext}")

            if not filepath:
                continue

            try:
                if fmt == "CSV":
                    df.to_csv(filepath, index=False)
                elif fmt == "Excel (.xlsx)":
                    df.to_excel(filepath, index=False, engine="openpyxl")
                elif fmt == "JSON":
                    df.to_json(filepath, orient="records", indent=2,
                               force_ascii=False)
                elif fmt == "Parquet":
                    df.to_parquet(filepath, index=False)

                self.app.log(f"Dados {label} exportados: {os.path.basename(filepath)} ({fmt})")
                messagebox.showinfo("Exportação Concluída",
                                    f"Dados {label} exportados com sucesso!\n\n{filepath}")

            except ImportError as e:
                missing = str(e)
                messagebox.showerror("Dependência Faltando",
                    f"Para exportar em {fmt}, instale a dependência:\n{missing}")
            except Exception as e:
                messagebox.showerror("Erro ao Exportar",
                                     f"Não foi possível exportar:\n{e}")

    def _clear_all_data(self):
        """Clear all loaded data but keep settings."""
        if not self.app:
            return

        confirm = messagebox.askyesno(
            "Confirmar Limpeza",
            "Deseja limpar todos os dados carregados?\n\n"
            "Isso irá remover os datasets bruto e tratado,\n"
            "além de todos os resultados de análise e previsão.\n\n"
            "As configurações serão mantidas.")

        if not confirm:
            return

        state = self.app.app_state
        state["raw_df"] = None
        state["treated_df"] = None
        state["raw_path"] = None
        state["treated_path"] = None
        state["raw_columns"] = []
        state["treated_columns"] = []
        state["analysis_ran"] = False
        state["analysis_results"] = None
        state["analysis_config"] = None
        state["comparison_ran"] = False
        state["comparison_results"] = None
        state["model_trained"] = False
        state["model_type"] = None
        state["forecast_results"] = None

        self._update_export_status()
        self.app.log("Todos os dados e resultados foram limpos")
        messagebox.showinfo("Dados Limpos", "Todos os dados foram removidos da memória.")

    def _reset_all(self):
        """Reset everything including settings."""
        if not self.app:
            return

        confirm = messagebox.askyesno(
            "⚠️ Resetar Tudo",
            "ATENÇÃO: Isso irá resetar TUDO:\n\n"
            "• Dados carregados\n"
            "• Resultados de análise\n"
            "• Modelo treinado\n"
            "• Configurações de tema e CSV\n\n"
            "Deseja continuar?")

        if not confirm:
            return

        # Clear all state
        state = self.app.app_state

        state["raw_df"] = None
        state["treated_df"] = None
        state["raw_path"] = None
        state["treated_path"] = None
        state["raw_columns"] = []
        state["treated_columns"] = []
        state["analysis_ran"] = False
        state["analysis_results"] = None
        state["analysis_config"] = None
        state["comparison_ran"] = False
        state["comparison_results"] = None
        state["model_trained"] = False
        state["model_type"] = None
        state["forecast_results"] = None

        # Reset settings
        state["csv_separator"] = "Auto-detectar"
        state["csv_encoding"] = "UTF-8"
        state["csv_date_col"] = "Auto-detectar"
        state["export_format"] = "CSV"
        state["theme"] = "Escuro (Padrão)"
        state["scale"] = "100%"

        # Apply visual resets
        ctk.set_appearance_mode("dark")
        ctk.set_widget_scaling(1.0)

        # Reset UI
        self.theme_select.set("Escuro (Padrão)")
        self.scale_select.set("100%")
        self.separator.set("Auto-detectar")
        self.encoding.set("UTF-8")
        self.date_col.set("Auto-detectar")
        self.export_format.set("CSV")

        self._update_export_status()
        self.app._log_messages.clear()
        self.app.log("Aplicação resetada para o estado inicial")
        messagebox.showinfo("Reset Completo", "Todas as configurações e dados foram resetados.")
