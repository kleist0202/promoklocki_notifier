DATABASE_NAME := promo_database

IP := $(shell docker inspect -f \
		'{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(DATABASE_NAME))

SERVICES_DIR := services

USER :=

# Use the USER environment variable if available, otherwise get the current user
ifdef USER_ENV
    USER := $(USER_ENV)
else
    USER := $(shell whoami)
endif

install:
	cp ./$(SERVICES_DIR)/scrapper_notification@.service /etc/systemd/system/
	cp ./$(SERVICES_DIR)/scrapper_notification@.timer /etc/systemd/system/
	cp ./$(SERVICES_DIR)/scrapper_database@.service /etc/systemd/system/
	systemctl daemon-reload
	systemctl start scrapper_notification@$(USER).service
	systemctl start scrapper_notification@$(USER).timer
	systemctl start scrapper_database@$(USER).service
	systemctl enable scrapper_notification@$(USER).service
	systemctl enable scrapper_notification@$(USER).timer
	systemctl enable scrapper_database@$(USER).service

uninstall:
	systemctl disable scrapper_notification@$(USER).service
	systemctl disable scrapper_notification@$(USER).timer
	systemctl disable scrapper_database@$(USER).service
	systemctl stop scrapper_notification@$(USER).service
	systemctl stop scrapper_notification@$(USER).timer
	systemctl stop scrapper_database@$(USER).service
	systemctl daemon-reload
	rm /etc/systemd/system/scrapper_notification@.service
	rm /etc/systemd/system/scrapper_notification@.timer
	rm /etc/systemd/system/scrapper_database@.service

docker_run:
	docker-compose up -d

docker_clean:
	docker-compose stop
	docker-compose rm
	docker-compose down
	rm -rf ./db-data

docker_ip:
	@echo $(IP)

docker_connect:
	psql -h $(IP) -p 5432 -U promo_manager -d $(DATABASE_NAME)

tables:
	psql -U promo_manager -f tables.sql promo_database 


.PHONY: all run docker_run docker_connect docker_clean docker_ip tables install uninstall
