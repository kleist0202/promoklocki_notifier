from dataclasses import dataclass
import datetime


@dataclass
class MainData:
    catalog_number: int
    production_link: str
    name: str
    lowest_price: float
    number_of_elements: int
    number_of_minifigures: int
    date: datetime.date

    def get_differences(self, other):
        differences = {}
        for field in self.__annotations__:
            if getattr(self, field) != getattr(other, field):
                differences[field] = [getattr(self, field), getattr(other, field)]
        return differences

    @classmethod
    def create_from_tuple(cls, data_tuple):
        return MainData(*data_tuple)


@dataclass
class MainDataLog:
    log_id: int
    catalog_number: int
    production_link: str
    name: str
    lowest_price: float
    number_of_elements: int
    number_of_minifigures: int
    date: datetime.date
    operation: str
    changed_on: datetime.datetime
    accepted: bool

    def get_differences(self, other):
        differences = {}
        for field in self.__annotations__:
            if field in ["accepted", "log_id", "changed_on"]:
                continue
            if getattr(self, field) != getattr(other, field):
                differences[field] = [getattr(self, field), getattr(other, field)]
        return differences

    @classmethod
    def create_from_tuple(cls, data_tuple):
        return MainDataLog(*data_tuple)
