# labo
# equivalent traitement
# année commercialisation
# mois commercialisation
# prix
# restriction age
# restriction poids


import re
import numpy as np
import pandas as pd
import requests


query_url = "https://www.open-medicaments.fr/api/v1/medicaments?query="
info_url = "https://www.open-medicaments.fr/api/v1/medicaments/"
cols = ['labo', 'equivalent_traitement', 'annee_com', 'mois_com', 'prix', 'restriction_age', 'restriction_poids']
regex = re.compile('(\d+) (m?g)')


def get_med_info(code_cis):
    return requests.get(info_url + code_cis).json()


def get_equivalent_traitement(composition):
    for substance in composition['substancesActives']:
        if substance['denominationSubstance'] != 'IBUPROFÈNE':
            continue
        dosage = substance['dosageSubstance']
        match = regex.match(dosage)
        if match is None:
            return ''
        groups = match.groups()
        quantity = int(groups[0])
        factor = 1 if groups[1] == 'g' else 1 / 1000
        return quantity * factor
    return ''


def get_results(query):
    reqs = requests.get(query_url + query).json()
    res = pd.DataFrame(0, index=np.arange(len(reqs)), columns=cols)
    for i, req in enumerate(reqs):
        code_cis = req['codeCIS']
        med_info = get_med_info(code_cis)
        res.iloc[i, 0] = med_info['titulaires'][0]
        compositions = med_info['compositions']
        res.iloc[i, 1] = get_equivalent_traitement(compositions[0])
        res.iloc[i, 2] = med_info['presentations'][0]
        res.iloc[i, 3] = ''
    return res


results = get_results('IBUPROFENE')
results.to_csv('results_ibo.csv', sep=',', index=False)
