#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script indiquant les changements récents (ajouts / retraits) dans la Catégorie:Admissibilité à vérifier
# Auteur: Linedwell
# Licence: <à définir>

import sys
sys.path.insert(1, '..') #ajoute au PYTHONPATH le répertoire parent

import pywikibot
from pywikibot import pagegenerators
import time

import lined_log

# Déclarations
site = pywikibot.getSite('fr','wikipedia')
nbrModif = 0
nbrTotal = 0

def admissibilite(pagesList):
    log = u''
    backupList = loadBackupFile()
    actualList = titleList(pagesList)

    addList = list(set(actualList) - set(backupList))
    remList = list(set(backupList) - set(actualList))

#Return the content of the given category (only pages from namespace 0)
def getCategoryContent(catname):
    cat = pywikibot.Category(site,catname)
    pagesInCat = list(cat.articles(False))
    pagesList = pagegenerators.PreloadingGenerator(pagesInCat) # On génère la liste des pages incluses dans la catégorie
    pagesList = pagegenerators.NamespaceFilterPageGenerator(pagesList,[0]) #On ne garde que les articles (Namespace 0)
    
    return pagesList

#Return the list of titles from pagesList
def titleList(pagesList):
    list = []
    for page in pagesList:
        list.append(page.title())
    
    return list

#Save a list to the backup file
def saveBackupFile(list):
    file = open("_admissibilite.bak","w+")
    for s in list:
        file.write(s.encode('utf-8') + '\n')
    file.close()

#Load a list from the backup file
def loadBackupFile():
    file = open("_admissibilite.bak","r")
    oldList = file.readlines()
    oldList = [s.strip('\n') for s in oldList]
    oldList = [s.decode('utf-8') for s in oldList]
    file.close()
    
    return oldList


#Exécution
def main():
    log = u''
    timeStart = time.time()
    catname = u"Tous les articles dont l'admissibilité est à vérifier"
    pagesList = getCategoryContent(catname)
    log += admissibilite(pagesList)
    ###
    timeEnd = time.time()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
