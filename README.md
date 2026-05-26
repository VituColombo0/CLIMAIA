# CLIMAIA

<div align="center">

### 🌩️ Climate AI Analysis

**Sistema de Inteligência Artificial para Previsão e Validação de Eventos Climáticos Extremos**

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2+-1e293b?style=flat-square)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?style=flat-square&logo=pandas&logoColor=white)
![Status](https://img.shields.io/badge/Status-Conclu%C3%ADdo-10b981?style=flat-square)

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

---

## 🚀 Como Executar e Testar

Siga as instruções abaixo de acordo com o seu sistema operacional. O sistema configurará as bibliotecas automaticamente.

### 🪟 Windows (Método Recomendado)

Se você baixou este código no Windows, você pode rodar o sistema diretamente ou gerar o seu executável `.exe` final.

1. Baixe e instale o **Python** (certifique-se de marcar a opção "Add Python to PATH" durante a instalação).
2. Para **Apenas Testar/Rodar** a interface:
   - Dê um duplo clique no arquivo **`run_windows.bat`**. 
   - Ele criará o ambiente virtual sozinho, instalará as dependências e abrirá a interface na tela.
3. Para **Gerar o Executável (.exe)** final:
   - Dê um duplo clique no arquivo **`build_windows.bat`**.
   - Aguarde o processo terminar. O seu aplicativo final estará dentro da pasta `dist/` com o nome `CLIMAIA.exe`.

### 🐧 Linux / Mac (Terminal)

Para rodar nativamente em ambientes Linux ou macOS:

```bash
# 1. Clone o repositório e acesse a pasta
git clone https://github.com/VituColombo0/CLIMAIA.git
cd CLIMAIA

# 2. (Apenas Ubuntu/Debian) Instale o pacote tkinter do sistema
sudo apt install python3-tk

# 3. Crie e ative o ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 4. Instale as dependências
pip install -r requirements.txt

# 5. Execute o software
python main.py
```

---

## 🔬 Como Funciona

1. **Ingestão de Dados:** Carregue os CSVs brutos e tratados na aba "Dados".
2. **Detecção Estatística:** Configure o método (EVT, Gumbel, Z-Score, Percentil, IQR) na aba "Análise" para identificar eventos extremos.
3. **Comparação Analítica:** A aba "Comparação" audita as diferenças entre as detecções nos dados brutos vs tratados.
4. **Previsão com IA:** Treine modelos LSTM/XGBoost para prever eventos extremos futuros.

---

## 📅 Linha do Tempo do Projeto (Cronograma)

```text
                    CLIMAIA — Roadmap de Desenvolvimento
═══════════════════════════════════════════════════════════════════
```

### 📌 05/05/2026 a 08/05/2026 — Planejamento e Estruturação
- Definição da arquitetura e escopo do projeto.
- Análise de viabilidade matemática dos modelos (EVT vs Gumbel).
- Estudo dos scripts base fornecidos (`lstm_only.py`, `pv_forecasting.py`).
- Criação do repositório, documentação inicial e definição da stack tecnológica.

### 🎨 10/05/2026 a 12/05/2026 — Arquitetura de Interface (Fase 1A)
- Pesquisa de referências visuais (Dark Mode, UI Premium, Dashboard).
- Implementação do **Design System** (`theme.py`) e componentes reaproveitáveis (StatCards, Botões Animados).
- Criação das 6 abas principais do sistema integradas a um menu lateral.

### 🧠 14/05/2026 a 16/05/2026 — Lógica de Estado e Matemática
- Desenvolvimento do **Estado Centralizado** (Single Source of Truth) para sincronizar dados entre as telas.
- Implementação dos algoritmos estatísticos puros (`extreme_detection.py`), validando a sensibilidade do Z-Score e do Range Interquartil (IQR).

### ⚙️ 19/05/2026 a 21/05/2026 — Motores de Comparação e IA
- Criação do "Motor Analítico" para gerar o laudo de discrepância (Bruto vs Tratado).
- Modelagem preditiva com Redes Neurais (**LSTM**) e **XGBoost** (`forecaster.py`).
- Implementação de sub-processos (threading) para evitar que a interface travasse durante o treinamento da Inteligência Artificial.

### 📊 23/05/2026 a 25/05/2026 — Visualização de Dados e Refinamentos
- Integração da biblioteca Matplotlib no framework gráfico para plotagem interativa.
- Cálculos de limite de confiança e renderização visual das bandas de incerteza da previsão (sombreamento nos gráficos).
- Testes exaustivos de Experiência do Usuário (UX): inserção de validações de pré-requisitos e painéis de aviso amigáveis.

### 🚀 26/05/2026 — Empacotamento e Entrega (Deploy)
- Criação dos scripts automatizados (`.bat`) para uso facilitado por leigos no Windows.
- Auditoria final de código e refatoração do `.spec` para o PyInstaller garantir a compatibilidade cruzada das bibliotecas pesadas.
- Sistema 100% testado, finalizado e com código-fonte empurrado para produção.

---

## 💡 Status Final

```text
Fase 1 (Interface e UX Design):        ██████████████████████████████ 100% ✅
Fase 2 (Motor Estatístico de Eventos): ██████████████████████████████ 100% ✅
Fase 3 (Modelagem LSTM/XGBoost):       ██████████████████████████████ 100% ✅
Fase 4 (Comparador Bruto vs Tratado):  ██████████████████████████████ 100% ✅
Fase 5 (Gráficos e Laudos):            ██████████████████████████████ 100% ✅
Fase 6 (Scripts Windows & Setup):      ██████████████████████████████ 100% ✅
```

---

## 👤 Autor

**Victor Vieira Colombo**  
Repositório: [github.com/VituColombo0/CLIMAIA](https://github.com/VituColombo0/CLIMAIA)  
Licença: Privado
