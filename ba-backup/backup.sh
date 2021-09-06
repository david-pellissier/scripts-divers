#!/bin/bash
echo Début de la synchronisation
# source
root="/home/david/Cours"
sourcedir=$root"/BA_ALL"
confdir=$root"/.backups"
logdir=$root"/.backups" #"/tmplog" # for debug

# destination
remote="gdrive-enc"
remotedir="backups/BA"
destination=$remote:$remotedir

# old
now=$(date +"%Y-%m-%d-%T")
oldroot=$destination"_old"
backupdir=$oldroot"/"$now

# logs and config
logfile=$logdir"/log-"$now
filterfile=$confdir"/filter.txt"

# Argument preparation
flag_backup=" --backup-dir "$backupdir
flag_log=" --log-file "$logfile
flag_filter=" --filter-from "$filterfile
options="-v -P "$flag_backup$flag_log


# Final command
rclone sync $sourcedir $flag_filter $destination $options



# End of the script
echo
echo Fin de la synchronisation 
notify-send "Fin de la synchronisation"
