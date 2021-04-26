regs = set()
for line in open("r_confus.vcd","r"):
	if "dumpvars" in line:
		regs = list(regs)
		regs.sort()
		open("regs.txt","w").write(str(regs))
	if "var reg" in line and "acw1" in line: # shadow state is in wires
		regs.add(line.split()[4].replace("_",".",1))