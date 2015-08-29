#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script de nettoyage du bac à sable de Vikidia

# (C) Linedwell, 2011-2015
#
# Distribué sous licence GNU GPLv3
# Distributed under the terms of the GNU GPLv3 license
# http://www.gnu.org/licenses/gpl.html

import sys
sys.path.insert(1, '..') #ajoute au PYTHONPATH le répertoire parent

import pywikibot
import time
from datetime import date, datetime, timedelta

# Déclarations
site = pywikibot.Site('fr','vikidia')
page = pywikibot.Page(site,u"Vikidia:Bac à sable")
template = u"{{subst:Vikidia:Bac à sable/Zéro}}"
summary = u"[[Vikidia:Robot|Robot]] : Nettoyage du bac à sable"


siteit = pywikibot.Site('it','vikidia')
pageit = pywikibot.Page(siteit,u"Vikidia:Area giochi")
templateit = u"{{subst:Vikidia:Area giochi/Zero}}"
summaryit = u"[[Vikidia:Bot|Bot]] : Pulizia dell'area giochi"


delay = 30

#BUGFIX
site.login()
#END OF FIX


#Recharge le bac à sable avec un contenu prédéfini
def clean(page,template,summary,delay):
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
    clean(page,template,summary,delay) #nettoyage fr
    clean(pageit,templateit,summaryit,delay) #nettoyage it

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
