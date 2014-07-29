#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script de mise à jour semi-automatique de {{Avertissements d'homonymie restants}}

# (C) Linedwell, 2011-2014
#
# Distribué sous licence GNU GPLv3
# Distributed under the terms of the GNU GPLv3 license
# http://www.gnu.org/licenses/gpl.html

import sys
sys.path.insert(1, '..') #ajoute au PYTHONPATH le répertoire parent

import re
import time
#import locale
#locale.setlocale(locale.LC_TIME,'fr_fr') #remplacer 'fr_fr' par 'fra_fra' sur Windows
from datetime import datetime

import pywikibot
from pywikibot import pagegenerators

# Déclarations
site = pywikibot.getSite('fr','wikipedia')

#Met à jour le tableau récapitulatif
def disambigWarningUpdater(pageTemp,newNumber):
    pageTemp = re.split('(\|-\n)', pageTemp, maxsplit=3)
    pageTempBegin = u''.join(pageTemp[:-1])
    pageTempBody = u''.join(pageTemp[-1:])
    pageTempBody = re.split('\|\}\n',pageTempBody)
    pageTempEnd = u'|}\n' + u''.join(pageTempBody[-1:])
    pageTempBody = u''.join(pageTempBody[:-1])
    lastRaw = pageTempBody.rsplit('|-\n',1)[1]

    rawObj = rawParser(lastRaw)
    newRaw = rawMaker(rawObj,newNumber)

    pageTemp = pageTempBegin + pageTempBody + newRaw + pageTempEnd

    return pageTemp


#Convertit une ligne en "objet" utilisable
def rawParser(raw):
    rawItems = raw.split('|')
    
    id = ''.join(rawItems[1].split())
    date = ''.join(rawItems[2].split())
    number = ''.join(re.findall('\d+',rawItems[5]))
    
    rawObj = {
        'id' : id,
        'date' : date,
        'number' : number
    }

    return rawObj


#Génère la ligne supplémentaire du tableau, calculée à partir de la dernière ligne
def rawMaker(prevRaw, newNumber):
    
    oldId = int(prevRaw['id'])
    oldDate = prevRaw['date']
    oldNumber = int(prevRaw['number'])
    
    dateObj = datetime.today()
    date = dateObj.strftime('%d-%m-%Y').lstrip('0') #suppression du 0 initial
    
    oldDateObj = datetime.strptime(oldDate,'%d-%m-%Y')
    
    durationObj = dateObj - oldDateObj
    duration = str(durationObj.days) + ' jours'

    diffSize = newNumber - oldNumber
    diffPercent = (diffSize * 100.) / newNumber
    diffPercent = round(diffPercent,2)
    
    if diffSize > 0:
        diffColor = '{{rouge|+'
    else:
        diffColor = '{{vert|'

    newRaw = '|-\n| ' + str(oldId+1) + '\n| ' + date + '\n|| ' + duration + '\n| {{formatnum:' + str(newNumber) +'}} || ' + diffColor + str(diffPercent) + '%}}\n|| ' + diffColor + str(diffSize) + '}}\n'
    
    return newRaw


#Exécution
def main(args):
    if len(args) == 1:
        newNumber = int(args[0])
        target = u"Modèle:Avertissements d'homonymie restants"
        page = pywikibot.Page(site,target)
        
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
    
            pageTemp = disambigWarningUpdater(pageTemp,newNumber)
            
            if pageTemp != page.get():
                page.text = pageTemp
                page.save(u"[[WP:Bot|Robot]] : mise à jour")
            else:
                print u"Aucune mise à jour n'a été faite."
    else:
        print u"usage: python " + sys.argv[0] + " <number of pages>"
        sys.exit(2)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    finally:
        pywikibot.stopme()