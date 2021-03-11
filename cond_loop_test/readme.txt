Test directory, research plan:

1) Consult 2pass.py generation in main directory, set n = 1.

    This is included in cond_loop_test as r_CLT_TR0_M_AXI_AWADDR_wire*

2) Select one conditionally tainted register, test_reg_n.

    Look at *.spinfo, select a file. Selection criteria, M_AXI_*_wire, break ties alphabetically

3) [On Fabricant] Using Tortuga, set test_reg_1 as a taint source using a dummy property.

    Edit iACW_sps.as in local folder found by following do_fabricant in main directory.
    Verify novel vcd generation using greg assert iACW.vcd

4) [Fabricant -> Local] Convert Tortuga output .vcd to a 2pass.py input .vcd using refine_vcd.py

    Current best practice is on an intermediate work directory on fabricant between Isadora and iterative_build.

5) [Local] Configure and run 2pass.py, with cleanup configured. 

    This directories 2pass has the 2nd pass commenting out, cleanup commented in, and spinfo cleanup commented out. The input also varies.

6) [Local -> Fabricant] Consult 2pass.py generation and repeat loop beginning at step 2 with n = n+1

Process Notes:

Only run 2pass up until second miner pass to identifying conditional taints without incurring the second pass mining cost.

Name VCD's using trn for test_reg_n, maintain this terminology through the loop.

Rename the internal 2pass spinfos to retain the list of conditional taints at each stage - consider encoding here with *_ts.out.

Performance Notes:

Tortuga stage takes about 160 seconds

Daikon stage takes about 10 seconds.

All other stages about a second or less.

Transmitting VCD's from UCSD to my local Daikon environment has some non-zero time cost.
