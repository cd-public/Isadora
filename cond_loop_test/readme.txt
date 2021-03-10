Test directory, research plan:

1) Consult 2pass.py generation in main directory, set n = 1.

2) Select one conditionally tainted register, test_reg_n.

    Look at *.spinfo, select a file. Selection criteria, M_AXI_*_wire, break ties alphabetically

3) [On Fabricant] Using Tortuga, set test_reg_1 as a taint source using a dummy property.

    Edit iACW_sps.as in local folder found by following do_fabricant in main directory.

4) [Fabricant -> Local] Convert Tortuga output .vcd to a 2pass.py input .vcd using refine_vcd.py

5) [Local -> Daikon] Configure and run 2pass.py, with cleanup configured. 

6) [Daikon -> Fabricant] Consult 2pass.py generation and repeat loop beginning at step 2 with n = n+1

Process Notes:

Only run 2pass up until second miner pass to identifying conditional taints without incurring the second pass mining cost.

Name VCD's using trn for test_reg_n, maintain this terminology through the loop.

Rename the internal 2pass spinfos to retain the list of conditional taints at each stage - consider encoding here with *_ts.out.
