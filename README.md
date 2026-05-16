# CLIMAIA

## 🌍 Visão Geral
**CLIMAIA** é um sistema de Inteligência Artificial desenhado para prever, identificar e validar eventos climáticos extremos com base na análise comparativa de dados meteorológicos brutos e pré-processados (tratados).

Este projeto utiliza métodos de Deep Learning (como LSTMs) e algoritmos de Machine Learning (como XGBoost) em paralelo com modelos estatísticos clássicos e teoremas de eventos extremos para avaliar as séries temporais.

## 🎯 Principais Objetivos
1. **Previsão de Eventos Extremos:** Utilização de modelos preditivos para antecipar ocorrências críticas.
2. **Avaliação da Integridade dos Dados:** Validação do impacto de tratamentos de dados (interpolação e limpeza) comparando as marcações de eventos extremos entre a série bruta e a série tratada.
   - Os eventos são criados artificialmente devido à interpolação?
   - Os eventos extremos reais são suprimidos durante o tratamento?
3. **Software Premium:** Uma aplicação desktop clara, rápida e altamente estética para interação humana e visualização de resultados.

## 🏗️ Estrutura do Projeto (Planejada)

```
/CLIMAIA
│
├── /data                # Base de dados (brutos e tratados) - Adicione os CSVs aqui!
├── /app                 # Interface de usuário (Software Desktop interativo em CustomTkinter)
│   ├── /pages           # Páginas principais (Dashboard, Data, Analysis, etc.)
│   ├── components.py    # Componentes reutilizáveis (StatCards, Botões, Badges)
│   ├── theme.py         # Design System (Cores, Tipografia, Espaçamentos)
│   └── main_app.py      # Casca principal, roteamento e sidebar
├── main.py              # Ponto de entrada do executável da aplicação
├── lstm_only.py         # Código fornecido de Forecasting com LSTM
├── pv_forecasting.py    # Código fornecido de Forecasting PV com XGBoost
├── PROJECT_LOG.md       # Acompanhamento do progresso de desenvolvimento
├── README.md            # Este arquivo
└── requirements.txt     # Dependências de projeto (pandas, customtkinter, matplotlib, etc)
```

## 🚀 Como Funciona

1. **Definição Base:** Aplicação da Teoria de Valores Extremos (EVT) para delimitar o que caracteriza um evento climático crítico no escopo de cada variável (Vento, Radiação, Temperatura).
2. **Modelagem IA:** A arquitetura do modelo aprende a dinâmica das séries temporais baseando-se no histórico fornecido.
3. **Motor de Comparação:** A IA compara a saída do aprendizado dos dados sem tratamento contra o set de dados tratados, emitindo um relatório analítico.

## 💡 Status do Projeto
**Fase 1 (Arquitetura e Interface): CONCLUÍDA!** 
O sistema desktop está completamente estruturado com navegação funcional, design system (Dark Mode Premium), e componentes prontos.

**Fase 2 (Processamento e IA): PRÓXIMO PASSO.** 
Aguardando o input dos arquivos de dados (CSVs) para injetar a lógica estatística (EVT, Gumbel) e o motor de Deep Learning nos botões da interface.

Consulte o arquivo `PROJECT_LOG.md` para verificar o histórico detalhado e anotações técnicas do andamento atual.
