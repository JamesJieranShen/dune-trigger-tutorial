# dunetrigger Tutorial 
## Setting up a fresh build of LArsoft 
1. Get the container (all LArSoft code needs to be currently run with the apptainer environment).
<span style="color: blue;">```/cvmfs/oasis.opensciencegrid.org/mis/apptainer/current/bin/apptainer shell --shell=/bin/bash -B /cvmfs,/exp,/nashome,/pnfs/dune,/opt,/run/user,/etc/hostname,/etc/hosts,/etc/krb5.conf --ipc --pid /cvmfs/singularity.opensciencegrid.org/fermilab/fnal-dev-sl7:latest```</span>

2. Ensure you have got the rught UPS products.
<span style="color: blue;">```export UPS_OVERRIDE="-H Linux64bit+3.10-2.17"```</span>

3. Setup DUNE software:
<span style="color: blue;">```source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh```</span>

 4. Set up specific version of DUNE code locally. Let's use v10_04_07d00 in this tutorial.  
<span style="color: blue;">```setup dunesw v10_04_07d00 -q e26:prof```</span>
> Note: you can see the list of available dunesw releases with  *ups list -aK+ dunesw*

5. Make a work area (development area where you work on code) and cd into that area. On dunegpvms this is done within the *app* directory:
<span style="color: blue;">```/exp/dune/app/users/$USER```</span>
<span style="color: blue;">```mkdir trigger_tutorial```</span>
<span style="color: blue;">```cd trigger_tutorial```</span>

6. Create a fresh development/work area with the version of the dunesw code you previously picked
<span style="color: blue;">```mrb newDev -v v10_04_07d00 -q e26:prof```</span>

7. At this stage the output should tell you to source local products - which you should do!
<span style="color: blue;">```source localProducts_larsoft_v10_04_07d00_e26_prof/setup```</span> 

8. Time to get the code. Go into the source directory and clone the repositories you want.
<span style="color: blue;">```cd $MRB_SOURCE ```</span>
<span style="color: blue;">```mrb g  -t v10_04_07d00 dunetrigger```</span>

8. Build the code!
<span style="color: blue;">```cd $MRB_BUILDDIR```</span>  #*(go to build directory)*
<span style="color: blue;">```mrbsetenv```</span> #*(set up environment variables)*
<span style="color: blue;">```mrb i -j4```</span> #*(compile)*
> Note: -j flag tells the compiler the number of cores to use, N. Maximum number available for building depends on machine type. N = 4 for dunegpvms 01-15, N = 16 for dunebuild 01-03.

9. Once compiling is finished, set up all the products in localProducts directory.
<span style="color: blue;"> ```mrbslp```</span>

## Next time you log back in 

You *only* need to go through the previous stages when setting up a fresh development area. 
Otherwise, simply make a script e.g. *setup_dune.sh* which should let you pick up where you left off once you log back in: 
```
#!/bin/bash
VERSION=v10_04_07d00  
QUALS=e26:prof  
export UPS_OVERRIDE="-H Linux64bit+3.10-2.17"

# Source the setup script for the DUNE software
source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh

# Setup the specific version of the DUNE software
setup dunesw ${VERSION} -q ${QUALS}

# Source the setup script for the local products associated to the development area
source localProducts_*/setup

# Set up the MRB source local products
mrbslp

# Speedy building! 
alias build="mrbsetenv; cd $MRB_BUILDDIR; mrb i -j4; mrbslp"
```

**The above needs to be run within the container environment.**


## Running Simulations
As an example, let's run 10 events consisting of 500 MeV electrons in the 1z2x6 FD HD geometry. These things are typically done in the /data directory on FNAL machines.

<span style="color: blue;">```cd  /exp/dune/app/users/${USER}```</span>

**Generator stage**
<span style="color: blue;">```lar -c prod_eminus_500MeV_xscan_dune10kt_1x2x6.fcl -n 10 -o singlee_test_gen.root ```</span>

Each consecutive stage takes the artROOT output from the previous stage as input. 

**Geant4 stage**
<span style="color: blue;">```lar -c standard_g4_dune10kt_1x2x6.fcl singlee_test_gen.root -o singlee_test_g4.root -n -1```</span>

**Detsim stage**
<span style="color: blue;">```lar -c detsim_dune10kt_1x2x6_notpcsigproc.fcl singlee_test_g4.root -o singlee_test_detsim.root -n -1```</span>

**Trigger Primitive Generation**
I have a basic fcl *run_tpg.fcl* which runs the TPG. 
```#include "geometry_dune.fcl"
#include "services_dunefd_horizdrift_1x2x6.fcl"
#include "tools_dune.fcl"

process_name: TriggerSimOnline 

services:
{
  TFileService: { fileName: "deleteme.root" }
  RandomNumberGenerator: {} #ART native random number generator
  WireReadout:          @local::dune_wire_readout
  Geometry:             @local::dune10kt_1x2x6_v6_refactored_geo
  message:              @local::dune_message_services_prod
  IFDH: {}
}

source:
{
  module_type: RootInput
  maxEvents:  10        # Number of events to create
  saveMemoryObjectThreshold: 0
}

physics:
{
  producers:
  {
    tpmakerTPC:
    {
     module_type: TriggerPrimitiveMakerTPC
     rawdigit_tag: "tpcrawdecoder:daq" #input to TPG-> Raw Digits
     tpalg: {
      tool_type: TPAlgTPCSimpleThreshold #Use Simple Threshold TPG alg.
      verbosity: 0
      threshold_tpg_plane0: 30 #induction U
      threshold_tpg_plane1: 30 #induction V
      threshold_tpg_plane2: 25 #collection plane threshold
     }
    }
  }

 stream1:  [ out1 ]
 sim: [ tpmakerTPC ]
 trigger_paths: [sim]

 end_paths: [stream1]
}

outputs:
{
 out1:
 {
   module_type: RootOutput
   fileName:    "singlee_test_trigprims.root"
   compressionLevel: 1
   saveMemoryObjectThreshold: 0 
   # drop the rawdigits after TPs are generated 
   outputCommands: ["keep *_*_*_*", "drop raw::RawDigit*_*_*_*"] 
 }
}
```

The TPMakers take ```raw::RawDigit``` as input, and output ```dunedaq::trgdataformats::TriggerPrimitive``` objects. 

Run the above with
<span style="color: blue;">```lar -c run_tpg.fcl singlee_test_detsim.root -o singlee_test_trigprims.root -n -1```</span>

