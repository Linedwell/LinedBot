#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script d'accueil pour vikidia


# (C) Linedwell, 2011-2018
#
# Distribué sous licence GNU GPLv3
# Distributed under the terms of the GNU GPLv3 license
# http://www.gnu.org/licenses/gpl.html

import sys, getopt
sys.path.insert(1, '..') #ajoute au PYTHONPATH le répertoire parent

import mylogging

import re, time
from datetime import timedelta

from random import choice

import pywikibot
from pywikibot import i18n
from pywikibot.tools.formatter import color_format

import callback
import logger


# Déclarations

globalsettings = {
    'reqEditCount' : 1, 		#number of edits required to welcome an user
    'timeoffset' : 60,			#skip users newer than # minutes
    'defaultSign' : '--~~~~',		#default signature
    'randomSign' : False,		#pick a random signature instead of default
    'queryLimit' : 50,			#number of users loaded by the bot
}

welcomemsg = {
    'fr' : u'{{Bienvenue}}%s',
    'it' : u'{{Benvenuto}}%s',
}

welcomelog = {
    'fr' : u'User:LinedBot/Welcome/Log',
    'it' : u'User:LinedBot/Welcome/Log',
}

random_sign = {
    'fr' : u'User:LinedBot/Welcome/Signatures',
    'it' : u'User:LinedBot/Welcome/Firme',
    #'it' : u'wp:Wikipedia:Benvenuto Bot/Firme',
}

class WelcomeBot:

    # bot initialization
    def __init__(self,viki):
        self.site = pywikibot.Site(viki,'vikidia')
        self.checkManagedSites()
        if globalsettings['randomSign']:
	    self.signList = self.getSignList()
        self.welcomed_users = list()    

    # chek if "autowelcome" is enabled or not on the wiki
    def checkManagedSites(self):
        wlcmsg = i18n.translate(self.site, welcomemsg)
        if wlcmsg is None:
            raise KeyError(
                'welcome.py is not localized for site {0} in welcomemsg dict.'
                ''.format(self.site))    
    
    # random list of signatures used for the welcome message
    def getSignList(self):
        signPageName = creg = i18n.translate(self.site, random_sign)
        if not signPageName:
            pywikibot.output("Random signature disabled on %s; disabling random sign" % self.site)
	    globalsettings['randomSign'] = False
            return

	signPage = pywikibot.Page(self.site, signPageName)

        if signPage.exists():
            sign = u''
            creg = re.compile(r"^\* ?(.*?)$", re.M)
            signText = signPage.get()
            return creg.findall(signText)
        else:
            pywikibot.output("The random signature list doesn't exist; disabling random sign")
            globalsettings['randomSign'] = False
            return

    # retrieve new users list
    def parseNewUserLog(self):
        start = self.site.server_time() - timedelta(minutes=globalsettings['timeoffset'])
        for ue in self.site.logevents('newusers', total=globalsettings['queryLimit'], start=start):
            yield pywikibot.User(ue.page())


    def run(self):
        for user in self.parseNewUserLog():
	    #print user.name()
	    if user.isBlocked():
                #showStatus(3)
                pywikibot.output(u" %s is blocked; skipping." % user.name())
                continue
            if "bot" in user.groups():
                #showStatus(3)
                pywikibot.output(u"%s is a bot; skipping." % user.name())
                continue
            if "bot" in user.name().lower():
                #showStatus(3)
                pywikibot.output(u"%s is probably a bot; skipping." % user.name())
                continue
            if user.editCount() >= globalsettings['reqEditCount']:
                #showStatus(2)
                pywikibot.output(u"%s has enough edits to be welcomed." % user.name())
                ustp =  user.getUserTalkPage()
                if ustp.exists():
                    #showStatus(3)
                    pywikibot.output(u"%s has been already welcomed; skipping." % user.name())
                    continue
                else:
                    welcome_text = i18n.translate(self.site, welcomemsg)
                    if globalsettings['randomSign'] and len(self.signList) > 0:
			sign = choice(self.signList)
		    else:
                        sign = globalsettings['defaultSign']

                    welcome_text = (welcome_text % sign)
                    welcome_cmnt = u"Robot: " + i18n.twtranslate(self.site,'welcome-welcome')

		    #print welcome_text
                    #print welcome_cmnt
                    ustp.text = welcome_text
                    
                    try:
                        ustp.save(welcome_cmnt,minor=False)
                        pass
                    except pywikibot.EditConflict:
                        pywikibot.output(u"An edit conflict has occurred, "
                                             u"skipping %s." % user.name())


def showStatus(n=0):
    """Output colorized status."""
    staColor = {
        0: 'lightpurple',
        1: 'lightaqua',
        2: 'lightgreen',
        3: 'lightyellow',
        4: 'lightred',
        5: 'lightblue'
    }
    staMsg = {
        0: 'MSG',
        1: 'NoAct',
        2: 'Match',
        3: 'Skip',
        4: 'Warning',
        5: 'Done',
    }
    pywikibot.output(color_format('{color}[{0:5}]{default} ',
                                  staMsg[n], color=staColor[n]), newline=False)

# Exécution
def main():
    
    site = sys.argv[1]
    try:
        wb = WelcomeBot(site)
    except KeyError as error:
        # site not managed by welcome.py
        pywikibot.error(error)
        return False
    wb.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
