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

summary = {
    'fr' : u'[[Vikidia:Robot|Robot]] : mise à jour des interwikis',
    'it' : u'Bot : interwiki update',
    'es' : u'Bot : interwiki update',
    'ru' : u'Bot : interwiki update',
}


nbrModif = 0
nbrTotal = 0

def inter(page):
    pageTemp = page.get()
    iwList = list(getInterwiki(page))
    pageLang = page.site.lang
    
    allList = []
    allList.append(pywikibot.Link(page.title(), page.site))
    
    #premier tour pour récupérer la liste des intervikis (valides)
    for iw in iwList:
        lang = iw.site.lang
        pageExt = pywikibot.Page(site[lang],iw.title)
        if not pageExt.exists():
            link = iw.astext()
            pageTemp = pageTemp.replace(link+'\n','')
            pageTemp = pageTemp.replace(link,'') #necessaire si dernier lien
        else:
            allList.append(iw)

    page.put(pageTemp,summary[pageLang])


    #second tour pour la mettre à jour sur tous les autres vikis
    for a in allList[1:]:
        linkList = list(allList)
        linkList.remove(a)
        
        pageLoc = pywikibot.Page(a.site,a.title)
        
        localIwList = list(getInterwiki(pageLoc))
        
        pageLocTemp = pageLoc.get()
        
        #retrait des interviki non valides (non liés depuis le viki source)
        for liw in localIwList:
            if not liw in linkList:
                link = liw.astext()
                pageLocTemp = pageLocTemp.replace(link+'\n','')
                pageLocTemp = pageLocTemp.replace(link,'') #necessaire si dernier lien

        #ajout des nouveaux interviki
        for lnk in linkList:
            if not lnk in localIwList:
                link = lnk.astext(onsite=a.site) #on force le lien à être "vu" depuis le wiki de destination
                pageLocTemp += '\n' + link

        pageLoc.put(pageLocTemp, summary[a.site.lang])



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
    page = pywikibot.Page(site[lang],u'Turin')
    inter(page)
    timeEnd = time.time()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()