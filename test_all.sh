#!/bin/sh

# Expect failure from the "bad" tests.

expect_failure() {
    return `echo "$FILENAME" | grep -q '_bad[._]'`
}

# Check deduction output for type warnings, indicating that the program contains
# errors.

check_type_warnings() {

    if [ -e "_deduced/type_warnings" ] && \
       [ `stat -c %s "_deduced/type_warnings"` -ne 0 ] && \
       ! expect_failure ; then

       echo "Type warnings in deduced information." 1>&2
       return 1
    fi

    return 0
}

# Main program.

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
       ! expect_failure ; then

       echo "Unresolved names in the cache." 1>&2
       exit 1
    fi

    # Check for type warnings in deduction output.

    echo " (warnings)..." 1>&2
    if ! check_type_warnings ; then exit 1 ; fi

    # Run tests with an existing cache.

    echo " (cached)..." 1>&2
    if ! ./lplc "$FILENAME" ; then exit 1 ; fi

    echo " (warnings)..." 1>&2
    if ! check_type_warnings ; then exit 1 ; fi

    echo 1>&2
done
