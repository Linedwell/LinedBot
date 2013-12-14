#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script permettant de révoquer les modifications récentes d'un utilisateur donné
# Auteur: Linedwell
# Licence: <à définir>

import sys
sys.path.insert(1, '..') #ajoute au PYTHONPATH le répertoire parent

import pywikibot
from pywikibot import pagegenerators
import time
from datetime import date, datetime, timedelta

# Déclarations
site = pywikibot.getSite('fr','wikipedia')
nbrModif = 0
nbrTotal = 0


def mass_rollback(user,delay):
	contribs = pagegenerators.UserContributionsGenerator(user)
	limit = calcLimit(delay)
	for c in contribs:
		if c.editTime() > limit:
			if c.userName() == user:
				print c.title() + " : " + str(c.editTime()) + " < " + str(limit)
		else:
			break
	print "yoo"

#Retourne la date jusqu'à laquelle on souhaite révoquer
def calcLimit(delay):
	today = datetime.utcnow()
	limite = today - timedelta(seconds=delay)
	return limite

#Exécution
def main():
    timeStart = time.time()
    delay = 60*15
    mass_rollback(u"Linedwell",delay)
    timeEnd = time.time()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
