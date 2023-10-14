#!/bin/bash
set -e

#
# sets up the cvs repository with timestamps etc
#

###
# global configuration
###
CVSROOT="/cvs"
TMP_DIR="/tmp${CVSROOT}"

# file names for playfair cipher challenge
# "icantthinkpasthtecorners"
CHALLENGE_DIR="${TMP_DIR}/6963616E747468696E6B70617374746865636F726E657273"
IN=$(echo IN | translation-table)
OUT=$(echo OUT | translation-table)
KEY=$(echo KEY | translation-table)
mainh=$(echo main.h | translation-table)
mainc=$(echo main.c | translation-table)
main=$(echo main | translation-table)
archiverc=$(echo archiver.c | translation-table)

# timestamps for csv commits
TIMESTAMP_CODE_CHALLENGE="2023-06-20 03:00:00"
TIMESTAMP_CODE_CHALLENGE_CORRUPTED="2023-06-22 23:47:59"
# unused timestamp
#TIMESTAMP_CODE_CHALLENGE_ARCHIVER="2001-12-15 05:13:00"
TIMESTAMP_CODE_CHALLENGE_HELP="2023-09-02 03:12:23"

TIMESTAMP_CODE_CHALLENGE_LINUX="2021-01-14 01:00:00"
TIMESTAMP_CODE_CHALLENGE_ADDRESS_MANAGEMENT="2021-03-14 02:17:00"
TIMESTAMP_CODE_CHALLENGE_EASY_ACCOUNTING="2021-03-14 04:29:00"
TIMESTAMP_CODE_CHALLENGE_SIMPLE_MATH="2021-05-28 01:56:00"
TIMESTAMP_CODE_CHALLENGE_MUD_CLIENT="2021-09-29 03:36:00"
# JMJ updates the mud client on 2023-10-03 07:21:00 (tuesday in last week of arg)
TIMESTAMP_CODE_CHALLENGE_MUD_CLIENT_MODIFIED="2023-10-03 07:21:00"

# users for code challenge
URCLNA="urclna"
NO24R2=NO24R2
# j🜐j
JMJ="_6A1F7106A_$"

# text for HELP.txt in code challegne repo
HELP_TEXT="Found all over environment. Figure out a way to just fucking magically secure this piece of crap because the high-ups have their heads too far up their own asses to update anything. Also get a fucking raise."

###
# functions
###

function cvs_add() {
    user="${1}"
    timestamp="${2}"
    path="${3}"

    cd "$(dirname "${path}")"
    set +e
    su "${user}" -c "faketime \"${timestamp}\" cvs -d "${CVSROOT}" add $(basename "${path}")"
    set -e
}

function cvs_commit() {
    user="${1}"
    timestamp="${2}"
    message="${3}"
    path="${4}"

    cd "$(dirname "${path}")"
    su "${user}" -c "faketime \"${timestamp}\" cvs -d "${CVSROOT}" commit -m \"${message}\" \"$(basename "${path}")\""
}

function setup_environment() {
    # add cvs group
    groupadd -g 999 cvs
    # create user for code uploads
    adduser --uid 1000 --no-create-home --disabled-password --disabled-login --gecos "" --gid 999 "${URCLNA}"
    usermod -a -G cvs "${URCLNA}"
    # translatets to j🜐j -> jmj
    adduser --uid 65535 --no-create-home --disabled-password --disabled-login --gecos "" --gid 999 --force-badname "${JMJ}"
    usermod -a -G cvs "${JMJ}"
    adduser --uid 11 --no-create-home --disabled-password --disabled-login --gecos "" --gid 999 --force-badname "${NO24R2}"
    usermod -a -G cvs "${NO24R2}"
    # create the cvs repository
    mkdir -p "${CVSROOT}"
    # icrnitialize cvs root
    faketime "${TINESTAMP_REPOSITORY}" cvs -d "${CVSROOT}" init
    chown -R root:cvs "${CVSROOT}"
    chmod -R 770 "${CVSROOT}"
}

function create_repository_clone() {
    mkdir -p "${TMP_DIR}"
    cd "${TMP_DIR}"
    cvs -d "${CVSROOT}" checkout .
    chown -R root:cvs "${TMP_DIR}"
    chmod -R 770 "${TMP_DIR}"
}

function setup_code_challenge_repository() {
    mkdir "${CHALLENGE_DIR}"
}

function copy_source_code() {
    cd "${CHALLENGE_DIR}"
    cp "/bootstrap/playfair/main.c" main.c
    cp "/bootstrap/playfair/main.h" main.h
    cp "/bootstrap/playfair/archiver.c" archiver.c
}

function compile_source_code() {
    cd "${CHALLENGE_DIR}"
    gcc -o main main.c
    gcc -o archiver archiver.c
}

function create_cipher_files_and_encrypt_text() {
    cd "${CHALLENGE_DIR}"
    echo "${INPUT}" > "IN"
    echo "${CIPHER}" > "KEY"

    # execute playfair to encrypt the input
    ./main
}

function encode_playfair_outputs() {
    cd "${CHALLENGE_DIR}"

    # encode KEY, pass it trough the translation table
    # add newlines and convert it to hex
    # push back to file
    echo "${CIPHER}" | sed 's/./\0\n/g' | translation-table  | sed '/^$/d' | od -A n -v -t x1 > "KEY"
    # overwrite the input with the corrupted string
    echo "${INPUT_CORRUPTED}" > "IN"

    # rename the files
    mv "IN" "${IN}"
    mv "OUT" "${OUT}"
    mv "KEY" "${KEY}"
}

function encode_source_code_for_v1() {
    cd "${CHALLENGE_DIR}"
    # replace strings in main.c
    sed -i "s/IN/${IN}/g" main.c
    sed -i "s/OUT/${OUT}/g" main.c
    sed -i "s/KEY/${KEY}/g" main.c
    sed -i "s/main.h/${mainh}/g" main.c
    # rename source code files
    mv "main.c" "${mainc}"
    mv "main.h" "${mainh}"
    mv "main" "${main}"
}

function encode_source_code_for_v2() {
    cd "${CHALLENGE_DIR}"
    # encode source code with translation table
    mv main.c main.c.orig
    mv main.h main.h.orig
    translation-table main.c.orig > main.c
    translation-table main.h.orig > main.h
    rm main.c.orig
    rm main.h.orig
    mv archiver.c archiver.c.orig
    translation-table archiver.c.orig > archiver.c
    rm archiver.c.orig
    # rename files
    mv "main.c" "${mainc}"
    mv "main.h" "${mainh}"
    mv "main" "${main}"
    mv "archiver.c" "${archiverc}"
}

function fix_permissions_for_challenge() {
    chown -R root:cvs "${CHALLENGE_DIR}"
    chmod -R 770 "${CHALLENGE_DIR}"
}


function commit_code_challenge_repo() {
    cvs_add "${JMJ}" "${TIMESTAMP_CODE_CHALLENGE}" "${CHALLENGE_DIR}"
    # cvs_add "${JMJ}" "${TIMESTAMP_CODE_CHALLENGE}" "${CHALLENGE_DIR}/*"
    cvs_commit "${JMJ}" "${TIMESTAMP_CODE_CHALLENGE}" "" "${CHALLENGE_DIR}"
}

function commit_code_challenge_jmj() {
    cvs_add "${JMJ}" "${TIMESTAMP_CODE_CHALLENGE}" "${CHALLENGE_DIR}/${OUT}"
    cvs_add "${JMJ}" "${TIMESTAMP_CODE_CHALLENGE}" "${CHALLENGE_DIR}/${KEY}"
    cvs_add "${JMJ}" "${TIMESTAMP_CODE_CHALLENGE}" "${CHALLENGE_DIR}/${mainc}"
    cvs_add "${JMJ}" "${TIMESTAMP_CODE_CHALLENGE}" "${CHALLENGE_DIR}/${mainh}"
    cvs_commit "${JMJ}" "${TIMESTAMP_CODE_CHALLENGE}" "" "${CHALLENGE_DIR}/${OUT}"
    cvs_commit "${JMJ}" "${TIMESTAMP_CODE_CHALLENGE}" "" "${CHALLENGE_DIR}/${KEY}"
    cvs_commit "${JMJ}" "${TIMESTAMP_CODE_CHALLENGE}" "" "${CHALLENGE_DIR}/${mainc}"
    cvs_commit "${JMJ}" "${TIMESTAMP_CODE_CHALLENGE}" "" "${CHALLENGE_DIR}/${mainh}"
    # use same date for the archiver as the other codes from jmj
    cvs_add "${JMJ}" "${TIMESTAMP_CODE_CHALLENGE}" "${CHALLENGE_DIR}/${archiverc}"
    cvs_commit "${JMJ}" "${TIMESTAMP_CODE_CHALLENGE}" "" "${CHALLENGE_DIR}/${archiverc}"
}

function commit_code_challenge_no24r2() {
    chown -R ${NO24R2}:cvs "${CHALLENGE_DIR}"
    cvs_add "${NO24R2}" "${TIMESTAMP_CODE_CHALLENGE_CORRUPTED}" "${CHALLENGE_DIR}/${IN}"
    cvs_commit "${NO24R2}" "${TIMESTAMP_CODE_CHALLENGE_CORRUPTED}" "" "${CHALLENGE_DIR}/${IN}"
}

function add_help_text_for_code_challenge_repo() {
    echo "${HELP_TEXT}" > "${CHALLENGE_DIR}/HELP.txt"
    chown -R ${URCLNA}:cvs "${CHALLENGE_DIR}"
    cvs_add "${URCLNA}" "${TIMESTAMP_CODE_CHALLENGE_HELP}" "${CHALLENGE_DIR}/HELP.txt"
    cvs_commit "${URCLNA}" "${TIMESTAMP_CODE_CHALLENGE_HELP}" "What the actual fuck is this???" "${CHALLENGE_DIR}/HELP.txt"
}

function add_linux_repository() {
    cp -a /bootstrap/cvs/linux-1.0 "${TMP_DIR}/linux-1.0"
    chown -R ${URCLNA}:cvs "${TMP_DIR}/linux-1.0"

    cvs_add "${URCLNA}" "${TIMESTAMP_CODE_CHALLENGE_LINUX}" "${TMP_DIR}/linux-1.0"
    for f in $(find "${TMP_DIR}/linux-1.0" -type d); do
        cvs_add "${URCLNA}" "${TIMESTAMP_CODE_CHALLENGE_LINUX}" "${f}"
    done
    for f in $(find "${TMP_DIR}/linux-1.0" -type f); do
        cvs_add "${URCLNA}" "${TIMESTAMP_CODE_CHALLENGE_LINUX}" "${f}"
    done

    cvs_commit "${URCLNA}" "${TIMESTAMP_CODE_CHALLENGE_LINUX}" "Linux 1.0 - let's see what I can improve" "${TMP_DIR}/linux-1.0"
}

function add_address_management_repository() {
    cp -a /bootstrap/cvs/address_management "${TMP_DIR}/address_management"
    chown -R ${URCLNA}:cvs "${TMP_DIR}/address_management"

    cvs_add "${URCLNA}" "${TIMESTAMP_CODE_CHALLENGE_ADDRESS_MANAGEMENT}" "${TMP_DIR}/address_management"
    for f in $(find "${TMP_DIR}/address_management" -type d); do
        cvs_add "${URCLNA}" "${TIMESTAMP_CODE_CHALLENGE_ADDRESS_MANAGEMENT}" "${f}"
    done
    for f in $(find "${TMP_DIR}/address_management" -type f); do
        cvs_add "${URCLNA}" "${TIMESTAMP_CODE_CHALLENGE_ADDRESS_MANAGEMENT}" "${f}"
    done

    cvs_commit "${URCLNA}" "${TIMESTAMP_CODE_CHALLENGE_ADDRESS_MANAGEMENT}" "PoC for PL1 ADDR MGMT" "${TMP_DIR}/address_management"
}

function add_easy_accounting_repository() {
    cp -a /bootstrap/cvs/easy_accounting "${TMP_DIR}/easy_accounting"
    chown -R ${URCLNA}:cvs "${TMP_DIR}/easy_accounting"

    cvs_add "${URCLNA}" "${TIMESTAMP_CODE_CHALLENGE_EASY_ACCOUNTING}" "${TMP_DIR}/easy_accounting"
    for f in $(find "${TMP_DIR}/easy_accounting" -type d); do
        cvs_add "${URCLNA}" "${TIMESTAMP_CODE_CHALLENGE_EASY_ACCOUNTING}" "${f}"
    done
    for f in $(find "${TMP_DIR}/easy_accounting" -type f); do
        cvs_add "${URCLNA}" "${TIMESTAMP_CODE_CHALLENGE_EASY_ACCOUNTING}" "${f}"
    done

    cvs_commit "${URCLNA}" "${TIMESTAMP_CODE_CHALLENGE_EASY_ACCOUNTING}" "Let's get our spending under control" "${TMP_DIR}/easy_accounting"
}

function add_simple_math_repository() {
    cp -a /bootstrap/cvs/simple_math "${TMP_DIR}/simple_math"
    chown -R ${URCLNA}:cvs "${TMP_DIR}/simple_math"

    cvs_add "${URCLNA}" "${TIMESTAMP_CODE_CHALLENGE_SIMPLE_MATH}" "${TMP_DIR}/simple_math"
    for f in $(find "${TMP_DIR}/simple_math" -type d); do
        cvs_add "${URCLNA}" "${TIMESTAMP_CODE_CHALLENGE_SIMPLE_MATH}" "${f}"
    done
    for f in $(find "${TMP_DIR}/simple_math" -type f); do
        cvs_add "${URCLNA}" "${TIMESTAMP_CODE_CHALLENGE_SIMPLE_MATH}" "${f}"
    done

    cvs_commit "${URCLNA}" "${TIMESTAMP_CODE_CHALLENGE_SIMPLE_MATH}" "Test this new fancy python stuff" "${TMP_DIR}/simple_math"
}

function add_mud_client() {
    cp -a /bootstrap/cvs/mud_client "${TMP_DIR}/mud_client"
    rm -f "${TMP_DIR}/mud_client/mud_client_modified.cpp"
    chown -R ${URCLNA}:cvs "${TMP_DIR}/mud_client"

    cvs_add "${URCLNA}" "${TIMESTAMP_CODE_CHALLENGE_MUD_CLIENT}" "${TMP_DIR}/mud_client"
    for f in $(find "${TMP_DIR}/mud_client" -type d); do
        cvs_add "${URCLNA}" "${TIMESTAMP_CODE_CHALLENGE_MUD_CLIENT}" "${f}"
    done
    for f in $(find "${TMP_DIR}/mud_client" -type f); do
        cvs_add "${URCLNA}" "${TIMESTAMP_CODE_CHALLENGE_MUD_CLIENT}" "${f}"
    done

    cvs_commit "${URCLNA}" "${TIMESTAMP_CODE_CHALLENGE_MUD_CLIENT}" "Write my own mud client" "${TMP_DIR}/mud_client"
}

function update_mud_client {
    cp -a /bootstrap/cvs/mud_client/mud_client_modified.cpp "${TMP_DIR}/mud_client/mud_client.cpp"
    chown -R ${JMJ}:cvs "${TMP_DIR}/mud_client"

    cvs_add "${JMJ}" "${TIMESTAMP_CODE_CHALLENGE_MUD_CLIENT_MODIFIED}" "${TMP_DIR}/mud_client/mud_client.cpp"
    cvs_commit "${JMJ}" "${TIMESTAMP_CODE_CHALLENGE_MUD_CLIENT_MODIFIED}" "" "${TMP_DIR}/mud_client"
}

##
# main
##

# prepare base environemnt
setup_environment
create_repository_clone

# setup code challenge repo
setup_code_challenge_repository
copy_source_code
compile_source_code
create_cipher_files_and_encrypt_text
encode_playfair_outputs
if [ "${USE_CHALLENGE}" -eq 1 ]; then
    encode_source_code_for_v1
fi
if [ "${USE_CHALLENGE}" -eq 2 ]; then
    encode_source_code_for_v2
fi
fix_permissions_for_challenge
commit_code_challenge_repo
commit_code_challenge_jmj
commit_code_challenge_no24r2
add_help_text_for_code_challenge_repo

# setup additional repositories
add_linux_repository
add_address_management_repository
add_easy_accounting_repository
add_simple_math_repository
add_mud_client
update_mud_client

sleep 3
