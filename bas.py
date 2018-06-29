#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script de nettoyage du bac à sable de Vikidia

# (C) Linedwell, 2011-2018
#
# Distribué sous licence GNU GPLv3
# Distributed under the terms of the GNU GPLv3 license
# http://www.gnu.org/licenses/gpl.html

import sys
sys.path.insert(1, '..') #ajoute au PYTHONPATH le répertoire parent

import mylogging

import pywikibot
import time
from datetime import datetime, timedelta

# Déclarations
dicoFR = {
    'site' : pywikibot.Site('fr','vikidia'),
    'page' : u"Vikidia:Bac à sable",
    'template' : u"{{subst:Vikidia:Bac à sable/Zéro}}",
    'summary' : u"[[Vikidia:Robot|Robot]] : Nettoyage du bac à sable",
    'delay' : 30,
}

dicoIT = {
    'site' : pywikibot.Site('it','vikidia'),
    'page' : u"Vikidia:Area giochi",
    'template' : u"{{subst:Vikidia:Area giochi/Zero}}",
    'summary' : u"[[Vikidia:Bot|Bot]] : Pulizia dell'area giochi",
    'delay' : 30,
}


#Recharge le bac à sable avec un contenu prédéfini
def clean(dico):
    site = dico['site']
    page = pywikibot.Page(site,dico['page'])
    template = dico['template']
    summary = dico['summary']
    delay = dico['delay']
    if not page.userName() == site.user():
        limite = calcLimit(delay)
        if page.editTime() < limite:
            page.text = template
            page.save(summary)

#Calcule la "date" avant laquelle on s'autorise à blanchir le bas
def calcLimit(delay):
    today = datetime.utcnow()
    limit = today - timedelta(minutes=delay)
    return limit


#Exécution
def main():
    clean(dicoFR) #nettoyage fr
    clean(dicoIT) #nettoyage it

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
