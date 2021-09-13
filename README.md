# Liste des scripts

## ba-backup 
Prérequis: rclone

Script de backup des cours grâce à rclone

## gaps-check
Prérequis: python w/ requests

Récupération des notes de cours 

## scheck

Prérequis: python, notify-send

Vérifie la présence d'un substring en résultat d'une commande à intervalle régulier

Exemple utile: 

```bash
scheck "ping 1.1.1.1 -c 1" "bytes from" "connection restored" -i 30
```



## xfce-workspace-switch-with-notif

Prérequis: xfce

Envoie une notification avec le numéro du workspace lors d'un changement. Il faut configurer les raccourcis en appelant ce script

## ba-prepare-folders
Prérequis: aucun

Crée la structure de dossiers pour un nouveau semestre

## volume

Prérequis: alsa & dunst

Modifie le volume via ALSA et envoie une notification avec progress bar vers DUNST

exemple: `volume up`

![image-20210913191828231](/home/david/Projets/scripts-divers/README.assets/image-20210913191828231.png)

