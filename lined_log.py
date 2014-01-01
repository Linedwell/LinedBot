#!/usr/bin/python
# -*- coding: utf-8 -*-
# author : [[fr:User:Linedwell]]

import sys
sys.path.insert(1, '..') #ajoute au PYTHONPATH le répertoire parent

import time
import pywikibot

#Variables globales

site = pywikibot.getSite()
summaryHeader = {
    'wikipedia' : u'[[WP:Bot|Robot]] : ',
    'vikidia' : u'[[VD:Robot|Robot]] : ',
}


#Met à jour la page de journalisation du bot
def editLog(site,log,page='Utilisateur:LinedBot/Log',summary='',ar=True):
    if log != '':
        family = site.family.name
        year = time.strftime('%Y')
        month = [u'',u'Janvier',u'Février',u'Mars',u'Avril',u'Mai',u'Juin',u'Juillet',u'Août',u'Septembre',u'Octobre',u'Novembre',u'Décembre']
        pageLog = pywikibot.Page(site,page)
        pageArchive = pywikibot.Page(site,pageLog.title() + '/' + str(int(year) - 1))
        if ar and not pageArchive.exists():
            pageLogTemp = archive(site,pageLog,pageArchive)
        else:
            pageLogTemp = pageLog.get()
        if pageLogTemp.find(u'== ' + month[int(time.strftime('%m'))] + ' ==') == -1: pageLogTemp += u'\n\n== ' + month[int(time.strftime('%m'))] + ' =='
        if pageLogTemp.find(u'== ' + time.strftime('%Y-%m-%d') + ' ==') != -1: pageLogTemp += '\n' + log
        else :
            pageLogTemp += '\n' + u'=== ' + time.strftime('%Y-%m-%d') + ' ===\n' + log
        if summary == '':
            summary = summaryHeader[family] + u"Mise à jour du journal (OK:" + str(nbrModif) + ", KO:" + str(nbrTotal - nbrModif) +")"
        else:
            summary= summaryHeader[family] + summary

        pageLog.put(pageLogTemp,summary)

#Archive la page de journalisation du bot et réinitialise la page pour la nouvelle année
def archive(site,pageLog,pageArchive):
    family = site.family.name
	pageLog.move(pageArchive.title(),u'Archivage annuel') #Déplacement de pageLog vers pageArchive
	pageArchive = pywikibot.Page(site,pageArchive.title())
	
	#Retrait du modèle de mise à jour de pageArchive
	pageArchiveTemp = pageArchive.get(get_redirect=True)
	pageArchiveTemp = pageArchiveTemp.replace(u'{{Mise à jour bot|Linedwell}}\n','',1)
	summary = summaryHeader[family] + u"Retrait de {{Mise à jour bot}}, page d'archive n'étant plus mise à jour"
	pageArchive.put(pageArchiveTemp,summary,force=True)
	
	pageLogTemp = u'__NOINDEX__\n{{Mise à jour bot|Linedwell}}\n{{Sommaire|niveau=1}}\n' #On réinsère le modèle de màj sur pageLog
	return pageLogTemp

def setValues(nbTotal, nbModif):
	global nbrTotal, nbrModif
	nbrTotal = nbTotal
	nbrModif = nbModif