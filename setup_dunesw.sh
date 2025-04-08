#!/bin/bash
export UPS_OVERRIDE="-H Linux64bit+3.10-2.17" # makes certain you get the right UPS
source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh
export DUNESW_QUALIFIER=e26:prof
export COMPILER=e26

export DUNESW_VERSION=v10_04_07d00
setup dunesw $DUNESW_VERSION -q $DUNESW_QUALIFIER
source dunesw-${DUNESW_VERSION}/localProducts_larsoft_*/setup
mrbslp

# setup larsoft ${LARSOFT_VERSION} -q debug:${COMPILER}
alias buildsw='ninja -C ${MRB_BUILDDIR} -k 0 install | grep -v "Up-to-date" '

