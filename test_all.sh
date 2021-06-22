#!/bin/sh

# This tool runs the toolchain for each of the tests, optionally building and
# running the test programs.
#
# Copyright (C) 2016, 2017, 2021 Paul Boddie <paul@boddie.org.uk>
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

PROGNAME=$0
OPTION=$1
shift 1
MAKE_OPTIONS="$*"

LPLC="./lplc"
DATADIR="_main.lplc"
TESTINPUT="_results/testinput.txt"

# Expect failure from the "bad" tests.

expect_failure() {
    echo "$FILENAME" | grep -q '_bad[._/]'
    return $?
}

# Check deduction output for type warnings, indicating that the program contains
# errors.

check_type_warnings() {

    if [ -e "$DATADIR/_deduced/type_warnings" ] && \
       [ `stat -c %s "$DATADIR/_deduced/type_warnings"` -ne 0 ] ; then

       echo "Type warnings in deduced information." 1>&2
       return 1
    fi

    return 0
}

# Main program.

# Show help if requested.

if [ "$OPTION" = '--help' ] ; then
    cat 1>&2 <<EOF
Usage: $0 [ --build | --build-only | --run-built ] [ <make options> ]

Run the toolchain over all tests in the tests directory.

If --build is specified, the generated program code will be compiled and run,
with the results collected in the _results directory.

If --build-only is specified, the generated programs themselves will be
collected in the _results directory, each taking their name from that of the
main program file used as input.

If --run-built is specified, any generated programs in the _results directory
will be run and their output collected in the _results directory.

By using --build-only on one system, copying the _results directory to another
system, and then running this script with the --run-built option on the other
system, it becomes possible to test the toolchain output on the other system
without needing to actually use the toolchain on that system. This permits the
testing of cross-compiled programs.

For example, to build on one system but not run the generated programs:

ARCH=mipsel-linux-gnu $PROGNAME --build-only

And to run the generated programs on another system:

$PROGNAME --run-built

Of course, this script will need to be copied to the target system if it is not
already available there.

Build and output logs are stored in the _results directory with the .build and
.out suffixes employed respectively, one of each kind for each generated
program.

The make options can be used to specify things like the number of processes
employed to perform a build of each program. For example:

$PROGNAME --build -j8
EOF
    exit 1
fi

# If just running existing programs, do so now and exit.

if [ "$OPTION" = '--run-built' ] ; then
    for FILENAME in _results/* ; do
        TESTNAME=`basename "$FILENAME"`

        # Skip non-program files.

        if [ ! -x "$FILENAME" ]; then
            continue
        fi

        echo "$FILENAME..." 1>&2
        OUTLOG="_results/$TESTNAME.out"
        OUTCODE="_results/$TESTNAME.exitcode"

        echo " (run)..." 1>&2
        "$FILENAME" > "$OUTLOG" < "$TESTINPUT"
        echo $? > "$OUTCODE"
    done

    exit 0
fi

# Make any required results directory.

if [ "$OPTION" = '--build' ] || [ "$OPTION" = '--build-only' ] ; then
    if [ ! -e "_results" ]; then
        mkdir "_results"
    else
        rm "_results/"*
    fi

    cp "tests/testinput.txt" "$TESTINPUT"
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

    # Skip non-program files.

    if [ `basename "$FILENAME"` = "$TESTNAME" ]; then
        continue
    fi

    # Compile tests without an existing cache.

    echo "$FILENAME..." 1>&2
    if ! "$LPLC" -c -r "$FILENAME" ; then
        if ! expect_failure ; then
            exit 1
        else
            echo 1>&2
            continue
        fi
    fi

    # Check for unresolved names in the cache.

    echo " (depends)..." 1>&2
    for CACHEFILE in "$DATADIR/_cache/"* ; do
        STARTLINE=`grep -n '^deferred:' "$CACHEFILE" | cut -d: -f 1`
        if tail -n +$(($STARTLINE + 2)) "$CACHEFILE" | grep -q '<depends>' ; then
           echo "Unresolved names in the cache." 1>&2
           exit 1
        fi
    done

    # Check for type warnings in deduction output.

    echo " (warnings)..." 1>&2
    if ! check_type_warnings ; then exit 1 ; fi

    # Compile tests with an existing cache.

    echo " (cached)..." 1>&2
    if ! "$LPLC" -c "$FILENAME" ; then exit 1 ; fi

    echo " (warnings)..." 1>&2
    if ! check_type_warnings ; then exit 1 ; fi

    # Build and run if appropriate.

    if [ "$OPTION" = '--build' ] || [ "$OPTION" = "--build-only" ] ; then
        BUILDLOG="_results/$TESTNAME.build"
        OUTLOG="_results/$TESTNAME.out"
        OUTCODE="_results/$TESTNAME.exitcode"

        echo " (build)..." 1>&2
        if ! make -C "$DATADIR/_generated" clean > "$BUILDLOG" 2>&1 || \
           ! make -C "$DATADIR/_generated" $MAKE_OPTIONS > "$BUILDLOG" 2>&1 ; then
            exit 1
        fi

        if [ "$OPTION" = "--build-only" ]; then
            mv "$DATADIR/_generated/main" "_results/$TESTNAME"
        else
            echo " (run)..." 1>&2
            "$DATADIR/_generated/main" > "$OUTLOG" < "$TESTINPUT"
            echo $? > "$OUTCODE"
        fi
    fi

    echo 1>&2
done
