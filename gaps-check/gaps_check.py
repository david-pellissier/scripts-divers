#!/usr/bin/python3

# David Pellissier
# Dépendances: requests
#
# Prévu pour Linux, mais fonctionne aussi sous Windows

import requests, webbrowser, os, html
from hashlib import md5
from sys import argv,path
from getpass import getpass
from datetime import datetime, time
from tempfile import mkstemp

help_str= \
    '''
    usage: gaps_check [-f <creds file> | -s <creds string>] [-y <year>] [--save-html <output file>]
    
    Paramètres de login:

        -f  <creds file>    :   récupère les identifiants dans le fichier spécifié contenant la "creds string".
        -s  <creds string>  :   utilise les identifiants donnés par la string   
        (rien)              :   toutes les infos seront demandées par le processus

        Format des creds string: <user id>:<user>:<password>
        Un ou plusieurs champs peuvent rester vide. Ils seront alors demandés pendant l'exécution.

        IMPORTANT:  Il est conseillé de toujours omettre le mdp de la "creds string" afin d'éviter qu'il puisse être lu en clair sur votre système.
                    Stocker en clair votre mdp est à vos risques et périls.
    
    Paramètres généraux:
        --hash  <file>      :   Permet de préciser un fichier contenant le hash. Par défaut: "notes<year>.hash" dans le dossier courant

        -o                  :   Affiche le résultat dans le navigateur

        --save-html  <file> :   Enregistre le résultat dans le fichier donné  

        -y  <year>          :   L'année scolaire en cours. Par défaut = 2021 (pour l'année 2021-2022)
        
    '''
style_str= \
    '''
    <head>
        <title>Notes</title>
        <style type="text/css">
            .bigheader { background-color : #14161B; color : white ; }
            .odd, .edge, .l2header { background-color : #8C9BBD; }
            table { width:90%; padding: 5%; margin:auto	}
        </style>
    </head>
    '''

default_year = 2021
default_hashfile = path[0]+"/notes%d.hash" % (default_year)

class Credentials:
    id = 0
    user = ''
    password = ''

    def isSet(self):
        return self.id and self.user and self.password

    @staticmethod
    def parseCreds(creds_string):
        # format = <id>:<username>:<password>

        sepID = creds_string.find(':')
        sepUser = creds_string.find(':', sepID + 1)

        tid = creds_string[:sepID]
        tusername = creds_string[sepID + 1:sepUser]
        tpassword = creds_string[sepUser + 1:]

        return tid, tusername, tpassword

    def prompt(self):
        tid=self.id
        tusername=self.user
        tpassword=self.password

        if tid == 0 or not tid:
            print("ID Gaps:", end=" ")
            tid = input()
        if not tusername:
            print("Utilisateur:", end=" ")
            tusername = input()
        
        if not tpassword:
            tpassword = getpass('Mot de passe: ')

        return tid,tusername,tpassword

    def read(self, file):
        fs = open(file, "r")
        creds_string = fs.readline()

        # enleve le retour à la ligne s'il existe
        if creds_string[-1] == '\n':
            creds_string = creds_string[:-1]

        return self.parseCreds(creds_string)

    def set(self, tid='', tusername='', tpassword=''):
        if tid:
            if not str(tid).isdecimal():
                print("\n~ ERREUR: L'id doit être un nombre entier")
                exit(1)
            self.id = int(tid)            
        if tusername:
            self.user = tusername
        if tpassword:
            self.password = tpassword

def checkModification(reponse, file=default_hashfile):
    old_hash = ''
    new_hash = md5(reponse.text.encode("utf-8")).hexdigest()
   
    if os.path.exists(file):
        fs = open(file, "r")
        old_hash = fs.readline()
        fs.close()

    if old_hash != new_hash:
        # pas de message la première fois que le script est exécuté
        if old_hash:
            print("Il y a du changement dans les notes GAPS !")
            if os.name != "nt":
                os.popen("notify-send 'GAPS' 'Il y a du changement dans les notes !' -t 0")

        fs = open(file, "w+")
        fs.write(str(new_hash))
        fs.close()

        return True
    else:
        print("Pas de changement.")
        return False

def decodeReponse(s):
    text_decoded = html.unescape(s)
    text_decoded = text_decoded.replace("\\/", "/")
    text_decoded = text_decoded.encode("latin1").decode('unicode_escape')

    # il y a ces caractères dans la réponse je sais pas pourquoi
    if text_decoded[:3] == '+:"':
        text_decoded = text_decoded[3:]
    if text_decoded[-1] == '"':
        text_decoded = text_decoded[:-1]

    return text_decoded

def output(reponse, open_in_browser=False, outputfile=''):
    # crée un fichier temporaire si l'utilisateur n'a pas mis l'option '--save-html'
    if not outputfile:
        outputfile=mkstemp("_gaps.html")[1]

    text_decoded = decodeReponse(reponse.text)
    text_decoded = text_decoded + "État des notes du %s" % (datetime.now().strftime("%d.%m.%Y à %H:%M"))

    # appliquer le CSS
    html_code = style_str + text_decoded

    fs = open(outputfile, "w+") # créé si besoin
    fs.write(html_code)
    fs.close()

    if open_in_browser:
        webbrowser.open(outputfile, new=2)
    
def showHelp():
    print(help_str)
    exit()


def getNotes(creds, open_in_browser=False, outputfile='', year=default_year, hashfile=default_year):
    base_site = 'https://gaps.heig-vd.ch/consultation'
    cc = base_site + '/controlescontinus/consultation.php?idst=' + str(creds.id)

    # init session
    gaps_session = requests.Session()

    # connexion
    connect_params = {'login': creds.user, 'password': creds.password, 'submit': 'Entrer'}
    gaps_session.get(url=base_site, params=connect_params)

    # récupération des notes
    cc_headers= {'Accept-Encoding': 'identity' }
    cc_params = {'rs': 'getStudentCCs', 'rsargs': '[%d, %d, null]' % (creds.id, year)}
    notes = gaps_session.post(url=cc, params=cc_params, headers=cc_headers)

    # fermeture de session
    gaps_session.post(base_site, params={'logout': 'yes'})
    gaps_session.close()

    res = checkModification(notes, hashfile)

    if open_in_browser or outputfile:
        output(notes, open_in_browser, outputfile)


def main():
    creds = Credentials()
    
    outputfile = ''
    open_in_browser = False
    hashfile = default_hashfile
    year = default_year

    # Parser les arguments
    index = 1
    while index < len(argv):

        a=argv[index]

        # -o
        if a == '-o':
            open_in_browser = True
        elif a ==  '-h' or a == '--help':
            showHelp()

        # Les arguments suivants ont besoin d'une valeur
        elif index < len(argv) -1: 
            value = argv[index + 1]

            # -f <creds file>
            if a == '-f':
                creds.set(*creds.read(value))
            # --hash <file>
            elif a == '--hash':
                hashfile=value
            # -s <creds string>
            elif a == '-s':
                creds.set(*creds.parseCreds(value))
            # --save-html <file>
            elif a == '--save-html':
                outputfile = value
            # -y <year>
            elif a == '-y':
                year = int(value)
            else:
                showHelp()
            
            index += 1
        else:
            print("L'option \"", a, "\" n'existe pas, ou a besoin d'une valeur.", sep="")
            exit(0)
        index += 1
        


    while not creds.isSet():
        creds.set(*creds.prompt())
        
    getNotes(creds, open_in_browser, outputfile, year, hashfile)


if __name__ == "__main__":    
    main()
