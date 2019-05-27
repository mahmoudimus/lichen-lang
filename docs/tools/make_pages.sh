#!/bin/sh

DIRNAME=`dirname $0`
PROGNAME=`basename $0`
OUTDIR=$1

if [ ! "$OUTDIR" ] || [ "$1" = '--help' ] ; then
    cat 1>&2 <<EOF
Usage: $PROGNAME <output directory> [ <page prefix> ] [ --releases [ --sign ] ]
EOF
    exit 1
fi

if [ -e "$OUTDIR" ]; then
    echo "Please remove $OUTDIR before generating a new package." 1>&2
    exit 1
fi

if [ "$2" = '--releases' ]; then
    PREFIX=
    RELEASES=$2
    SIGN=$3
else
    PREFIX=$2
    RELEASES=$3
    SIGN=$4
fi

# Generate release archives. These are held in a separate, semi-permanent
# place so that archives and signatures are not regenerated unnecessarily.

if [ "$RELEASES" ]; then
    "$DIRNAME/make_releases.sh" releases
fi

if [ "$SIGN" ]; then
    "$DIRNAME/sign_releases.sh" releases
fi

# Generate a manifest for the page package.

MANIFEST="$OUTDIR/MOIN_PACKAGE"

mkdir "$OUTDIR"
cat > "$MANIFEST" <<EOF
MoinMoinPackage|1
EOF

# Add the pages to the manifest.

DOCS="$DIRNAME/../wiki"

cp "$DOCS/"* "$OUTDIR"

for FILENAME in "$DOCS/"* ; do
    BASENAME=`basename "$FILENAME"`
    PAGENAME=`echo "$BASENAME" | sed 's/--/\//g'`
    if [ "$PREFIX" ]; then
        if [ "$PAGENAME" = "Lichen" ]; then
            PAGENAME="$PREFIX"
        else
            PAGENAME="$PREFIX/$PAGENAME"
        fi
    fi
    echo "AddRevision|$BASENAME|$PAGENAME" >> "$MANIFEST"
done

if [ ! -e "releases" ]; then
    echo "No releases to add to the page package!" 1>&2
else
    # Combine the releases with the pages.

    ATTACHMENT="attachment_"

    for FILENAME in releases/* ; do
        BASENAME=`basename "$FILENAME"`
        cp "$FILENAME" "$OUTDIR/$ATTACHMENT$BASENAME"
    done

    # Add the releases to the manifest.

    for FILENAME in releases/* ; do
        BASENAME=`basename "$FILENAME"`
        PAGENAME="Downloads"
        if [ "$PREFIX" ]; then
            PAGENAME="$PREFIX/$PAGENAME"
        fi
        echo "AddAttachment|$ATTACHMENT$BASENAME|$BASENAME|$PAGENAME" >> "$MANIFEST"
    done
fi

zip -j "$OUTDIR" "$OUTDIR/"*
