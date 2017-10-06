#!/usr/bin/python3.5

import requests
from bs4 import BeautifulSoup


def sanitize(amount):
    return int(amount.strip().replace(" ", ""))


class CrawlExercice:
    def __init__(self, year):
        self.year = year
        self.product_by_inhabitant = 0
        self.product_by_strate = 0
        self.charge_by_inhabitant = 0
        self.charge_by_strate = 0
        self.resource_by_inhabitant = 0
        self.resource_by_strate = 0
        self.usage_by_inhabitant = 0
        self.usage_by_strate = 0
        self.url = "http://alize2.finances.gouv.fr/communes/eneuro/detail.php?icom=056&dep=075&type=BPS&param=5&exercice=" + str(year)

    def run(self):
        request_result = requests.get(self.url)
        soup = BeautifulSoup(request_result.text, 'html.parser')

        for row in soup.select("table > tr"):
            cells = row.find_all("td")
            if len(cells) < 4:
                continue
            elif cells[3].text == "TOTAL DES PRODUITS DE FONCTIONNEMENT = A":
                self.product_by_inhabitant = sanitize(cells[1].text)
                self.product_by_strate = sanitize(cells[2].text)
            elif cells[3].text == "TOTAL DES CHARGES DE FONCTIONNEMENT = B":
                self.charge_by_inhabitant = sanitize(cells[1].text)
                self.charge_by_strate = sanitize(cells[2].text)
            elif cells[3].text == "TOTAL DES RESSOURCES D'INVESTISSEMENT = C":
                self.resource_by_inhabitant = sanitize(cells[1].text)
                self.resource_by_strate = sanitize(cells[2].text)
            elif cells[3].text == "TOTAL DES EMPLOIS D'INVESTISSEMENT = D":
                self.usage_by_inhabitant = sanitize(cells[1].text)
                self.usage_by_strate = sanitize(cells[2].text)

    def print(self):
        print("ANALYSE DES EQUILIBRES FINANCIERS FONDAMENTAUX POUR L'ANNEE " + str(self.year))
        print()
        print("TOTAL DES PRODUITS DE FONCTIONNEMENT EN EURO PAR HABITANT = " + str(self.product_by_inhabitant))
        print("TOTAL DES PRODUITS DE FONCTIONNEMENT EN EURO PAR STRATE = " + str(self.product_by_strate))
        print("TOTAL DES CHARGES DE FONCTIONNEMENT EN EURO PAR HABITANT  = " + str(self.charge_by_inhabitant))
        print("TOTAL DES CHARGES DE FONCTIONNEMENT EN EURO PAR STRATE  = " + str(self.charge_by_strate))
        print("TOTAL DES RESSOURCES D'INVESTISSEMENT EN EURO PAR HABITANT = " + str(self.resource_by_inhabitant))
        print("TOTAL DES RESSOURCES D'INVESTISSEMENT EN EURO PAR STRATE = " + str(self.resource_by_inhabitant))
        print("TOTAL DES EMPLOIS D'INVESTISSEMENT EN EURO PAR HABITANT = " + str(self.usage_by_inhabitant))
        print("TOTAL DES EMPLOIS D'INVESTISSEMENT EN EURO PAR STRATE = " + str(self.usage_by_inhabitant))


if __name__ == '__main__':
    for year in range(2010, 2016):
        crawl = CrawlExercice(year)
        crawl.run()
        crawl.print()
        print()
        print()