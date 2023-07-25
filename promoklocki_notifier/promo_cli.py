from typing import Any
from .promo_database import DataBase
from .promo_utils import *
from .promo_scrapper import MainData, MainDataLog
import os
from configparser import ConfigParser
import argparse
from abc import ABC, abstractmethod


class CliFormat(ABC):
    def __init__(self, db) -> None:
        self.db: DataBase = db
        self.logs_number: int = 0
        self.current_entry: int = 0
        self.rows: list[tuple[Any, ...]] = []

        self.get_all_logs()

    @abstractmethod
    def get_all_logs(self):
        pass


class LogsFormat(CliFormat):
    def __init__(self, db) -> None:
        super().__init__(db)

    def format_log(self, log_object: MainDataLog) -> None:
        print(f"Log id: {log_object.log_id}")
        print(f"Catalog number: {log_object.catalog_number}")
        print(f"Name: {log_object.name}")
        print(f"Link: {log_object.production_link}")
        print(f"Number of elements: {log_object.number_of_elements}")
        print(f"Number of minifigures: {log_object.number_of_minifigures}")
        print(f"Date: {log_object.date}")
        print(f"Price: {log_object.lowest_price}")
        print(f"Operation: {log_object.operation}")
        print(f"Log Timestamp: {log_object.changed_on}")
        print(f"Accepted?: {log_object.accepted}")

        rows = self.db.get_product_logs(log_object.catalog_number, log_object.changed_on)
        if len(rows) > 1:
            latest_log = MainData.create_from_tuple(rows[0][1:-3])
            second_latest_log = MainData.create_from_tuple(rows[1][1:-3])
            diff = latest_log.get_differences(second_latest_log)
            info = print_bold("Changes:\n")
            for key, val in diff.items():
                info += f"{key :<20}:  "
                info += print_gray(f"Old: {val[1]}  ")
                info += print_warning(f"New: {val[0]}\n")
            print(f"{info}")

    def get_all_logs(self) -> None:
        self.rows = self.db.select_not_accepted_logs_reverse()
        self.logs_number = len(self.rows)

    def show(self):
        if self.logs_number == 0:
            print("No products.")
            return False
        md = MainDataLog.create_from_tuple(self.rows[self.current_entry])
        is_accepted = md.accepted

        print("--------------------------------")
        self.format_log(md)
        print("--------------------------------")

        if not is_accepted:
            print("Accept current log? [a]")

        print("Exit program. [q]")
        print(f"Next or previous log ({self.current_entry+1}/{self.logs_number}). [n/p]")
        action = input("Action: ")

        if action in ["n", "N"]:
            if self.current_entry < self.logs_number - 1:
                self.current_entry += 1
        elif action in ["p", "P"]:
            if self.current_entry > 0:
                self.current_entry -= 1
        elif action in ["q", "Q"]:
            return False

        if not is_accepted:
            if action == "a":
                self.db.accept_log(md.log_id)
                if self.current_entry == self.logs_number - 1:
                    self.current_entry -= 1
                self.get_all_logs()

        return True


class ProdcutsFormat(CliFormat):
    def __init__(self, db) -> None:
        super().__init__(db)

    def get_all_logs(self) -> None:
        self.rows = self.db.get_products_reverse()
        self.logs_number = len(self.rows)

    def format_log(self, object: MainData) -> None:
        print(f"Catalog number: {object.catalog_number}")
        print(f"Name: {object.name}")
        print(f"Link: {object.production_link}")
        print(f"Number of elements: {object.number_of_elements}")
        print(f"Number of minifigures: {object.number_of_minifigures}")
        print(f"Date: {object.date}")
        print(f"Price: {object.lowest_price}")

    def show(self):
        if self.logs_number == 0:
            print("No products.")
            return False
        mdl = self.rows[self.current_entry]

        print("--------------------------------")
        self.format_log(mdl)
        print("--------------------------------")

        print("Exit program. [q]")
        print(f"Next or previous product ({self.current_entry+1}/{self.logs_number}). [n/p]")
        action = input("Action: ")

        if action in ["n", "N"]:
            if self.current_entry < self.logs_number - 1:
                self.current_entry += 1
        elif action in ["p", "P"]:
            if self.current_entry > 0:
                self.current_entry -= 1
        elif action in ["q", "Q"]:
            return False

        return True


class Cli:
    def __init__(self, db: DataBase) -> None:
        self.db = db
        self.handler = None

    def format_log(self, log_object: MainDataLog) -> None:
        print(f"Log id: {log_object.log_id}")
        print(f"Catalog number: {log_object.catalog_number}")
        print(f"Name: {log_object.name}")
        print(f"Link: {log_object.production_link}")
        print(f"Number of elements: {log_object.number_of_elements}")
        print(f"Number of minifigures: {log_object.number_of_minifigures}")
        print(f"Date: {log_object.date}")
        print(f"Price: {log_object.lowest_price}")
        print(f"Operation: {log_object.operation}")
        print(f"Log Timestamp: {log_object.changed_on}")
        print(f"Accepted?: {log_object.accepted}")

        rows = self.db.get_product_logs(log_object.catalog_number, log_object.changed_on)
        if len(rows) > 1:
            latest_log = MainData.create_from_tuple(rows[0][1:-3])
            second_latest_log = MainData.create_from_tuple(rows[1][1:-3])
            diff = latest_log.get_differences(second_latest_log)
            info = print_bold("Changes:\n")
            for key, val in diff.items():
                info += f"{key :<20}:  "
                info += print_gray(f"Old: {val[1]}  ")
                info += print_warning(f"New: {val[0]}\n")
            print(f"{info}")

    def get_all_logs(self) -> None:
        self.rows = self.db.select_not_accepted_logs_reverse()
        self.logs_number = len(self.rows)

    def main_loop(self, arg) -> None:
        if arg:
            self.handler = LogsFormat(self.db)
        else:
            self.handler = ProdcutsFormat(self.db)

        os.system('cls' if os.name == 'nt' else 'clear')
        while True:
            result = self.handler.show()
            if not result:
                break
            os.system('cls' if os.name == 'nt' else 'clear')

        
def main() -> None:
    p = argparse.ArgumentParser(formatter_class=argparse.MetavarTypeHelpFormatter)
    group = p.add_mutually_exclusive_group()
    group.add_argument(
        "--logs", "-l", action="store_true", help="shows only not accepted logs"
    )
    group.add_argument(
        "--products", "-p", action="store_true", help="shows products currently stored in database"
    )

    args = vars(p.parse_args())

    if args["logs"]:
        logs_or_products = True
    elif args["products"]:
        logs_or_products = False
    else:
        print("Something went wrong.")
        quit()

    configure = ConfigParser()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.ini')
    print(config_path)
    configure.read(config_path)

    name = configure.get("database", "name")
    user = configure.get('database','user')
    password = configure.get('database', 'pass')
    host = configure.get('database', 'host')
    port = configure.getint('database', 'port')
    db_data = (name, user, password, host, port)

    db = DataBase(db_data)
    cli = Cli(db)
    cli.main_loop(logs_or_products)


if __name__ == "__main__":
    main()
