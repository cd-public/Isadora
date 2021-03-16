import glob

for file in glob.glob("*.spinfo"):
	in_file = open(file,"r")
	out_file = open(file.replace(".spinfo","_ts.out"),"a")
	cts = []
	for line in in_file:
		# want to handle lines that look like "0==orig(shadow_AW_ADDR_VALID) && 0!=shadow_AW_ADDR_VALID"
		if "0==orig(shadow_" in line:
			cts = cts + [line.split()[0].replace("0==orig(shadow_","")[:-1]]
	out_file.write("CONDTAINT REGS: " + str(cts) + "\n")