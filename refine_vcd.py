def refine(name):

## refine vcd

	vcd_in = open(name + ".vcd","r")
	vcd_out = open("r_" + name + ".vcd","w")
	
	## inits
	step0 = True 						# tracks location in the VCD
	step1 = False
	step2 = False
	step3 = False
	curr_module = ""
	tag = ""
	needed_regs = ["ARESETN"]		 	# tracks elements of original design state to preserve in refinement
	refined_vars = []					# tracks VCD internal names of preserved state
	cache = ""
	cache_live = False
	
	for line in vcd_in:

## step 0: copy header

		if step0:
			if "scope" in line:
				step0 = False
				step1 = True
			else:
				vcd_out.write(line)

## step 1: copy original design state

		if step1:
			if needed_regs == []:
				step1 = False
				step2 = True
			else:
				for needed_reg in needed_regs:
					if " " + needed_reg + " $end" in line:
						vcd_out.write(line)
						refined_vars = refined_vars + [line.split()[3]]
						needed_regs.remove(needed_reg)
						
## step 2: modules
		
		## target is modules named test.u0.sec_inst_assertion_SP01_<SEND/RECEIVE>_M_AXI_<REG>.shadow_dut.shadow_M_AXI_<REG>*

		if step2:
			
			## track the current module
			
			if "dumpvars" in line:
				step2 = False
				step3 = True
				vcd_out.write("$enddefinitions $end\n$dumpvars\n#0\n")
			elif "$scope module " in line:
				if "shadow_dut" in line:
					tag = curr_module.split("_AXI_")[1]
				else:
					tag = ""
				curr_module = line.split()[2]
			elif tag != "" and "shadow_M_AXI_" + tag in line:
				vcd_out.write(line)
				refined_vars = refined_vars + [line.split()[3]]

# step 3:
		
		if step3:
		
		## two line cases, two var cases

			if "#" in line[0]:
				if line.strip() != "#0":
					cache = line
					cache_live = True
			else:
				splits = line.strip().split()
				if len(splits) == 1:
					tag = line[1:].strip()
				else:
					tag = splits[1]
				if tag in refined_vars:
					if cache_live:
						vcd_out.write(cache)
						cache_live = False
					vcd_out.write(line)
				
refine("aac_sp_01")
#refine("aac_samp")