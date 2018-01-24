#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script de maintenance pour vikidia


# (C) Linedwell, 2011-2018
#
# Distribué sous licence GNU GPLv3
# Distributed under the terms of the GNU GPLv3 license
# http://www.gnu.org/licenses/gpl.html

import sys, getopt
sys.path.insert(1, '..') #ajoute au PYTHONPATH le répertoire parent

import mylogging

import re, time
from datetime import date, datetime, timedelta

import pywikibot
from pywikibot import pagegenerators

import callback
import logger


# Déclarations
site = pywikibot.Site('fr','vikidia')

# Traitement des nouvelles pages
def cleanWIP(delay):
    limit = calcLimit(delay)
    log = u''
      
    wipCat = pywikibot.Category(site,u"Article en travaux")
    wipPages = list(wipCat.articles(False))
    pagesList = pagegenerators.PreloadingGenerator(wipPages) # On génère la liste des pages incluses dans la catégorie
    pagesList = pagegenerators.NamespaceFilterPageGenerator(pagesList,[0]) #On ne garde que les articles (Namespace 0)


    for page in pagesList:
        
        try:
            pageTemp = page.get()
            
        except pywikibot.NoPage:
            pywikibot.output(u"Page %s does not exist; skipping."
                             % page.title(asLink=True))
        except pywikibot.IsRedirectPage:
            pywikibot.output(u"Page %s is a redirect; skipping."
                             % page.title(asLink=True))
        except pywikibot.LockedPage:
            pywikibot.output(u"Page %s is locked; skipping."
                             % page.title(asLink=True))
        else:
        	summary = u''
        	lastEdit = page.editTime()

        	if lastEdit < limit:
				duration = calcDuration(lastEdit)
				pageTemp, templateResult = removeTemplate(pageTemp)
				summary = u"[[VD:Robot|Robot]] : Retrait du bandeau %s (article non modifié depuis plus de %s jours)" %(templateResult,duration.days)
				pywikibot.showDiff(page.text, pageTemp)
				print summary
				page.save(summary)
            
    return log

#Retourne la date avant laquelle on considère obsolète l'usage du modèle
def calcLimit(delay):
	today = datetime.utcnow()
	limite = today - timedelta(seconds=delay)
	return limite

#Retourne le temps écoulé entre une date et le jour courant
def calcDuration(date):
	today = datetime.utcnow()
	duration = today - date
	return duration

# Retrait du bandeau si besoin
def removeTemplate(pageTemp):
	templateResult = ''
	parser = re.compile(r'{{(En)?Trav(ail|aux)(?:\|.*?)?}}(?P<fin>\r\n|\n|\ )?',re.I | re.U | re.DOTALL)
	searchResult = parser.search(pageTemp)
	if searchResult:
		pageTemp = parser.sub('',pageTemp,1)
		templateResult = searchResult.group()
		templateResult = templateResult.replace('\r\n','') #Retire les sauts de ligne contenus dans le modèle avant de l'ajouter au résumé
		templateResult = templateResult.replace('\n','') #Correspond au second type de retour à la ligne
	return pageTemp, templateResult

# Exécution
def main():
    cleanWIP(delay=15552000)

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
