export UPS_OVERRIDE="-H Linux64bit+3.10-2.17" # makes certain you get the right UPS
source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh
export DUNESW_QUALIFIER=e26:prof
export COMPILER=e26

export DUNESW_VERSION=v10_04_07d00
setup dunesw $DUNESW_VERSION -q $DUNESW_QUALIFIER
mkdir trigger_tutorial
cd trigger_tutorial
mrb newDev -v $DUNESW_VERSION -q $DUNESW_QUALIFIER
source localProducts_*/setup
cd $MRB_SOURCE
mrb g -t $DUNESW_VERSION dunetrigger 
cd $MRB_BUILDDIR
mrbsetenv
mrb i --generator=ninja
mrbslp

