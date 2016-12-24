#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script XXXX

# (C) Linedwell, 2011-2016
#
# Distribué sous licence GNU GPLv3
# Distributed under the terms of the GNU GPLv3 license
# http://www.gnu.org/licenses/gpl.html


import sys
sys.path.insert(1, '..') #ajoute au PYTHONPATH le répertoire parent

import mylogging

import pywikibot
import time

# Déclarations
site = pywikibot.Site('fr','wikipedia')
nbrModif = 0
nbrTotal = 0


# Récupère la liste des éditions du compte ciblé au cours du délai donné
def getRecentEdits(userName,timestamp):
    recentEdits = site.usercontribs(user=userName,top_only=True,end=timestamp)
    print u"Number of recent edits for " + userName + " : " + str(len(list(recentEdits)))
    acceptAll = False
    
    for edit in recentEdits:
        page = pywikibot.Page(site,edit[u'title'])
        hist = page.getVersionHistory()
        
        previous_revision = ()
    
        for hist_entry in hist:
            #On renvoit la revision précédant celle(s) de <userName>
            if hist_entry.user != userName:
                previous_revision = hist_entry.revid, hist_entry.user
                break
        
        oldVersion = page.getOldVersion(previous_revision[0])

        # Affichage du diff
        pywikibot.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<"
                 % page.title())
        pywikibot.showDiff(page.text,oldVersion)
        summary = u"Révocation massive des modifications de %s (retour à la version de %s)" %(userName,previous_revision[1]);
        

        if not acceptAll:
            choice = pywikibot.input_choice(u'Do you want to accept these changes?',
                                            [('Yes', 'y'), ('No', 'n'), ('All', 'a')], 'N')


            if choice == 'a':
                acceptAll = True
            
            elif choice == 'n':
                continue

        if acceptAll or choice == 'y':
            try:
                page.text = oldVersion
                page.save(summary)

            except pywikibot.EditConflict:
                pywikibot.output(u"Skipping %s because of edit conflict"
                     % (page.title(),))
            except pywikibot.SpamfilterError, e:
                pywikibot.output(u"Cannot change %s because of blacklist entry %s"
                             % (page.title(), e.url))
            except pywikibot.PageNotSaved, error:
                pywikibot.output(u"Error putting page: %s"
                                % (error.args,))
            except pywikibot.LockedPage:
                pywikibot.output(u"Skipping %s (locked page)"
                                % (page.title(),))



# Exécution
def main():
    if len(sys.argv) > 2:
        timeStart = time.time()
        user = sys.argv[1]
        timestamp = sys.argv[2]
        getRecentEdits(user,timestamp)
        timeEnd = time.time()
    else:
        print "usage: python " + sys.argv[0] + " <target> <YYYY-mm-ddTHH:MM:SSZ>"
        exit(2)

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
