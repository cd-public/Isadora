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
	#needed_regs = ["ARESETN","ACLK"]	# tracks elements of original design state to preserve in refinement
	refined_vars = []					# tracks VCD internal names of preserved state
	cache = ""
	cache_live = False
	# values equal to a constant in first pass - created using the get_shadows function in 2pass.py and manually editing r_iACW_1_s.out into a single list
	ban_list = []
	
## step -1: populated needed_regs	

	#needed_regs = needed_regs + ["M_AXI_AWADDR_wire"] + ["M_AXI_AWADDR_INT"]
	#for i in range(22,37):
	#	needed_regs = needed_regs + ["reg" + str(i) + "_w_config"]
	
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
			if "module myHWtask" in line:
				step1 = False
				step2 = True
			else:
				#for needed_reg in needed_regs:
					#if " " + needed_reg + " " in line:
				if "_AXI_" in line and "wire" in line and line.split()[4] not in ban_list:
						vcd_out.write(line)
						refined_vars = refined_vars + [line.split()[3]]
						
						
## step 2: modules
		
		## target is modules named test.u0.sec_inst_assertion_SP01_<SEND/RECEIVE>_M_AXI_<REG>.shadow_dut.shadow_M_AXI_<REG>*

		if step2:
			
			## track the current module
			
			if "dumpvars" in line:
				step2 = False
				step3 = True
				vcd_out.write("$enddefinitions $end\n$dumpvars\n#0\n")
			elif "$scope module " in line:
				if "shadow_dut" in line:# and "_AXI_" in curr_module:
					tag = curr_module #curr_module.split("_AXI_")[1]
				else:
					tag = ""
				curr_module = line.split()[2]
			#elif tag != "" and "shadow_M_AXI_" + tag in line and "_or" not in line and "_old" not in line and "_ctr" not in line and "_tnt" not in line:
			elif tag != "" and "shadow_" in line and "_or" not in line and "_old" not in line and "_ctr" not in line and "_tnt" not in line and "shadow_n" not in line and "shadow_open" not in line and line.split()[4] not in ban_list:
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

refine("iCTreply37")
#refine("aac_samp")