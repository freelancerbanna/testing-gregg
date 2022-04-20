#!/bin/bash

usage()
{
cat << EOF
usage: $0 options

This script set ownership for all table, sequence and views for a given database

Credit: Based on http://stackoverflow.com/a/2686185/305019 by Alex Soto
        Also merged changes from @sharoonthomas

OPTIONS:
   -h      Show this message
   -d      Database name
   -o      Owner
   -s      Schema (defaults to public)
EOF
}

DB_NAME="";
NEW_OWNER="";
SCHEMA="public";
while getopts "hd:o:s:" OPTION; do
    case $OPTION in
        h)
            usage
            exit 1
            ;;
        d)
            DB_NAME=$OPTARG
            ;;
        o)
            NEW_OWNER=$OPTARG
            ;;
        s)
            SCHEMA=$OPTARG
            ;;
    esac
done

if [[ -z $DB_NAME ]] || [[ -z $NEW_OWNER ]]; then
     usage;
     exit 1;
fi


for tbl in `psql -qAt -c "SELECT tablename FROM pg_tables WHERE schemaname = '${SCHEMA}';" ${DB_NAME} -U postgres` \
           `psql -qAt -c "SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = '${SCHEMA}';" ${DB_NAME} -U postgres` \
           `psql -qAt -c "SELECT table_name FROM information_schema.views WHERE table_schema = '${SCHEMA}';" ${DB_NAME} -U postgres`;
do
    psql -c "ALTER TABLE \"${SCHEMA}\".\"$tbl\" OWNER TO ${NEW_OWNER}" ${DB_NAME}  -U postgres;
done
unset IFS;
