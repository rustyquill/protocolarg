#!/bin/sh
set -e
#
# helper script for the website pipelines
# gather all javascript files and obfuscate them
#

# check if a path was given
WORKDIR="${1}"
[ -z "${WORKDIR}" ] && echo please specify workdir && exit 1

# gather all javascript files from the given path
cd "${WORKDIR}"
JS_FILES=$(find . -type f -name "*.js")

# obfuscate all javascript files
for JS_FILE in $JS_FILES; do
    echo "obfuscating ${JS_FILE}"
    npx javascript-obfuscator "${JS_FILE}" --output "${JS_FILE}"
done
