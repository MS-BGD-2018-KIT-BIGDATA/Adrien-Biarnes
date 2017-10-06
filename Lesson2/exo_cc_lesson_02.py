#!/usr/bin/python3.5

import requests
from bs4 import BeautifulSoup


class CrawlExercice:
    def __init__(self):
        self.acer_url = "https://www.cdiscount.com/m-298-acer.html"
        self.dell_url = "https://www.cdiscount.com/informatique/ordinateurs-pc-portables/pc-portables/lf-228394_6-dell.html#_his_"

    def extract_price_from_string(self, string, sep=","):
        splitted_price = string.split(sep)
        return int(splitted_price[0])

    def extract_prices(self, url):
        res = []
        request_result = requests.get(url)
        soup = BeautifulSoup(request_result.text, 'html.parser')
        reduced_prices = soup.find_all("div", { "class" : "prdtPrSt" })
        for reduced_price_div in reduced_prices:
            parent_zone = reduced_price_div.find_parents("div", "prdtBZPrice")[0]
            real_price_parent = parent_zone.find_all("div", { "class": "prdtPrice" })[0]
            real_price_span = real_price_parent.find_all("span", { "class": "price" })[0]
            reduced_price = self.extract_price_from_string(reduced_price_div.text)
            real_price = self.extract_price_from_string(real_price_span.text, "€")
            res.append((reduced_price, real_price))
        return res

    def compute_rebate(self, prices):
        ratios = [ (price2 - price1) / price1 for (price1, price2) in prices ]
        return sum(ratios) / len(ratios) * 100

    def print_rebate(self, prefix, url):
        prices = self.extract_prices(url)
        rebate = self.compute_rebate(prices)
        print(prefix + " rebate = " + str(rebate))

    def run(self):
        self.print_rebate("acer", self.acer_url)
        self.print_rebate("dell", self.dell_url)


if __name__ == '__main__':
    crawl = CrawlExercice()
    crawl.run()
