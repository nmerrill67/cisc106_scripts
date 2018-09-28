#!/bin/bash



# This file is part of VPL for Moodle - http://vpl.dis.ulpgc.es/
# Script for running Python language
# Copyright (C) 2014 onwards Juan Carlos Rodríguez-del-Pino
# License http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
# Author Juan Carlos Rodríguez-del-Pino <jcrodriguez@dis.ulpgc.es>

# @vpl_script_description Using python3 with the first file
# load common script and check programs
. common_script.sh
check_program python3
if [ "$1" == "version" ] ; then
        echo "#!/bin/bash" > vpl_execution
        echo "python3 --version" >> vpl_execution
        chmod +x vpl_execution
        exit
fi
cat common_script.sh > vpl_execution

if [ "`cat $VPL_SUBFILE0 | grep matplotlib`" == "" ];  then
    TERM=
else
    TERM="xterm -e "
fi
echo $TERM
check_program xterm
echo "${TERM}python3 $VPL_SUBFILE0 \$@" >>vpl_execution
chmod +x vpl_execution
grep -E "matplotlib" $VPL_SUBFILE0 &> /dev/null
if [ "$?" -eq "0" ]     ; then
    mv vpl_execution vpl_wexecution
fi
