ALTER DATABASE promo_database SET TIMEZONE='Europe/Warsaw';

CREATE TABLE lego_main_info
(
    catalog_number INTEGER PRIMARY KEY UNIQUE NOT NULL,
    production_link VARCHAR ( 200 ),
    name VARCHAR ( 200 ),
    lowest_price NUMERIC(10, 2),
    number_of_elements INTEGER,
    number_of_minifigures INTEGER,
    date DATE
);

CREATE TABLE lego_main_info_log
(
    log_id BIGSERIAL PRIMARY KEY UNIQUE NOT NULL,
    catalog_number INTEGER NOT NULL,
    production_link VARCHAR ( 200 ),
    name VARCHAR ( 200 ),
    lowest_price NUMERIC(10, 2),
    number_of_elements INTEGER,
    number_of_minifigures INTEGER,
    date DATE,
    operation CHAR ( 1 ),
    changed_on TIMESTAMP DEFAULT NOW(),
    accepted BOOLEAN DEFAULT FALSE
);

CREATE OR REPLACE FUNCTION log_lego_main_info_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO lego_main_info_log (catalog_number, production_link, name, lowest_price, number_of_elements, number_of_minifigures, date, operation)
        VALUES (NEW.catalog_number, NEW.production_link, NEW.name, NEW.lowest_price, NEW.number_of_elements, NEW.number_of_minifigures, NEW.date, 'I');
    ELSIF TG_OP = 'UPDATE' THEN
        IF (OLD.catalog_number, OLD.production_link, OLD.name, OLD.number_of_elements, OLD.number_of_minifigures, OLD.date) IS DISTINCT FROM
           (NEW.catalog_number, NEW.production_link, NEW.name, NEW.number_of_elements, NEW.number_of_minifigures, NEW.date) OR ABS(NEW.lowest_price - OLD.lowest_price) > 1.00
        THEN
            INSERT INTO lego_main_info_log (catalog_number, production_link, name, lowest_price, number_of_elements, number_of_minifigures, date, operation)
            VALUES (NEW.catalog_number, NEW.production_link, NEW.name, NEW.lowest_price, NEW.number_of_elements, NEW.number_of_minifigures, NEW.date, 'U');
        END IF;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO lego_main_info_log (catalog_number, production_link, name, lowest_price, number_of_elements, number_of_minifigures, date, operation)
        VALUES (OLD.catalog_number, OLD.production_link, OLD.name, OLD.lowest_price, OLD.number_of_elements, OLD.number_of_minifigures, OLD.date, 'D');
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER main_table_trigger
AFTER INSERT OR UPDATE OR DELETE ON lego_main_info
FOR EACH ROW
EXECUTE FUNCTION log_lego_main_info_changes();
