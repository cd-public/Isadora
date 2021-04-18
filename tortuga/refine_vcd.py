def refine(name):

## refine vcd

	vcd_in = open(name + ".vcd","r")
	vcd_out = open("r_" + name + ".vcd","w")
	
	## inits
	step0 = True 						# tracks location in the VCD
	step1 = False
	step2 = False
	step3 = False
	orig_design_regs = set()			# tracks verilog names of origianl design
	refined_vars = []					# tracks VCD internal names of original design
	cache = ""							# tracks timing info
	cache_live = False
	tag = ""							# internal line read variable for vcd encoding
	active = False						# tracks if copying is active
	
	for line in vcd_in:
	
## step 0: copy header

		if step0:
   
			if "scope" in line:
				step0 = False
				step1 = True
			else:
				vcd_out.write(line)

## step 1: copy original design state

		## assume all state in "u0" module

		if step1:
			
			if "module " in line and "module u0" not in line and active:
				step1 = False
				step2 = True
				active = False
			elif "module u0" in line:
				active = True
			elif active and "var" in line:
				vcd_out.write(line)
				orig_design_regs.add(line.split()[4])
				refined_vars = refined_vars + [line.split()[3]]
				
						
						
## step 2: modules
		
		## assume a single relevant shadow_dut
		
		if step2:
						
			orig_design_regs = list(orig_design_regs)
			orig_design_regs.sort()
			
			if "dumpvars" in line:
				step2 = False
				step3 = True
				vcd_out.write("$enddefinitions $end\n$dumpvars\n#0\n")
				active = False
			elif "module" in line:
				if "module shadow_dut" in line:
					active = True
				else:
					module_name = line.split()[2]
					active = False
			elif active:
				for reg in orig_design_regs:
					if "shadow_" + reg + " " in line:
						vcd_out.write(line.replace("shadow","shadow_" + module_name)
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

refine("iACW")