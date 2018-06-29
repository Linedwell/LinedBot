#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script de génération de liste d'articles à traduire

# (C) Linedwell, 2011-2018
#
# Distribué sous licence GNU GPLv3
# Distributed under the terms of the GNU GPLv3 license
# http://www.gnu.org/licenses/gpl.html


import sys
sys.path.insert(1, '..') #ajoute au PYTHONPATH le répertoire parent

import re

import logging
logging.basicConfig(filename='log/translation_drive.log', format='%(asctime)s :: %(levelname)s :: %(message)s', level=logging.INFO)

import pywikibot
from pywikibot import textlib
import time

# Déclarations
site = {
    'fr' : pywikibot.Site('fr','vikidia'),
    'en' : pywikibot.Site('en','vikidia'),
    'es' : pywikibot.Site('es','vikidia'),
    'it' : pywikibot.Site('it','vikidia'),
    'scn' : pywikibot.Site('scn','vikidia'),
}

siteWP = {
    'fr' : pywikibot.Site('fr','wikipedia'),
    'en' : pywikibot.Site('en','wikipedia'),
    'es' : pywikibot.Site('es','wikipedia'),
    'it' : pywikibot.Site('it','wikipedia'),
    'scn' : pywikibot.Site('scn','wikipedia'),
}

translationPage = {
    'fr' : pywikibot.Page(site['fr'],'Utilisateur:LinedBot/Sandbox'),
}

summary = {
    'fr' : u"Mise à jour des listes d'articles à traduire"
}

nbrModif = 0
nbrTotal = 0

templateName = '/TranslationDrive'
projects = ['commons', 'incubator', 'mediawiki', 'meta', 'species', 'test',
            'wikibooks', 'wikidata', 'wikinews', 'wikipedia', 'wikiquote',
            'wikisource', 'wikiversity', 'wiktionary']


class TranslationDrive:


    def __init__(self, translatePage):
        self.translationLang = ['fr','en','es']
        self.translationParam = ['fr','en','es','nolink']
        self.translationPage = translatePage
        self.lang = translatePage.site.lang
        self.translateList = []



    # Recupere la liste des traductions demandées
    def getList(self):
        input_requests = textlib.extract_templates_and_params(self.translationPage.text)
        for row in input_requests:
            if row[0] == templateName:
                dicoTrans = {}
                for p in self.translationParam:
                    try:
                        #print row[1]
                        dicoTrans[p] = u"" + row[1][p]
                    except KeyError:
                        dicoTrans[p] = ''
                self.translateList.append(dicoTrans)
        return self.translateList


    def updateList(self):
        for row in self.translateList:
            index = 0
            #print row
            try:
                transSource = pywikibot.Page(site[self.lang],row[self.lang])
            except ValueError:
                nextlang = next(k for k,v in row.iteritems() if v)
                transSource = pywikibot.Page(site[nextlang],row[nextlang])
                #print transSource
            nolink = []
            for k, v in row.iteritems():
                if k in self.translationLang:
                    if not testPageinLang(v,k): #Si le lien pointe vers une page vide OU aucun
                        if testPageinLang(v,k) == None: #Si aucun lien
                            transTitle = findPageinLang(transSource, k)
                            row[k] = transTitle
                            if testPageinLang(transTitle, k):
                                continue #le lien pointe désormais vers une page existante
                        nolink.append(k)
                    elif testPageinLang(v,k):
                        try:
                            nolink.remove(k)
                        except ValueError:
                            pass
                row['nolink'] = ",".join(nolink)
                    #print k +  ": " + v + " = " + str(testPageinLang(v,k))
                    #self.translateList[index] = row
        return self.translateList


    def updateTranslationPage(self):
        delimiterStart = u"<!-- #START# -->"
        delimiterEnd = u"<!-- #END# -->"
        pageTempBody = ""
        pageTempStart, pageTempEnd = re.split(delimiterStart,self.translationPage.text)
        _, pageTempEnd = re.split(delimiterEnd,pageTempEnd)
        pageTempStart += delimiterStart + "\n"
        pageTempEnd = delimiterEnd + pageTempEnd
        
        for trans in self.translateList:
            row = "{{%s|"%templateName
            row += "|".join("%s=%s"%(k,v) for k, v in trans.iteritems())
            row += "}}"
            pageTempBody += row + "\n"
        
        self.translationPage.text = pageTempStart + pageTempBody +pageTempEnd
        print self.translationPage.text
        self.translationPage.save("[[VD:Robot]] : " + summary[self.lang])


# Teste l'existance des pages liées dans le tableau
def testPageinLang(title,lang):
    if title != '':
        pageToTest = pywikibot.Page(site[lang], title)
        return pageToTest.exists()


# Tente de trouver un interwiki vers l'article dans la langue demandée, si aucun résultat, essaie de le trouver en passant par Wikipedia.
def findPageinLang(pageOrigin, lang):
    titleinLang = ''
    originLang = pageOrigin.site.lang
    iwDict = getInterwiki(pageOrigin)
    try:
        titleinLang = str(iwDict[site[lang]].title)
    except KeyError:
        # Il n'y a pas d'interwiki local, on va chercher via Wikipedia
        try:
            pageinWP = iwDict[siteWP[originLang]]
            iwDict = list(pywikibot.Page(pageinWP).langlinks())
            for iw in iwDict:
                if iw.site == siteWP[lang]:
                    titleinLang = iw.title
        except KeyError:
            titleinLang = ""
    return titleinLang

#print iwDict


#Récupération de la liste des interwikis "réguliers"
def getInterwiki(page):
    text = page.text
    iwDict = {}
    
    for linkmatch in pywikibot.link_regex.finditer(pywikibot.textlib.removeDisabledParts(text)):
        
        linktitle = linkmatch.group("title")
        link = pywikibot.Link(linktitle, page.site)
        #print link.site
        
        try:
            if link.site != page.site:
                iwDict[link.site] = link
        #yield link
        except pywikibot.Error:
            continue

    return iwDict


#Exécution
def main():
    timeStart = time.time()
    page = translationPage['fr']
    transDrive = TranslationDrive(page)
    print transDrive.getList()
    transDrive.updateList()
    transDrive.updateTranslationPage()
    #page = pywikibot.Page(site['fr'],'Skidbladnir')
    #print findPageinLang(page,'scn')
    #print list(translationPage['fr'].linkedPages())
    
    
    
    timeEnd = time.time()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
