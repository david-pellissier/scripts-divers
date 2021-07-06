# David Pellissier
# Dépendances: module requests
#
# Prévu pour Linux, mais fonctionne aussi sous Windows en commentant la ligne 80 (os.popen(...))

import requests
import webbrowser
import os
from hashlib import md5
from sys import argv
from getpass import getpass

year = 2020

class Credentials:
    id = 0
    user = ''
    password = ''

    @staticmethod
    def parseCreds(creds_string):
        # format = <id>:<username>:<password>

        sepID = creds_string.find(':')
        sepUser = creds_string.find(':', sepID + 1)

        tid = creds_string[:sepID]
        tusername = creds_string[sepID + 1:sepUser]
        tpassword = creds_string[sepUser + 1:]

        return tid, tusername, tpassword

    def set(self, tid, tusername, tpassword):
        self.id = int(tid)
        self.user = tusername
        self.password = tpassword

    def prompt(self):
        print("ID Gaps:", end=" ")
        tid = input()
        print("Utilisateur:", end=" ")
        tusername = input()
        tpassword = getpass('Mot de passe: ')

        self.set(tid, tusername, tpassword)

    def read(self, file):
        fs = open(file, "r")
        creds_string = fs.readline()

        # enleve le retour à la ligne s'il existe
        if creds_string[-1] == '\n':
            creds_string = creds_string[:-1]

        tid, tusername, tpassword = self.parseCreds(creds_string)

        self.set(tid, tusername, tpassword)

    def setFromString(self, s):
        tid, tusername, tpassword = self.parseCreds(s)
        self.set(tid, tusername, tpassword)

    def isSet(self):
        return self.user and self.password


def checkModification(reponse, file="./latest.hash"):
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
            os.popen("notify-send 'GAPS checker' 'Il y a du changement dans les notes !' -t 0")

        fs = open(file, "w")
        fs.write(str(new_hash))
        fs.close()
        return True
    else:
        print("Pas de changement.")
        return False


def output(reponse, outputfile):
    # decode la réponse GZIP (un peu à l'arrache, mais pour l'instant ça fait son travail)
    text_decoded = reponse.text.replace("\\", "")

    if text_decoded[:3] == '+:"':
        text_decoded = text_decoded[3:]
    if text_decoded[-1] == '"':
        text_decoded = text_decoded[:-1]

    # style du tableau, pour le swag
    style = \
        '''
        <head>
        <style type="text/css">
            .bigheader              { background-color : #14161B; color : white ;}
            .odd, .edge, .l2header  { background-color : #8C9BBD; }
        </style>
        </head>
        '''
    html = style + text_decoded

    fs = open(outputfile, "w")
    fs.write(html)
    fs.close()

    webbrowser.open(outputfile, new=2)


def showHelp():
    text = \
        '''
usage: gaps_check [-f <creds file> | -u <gaps_id>:<user>:<password>] [-y <year>] [--html <output file>]
    
    Paramètres de login:
        -f  <creds file>    :   récupère les identifiants dans le fichier spécifié.
        -u  <creds string>  :   utilise les identifiants donnés par la string   
    
        Attention: d'un point de vue sécurité, il n'est pas recommandé d'utiliser -f et -u car il est possible de 
        retrouver les valeurs en clair sur le système.
        
        Si aucune option de login n'est spécifié. Le script demandera les infos dans la console.
    
    Paramètres généraux:
        -y  <year>          :   L'année scolaire en cours. Par défaut = 2020 (pour l'année 2020-2021)
                                
        --html  <output>    :   Enregistre les notes dans le fichier html donné. 
                                Affiche immédiatement le fichier dans le navigateur 
    Remarques:
        - Le hash (latest.hash) est enregistré dans le dossier courant.
            - Il faut toujours exécuter le script dans le dossier où se trouve le hash

'''

    print(text)
    exit()


def main(creds, outputfile=''):
    base_site = 'https://gaps.heig-vd.ch/consultation'
    cc = base_site + '/controlescontinus/consultation.php?idst=' + str(creds.id)

    # init session
    gaps_session = requests.Session()

    # connexion
    connect_params = {'login': creds.user, 'password': creds.password, 'submit': 'Entrer'}
    gaps_session.get(url=base_site, params=connect_params)

    # récupération des notes
    cc_params = {'rs': 'getStudentCCs', 'rsargs': '[%d, %d, null]' % (creds.id, year)}
    notes = gaps_session.post(url=cc, params=cc_params)

    # fermeture de session
    gaps_session.post(base_site, params={'logout': 'yes'})
    gaps_session.close()

    res = checkModification(notes)

    if outputfile:
        output(notes, outputfile)


# Parser les arguments
if __name__ == "__main__":

    tcreds = Credentials()
    toutputfile = ''

    index = 1

    if (len(argv) == 2 and argv[1] == '-h') or (len(argv) % 2 == 0):
        showHelp()

    while index < len(argv) - 1:
        value = argv[index + 1]

        # -f <creds file>
        if argv[index] == '-f':
            tcreds.read(value)
        # -u <creds string>
        elif argv[index] == '-u':
            tcreds.setFromString(value)
        # --html <output file>
        elif argv[index] == '--html':
            toutputfile = value
        # -y <year>
        elif argv[index] == '-y':
            year = value
        else:
            showHelp()

        index += 2

    if not tcreds.isSet():
        tcreds.prompt()

    main(tcreds, toutputfile)
