#!/bin/sh

for FILENAME in tests/* ; do

    # Detect tests in their own subdirectories.

    if [ -d "$FILENAME" ] ; then
        if [ -e "$FILENAME/main.py" ] ; then
            FILENAME="$FILENAME/main.py"
        else
            continue
        fi
    fi

    # Run tests without an existing cache.

    echo "$FILENAME..." 1>&2
    if ! ./lplc "$FILENAME" -r ; then exit 1 ; fi

    # Check for unresolved names in the cache.

    echo " (depends)..." 1>&2
    if grep '<depends>' -r "_cache" && \
       ! echo "$FILENAME" | grep -q '_bad[._]' ; then
       exit 1
    fi

    # Run tests with an existing cache.

    echo " (cached)..." 1>&2
    if ! ./lplc "$FILENAME" ; then exit 1 ; fi
    echo 1>&2

done
