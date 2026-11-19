# Relatório de Machine Learning · Alaga

**GS 2026.2 · CitizenTech · IA & Machine Learning** · Notebook: `ml/alaga_risco_alagamento.ipynb` · Modelo: XGBoost

**Integrantes:** Eduardo Dallabella Lima (RM556803) · Guilherme Abe (RM554743) · Gustavo Ruiz Vieira Paulino (RM554779) · Heloísa Real (RM554535) · Victor Pacifico Dias (RM558017)

## 1. Problema e dados reais

O Alaga avisa motoristas, entregadores e moradores de São Paulo sobre alagamentos. A camada **"Risco estimado: baixo / moderado / elevado"** do app depende de um modelo.

**Pergunta de ML (classificação binária):** *dada a chuva do dia e dos dias anteriores, o tempo, a época do ano e o histórico da subprefeitura, qual a probabilidade de o CGE registrar ≥ 1 ponto de alagamento naquela subprefeitura naquele dia?* Unidade: subprefeitura × dia (32 subprefeituras).

| Base | Fonte | Período usado |
|---|---|---|
| 19.574 pontos de alagamento | CGE – Prefeitura de SP (`cgesp.org/v3/alagamentos.jsp`), extração aberta em `github.com/yssgor/sp-alagamentos` | 01/08/2006 – 24/04/2025 |
| Chuva, temperatura, umidade, vento (diário) | INMET – BDMEP, estação A701 Mirante de Santana | idem |

Links e hashes em `ml/dados/README.md`; nenhum dado é simulado. Com 0 mm a subprefeitura alaga em 0,4% dos dias; com 30–50 mm, em 20,9%.

## 2. Escolha do modelo

**XGBoost** (árvores de decisão em sequência, cada uma corrigindo os erros da anterior). Motivos: o alagamento tem **limiares e interações** (a mesma chuva alaga a Sé e não Parelheiros; solo encharcado reduz o limiar), os dados são **tabulares e desbalanceados** (3,5% de positivos), e o modelo gera **probabilidades** (viram as faixas do app) e **importância de atributos** (explicabilidade). Referências: regra "chuva ≥ 30 mm" e Regressão Logística.

## 3. Preparação e divisão treino/teste

- **Correção de datas:** os alagamentos do dia *d* correlacionam 0,58 com a chuva rotulada *d+1* no INMET e só 0,34 com o mesmo dia (o temporal de 24/01/2025 aparece no INMET em 25/01). O INMET foi deslocado −1 dia.
- **Grade completa** subprefeitura × dia (dias sem registro = negativos): 209.856 linhas. Dias sem chuva medida (4,2%) removidos, sem imputação.
- **19 atributos:** chuva do dia, de 1 e 2 dias antes, acumulado de 3 dias, acumulados antecedentes de 7 e 30 dias, temperatura, umidade, vento, sazonalidade (seno/cosseno), zona e histórico da subprefeitura.
- **Divisão temporal:** treino ago/2006–dez/2021 (174.944 linhas) e teste jan/2022–abr/2025 (34.912). O histórico da subprefeitura é calculado **só com o treino**.

## 4. Treino com diferentes hiperparâmetros

18 combinações: `max_depth` {3, 5, 8} × `learning_rate` {0,03; 0,1; 0,3} × `n_estimators` {100, 400}, com **validação cruzada temporal de 5 folds só no treino** (90 treinos) e seleção por **PR-AUC**, já que a acurácia engana com 3,5% de positivos.

| Combinação | PR-AUC no treino do fold | PR-AUC na validação |
|---|---|---|
| **5 · 0,03 · 100 (escolhida)** | 0,518 | **0,373** |
| 3 · 0,03 · 100 | 0,444 | 0,365 |
| 8 · 0,3 · 400 (mais complexa) | **1,000** | 0,311 (pior) |

**Overfitting:** a combinação mais complexa decorou o treino e foi a pior na validação; na curva de log-loss, a validação piora após 200–300 árvores. O limiar do alerta (0,17) foi escolhido fora da amostra, sem olhar o teste.

## 5. Resultados em treino e teste

| Métrica | XGBoost treino | **XGBoost teste** | Reg. Logística teste | Regra ≥ 30 mm teste |
|---|---|---|---|---|
| PR-AUC (aleatório = 0,038) | 0,450 | **0,335** | 0,295 | 0,100 |
| ROC-AUC | 0,946 | **0,917** | 0,878 | 0,640 |
| Precisão / Recall | 0,371 / 0,597 | 0,310 / **0,528** | 0,321 / 0,415 | 0,232 / 0,321 |
| F1 | 0,457 | **0,391** | 0,362 | 0,269 |

No teste (anos nunca vistos), o XGBoost fica ~9× acima do aleatório e supera as referências em PR-AUC, ROC-AUC, recall e F1. A queda moderada de treino para teste indica que não há overfitting severo. Atributos mais importantes: chuva do dia (41%) e histórico da subprefeitura (16%).

## 6. Conclusão e leitura para o cidadão

| Faixa no app | Probabilidade | Alagou de fato no teste |
|---|---|---|
| baixo | < 10% | **1,3%** dos casos |
| moderado | 10–40% | **19,4%** |
| elevado | ≥ 40% | **46,9%** |

Quando o Alaga marca **elevado**, a região alagou em quase metade dos casos; quando marca **baixo**, em pouco mais de 1%. Isso é informação acionável: evitar baixadas, não estacionar em ponto crítico, acompanhar os alertas. No temporal de 24/01/2025, o modelo pôs 7 subprefeituras em risco elevado, e 6 delas tiveram alagamento registrado. O app mostra a faixa sempre como "risco estimado": ela não confirma água na pista nem substitui CGE e Defesa Civil (199).

**Limitações:** um único pluviômetro para a cidade, chuva diária (não horária) e o CGE monitora sobretudo vias principais. Próximo passo: pluviômetros do CEMADEN por região. O modelo está em `ml/modelo/`, e `ml/prever_risco.py` gera o JSON para `GET /riscos?regiao=`.
