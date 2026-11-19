# Dados (`ml/dados/`)

Todos os dados são **reais e públicos**. Nenhum dado foi simulado ou gerado.

## 1. Pontos de alagamento — CGE / Prefeitura de São Paulo

| Item | Valor |
|---|---|
| Arquivo | `ocorrencias_cge_2005_2026.csv` (19.589 linhas, 15 duplicatas removidas no notebook) |
| Fonte oficial | CGE – Centro de Gerenciamento de Emergências Climáticas, Prefeitura de São Paulo |
| Link da fonte | https://www.cgesp.org/v3/alagamentos.jsp (consulta por data: `?dataBusca=DD%2FMM%2FAAAA`) |
| Como foi obtido | O CGE não oferece download em lote; usamos a extração dia a dia das páginas do CGE publicada no repositório aberto **yssgor/sp-alagamentos** (licença MIT), arquivo `data/processed/ocorrencias_padronizadas.csv`, commit `a4a9792` (11/11/2026). O HTML bruto de cada dia está na branch `dados` desse repositório, permitindo auditar qualquer linha. |
| Link do repositório | https://github.com/yssgor/sp-alagamentos |
| Período disponível | 03/01/2005 – 29/10/2026 |
| Período usado no modelo | 01/08/2006 – 24/04/2025 (interseção com o INMET) |
| Colunas principais | `data`, `inicio`, `fim`, `zona`, `subprefeitura`, `local`, `sentido`, `referencia`, `intransitavel`, `ponto_id` |
| SHA-256 | `75152ed78ec42c12daff8dfede4e071ab752308157116d99705924db2e7d9f27` |

Uso no modelo: contamos quantos pontos o CGE registrou por subprefeitura e dia. O alvo é `alagou = 1` se houve ≥ 1 ponto.

## 2. Chuva e tempo — INMET, estação A701 (São Paulo – Mirante de Santana)

| Item | Valor |
|---|---|
| Arquivo | `dados_A701_D_2006-07-24_2025-04-25.csv` (série diária, formato de exportação do BDMEP) |
| Fonte oficial | INMET – Instituto Nacional de Meteorologia, BDMEP (Banco de Dados Meteorológicos) |
| Link da fonte | https://bdmep.inmet.gov.br/ · dados históricos: https://portal.inmet.gov.br/dadoshistoricos |
| Estação | A701 – SAO PAULO - MIRANTE · lat −23,4963 · lon −46,6201 · altitude 785,6 m |
| Como foi obtido | Arquivo exportado do BDMEP (cabeçalho original preservado), espelhado em https://github.com/wmpjrufg/climatetwin (`BD/dados/wander/`). Pode ser regerado no BDMEP escolhendo a estação A701, periodicidade diária, 24/07/2006 – 25/04/2025. |
| Período | 24/07/2006 – 25/04/2025 |
| Colunas usadas | precipitação total diária (mm), temperatura média (°C), umidade relativa média (%), vento médio (m/s) |
| Faltantes | 1,2% dos dias sem chuva registrada (removidos, não imputados) |
| SHA-256 | `0663a8bc4ef0e9a7d0e80b12728ff23874e0cd222db9a64f15fdf095d7915463` |

### Ajuste de datas

O total diário do INMET não corresponde ao dia civil de São Paulo usado pelo CGE. No notebook (seção 2.3) mostramos que o nº de alagamentos do dia *d* correlaciona 0,58 com a chuva rotulada *d+1* no INMET, contra 0,34 com o mesmo rótulo; o temporal de 24/01/2025 (39 pontos no CGE) aparece no INMET como 25/01. Por isso a série do INMET é deslocada −1 dia antes do cruzamento.

## Verificar a integridade

```bash
sha256sum dados/*.csv
```

## Créditos

- Dados de alagamento: CGE – Prefeitura do Município de São Paulo.
- Dados meteorológicos: INMET – Instituto Nacional de Meteorologia.
- Extração do CGE: projeto aberto sp-alagamentos (Ygor Silva, MIT).
