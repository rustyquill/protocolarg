#!/bin/bash
set -e

#
# helper script to create a 7z file with defined content
# execute in github action or in docker container!
#

# create the zip file to match the last message from einsamernarr
# on the 2001-12-15 03:32:00
TIMESTAMP_ZIP_FILE="2001-12-15 05:13:00"
TIMESTAMP_ZIP_FILE_TOUCH="200112150513"

# install requirements
apt-get update
apt-get install -y p7zip-full git make gcc

current_dir=$(pwd)

git clone https://github.com/wolfcw/libfaketime.git /tmp/libfaketime \
  && cd /tmp/libfaketime \
  && make install \
  && cd "${current_dir}" \
  && rm -rf /tmp/libfaketime

zip_password="${1}"
[ -z "${zip_password}" ] && echo "no password given" && exit 1

# collect files
rm -rf ./zip-data/
rm -f ./dokumente.7z
mkdir ./zip-data
cp BonzoBuck1.png ./zip-data/BonzoBuck1.png
cp BonzoBuck2.png ./zip-data/BonzoBuck2.png
cp chdb.xls ./zip-data/chdb.xls
cp "Of the Generation of things.pdf" "./zip-data/Of the Generation of things.pdf"

touch -a -m -t $TIMESTAMP_ZIP_FILE_TOUCH ./zip-data/BonzoBuck1.png
touch -a -m -t $TIMESTAMP_ZIP_FILE_TOUCH ./zip-data/BonzoBuck2.png
touch -a -m -t $TIMESTAMP_ZIP_FILE_TOUCH ./zip-data/chdb.xls
touch -a -m -t $TIMESTAMP_ZIP_FILE_TOUCH "./zip-data/Of the Generation of things.pdf"

# create 7zip file with the file "test.txt" in this directory and the name dokumente.7z
# the 7z will have the -stl option set, so the archive timestamps are the same as
# the file timestamps
cd ./zip-data
LD_PRELOAD=/usr/local/lib/faketime/libfaketime.so.1 FAKETIME="${TIMESTAMP_ZIP_FILE}" 7z a -p"${zip_password}" -mhe=on -t7z ../dokumente.7z "*"

