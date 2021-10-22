Code:  https://github.com/cd-public/Isadora
Paper: https://cd-public.github.io/papers/2021/ASHES2021.pdf

Script: https://github.com/cd-public/Isadora/blob/master/model/single/utils/times.py
Daikon output file example: https://github.com/cd-public/Isadora/blob/master/model/single/outs/edges/0_117_246_375_539.txt
Post-processed file example: https://github.com/cd-public/Isadora/blob/master/model/single/outs/posts/0_117_246_375_539.p.txt
Conditions.txt, which is S_flows from the paper: https://github.com/cd-public/Isadora/blob/master/model/single/utils/conditions.txt

Target optimizations:
(1) Stop using VCDs
(2) Easy way of running miner 
(3) Move to group github

Target functionality expansions:
(1) Lossless postprocessing
(2) Decouple src-model-vcd 1:1:1 technique for flow tracking
(3) Symbolic execute security models rather than simulating
(4) End testbench reliance

Symbolic execution paper: https://madhu.cs.illinois.edu/cs598-fall10/king76symbolicexecution.pdf
The Zhang/Sturton paper on hw symbolic execution: https://www.cs.unc.edu/~csturton/papers/FMS2018.pdf

Running Isadora on Fabricant end-to-end right now, which should work on ACW/Pico and probably nothing else:

(0) Set up the environment. (https://github.com/cd-public/Isadora/tree/master/tortuga)
a. do_all first couple lines does this for Tortuga (mentioned below)
b. Daikon.txt includes the 3 lines used to add Daikon to path and how to verify it's set up.
(0 part 2) Decide what sources you want and load them into the autogen scripts
(1) Do vcd gen, two options
a. "autogen" which lives on fabricant somewhere
b. "do_all" using "make_do_all" and copy-pastes "do_all" into terminal
(2) Refine the vcds and move them into a vcd subdirectory, with times.py in a util subdirectory.
a. refine_vcd.py does this for one vcd with a no hierarchy 
b. refine_2.py is a combination refiner/module flattener that might do this for vcds with a hierarchy but it might also just not work. 
(3) Run times.py which should generate the full model.
