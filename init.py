#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script d'initialisation des sections hebdomadaires / mensuelles

# (C) Linedwell, 2011-2016
#
# Distribué sous licence GNU GPLv3
# Distributed under the terms of the GNU GPLv3 license
# http://www.gnu.org/licenses/gpl.html

import sys
sys.path.insert(1, '..') #ajoute au PYTHONPATH le répertoire parent

import pywikibot
import time
from datetime import date

# Variables temporelles
dt = date.today()
yr = int(dt.strftime('%Y'))
mt = dt.strftime('%m')
wk = dt.isocalendar()[1]
if wk > 52:
    yr += 1
    wk -= 52
if wk < 10:
    wk = '0'+ str(wk)
    wk = str(wk)

# Listes de pages
## Wikipedia
dicoWP = {
    'site' : pywikibot.Site('fr','wikipedia'),
    'pagesList' : [u'Wikipédia:Bulletin des administrateurs/%s/Semaine %s' % (str(yr),str(wk))],
    'pagesHeader' : [u'<noinclude>{{Wikipédia:Bulletin des administrateurs/en-tête court|année='+ str(yr) +u'}}</noinclude>'],
    'summary' : u'[[WP:Bot|Robot]] : initialisation de sous-page périodique'
}

##Vikidia
dicoVD = {
    'site' : pywikibot.Site('fr','vikidia'),
    'pagesList' : [u'Vikidia:Bavardages/%s/%s' % (str(yr),str(wk)), u'Vikidia:La cabane/%s/%s' % (str(yr), str(mt)), u'Vikidia:Bulletin des administrateurs/%s %s' % (str(yr),str(mt)), u'Vikidia:Demandes aux administrateurs/%s %s' % (str(yr),str(mt))],
    'pagesHeader' : [u'{{subst:Vikidia:Bavardages/Initialisation}}',u'<noinclude>{{Vikidia:La cabane/Navigation|année='+str(yr)+u'}}</noinclude>',u'<noinclude>{{Vikidia:Bulletin des administrateurs/Navigation|année='+str(yr)+u'}}</noinclude>',u'<noinclude>{{Vikidia:Demandes aux administrateurs/Navigation|année='+str(yr)+u'}}</noinclude>'],
    'summary' : u'[[VD:Robot|Robot]] : initialisation de sous-page périodique'
}


#initialise les pages si besoin
def initPages(dico):
    index = 0
    for pageName in dico['pagesList']:
        page = pywikibot.Page(dico['site'],pageName)

        if not page.exists():
            pageTemp = dico['pagesHeader'][index]
            summary = dico['summary']
            page.text = pageTemp
            page.save(summary,force=True)

	else:
	    pywikibot.output(u"Page %s already exists; skipping."
                         % page.title(asLink=True))

	index += 1

#Exécution
def main():
    #timeStart = time.time()
    initPages(dicoWP)
    initPages(dicoVD)
    #initMonthlyPages()
    #timeEnd = time.time()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
