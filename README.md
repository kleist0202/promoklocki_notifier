# Promoklocki notifier
![Tests](https://github.com/kleist0202/promoklocki_notifier/actions/workflows/tests.yml/badge.svg)

Program that scraps ![promoklocki.pl](https://promoklocki.pl) site and notifies about lego set's price changes.
It uses *notify-send* and *dunst* for notifications. And currently works (was tested) only on linux.

# Setup
The best way would be to create virtual environment:  

`python -m venv env`

Then activate it:  

`source env/bin/activate`

Install it with pip, running below command in project directory:  

`pip install -e .`

You might want to configure database connection in *src/promoklocki_notifier/config.ini* file.
Currently it is configured to run with postgres docker container. To test it run:

`docker compose up -d`

Now to run scrapper:

`./env/bin/promo_start`

And program to to see logs:

`./env/bin/promo_cli`

You can install services that will run every 30 minutes by default:

`sudo make install USER_ENV=$USER`

Service will look for script at: */home/$USER/.local/bin/promo_start*. So you might need to install it via **pipx** (see below).

### System wide installation
You can install this package system wide using ***pipx***. Just run command below in root package directory:

```
pipx install .
```

It will most probably be installed in *~/.local/bin*, so make sure it is in your *$PATH*.
