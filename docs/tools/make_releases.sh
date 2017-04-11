#!/bin/sh

DIRNAME=`dirname "$0"`
PROGNAME=`basename "$0"`

ARCHIVE=Lichen

if [ ! "$1" ] || [ "$1" = '--help' ] ; then
    cat 1>&2 <<EOF
Usage: $PROGNAME <output directory> [ -f ]

Make release archives from tags starting with "rel-" in the repository,
storing the archives in the output directory. If an archive already exists for
a release, it is not regenerated unless the -f (force) option is given.

All newly-created archive filenames are emitted on standard output.
EOF
    exit 1
fi

OUTDIR=$1
FORCE=$2

if [ "$FORCE" != '-f' ]; then
    FORCE=
fi

if [ ! -e "$OUTDIR" ]; then
    mkdir -p "$OUTDIR"
fi

for TAG in `hg tags | grep ^rel- | cut -f 1 -d ' '` ; do
    NUM=`echo "$TAG" | sed 's/rel-//;s/-/./g'`
    OUTFILE="$OUTDIR/$ARCHIVE-$NUM.tar.bz2"
    if [ ! -e "$OUTFILE" ] || [ "$FORCE" ]; then
        hg archive -t tbz2 -r "$TAG" "$OUTFILE"
        echo "$OUTFILE"
    fi
done
