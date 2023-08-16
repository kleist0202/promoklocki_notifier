from datetime import datetime
from promoklocki_notifier.promo_database import DataBase
from promoklocki_notifier.promo_models import MainData
import pytest
import os
import psycopg2


@pytest.fixture(scope="session")
def correct_data():
    sample_data = MainData(
        catalog_number=11111,
        production_link="https://test.com",
        name="set1",
        lowest_price=100.0,
        number_of_elements=10,
        number_of_minifigures=3,
        date=datetime(2023, 5, 20, 0, 0, 0),
    )
    return sample_data


@pytest.fixture(scope="session")
def incorrect_data():
    sample_data = MainData(
        catalog_number=11111,
        production_link="https://test.com",
        name="set1",
        lowest_price="xyz",
        number_of_elements=10,
        number_of_minifigures=3,
        date=datetime(2023, 5, 20, 0, 0, 0),
    )
    return sample_data


@pytest.fixture(scope="session")
def test_database():
    # Set up a test database and yield the DataBase instance with test credentials
    postgres_ip = os.environ.get("POSTGRES_HOST", "localhost")
    test_db_credentials = (
        "promo_database",
        "promo_manager",
        "promo",
        postgres_ip,
        "5432",
    )
    db = DataBase(test_db_credentials)
    print("----------------------- Create db -----------------------")
    yield db
    print("----------------------- Disconnect from database -----------------------")
    db.close()


def test_database_connection(test_database):
    print("----------------------- Test connection -----------------------")
    assert test_database.conn is not None


def test_add_basic_info(test_database, correct_data):
    test_database.add_basic_info(correct_data)


def test_incorrect_add_basic_info(test_database, incorrect_data):
    with pytest.raises(psycopg2.errors.InvalidTextRepresentation):
        test_database.add_basic_info(incorrect_data)
    test_database.conn.rollback()


def test_get_products_reverse(test_database: DataBase, correct_data: MainData):
    data = test_database.get_products_reverse()
    data = data[0]
    print(data, correct_data)
    assert data.catalog_number == correct_data.catalog_number
    assert data.lowest_price == correct_data.lowest_price
    assert data.name == correct_data.name
    assert data.number_of_elements == correct_data.number_of_elements
    assert data.number_of_minifigures == correct_data.number_of_minifigures
    assert data.production_link == correct_data.production_link
    assert data.date == correct_data.date.date()


def test_select_all_logs(test_database: DataBase):
    logs = test_database.select_all_logs()
    assert len(logs) == 1


def test_accept_logs(test_database: DataBase):
    logs = test_database.select_all_logs()
    assert logs[0].accepted is False
    test_database.accept_log(logs[0].log_id)
    logs = test_database.select_all_logs()
    assert logs[0].accepted is True
