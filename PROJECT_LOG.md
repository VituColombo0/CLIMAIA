# CLIMAIA Project Log

## Introdução e Objetivos
**Data de Início:** 08/05/2026
**Objetivo Principal:** Desenvolver uma Inteligência Artificial capaz de identificar eventos climáticos extremos a partir de dados brutos e tratados, utilizando métodos estatísticos e modelos preditivos estabelecidos (fórmulas e teoremas climáticos).

O modelo será responsável por:
1. **Previsão:** Predizer a ocorrência de eventos baseando-se no histórico de dados climáticos.
2. **Análise de Dados Brutos vs Tratados:** Comparar as identificações de eventos nos dados não tratados com os dados tratados (interpolação/limpeza) para verificar se:
   - Um evento foi criado artificialmente devido ao tratamento?
   - Um evento foi mascarado (substituído) pelo tratamento?
   - O resultado bate em ambas as pontas?

## Estruturação do Projeto

O projeto será dividido em 6 fases principais:

### Fase 1: Ingestão e Estruturação de Dados
- **Fontes de Dados:** Arquivos fornecidos contendo as séries temporais brutas e as séries limpas/interpoladas.
- **Armazenamento:** Configurar banco de dados ou estrutura de arquivos local (como Parquet/CSV) para acesso rápido.
- **Variáveis Chave:** Temperatura, Velocidade do Vento (ex: `Wspd_avg_83m`), Radiação Solar, etc.

### Fase 2: Baseline Estatístico e Identificação Numérica
- Aplicar teoremas estatísticos (Ex: Teoria de Valores Extremos - EVT, Distribuição de Gumbel, Limiares de Percentil) para cravar o que é um "Evento Extremo".
- Rodar esta formulação matemática em ambos os conjuntos de dados (Bruto e Tratado).

### Fase 3: Desenvolvimento do Modelo de IA
- **Arquitetura Base:** Redes Neurais Recorrentes (LSTM/GRU) ou XGBoost Regressors (conforme os scripts fornecidos).
- **Treinamento:** Treinar o modelo não apenas para prever o valor da variável, mas também para *classificar* a ocorrência do evento extremo com base no que a modelagem estatística validou.
- **Integração de Base:** Utilizar as abstrações já presentes em `lstm_only.py` (previsão de vento) e `pv_forecasting.py` (previsão de energia solar) como alicerce.

### Fase 4: Comparador Analítico (O Diferencial)
- Criar o motor de comparação:
  - Input: Deteções no Dado Bruto vs Deteções no Dado Tratado.
  - Output Report: 
    - "Evento X foi suprimido no dado tratado"
    - "Alarme Falso: Evento Y criado pela interpolação"
    - Taxa de concordância geral.

### Fase 5: Desenvolvimento de Interface Web
- Desenvolver um frontend moderno e visualmente premium (Next.js/React ou dashboard robusto em Streamlit/Dash, conforme preferência).
- Interface deve ter opções claras: "Fazer Previsão", "Comparar Bruto vs Tratado", "Dashboard de Eventos Extremos".

### Fase 6: Automação e Deploy
- Agendamento de inferência e validação contínua (ex: rodar scripts de forecasting diariamente).
- Sistema de alertas e relatórios gerados.

## Log de Atividades
* **08/05/2026:** Planejamento estrutural do projeto criado. Analisados os scripts base fornecidos (`lstm_only.py`, `pv_forecasting.py`). Criado o repositório inicial e `README.md`. Aguardando validação do plano pelo usuário.
