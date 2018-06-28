#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script de mise à jour des modèles de protection

# (C) Linedwell, 2011-2017
#
# Distribué sous licence GNU GPLv3
# Distributed under the terms of the GNU GPLv3 license
# http://www.gnu.org/licenses/gpl.html

import sys
sys.path.insert(1, '..') #ajoute au PYTHONPATH le répertoire parent

import mylogging

import re, time

import pywikibot
from pywikibot import pagegenerators


# Déclarations
site = pywikibot.Site('fr','wikipedia')
nbrModif = 0
nbrTotal = 0


# Récupération des pages avec un modèle de protection inadapté
def getPagesList():
	cat = pywikibot.Category(site,u'Catégorie:Page dont la protection est à vérifier')
	pagesInCat = list(cat.articles(False))
    	pagesList = pagegenerators.PreloadingGenerator(pagesInCat)
    	pagesList = pagegenerators.NamespaceFilterPageGenerator(pagesList,[0]) #On ne garde que les articles (Namespace 0)

	return pagesList

# Mets à jour le modèle de protection présent sur une page afin de correspondre à la protection effective
def updatePage(page):
	protlev = getProtectionLevel(page)
	pywikibot.output(u"Current protection level: %s"
                                 % (protlev,))
	pageTemp = page.get()
	pageTempNew = updateEditProtectionTemplate(pageTemp, protlev[0])
	pageTempNew = updateMoveProtectionTemplate(pageTempNew, protlev[1])
	pywikibot.showDiff(pageTemp, pageTempNew)
	sk = raw_input()
	if sk != '':
		return
	summary = u"[[WP:Bot|Robot]] : Mise à jour du modèle de protection"
	page.text = pageTempNew
	page.save(summary)

# Récupère sous forme de tuple les niveaux de protection en écriture et en renommage de la page, None si aucune protection en cours
def getProtectionLevel(page):
        prot = page.protection()
	pl_ed = None
	pl_mv = None
        if u'edit' in prot: # Si la page est actuellement protégée en écriture
                pl_ed = prot[u'edit'][0]

	if u'move' in prot: # Si la page est actuellement protégée en renommage
		pl_mv = prot[u'move'][0]

        return (pl_ed, pl_mv)

# Retrait du modèle précédent et ajout si nécessaire du modèle de protection adéquat
def updateEditProtectionTemplate(text, protlev):
	motif = [u'SP(E)?',u'[Ss]emi-protégé',u'([Ss]emi[- ])?[Pp]rotection([_ ](étendue|(?P<SPL>longue)))?']

	protTemplate = {
		'autoconfirmed' : u'{{Semi-protection}}',
		'editextendedsemiprotected' : u'{{Semi-protection étendue}}',
		'sysop' : u'{{Protection}}',
	}

        for m in motif:
	        parser = re.compile(r'{{' + m + r'.*?}}(\s*?|(?={{))', re.U | re.DOTALL)
              	searchResult = parser.search(text) #On cherche si le motif {{m}} existe dans la page
                if searchResult:
		        pywikibot.output(u"Template found: %s" % searchResult.group())
                        text = parser.sub('',text,1) #Retire la 1re occurrence du motif dans la page
			if protlev and searchResult.group('SPL'):
				text = u'{{Semi-protection longue}}' + '\n' + text
			elif protlev: 
				text = protTemplate[protlev] + '\n' + text
	#print text
	return text

def updateMoveProtectionTemplate(text, protlev):
        motif = [u'Nom[_ ]protégé']

        for m in motif:
                parser = re.compile(r'{{' + m + r'}}(\s*?|(?={{))',re.I | re.U | re.DOTALL)
                searchResult = parser.search(text) #On cherche si le motif {{m}} existe dans la page
                if searchResult:
                        pywikibot.output(u"Template found: %s" % searchResult.group())
			if not protlev:
                        	text = parser.sub('',text,1) #Retire la 1re occurrence du motif dans la page
        #print text
        return text




#Exécution
def main():
    timeStart = time.time()
    pagesList = getPagesList()

    for page in pagesList:
	pywikibot.output("Checking %s;" % page.title(asLink=True))
        updatePage(page)

    timeEnd = time.time()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
