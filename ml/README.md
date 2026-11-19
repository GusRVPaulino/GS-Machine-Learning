# ml/ · Alaga — modelo de risco de alagamento

Parte de **Inteligência Artificial & Machine Learning** da Global Solution 2026.2 (CitizenTech · FIAP).

Pergunta: *dada a chuva e o histórico da região, qual a probabilidade de o CGE registrar alagamento numa subprefeitura de São Paulo num dia?* Modelo: **XGBoost**, treinado com dados reais do CGE e do INMET (2006–2021) e testado em 2022–2025.

**Vídeo de apresentação:** https://www.youtube.com/watch?v=cLd51xH-YBs

## Integrantes

| Nome | RM |
|---|---|
| Eduardo Dallabella Lima | RM556803 |
| Guilherme Abe | RM554743 |
| Gustavo Ruiz Vieira Paulino | RM554779 |
| Heloísa Real | RM554535 |
| Victor Pacifico Dias | RM558017 |

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `alaga_risco_alagamento.ipynb` | notebook **executado**, do dado bruto à conclusão |
| `RELATORIO_ML.md` | relatório da entrega |
| `dados/` | dados reais usados + `dados/README.md` (fonte, link, período, hash) |
| `figuras/` | gráficos e tabelas gerados pelo notebook |
| `modelo/` | modelo treinado (`modelo_risco_xgb.json`) e metadados (features, faixas, métricas) |
| `prever_risco.py` | previsão por linha de comando, saída JSON para a API (`GET /riscos?regiao=`) |
| `requirements.txt` | dependências |

## Como rodar

```bash
cd ml
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter nbconvert --to notebook --execute --inplace alaga_risco_alagamento.ipynb   # ~2 min
python prever_risco.py --chuva 60 --chuva-d1 10 --ant7 40 --ant30 200 --data 2026-01-20
```

## Resultado principal (teste 2022–2025, nunca visto no treino)

| Métrica | Treino | Teste |
|---|---|---|
| ROC-AUC | 0,946 | 0,917 |
| PR-AUC | 0,450 | 0,335 (aleatório = 0,038) |
| F1 (limiar 0,17) | 0,457 | 0,391 |

Faixas do app no teste: **baixo** alagou em 1,3% dos casos, **moderado** em 19,4%, **elevado** em 46,9%.
