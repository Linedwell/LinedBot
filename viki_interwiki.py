#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script d'ajout des liens interwiki
# Auteur: Linedwell
# Licence: <à définir>

import sys
sys.path.insert(1, '..') #ajoute au PYTHONPATH le répertoire parent

import pywikibot
from pywikibot import pagegenerators
import time
import itertools

# Déclarations
site = {
	'fr' : pywikibot.getSite('fr','vikidia'),
	'es' : pywikibot.getSite('es','vikidia'),
	'it' : pywikibot.getSite('it','vikidia'),
	'ru' : pywikibot.getSite('ru','vikidia'),
}


frwiki = pywikibot.getSite('fr','wikipedia')
enwiki = pywikibot.getSite('simple','wikipedia')
nbrModif = 0
nbrTotal = 0

def inter(page):
    page.get()
    iwList = getInterwiki(page)
    for iw in iwList:
        print pywikibot.Page(site[iw.site.lang],iw.title).get()




def getInterwiki(page, expand=True):
    if expand:
        text = page.expand_text()
    else:
        text = page.text
    for linkmatch in pywikibot.link_regex.finditer(pywikibot.removeDisabledParts(text)):
        linktitle = linkmatch.group("title")
        link = pywikibot.Link(linktitle, page.site)
        try:
            if link.site != page.site:
                yield link
        except pywikibot.Error:
            continue




#Exécution
def main():
    timeStart = time.time()
    lang = 'fr'
    pg = pywikibot.Page(site[lang],u'Turin')
    inter(pg)
    timeEnd = time.time()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()