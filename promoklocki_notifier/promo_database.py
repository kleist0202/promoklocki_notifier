from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .promo_scrapper import MainData
    import datetime

import psycopg2
from psycopg2 import sql

from dataclasses import asdict


class DataBase:
    def __init__(self, db_passes) -> None:
        name, user, password, host, port = db_passes
        self.conn = psycopg2.connect(
            database=name,
            user=user,
            password=password,
            host=host,
            port=port,
        )

    def add_basic_info(self, data: MainData) -> None:
        with self.conn.cursor() as cursor:
            data_tuple = tuple(asdict(data).values())

            query = sql.SQL(
                """
                INSERT INTO lego_main_info (catalog_number, production_link, name, lowest_price, number_of_elements, number_of_minifigures, date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (catalog_number) DO UPDATE
                SET production_link = EXCLUDED.production_link,
                name = EXCLUDED.name,
                lowest_price = EXCLUDED.lowest_price,
                number_of_elements = EXCLUDED.number_of_elements,
                number_of_minifigures = EXCLUDED.number_of_minifigures,
                date = EXCLUDED.date
                """
            )
            cursor.execute(query, data_tuple)
            self.conn.commit()

    def select_not_accepted_logs(self) -> list[tuple[Any, ...]]:
        rows = []
        with self.conn.cursor() as cursor:
            query = sql.SQL(
                """
                SELECT *
                FROM lego_main_info_log
                WHERE accepted = FALSE
                ORDER BY changed_on DESC
                """
            )
            cursor.execute(query)
            rows = cursor.fetchall()

        return rows

    def select_not_accepted_logs_reverse(self) -> list[tuple[Any, ...]]:
        rows = []
        with self.conn.cursor() as cursor:
            query = sql.SQL(
                """
                SELECT *
                FROM lego_main_info_log
                WHERE accepted = FALSE
                ORDER BY changed_on ASC
                """
            )
            cursor.execute(query)
            rows = cursor.fetchall()

        return rows

    def select_all_logs(self, order="DESC") -> list[tuple[Any, ...]]:
        query = ""
        rows: list[tuple[Any, ...]] = []
        with self.conn.cursor() as cursor:
            query_desc = sql.SQL(
                """
                SELECT *
                FROM lego_main_info_log
                ORDER BY changed_on DESC
                """
            )
            query_asc = sql.SQL(
                """
                SELECT *
                FROM lego_main_info_log
                ORDER BY changed_on ASC
                """
            )
            if order == "DESC":
                query = query_desc
            elif order == "ASC":
                query = query_asc
            else:
                return rows

            cursor.execute(query)
            rows = cursor.fetchall()

        return rows

    def accept_log(self, log_id: str) -> None:
        with self.conn.cursor() as cursor:
            query = "UPDATE lego_main_info_log SET accepted = TRUE WHERE log_id = %s"
            cursor.execute(query, (log_id, ))
            self.conn.commit()

    def get_product_logs(self, product_id: int, timestamp: datetime.datetime) -> list[tuple[Any, ...]]:
        rows: list[tuple[Any, ...]] = []
        with self.conn.cursor() as cursor:
            query = "SELECT * FROM lego_main_info_log WHERE catalog_number = %s AND changed_on <= %s ORDER BY changed_on DESC"
            cursor.execute(query, (product_id, timestamp))
            rows = cursor.fetchall()
        return rows

    def get_products_reverse(self) -> list[tuple[Any, ...]]:
        rows: list[tuple[Any, ...]] = []
        with self.conn.cursor() as cursor:
            query = "SELECT * FROM lego_main_info ORDER BY name ASC"
            cursor.execute(query)
            rows = cursor.fetchall()
        return rows
