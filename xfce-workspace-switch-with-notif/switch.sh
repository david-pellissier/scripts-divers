# Script utilisé pour XFCE pour switcher de workpace en envoyant une notif du numéro du bureau

function switch_workspace(){

wmctrl -s $1
notify-send $1 -t 1

}

switch_workspace $1

