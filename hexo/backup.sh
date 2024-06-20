#!/bin/bash
# backup.sh

cd "$(dirname "$(readlink -f "$0")")"

ErrorColor='\033[0;31m'
InfoColor='\033[0;32m'
NoColor='\033[0m'

git pull

if [ $? -ne 0 ]; then
    echo -e "${ErrorColor}[ERROR] Git pull failed. Aborting script.${NoColor}"
    exit 1
fi

git add source/

if [ $? -ne 0 ]; then
    echo -e "${ErrorColor}[ERROR] Git add failed. Aborting script.${NoColor}"
    exit 1
fi

git commit -m "Auto backup of blog from bash script."

if [ $? -ne 0 ]; then
    echo -e "${ErrorColor}[ERROR] Git commit failed. Aborting script.${NoColor}"
    exit 1
fi

git push

if [ $? -ne 0 ]; then
    echo -e "${ErrorColor}[ERROR] Git push failed. Aborting script.${NoColor}"
    exit 1
fi

echo -e "${InfoColor}[INFO] Auto backup successfully.${NoColor}"
