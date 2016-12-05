#!/bin/sh

# Expect failure from the "bad" tests.

expect_failure() {
    return `echo "$FILENAME" | grep -q '_bad[._]'`
}

# Check deduction output for type warnings, indicating that the program contains
# errors.

check_type_warnings() {

    if [ -e "_deduced/type_warnings" ] && \
       [ `stat -c %s "_deduced/type_warnings"` -ne 0 ] ; then

       echo "Type warnings in deduced information." 1>&2
       return 1
    fi

    return 0
}

# Main program.

OPTION=$1

# Make any required results directory.

if [ "$OPTION" = '--build' ]; then
    if [ ! -e "_results" ]; then
        mkdir "_results"
    else
        rm "_results/"*
    fi
fi

# Perform each test.

for FILENAME in tests/* ; do
    TESTNAME=`basename "$FILENAME" .py`

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
    if ! ./lplc "$FILENAME" -r ; then
        if ! expect_failure; then
            exit 1
        else
            echo 1>&2
            continue
        fi
    fi

    # Check for unresolved names in the cache.

    echo " (depends)..." 1>&2
    if grep '<depends>' -r "_cache" ; then
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

    # Build and run if appropriate.

    if [ "$OPTION" = '--build' ]; then
        BUILDLOG="_results/$TESTNAME.build"
        OUTLOG="_results/$TESTNAME.out"

        echo " (build)..." 1>&2
        if ! make -C _generated clean > "$BUILDLOG" || \
           ! make -C _generated > "$BUILDLOG" ; then
            exit 1
        fi

        echo " (run)..." 1>&2
        if ! "_generated/main" > "$OUTLOG" ; then
            exit 1
        fi
    fi

    echo 1>&2
done
