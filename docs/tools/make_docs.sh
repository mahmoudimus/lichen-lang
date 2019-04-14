#!/bin/sh

THISDIR=`dirname "$0"`
INDIR="$THISDIR/../wiki"
OUTDIR="$THISDIR/../html"

ROOT="Lichen"

MAPPING='--mapping WikiPedia https://en.wikipedia.org/wiki/'
THEME='--theme mercurial'

if [ "$1" = '--web' ] ; then
    DOCINDEX=
    shift 1
else
    DOCINDEX='--document-index index.html'
fi

FILENAMES=${*:-'--all'}

moinconvert --input-dir "$INDIR" \
            --input-page-sep '--' \
            --output-dir "$OUTDIR" \
            --root "$ROOT" \
            --format html \
            --macros \
            $DOCINDEX \
            $MAPPING \
            $THEME \
            $FILENAMES
