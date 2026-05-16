"""
CLIMAIA – Settings Page
Application configuration, about info and data export options.
"""

import customtkinter as ctk
from app.theme import Colors, Fonts, Spacing
from app.components import SectionHeader, ActionButton, LabeledOptionMenu, ConsoleBox


class SettingsPage(ctk.CTkFrame):
    """Settings and about page."""

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
                      subtitle="Configurações de processamento").pack(
                          fill="x", pady=(0, Spacing.MD))

        data_card = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD,
                                  corner_radius=Spacing.CORNER,
                                  border_width=1, border_color=Colors.BORDER)
        data_card.pack(fill="x", pady=(0, Spacing.XL))

        data_inner = ctk.CTkFrame(data_card, fg_color="transparent")
        data_inner.pack(fill="both", padx=Spacing.CARD_PAD, pady=Spacing.CARD_PAD)

        self.date_col = LabeledOptionMenu(
            data_inner, label="Coluna de Data (padrão)",
            values=["Date", "Datetime", "Timestamp", "date", "Auto-detectar"],
            default="Auto-detectar")
        self.date_col.pack(fill="x", pady=(0, Spacing.MD))

        self.separator = LabeledOptionMenu(
            data_inner, label="Separador CSV",
            values=["Vírgula (,)", "Ponto e Vírgula (;)", "Tab", "Auto-detectar"],
            default="Auto-detectar")
        self.separator.pack(fill="x", pady=(0, Spacing.MD))

        self.encoding = LabeledOptionMenu(
            data_inner, label="Encoding",
            values=["UTF-8", "Latin-1 (ISO-8859-1)", "Windows-1252", "Auto-detectar"],
            default="UTF-8")
        self.encoding.pack(fill="x")

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
            default="CSV")
        self.export_format.pack(fill="x", pady=(0, Spacing.MD))

        btn_row = ctk.CTkFrame(export_inner, fg_color="transparent")
        btn_row.pack(fill="x")

        ActionButton(btn_row, text="Exportar Dados Brutos", icon="📄",
                     color=Colors.PRIMARY, width=220,
                     command=lambda: self._export("raw")).pack(
                         side="left", padx=(0, Spacing.SM))

        ActionButton(btn_row, text="Exportar Dados Tratados", icon="✨",
                     color=Colors.SECONDARY, width=220,
                     command=lambda: self._export("treated")).pack(side="left")

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

    def _change_theme(self, value):
        mapping = {
            "Escuro (Padrão)": "dark",
            "Claro": "light",
            "Sistema": "system",
        }
        ctk.set_appearance_mode(mapping.get(value, "dark"))

    def _change_scale(self, value):
        scale_map = {
            "80%": 0.8, "90%": 0.9, "100%": 1.0,
            "110%": 1.1, "120%": 1.2,
        }
        ctk.set_widget_scaling(scale_map.get(value, 1.0))

    def _export(self, dtype):
        if self.app:
            self.app.log(f"Exportação de dados {dtype} ainda não implementada.")
