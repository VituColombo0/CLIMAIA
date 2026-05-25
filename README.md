# CLIMAIA

<div align="center">

### 🌩️ Climate AI Analysis

**Sistema de Inteligência Artificial para Previsão e Validação de Eventos Climáticos Extremos**

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2+-1e293b?style=flat-square)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?style=flat-square&logo=pandas&logoColor=white)
![Status](https://img.shields.io/badge/Status-Fase%201%20Conclu%C3%ADda-10b981?style=flat-square)

</div>

---

## 🌍 Visão Geral

**CLIMAIA** é um software desktop premium desenvolvido para prever, identificar e validar eventos climáticos extremos com base na análise comparativa de dados meteorológicos brutos e pré-processados (tratados).

O projeto combina **Deep Learning** (LSTM), **Machine Learning** (XGBoost) e **modelos estatísticos clássicos** (EVT, Gumbel, Z-Score) para avaliar séries temporais climáticas e detectar anomalias no tratamento de dados.

## 🎯 Principais Objetivos

1. **Previsão de Eventos Extremos:** Modelos preditivos para antecipar ocorrências climáticas críticas.
2. **Avaliação da Integridade dos Dados:** Validação do impacto de tratamentos de dados (interpolação/limpeza) comparando eventos extremos entre série bruta e tratada.
   - Os eventos são criados artificialmente pela interpolação?
   - Os eventos extremos reais são suprimidos durante o tratamento?
3. **Software Desktop Premium:** Aplicação com interface moderna, dark mode e componentes reutilizáveis para visualização profissional de resultados.

## 🏗️ Estrutura do Projeto

```
/CLIMAIA
│
├── /app                     # Interface Desktop (CustomTkinter)
│   ├── /pages               # Páginas do sistema
│   │   ├── dashboard.py     # Dashboard reativo com stats e console
│   │   ├── data_page.py     # Gestão de dados (upload/preview CSV)
│   │   ├── analysis_page.py # Análise de eventos extremos
│   │   ├── comparison_page.py # Comparação Bruto vs Tratado
│   │   ├── forecast_page.py # Previsão com IA (LSTM/XGBoost)
│   │   └── settings_page.py # Configurações e exportação
│   ├── components.py        # Componentes reutilizáveis (StatCard, ConsoleBox, etc.)
│   ├── theme.py             # Design System (Cores, Tipografia, Espaçamentos)
│   └── main_app.py          # Shell principal, estado centralizado e roteamento
│
├── /data                    # Base de dados (CSVs brutos e tratados)
├── /docs                    # Documentação adicional
├── /src                     # Scripts auxiliares
├── main.py                  # Entry point da aplicação
├── lstm_only.py             # Script base de Forecasting com LSTM
├── pv_forecasting.py        # Script base de Forecasting PV com XGBoost
├── requirements.txt         # Dependências do projeto
├── PROJECT_LOG.md           # Log técnico detalhado do desenvolvimento
└── README.md                # Este arquivo
```

## 🚀 Como Executar

```bash
# 1. Clone o repositório
git clone https://github.com/VituColombo0/CLIMAIA.git
cd CLIMAIA

# 2. Crie e ative o ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Certifique-se de ter o tkinter instalado
sudo apt install python3-tk   # Ubuntu/Debian

# 5. Execute
python main.py
```

## 🔬 Como Funciona

1. **Ingestão de Dados:** Carregue os CSVs brutos e tratados na aba "Dados".
2. **Detecção Estatística:** Configure o método (EVT, Gumbel, Z-Score, Percentil, IQR) na aba "Análise" para identificar eventos extremos.
3. **Comparação Analítica:** A aba "Comparação" audita as diferenças entre as detecções nos dados brutos vs tratados.
4. **Previsão com IA:** Treine modelos LSTM/XGBoost para prever eventos extremos futuros.

---

## 📅 Linha do Tempo do Projeto

```
                    CLIMAIA — Roadmap de Desenvolvimento
═══════════════════════════════════════════════════════════════════
```

### 📌 08/05/2026 — Planejamento e Estruturação Inicial
> **Fase 0 — Fundação**

- Definição da arquitetura e escopo do projeto
- Análise dos scripts base fornecidos (`lstm_only.py`, `pv_forecasting.py`)
- Criação do repositório GitHub, `README.md` e `PROJECT_LOG.md`
- Definição das 6 fases do projeto (Ingestão → Estatística → IA → Comparação → Software → Deploy)
- Escolha da stack: Python + CustomTkinter (Desktop), Pandas, NumPy, Matplotlib, TensorFlow/Keras, XGBoost

---

### 🎨 16/05/2026 — Interface Desktop Completa
> **Fase 1A — Construção da UI**

- **Design System** (`theme.py`): Paleta dark mode premium (Indigo/Cyan), tipografia Segoe UI escalada, espaçamentos padronizados
- **Componentes** (`components.py`): StatCard, NavItem, ActionButton, ConsoleBox, StatusBadge, LabeledEntry, LabeledOptionMenu
- **6 Páginas** construídas com layout profissional:
  - 🏠 Dashboard com cards de métricas e console
  - 📁 Gestão de Dados com upload duplo (bruto/tratado) e preview
  - 🔬 Análise com seleção de método estatístico e variáveis
  - 📊 Comparação com tabela de diagnóstico e área de gráficos
  - 🤖 Previsão IA com seleção de modelo e horizonte
  - ⚙️ Configurações com tema, escala e exportação
- **Shell Principal** (`main_app.py`): Sidebar com navegação, roteamento dinâmico de páginas
- Ambiente virtual configurado com todas as dependências

---

### ⚡ 25/05/2026 — Botões Funcionais e Estado Centralizado
> **Fase 1B — Lógica da Interface**

- **Estado centralizado** (`app_state`): Dados, análise, comparação, modelo e configurações compartilhados entre todas as abas
- **Sistema de log cross-page**: Mensagens persistem e são replayed no Dashboard
- **Dashboard reativo**: Stats, badges de status e console atualizam automaticamente ao navegar
- **Data Page inteligente**: Leitura de CSV respeita separator/encoding das Configurações. Restaura estado ao revisitar. Invalida análise/comparação ao trocar dados
- **Análise com detecção automática**: Variáveis numéricas do CSV detectadas automaticamente. Validação completa de todos os campos. Período auto-detecta range de datas
- **Comparação com pré-requisitos**: Checklist visual (✅/❌). Validação antes de executar. Exportação de relatório via file dialog
- **Previsão com fluxo completo**: Checklist de pré-requisitos, config de épocas, reset do modelo, dropdown dinâmico de variáveis, validação de confiança
- **Configurações persistentes**: Exportação funcional (CSV/Excel/JSON/Parquet). "Limpar Dados" e "Resetar Tudo" com confirmação. Log de alterações

---

### 🔮 Próximas Etapas

| Fase | Descrição | Status |
|------|-----------|--------|
| **Fase 2** | Motor estatístico (EVT, Gumbel, Z-Score, Percentil, IQR) | ⏳ Próximo |
| **Fase 3** | Modelo de IA (LSTM + XGBoost) e treinamento | 📋 Planejado |
| **Fase 4** | Comparador analítico Bruto vs Tratado | 📋 Planejado |
| **Fase 5** | Gráficos matplotlib integrados na interface | 📋 Planejado |
| **Fase 6** | Automação, alertas e deploy | 📋 Planejado |

---

## 💡 Status Atual

```
Fase 1 (UI + Botões Funcionais): ██████████████████████████████ 100% ✅
Fase 2 (Motor Estatístico):      ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0% ⏳
Fase 3 (Modelo IA):              ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0% 📋
```

> **Aguardando:** Input dos arquivos CSV para iniciar a Fase 2 (implementação do motor estatístico e gráficos).

Consulte o arquivo `PROJECT_LOG.md` para o histórico técnico detalhado.

---

## 👤 Autor

**Victor Vieira Colombo**  
Repositório: [github.com/VituColombo0/CLIMAIA](https://github.com/VituColombo0/CLIMAIA)  
Licença: Privado
