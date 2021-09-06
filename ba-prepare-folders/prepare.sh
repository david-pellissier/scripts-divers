#!/bin/bash
if [[ $# -lt 2 ]]
then
    echo "usage : prepare prefix c1 c2 ... cN"
    exit 1
fi

prefix="$1"
root_dir="/home/david/Cours"
all_dir="BA_ALL" # inside the root folder

shift # remove first argument

# Check the base folders
if [[ ! -d $root_dir ]]
then
    echo "Error: root dir ($root_dir) doesn't exist"
    exit 1
fi

cd $root_dir

if [[ ! -d $all_dir ]]
then
    mkdir "$all_dir"
    echo "Created $all_dir"
fi

touch aliases.txt # include this file in zshrc

for course in "$@"
do
    name="${prefix}_${course}"
    path="$all_dir/$name"

    if [[ -d $path ]]
    then
        echo "$name already exists. It has been skipped"
        continue
    fi

    # Create folder and subfolders
    mkdir "$path" "$path/exercices" "$path/labo" "$path/théorie" 
    
    # Create symbolic link
    ln -s "$path" "$name"

    # Add the alias
    echo "alias $course='cd $root_dir/$name'" >> aliases.txt

    echo "$name is ready"

done

echo -e "\nDone"
