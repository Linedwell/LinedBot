#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script indiquant les changements récents (ajouts / retraits) dans la Catégorie:Admissibilité à vérifier

# (C) Linedwell, 2011-2018
#
# Distribué sous licence GNU GPLv3
# Distributed under the terms of the GNU GPLv3 license
# http://www.gnu.org/licenses/gpl.html


import sys
sys.path.insert(1, '..') #ajoute au PYTHONPATH le répertoire parent

import time
import shutil

import mylogging

import pywikibot
from pywikibot import pagegenerators
import callback
import logger
import grapher

# Déclarations
site = pywikibot.Site('fr', 'wikipedia')

def admissibilite(pagesList):
    log = u''
    nbAdd = 0
    nbRem = 0
    backupList = loadBackupFile()
    actualList = titleList(pagesList)
    total = len(actualList)

    addList = list(set(actualList) - set(backupList))
    remList = list(set(backupList) - set(actualList))

    for add in addList:
        log += u"* {{Vert|'''+'''}} ajout du bandeau sur [[%s]]\n" %(add)
        nbAdd += 1

    for rem in remList:
        log += u"* {{Rouge|'''-'''}} retrait du bandeau sur [[%s]]\n" %(rem)
        nbRem += 1

    saveBackupFile(actualList)

    summary = u"Mise à jour (+%s; -%s; =%s)" %(nbAdd, nbRem, total)

    return log, summary, total

#Return the content of the given category (only pages from namespace 0)
def getCategoryContent(catname):
    cat = pywikibot.Category(site, catname)
    pagesInCat = list(cat.articles(False))
    pagesList = pagegenerators.PreloadingGenerator(pagesInCat) # On génère la liste des pages incluses dans la catégorie
    pagesList = pagegenerators.NamespaceFilterPageGenerator(pagesList, [0]) #On ne garde que les articles (Namespace 0)
    
    return pagesList

#Return the list of titles from pagesList
def titleList(pagesList):
    tlist = []
    for page in pagesList:
        tlist.append(page.title())
    
    return tlist

#Save a list to the backup file
def saveBackupFile(tlist):
    bfile = open('_admissibilite.bak', 'w+')
    for s in tlist:
        bfile.write(s.encode('utf-8') + '\n')
    bfile.close()

#Load a list from the backup file
def loadBackupFile():
    bfile = open('_admissibilite.bak', 'r')
    oldList = bfile.readlines()
    oldList = [s.strip('\n') for s in oldList]
    oldList = [s.decode('utf-8') for s in oldList]
    bfile.close()
    
    return oldList


#Exécution
def main():
    log = u''
    timeStart = time.time()
    shutil.copyfile('_admissibilite.bak', '_admissibilite.bak.bak')
    catname = u"Tous les articles dont l'admissibilité est à vérifier"
    pagesList = getCategoryContent(catname)
    log, summary, total = admissibilite(pagesList)
    grapher.update(total)
    logger.editLog(site, log, page=u"Projet:Maintenance/Suivi d'admissibilité", summary=summary, ar=False, cl=15)
    pywikibot.output(summary)
    timeEnd = time.time()
    pywikibot.output(u"%s in %s s."
                        %(summary, round(timeEnd-timeStart, 2)))


if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
