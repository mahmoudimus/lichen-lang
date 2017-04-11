#!/bin/sh

DIRNAME=`dirname "$0"`
PROGNAME=`basename "$0"`

if [ ! "$1" ] || [ "$1" = '--help' ] ; then
    cat 1>&2 <<EOF
Usage: $PROGNAME <archive directory> [ -f ]

Sign archives in the given archive directory, invoking GPG to produce a
detached signature. If a signature already exists for an archive, it is not
regenerated unless the -f (force) option is given.

All newly-created signature filenames are emitted on standard output.
EOF
    exit 1
fi

OUTDIR=$1
FORCE=$2

if [ "$FORCE" != '-f' ]; then
    FORCE=
fi

if [ ! -e "$OUTDIR" ]; then
    cat 1>&2 <<EOF
No archive directory to process.
EOF
    exit 1
fi

for FILENAME in "$OUTDIR/"*".tar.bz2" ; do
    OUTFILE="$FILENAME.asc"
    if [ ! -e "$OUTFILE" ] || [ "$FORCE" ]; then
        gpg --sign -a -b "$FILENAME"
        echo "$OUTFILE"
    fi
done
