import logging
import requests


def scrape(configs, morestuff):
    logger = logging.getLogger("scrap_logger");
    logger.debug("Starting esl scrape");
    
    url = "https://play.eslgaming.com/leagueoflegends/eu-west/tournaments"

    res = requests.get(url);
    try:
        res.raise_for_status()
    except Exception as exc:
        logger.error("Couldn't download the html file");
        logger.debug(exc);

    #speichern der html-datei, später nicht mehr nötig
    dfile = open("tmpsave.txt", "wb")
    for chunk in res.iter_content(100000):
        dfile.write(chunk)

    dfile.close()

#hab nen bisschen getestet, eigentlich sollte requests für esl perfekt gehen, aber in der herutergeladenen datei ist die league-list noch leer, irgendwie muss man die doch mit laden können, suche später dannach weiter
