#need:

#every reg in a module in u0

#every reg in a module in shadow_dut that is in the same module in u0 and prefixed with shadow_dut

#unique naming scheme (do we want to keep shadow or module name at the front?)

#do we want to redo main to recognize modules (and do comparisons within them)

#FOR NOW if we do unique naming scheme with module after shadow the miner should still work



def refine(name):

## refine vcd

	vcd_in = open(name + ".vcd","r")
	vcd_out = open("r_" + name + ".vcd","w")
	
	## inits
	step0 = True 						# tracks location in the VCD
	step1 = False
	step2 = False
	step3 = False
	orig_design_regs = set()			# tracks verilog names of original design
	refined_vars = []					# tracks VCD internal names of original design
	cache = ""							# tracks timing info
	cache_live = False
	tag = ""							# internal line read variable for vcd encoding
	active = False						# tracks if copying is active
	mod_path = []						# tracks current module location
	
	for line in vcd_in:
	
## tracking: track module path

		if "scope" in line:
			# either entering or exiting a module
			if "$scope " in line:
				# add module name
				mod_path = mod_path + [line.split()[2]]
			if "$upscope $end" in line:
				# clip module
				mod_path = mod_path[:-1]
	
## step 0: copy header

		if step0:
   
			if "scope" in line:
				step0 = False
				step1 = True
			else:
				vcd_out.write(line)

## step 1: copy original design state

		## assume all state in first degree submodules of the "u0" module

		if step1:
			
			if "module " in line:
				# check for the special Tortuga module name
				if "sec_inst_assertion" in line:
					step1 = False
					step2 = True
					# convert the set to a list for iterating
					orig_design_regs = list(orig_design_regs)
					orig_design_regs.sort()
			elif "u0" in mod_path:
				if "u0" in mod_path[-2] and "var reg" in line:
					# edit line to include module name
					splits = line.split()
					new_name = mod_path[-1] + "_" + splits[4]
					vcd_out.write(line.replace(splits[4],new_name))
					orig_design_regs.add(new_name)
					refined_vars = refined_vars + [splits[3]]
				
						
						
## step 2: modules
		
		## assume a shadow_dut with relevant first degree submodules 
		
		if step2:
			
			if "dumpvars" in line:
				step2 = False
				step3 = True
				vcd_out.write("$enddefinitions $end\n$dumpvars\n#0\n")
				active = False
			elif "shadow_dut" in mod_path:
				if "shadow_dut" == mod_path[-2] and "var" in line and "parameter" not in line:
					for reg in orig_design_regs:
						splits = line.split()
						test_name = splits[4].replace("shadow_", mod_path[-1] + "_")
						if reg == test_name:
							vcd_out.write(line.replace("shadow_","shadow_" + mod_path[-1] + "_"))
							refined_vars = refined_vars + [splits[3]]

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

refine("confus")