"""Previsão de risco de alagamento por subprefeitura (módulo IA preditiva do Alaga).

Uso:
    python prever_risco.py --chuva 45 --chuva-d1 12 --chuva-d2 0 --ant7 30 --ant30 180 \
        --temp 23 --umid 85 --vento 2 --data 2026-01-15 [--subpref "Sé"]

Saída: JSON por subprefeitura com probabilidade e faixa (baixo/moderado/elevado),
no formato que a API C# pode expor em GET /riscos?regiao=.
"""
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
from xgboost import XGBClassifier

AQUI = Path(__file__).parent
META = json.loads((AQUI / 'modelo' / 'metadados.json').read_text())
MODELO = XGBClassifier()
MODELO.load_model(AQUI / 'modelo' / 'modelo_risco_xgb.json')


def faixa(p):
    for nome, (a, b) in META['faixas'].items():
        if a <= p < b or (nome == 'elevado' and p >= a):
            return nome


def prever(chuva, chuva_d1, chuva_d2, ant7, ant30, temp, umid, vento, data, subpref=None):
    doy = pd.Timestamp(data).day_of_year
    subs = [subpref] if subpref else sorted(META['taxa_hist_subpref'])
    linhas = []
    for s in subs:
        zona = META['zona_por_subpref'][s]
        r = {'chuva': chuva, 'chuva_d1': chuva_d1, 'chuva_d2': chuva_d2, 'chuva_3d': chuva + chuva_d1 + chuva_d2,
             'chuva_ant_7d': ant7, 'chuva_ant_30d': ant30, 'temp': temp, 'umid': umid, 'vento': vento,
             'sazon_sin': np.sin(2 * np.pi * doy / 365.25), 'sazon_cos': np.cos(2 * np.pi * doy / 365.25),
             'taxa_hist_subpref': META['taxa_hist_subpref'][s], 'pontos_hist_subpref': META['pontos_hist_subpref'].get(s, 0)}
        for f in META['features']:
            if f.startswith('zona_'):
                r[f] = int(f == 'zona_' + zona.replace(' ', '_'))
        linhas.append(r)
    X = pd.DataFrame(linhas)[META['features']]
    p = MODELO.predict_proba(X)[:, 1]
    return [{'subprefeitura': s, 'probabilidade': round(float(pi), 3), 'risco': faixa(pi),
             'aviso': META['aviso']} for s, pi in sorted(zip(subs, p), key=lambda t: -t[1])]


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    for a, d in [('--chuva', 0), ('--chuva-d1', 0), ('--chuva-d2', 0), ('--ant7', 0), ('--ant30', 0),
                 ('--temp', 22), ('--umid', 75), ('--vento', 2)]:
        ap.add_argument(a, type=float, default=d)
    ap.add_argument('--data', default=str(pd.Timestamp.today().date()))
    ap.add_argument('--subpref', default=None)
    a = ap.parse_args()
    print(json.dumps(prever(a.chuva, a.chuva_d1, a.chuva_d2, a.ant7, a.ant30, a.temp, a.umid, a.vento,
                            a.data, a.subpref), ensure_ascii=False, indent=2))
