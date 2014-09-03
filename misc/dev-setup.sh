#!/bin/bash

#
# This assumes the argument to --prefix down below is somewhere you have
# write access.
#

waruninst() {
    if [ -r setup.py ] && python lib/warren/__init__.py ; then
        if [ -r install.log ]; then
            echo "Uninstalling ..."
            xargs rm -v < install.log
        else
            echo "Error: can't read install.log to uninstall"
            return 2
        fi
    else
        echo "Error: you must be in the root of the source distribution."
        return 1
    fi
}

warinst() {
    if [ -r setup.py ] && python lib/warren/__init__.py > /dev/null ; then
        if [ "$1" = "clean" ]; then
            waruninst
            python setup.py clean
        fi
        python setup.py install \
            --prefix=/usr/local --pack-resources --record install.log
    else
        echo "Error: you must be in the root of the source distribution."
        return 1
    fi
}

export -f waruninst
export -f warinst
