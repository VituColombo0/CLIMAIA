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

### Para Usuários de Windows (Mais Fácil)

Se você baixou este código no Windows e quer apenas abrir o software para testar:
1. Tenha o **Python** instalado na sua máquina (certifique-se de marcar a opção "Add Python to PATH" durante a instalação do Python).
2. Dê um duplo clique no arquivo **`run_windows.bat`**.
3. O script irá baixar as bibliotecas automaticamente, criar o ambiente virtual e abrir a interface do sistema.

### Para Desenvolvedores (Linux/Mac/Terminal)

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

- Definição da arquitetura e escopo do projeto.
- Análise dos scripts base fornecidos (`lstm_only.py`, `pv_forecasting.py`).
- Criação do repositório GitHub, `README.md` e `PROJECT_LOG.md`.
- Definição das fases do projeto (Ingestão → Estatística → IA → Comparação → Software → Deploy).

---

### 🎨 16/05/2026 — Interface Desktop Completa
> **Fase 1A — Construção da UI**

- **Design System** (`theme.py`): Paleta dark mode premium, tipografia e espaçamentos padronizados.
- **Componentes** (`components.py`): StatCards, ActionButtons, ConsoleBox, StatusBadges reativos.
- **Estruturação de Telas**: 6 abas principais integradas no painel lateral.

---

### ⚡ 25/05/2026 — Lógica Operacional e Motores de IA / Estatística
> **Fases 1B a 5 — Lógica, IA e Visualização**

- **Estado Centralizado** (`app_state`): Gerenciamento síncrono e integrado de fluxos entre páginas.
- **Motor Estatístico Real** (`src/statistical/evt.py`): Detecção real de eventos por EVT (Gumbel), Z-Score, IQR e Percentil.
- **Gráficos com Matplotlib**: Integração de gráficos reativos nas abas de Análise, Comparação e Previsão.
- **Motor de Previsão por IA** (`src/models/forecaster.py`):
  - Modelagem real com **LSTM**, **XGBoost** e **Ensemble** (LSTM + XGBoost).
  - Treinamento assíncrono em segundo plano (background threading) com logs em tempo real na interface gráfica para evitar congelamentos.
  - Previsão recursiva multi-step com cálculo dinâmico de bandas de incerteza (intervalos de confiança).
- **Validação de Prerrequisitos**: Checklist dinâmico com feedbacks visuais na UI.

---

## 💡 Status Atual

```text
Fase 1 (Interface e Lógica de Fluxo):  ██████████████████████████████ 100% ✅
Fase 2 (Motor Estatístico de Eventos): ██████████████████████████████ 100% ✅
Fase 3 (Motor de Previsão LSTM/XGBoost):██████████████████████████████ 100% ✅
Fase 4 (Comparador Bruto vs Tratado):  ██████████████████████████████ 100% ✅
Fase 5 (Visualização Matplotlib):      ██████████████████████████████ 100% ✅
Fase 6 (Ajustes Finais e Validação):   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0% ⏳
```

Consulte o arquivo `PROJECT_LOG.md` para o histórico técnico detalhado do desenvolvimento.


---

## 🪟 Executável para Windows (.exe)

O software já está preparado para ser compilado como um aplicativo nativo do Windows.

Para gerar o arquivo `.exe` contendo toda a interface e os modelos de IA embutidos, basta seguir os passos em um computador com **Windows**:
1. Tenha o **Python** instalado na sua máquina Windows.
2. Abra a pasta do projeto.
3. Dê dois cliques no arquivo `build_windows.bat`.

O script irá automaticamente instalar as dependências e empacotar o projeto. Ao final, o seu executável estará disponível dentro da pasta `dist/` com o nome `CLIMAIA.exe`.

---

## 👤 Autor

**Victor Vieira Colombo**  
Repositório: [github.com/VituColombo0/CLIMAIA](https://github.com/VituColombo0/CLIMAIA)  
Licença: Privado

