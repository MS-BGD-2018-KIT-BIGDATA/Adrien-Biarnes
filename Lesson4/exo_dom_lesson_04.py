#!/usr/bin/python3.5

import re
import json
import pandas as pd
import requests
from bs4 import BeautifulSoup, NavigableString


class ZoeCar:
    def __init__(self):
        self.version = ''
        self.year = ''
        self.kms = 0
        self.price = 0
        self.cotation = 0
        self.seller_phone = ''
        self.seller_type = ''
        self.postal_code = ''

    def set_version(self, version):
        self.version = version

    def set_year(self, year):
        self.year = year

    def set_kms(self, kms):
        self.kms = int(kms.replace(' ', '').replace('KM', ''))

    def set_price(self, price):
        self.price = int(price.replace(' ', '').replace('€', '').strip())

    def set_cotation(self, cotation):
        self.cotation = int(cotation)

    def set_seller_phone(self, seller_phone):
        self.seller_phone = seller_phone.replace(' ', '').replace('.', '')

    def set_seller_type(self, seller_type):
        self.seller_type = seller_type

    def set_postal_code(self, postal_code):
        self.postal_code = postal_code

    def get_values(self):
        return [self.version, self.year, self.kms, self.price, self.cotation, self.seller_phone, self.seller_type]

    def get_attributes(self):
        return ['version', 'year', 'kms', 'price', 'cotation', 'seller phone', 'seller type']


class LaCentralCrawler:
    def __init__(self):
        self.url = "https://www.lacentrale.fr/cote-auto-renault-zoe-{0}+charge+rapide-{1}.html"
        self.specific_url = "https://www.lacentrale.fr/get_co_prox.php?km={0}&zipcode={1}&month=01"

    def crawl_gross_cotation(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        quote_tag = soup.find('span', attrs={'class': 'jsRefinedQuot'})
        return quote_tag.strip()

    def make_specific_request(self, main_request, kms, postal_code):
        phpsessionid = main_request.cookies._cookies['.lacentrale.fr']['/']['php_sessid'].value
        cookies = {'php_sessid': phpsessionid}
        zipcode = postal_code if postal_code != '' else '75001'
        url = self.specific_url.format(kms, zipcode)
        return requests.post(url, cookies=cookies)

    def crawl(self, car):
        url = self.url.format(car.version, car.year)
        main_request = requests.get(url)
        specific_request = self.make_specific_request(main_request, car.kms, car.postal_code)
        if specific_request.status_code == 200:
            return specific_request.json()['cote_perso']
        return self.crawl_gross_cotation(main_request)


class LeBonCoinCrawler:
    def __init__(self):
        self.url = "https://www.leboncoin.fr/voitures/offres/ile_de_france/?q={0}&o={1}&f={2}"
        self.cotation_crawler = LaCentralCrawler()

    def crawl_ads(self, search_keyword, seller_type):
        print("Crawling pages for type " + seller_type + " :")

        results = []
        page_number = 0
        while True:
            if not self.crawl_ads_page(search_keyword, page_number, seller_type, results):
                return results
            page_number += 1
        return results

    # @staticmethod
    # def crawl_phone_number(list_id):
    #     headers = {'Host': 'api.leboncoin.fr', 'Origin': 'https://www.leboncoin.fr'}
    #     data = {'list_id': list_id, 'app_id': 'leboncoin_web_utils', 'key': '54bb0281238b45a03f0ee695f73e704f',
    #             'text': '1'}
    #     request_result = requests.post("https://api.leboncoin.fr/api/utils/phonenumber.json", data=data,
    #                                    headers=headers)
    #     if request_result.status_code != 200:
    #         return ''
    #     json = request_result.json()
    #     if not 'utils' in json:
    #         return ''
    #     utils = json['utils']
    #     if not 'phonenumber' in utils:
    #         return ''
    #     return utils['phonenumber']

    @staticmethod
    def crawl_phone_number(description_tag):
        if description_tag is None:
            return ''
        match = re.match(r'.*([0-9]{2}.?[0-9]{2}.?[0-9]{2}.?[0-9]{2}.?[0-9]{2})', description_tag.text)
        if match is None:
            return ''
        return match.groups()[0]

    @staticmethod
    def sanitize(property):
        return property.strip(' \t\n\r')

    @staticmethod
    def find_itemprop(properties_section, tag, property):
        return properties_section.find(tag, attrs={'itemprop': property})

    def crawl_sub_property(self, properties_section, tag, property):
        property_tag = self.find_itemprop(properties_section, tag, property)
        value = property_tag.find('span', attrs={'class': 'value'})
        return self.sanitize(value.text)

    def crawl_direct_property(self, properties_section, tag, property):
        property_tag = self.find_itemprop(properties_section, tag, property)
        return self.sanitize(property_tag.text)

    def crawl_text_property(self, properties_section, text):
        property_tag = properties_section.find('span', text=text)
        target = property_tag.nextSibling
        while isinstance(target, NavigableString) and target.strip(' ') == '\n':
            target = target.nextSibling
        return self.sanitize(target.text)

    @staticmethod
    def crawl_version(title, description_tag):
        versions = [('life', 'life'), ('intense?', 'intens'), ('zen', 'zen')]
        for couple in versions:
            if re.search(couple[0], title, re.IGNORECASE):
                return couple[1]

        if description_tag is not None:
            for couple in versions:
                if re.search(couple[0], description_tag.text, re.IGNORECASE):
                    return couple[1]

        if re.search(' int ', title, re.IGNORECASE):
            return 'Intense'

        return 'NA'

    def crawl_postal_code(self, properties_section):
        address = self.crawl_direct_property(properties_section, 'span', 'address')
        match = re.match(r'.*([0-9]{5})', address)
        if match is None:
            return ''
        return match.groups()[0]

    def check_model(self, properties_section):
        model = self.crawl_direct_property(properties_section, 'span', 'model')
        return re.search('Zoe', model, re.IGNORECASE)

    def crawl_ad(self, zoe_ad, list_id, title, seller_type):
        properties_section = zoe_ad.find("section", attrs={'class': 'properties'})
        description_tag = zoe_ad.find("p", attrs={'itemprop': 'description'})
        if not self.check_model(properties_section):
            return None
        car = ZoeCar()
        car.set_price(self.crawl_sub_property(properties_section, 'h2', 'price'))
        car.set_postal_code(self.crawl_postal_code(properties_section))
        car.set_year(self.crawl_direct_property(properties_section, 'span', 'releaseDate'))
        car.set_kms(self.crawl_text_property(properties_section, 'Kilométrage'))
        car.set_version(self.crawl_version(title, description_tag))
        car.set_seller_phone(self.crawl_phone_number(description_tag))
        car.set_seller_type(seller_type)
        car.set_cotation(self.cotation_crawler.crawl(car))
        return car

    def crawl_ad_from_link(self, link, seller_type):
        title = link.find('h2', attrs={'itemprop': 'name'}).text
        info = json.loads(link['data-info'])
        ad_request = requests.get('http:' + link['href'])
        ad_soup = BeautifulSoup(ad_request.text, 'html5lib')
        return self.crawl_ad(ad_soup, info['ad_listid'], title, seller_type)

    def crawl_ads_page(self, search_keyword, page_number, seller_type, all_results):
        print("Page " + str(page_number))
        type = 'p' if seller_type == 'Particulier' else 'c'
        formated_url = self.url.format(search_keyword.replace(' ', '%20'), page_number, type)
        request_result = requests.get(formated_url)
        soup = BeautifulSoup(request_result.text, 'html.parser')
        table = soup.find("section", attrs={'class': 'tabsContent'})
        if table is None:
            return False
        links = table.select('ul > li > a')
        if len(links) == 0:
            return False
        for link in links:
            car = self.crawl_ad_from_link(link, seller_type)
            if car is not None:
                all_results.append(car)
        return True


def persist(cars):
    filename = 'result.csv'
    print("Saving results to file " + filename)
    if len(cars) == 0:
        return
    cars_values = [car.get_values() for car in cars]
    attributes = cars[0].get_attributes()
    cars_df = pd.DataFrame(cars_values, columns=attributes)
    cars_df.to_csv(filename, sep=',', index=False)


if __name__ == "__main__":
    crawler = LeBonCoinCrawler()
    particuliers = crawler.crawl_ads('renault zoe', 'Particulier')
    pros = crawler.crawl_ads('renault zoe', 'Professionels')
    persist(particuliers + pros)
