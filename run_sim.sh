lar -c prod_eminus_500MeV_xscan_dune10kt_1x2x6.fcl -n 10 -o singlee_test_gen.root 
lar -c standard_g4_dune10kt_1x2x6.fcl singlee_test_gen.root -o singlee_test_g4.root -n -1
lar -c detsim_dune10kt_1x2x6_notpcsigproc.fcl singlee_test_g4.root -o singlee_test_detsim.root -n -1
lar -c fcls/run_tpg.fcl singlee_test_detsim.root -o singlee_test_tps.root -n -1
lar -c fcls/run_tam.fcl singlee_test_tps.root -o singlee_test_tas.root -n -1
lar -c fcls/run_ana.fcl singlee_test_tas.root -T singlee_test_ana.root -n -1

