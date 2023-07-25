from typing import Optional, Tuple
import requests
from bs4 import BeautifulSoup
import time
import re
import datetime

import subprocess
from .promo_database import DataBase
from .promo_utils import *
from configparser import ConfigParser
import os
import sys
from .promo_models import MainData, MainDataLog

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class Scrapper:
    def __init__(self, data_config: Tuple[str, int]) -> None:
        self.page_url = "https://promoklocki.pl"
        self.lego_type, self.max_pages = data_config

    def get_html(self, page: str) -> str:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0"
        }
        response = requests.get(page, headers=headers)
        if not response.ok:
            print(f"Code: {response.status_code}, url: {page}")

        return response.text

    def start_scrapping(self):
        all_sets = []
        counter = 1

        while True:
            if counter > self.max_pages:
                break

            subpage = f"/?s={self.lego_type}&p={counter}"
            prodcuts = self.get_sets(self.page_url , subpage)
            if prodcuts:
                all_sets.extend(prodcuts)
                counter += 1
                time.sleep(0.5)
            else:
                break

        return all_sets

    def get_sets(self, url: str, subpage: str):
        html = self.get_html(url + subpage)
        soup = BeautifulSoup(html, "lxml")
        all_links: list[MainData] = []

        products = soup.select("div.main > div.container > div.content > div.product")
        for p in products:
            product_link_raw = p.find("a", href=True)

            product_link = None
            name = None
            date = None
            catalog_number = None
            number_of_elements = None
            number_of_minifigures = None
            catalog_price = None
            lowest_price = None
            historically_lowest_price = None
            historically_lowest_price_date = None

            if product_link_raw and product_link_raw.text:
                product_link = url + product_link_raw["href"]
                product_html = self.get_html(product_link)
                product_soup = BeautifulSoup(product_html, "lxml")

                one_product_name = product_soup.select("div.main > div.container > div.content > div.d-flex")
                name_raw = one_product_name[0].find_all("h1")

                one_product = product_soup.select("div.main > div.container > div.content > div.row > div.col-md-6 > dl.row")
                values_raw = one_product[0].find_all("dd")
                titles_raw = one_product[0].find_all("dt")

                # must be hardcoded apparently
                product_name_recognizer = "Nazwa angielska"
                catalog_number_recognizer = "Numer katalogowy"
                number_of_elements_recognizer = "Liczba elementów"
                number_of_minifigures_recognizer = "Liczba minifigurek"
                date_recognizer = "Rok wydania"
                lowest_price_recognizer = "Aktualnie najniższa cena"
                catalog_price_recognizer = "Cena katalogowa"
                historically_lowest_price_recognizer = "Historycznie najniższa cena"

                for v, t in zip(values_raw, titles_raw):
                    if v and t:
                        if t.text == product_name_recognizer:
                            name = v.text.strip()
                        elif t.text == catalog_number_recognizer:
                            catalog_number_str = v.text.strip()
                            catalog_number_searched = re.search(r'\d+', catalog_number_str).group(0)
                            catalog_number = int(catalog_number_searched)
                        elif t.text == number_of_elements_recognizer:
                            number_of_elements_str = v.text.strip()
                            number_of_elements = int(number_of_elements_str)
                        elif t.text == number_of_minifigures_recognizer:
                            number_of_minifigures_str = v.text.strip()
                            number_of_minifigures = int(number_of_minifigures_str)
                        elif t.text == date_recognizer:
                            all_date_text = v.text.strip()
                            date_pattern = r"\((\d{1,2}\.\d{1,2}\.\d{4})\)"
                            matches = re.findall(date_pattern, all_date_text)
                            if matches:
                                date_temp = matches[0]
                                date_obj = datetime.datetime.strptime(date_temp, "%d.%m.%Y")
                                date = date_obj.strftime("%Y-%m-%d")
                        elif t.text == lowest_price_recognizer:
                            lowest_price_str = v.text.strip()
                            lowest_price = float(lowest_price_str.replace(",", ".").replace(" zł", ""))
                        elif t.text == catalog_price_recognizer:
                            catalog_price_str = v.text.strip()
                            catalog_price = catalog_price_str.replace(",", ".").replace(" zł", "")
                        elif t.text == historically_lowest_price_recognizer:
                            temp_string = v.text.strip()
                            price_date_pattern = r"(\d{1,2},\d{2}) zł\n\((\d{1,2}\.\d{2}\.\d{4})\)"
                            matches = re.search(price_date_pattern, temp_string)
                            if matches:
                                historically_lowest_price = matches.group(1).replace(",", ".")
                                historically_lowest_price_date = matches.group(2)

                if name is None and name_raw is not None:
                    name_text = name_raw[0].text
                    name_pattern = r"LEGO® \d+ Star Wars - (.+)"
                    match = re.match(name_pattern, name_text)
                    if match:
                        set_name = match.group(1)
                        name = set_name
                    else:
                        print("Set name not found.")
            
            all_links.append(
                MainData(
                    catalog_number,
                    product_link,
                    name,
                    lowest_price,
                    number_of_elements,
                    number_of_minifigures,
                    date,
                )
            )

        return all_links


class Notificator:
    def __init__(self, db: DataBase) -> None:
        self.expiration_time = 30 * 60 * 1000  # half of an hour
        self.command = "notify-send"
        self.message = ""
        self.db = db

    def assembly_message(self, latest_log) -> None:
        if latest_log.operation == "I":
            self.message = f"'New set: {latest_log.name} was added!' 'Check it on: {latest_log.production_link}'"
        elif latest_log.operation == "U":
            rows = self.db.get_product_logs(latest_log.catalog_number, latest_log.changed_on)
            if len(rows) > 1:
                latest_log = MainData.create_from_tuple(rows[0][1:-3])
                second_latest_log = MainData.create_from_tuple(rows[1][1:-3])
                diff = latest_log.get_differences(second_latest_log)
                info = "<b>Changes:</b>\n"
                for key, val in diff.items():
                    info += f"{key}:  "
                    info += f"Old: {val[1]}  "
                    info += f"<b>New: {val[0]}</b>\n"
                self.message = f"\"Set: {latest_log.name} was updated!\" \"Check it on: {latest_log.production_link}\n{info}\""

    def notify(self) -> None:
        latest_list = self.db.select_not_accepted_logs()
        for latest in latest_list:
            data_log_object = MainDataLog.create_from_tuple(latest)
            self.assembly_message(data_log_object)

            command = f"{self.command} -t {self.expiration_time} {self.message}"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)


def main() -> None:
    configure = ConfigParser()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.ini')
    configure.read(config_path)

    name = configure.get("database", "name")
    user = configure.get('database','user')
    password = configure.get('database', 'pass')
    host = configure.get('database', 'host')
    port = configure.getint('database', 'port')
    db_data = (name, user, password, host, port)

    subsite = configure.get("scraping", "subsite")
    pages = configure.get("scraping", "pages")

    scrap_config = (subsite, int(pages))

    db = DataBase(db_data)
    scrapper = Scrapper(scrap_config)

    all_sets = []
    all_sets = scrapper.start_scrapping()

    for set in all_sets:
        db.add_basic_info(set)

    notificator = Notificator(db)
    notificator.notify()


if __name__ == "__main__":
    main()
