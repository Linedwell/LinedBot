#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Linedwell, 2016

import os
import __main__ as main
logdir=os.getenv('LOGDIR',os.path.dirname(os.path.realpath(main.__file__))) #Récupération de la variable d'environnement LOGDIR si elle existe, . sinon on se place là où se trouve le script lancé
logname=os.path.splitext(os.path.basename(main.__file__))[0]+'.log' #On récupère le nom du script lancé (python <script.py> et on y appose l'extension .log)
logfile=logdir+os.sep+logname
import logging
logging.basicConfig(filename=logfile, format='%(asctime)s :: %(levelname)s :: %(message)s', level=logging.INFO)
