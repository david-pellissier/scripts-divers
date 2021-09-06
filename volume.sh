#!/bin/bash
# volume.sh : set volume and send **dunst** notifications

AUDIO_SRC="Master"
VALUE=1 # in percent
NOTIFY_ID=1337
PROGRESS_CHAR="━"
FILL_CHAR=" "
MUTED_CHAR=""


function helper(){
    echo "usage : volume [up|down|toggle]"
}

function notify(){
    
    echo $1
    vol=$(echo $1 | grep -o -E '[0-9]+%')
    vol=${vol::-1} # remove '%'

    status="?"
    if echo "$1" | grep '\[on\]'
    then
        status=$vol
    else
        status=$MUTED_CHAR
    fi

    # draw bar (inspired by: https://gist.github.com/sebastiencs/5d7227f388d93374cebdf72e783fbd6a)
    nb=$(($vol / 5))
    bar=$(python -c "print('$PROGRESS_CHAR' * $nb, '$FILL_CHAR' * $((20 - $nb)), sep='')") # not sure if this is better than "sed ... | tr"

    # send dunst notification
    dunstify -a "volume" -i none -u normal -t 1000 -r $NOTIFY_ID "  $status  $bar"

}

function toggle_f(){
    output=$(amixer set $AUDIO_SRC toggle)
    notify "$output"
}

function volume_f(){

    output=$(amixer set $AUDIO_SRC $VALUE%$1)
    notify "$output"
}


## Main : parse arguments

if [[ $# -ne 1 ]]
then
    helper
    exit 1
fi

case $1 in
    up)     volume_f "+" ;;
    down)   volume_f "-" ;;
    toggle) toggle_f ;;

    *)      helper ;;
esac

exit 1
