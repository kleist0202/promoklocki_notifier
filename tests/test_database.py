from promoklocki_notifier.promo_database import DataBase
import pytest
import os


@pytest.fixture
def test_database():
    # Set up a test database and return the DataBase instance with test credentials
    postgres_ip = os.environ.get("POSTGRES_HOST", "localhost")
    test_db_credentials = ("promo_database", "promo_manager", "promo", postgres_ip, "5432")
    return DataBase(test_db_credentials)


def test_database_connection(test_database):
    # Test that the database connection is established successfully
    assert test_database.conn is not None
