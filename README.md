# dunetrigger Tutorial

## Setting up a fresh build of LArsoft

1. Get the container (all LArSoft code needs to be currently run with the apptainer environment).
```sh
/cvmfs/oasis.opensciencegrid.org/mis/apptainer/current/bin/apptainer shell --shell=/bin/bash \
-B /cvmfs,/exp,/nashome,/pnfs/dune,/opt,/run/user,/etc/hostname,/etc/hosts,/etc/krb5.conf \
--ipc --pid /cvmfs/singularity.opensciencegrid.org/fermilab/fnal-dev-sl7:latest
```

2. Ensure you have got the right UPS products.

```export UPS_OVERRIDE="-H Linux64bit+3.10-2.17"```

3. Setup DUNE software:

```source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh```

4. Set up specific version of DUNE code locally. Let's use v10_04_07d00 in this tutorial.
  
```setup dunesw v10_04_07d00 -q e26:prof```

> Note: you can see the list of available dunesw releases with  *ups list -aK+ dunesw*

5. Make a work area (development area where you work on code) and cd into that area. On dunegpvms this is done within the *app* directory:

```sh
cd /exp/dune/app/users/$USER
mkdir trigger_tutorial
cd trigger_tutorial
```

6. Create a fresh development/work area with the version of the dunesw code you previously picked

```mrb newDev -v v10_04_07d00 -q e26:prof```

7. At this stage the output should tell you to source local products - which you should do!

```source localProducts_larsoft_v10_04_07d00_e26_prof/setup```

8. Time to get the code. Go into the source directory and clone the repositories you want.
```sh
cd $MRB_SOURCE
mrb g  -t v10_04_07d00 dunetrigger
```

9. Build the code!

```sh
cd $MRB_BUILDDIR  #go to build directory
mrbsetenv #set up environment variables for build
mrb i --generator=ninja  #compile
```

9. Once compiling is finished, set up all the products in localProducts directory.
 
 ```mrbslp```

## Next time you log back in

You *only* need to go through the previous stages when setting up a fresh development area.
Otherwise, simply make a script e.g. [setup_dune.sh](https://github.com/JamesJieranShen/dune-trigger-tutorial/blob/main/setup_dunesw.sh) which should let you pick up where you left off once you log back in:


**The above needs to be run within the container environment.**

## Running Simulations

As an example, let's run 10 events consisting of 500 MeV electrons in the 1z2x6 FD HD geometry. These things are typically done in the /data directory on FNAL machines.

```
cd  /exp/dune/app/users/${USER}
```

**Generator stage (Gen)**
```
lar -c prod_eminus_500MeV_xscan_dune10kt_1x2x6.fcl -n 10 -o singlee_test_gen.root
```

Each consecutive stage takes the artROOT output from the previous stage as input.

**Geant4 stage (G4)**
```
lar -c standard_g4_dune10kt_1x2x6.fcl singlee_test_gen.root -o singlee_test_g4.root -n -1
```

**Detector Simulation stage (detsim)**
```
lar -c detsim_dune10kt_1x2x6_notpcsigproc.fcl singlee_test_g4.root -o singlee_test_detsim.root -n -1
```

**Trigger Primitive Generation (TPG)**
Let's use this custom fcl file [run_tpg.fcl](https://github.com/JamesJieranShen/dune-trigger-tutorial/blob/main/fcls/run_tpg.fcl) which runs the TPG.

The TPMakers take `raw::RawDigit` as input, and output `dunedaq::trgdataformats::TriggerPrimitive` objects.

Run the above with
```
lar -c run_tpg.fcl singlee_test_detsim.root -o singlee_test_tps.root -n -1
```

**Trigger Activity Making**
Let's use this custom fcl file [run_tam.fcl](https://github.com/JamesJieranShen/dune-trigger-tutorial/blob/main/fcls/run_tam.fcl) which runs the ChannelAdjacency TA Maker.

The TAMaker take `dunedaq::trgdataformats::TriggerPrimitive` as input, and output `dunedaq::trgdataformats::TriggerActivityData` objects.


Run the above with
```
lar -c run_tam.fcl singlee_test_tps.root -o singlee_test_tas.root -n -1
```

**Generate AnaTree**
[run_ana.fcl](https://github.com/JamesJieranShen/dune-trigger-tutorial/blob/main/fcls/run_ana.fcl) will generate a series of trees for a root file's MCTruth, SIMIDE, and TP/TA/TC information.

Run the above with 
```
lar -c run_ana.fcl singlee_test_tas.root -T singlee_test_ana.root -n -1
```
Note the different output flag (`-T` vs `-o`), as we are now asking an _Analyzer_ to generate a ROOT File, but not asking a _Producer_ to generate an art output.

## Visualize the trigger objects
I've written a simple python script to help with visualizing the trigger objects created by the above simulation. To run this, you will need `numpy`, `matplotlib`, and `uproot`. 

To visualize an event from the anaTree created above, do 
```sh
python trigger_evd.py -i singlee_test_ana.root -e 1 [--combine]
```
The above command will display the 1st event of the file `singlee_test_ana.root`. If `--combine` is provided, the display will overlay signal from all APAs into one single APA (`channel = channel % channel_per_apa`). If all goes well, you well see:
- recangular blobs representing TPs. The color of the blob represents the magnitude of its peak.
- Red rectangular boxes representing TAs. The corners of the box signifies the channel/time of the start/end of the TA. The dotted crosshair inside each box signals the channel/time of the peak of the TA.



