liens utiles:
	- https://rclone.org/drive/#making-your-own-client-id
		- ne pas oublier de publier l'application
	- https://rclone.org/drive/

# Créer un client_id:
​	suivre : https://rclone.org/drive/#making-your-own-client-id

# rclone de base
rclone config
	n
		15
		credentials 
		3
		<root folder id vide>
		<service_account_file vide>
		n
		n
		team drive : no
		y
	quitter
	

# rclone chiffré
rclone config
	n
	11
	filename: simple obfuscation
	no dir name encryption
	password
	sel: david
	

# Script
set remote="cours-enc"
set remotedir=""  # = backup/BA-enc
set distant=$remote:$remotedir

echo $distant
#rclone sync 