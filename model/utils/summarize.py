# get only condtaints
# first run 
# head -n -0 *.txt > ../../utils/results.txt
# in outs/ts


def summarize(name):
	old_line = ""
	summ = open("summ.txt","w")
	no_flow = []
	for line in open(name + ".txt","r"):
		if "==> " in line:
			old_line = line.strip().replace(".ts.txt <==", " =?=>").replace("==> ","")
		elif "CONDTAINT REGS: [\'" in line:
			summ.write(line.replace("CONDTAINT REGS:",old_line))
		elif "CONDTAINT REGS:" in line:
			no_flow = no_flow + [old_line.replace(" =?=>","")]
	summ.write("\nNo flows: " + str(no_flow))
			
summarize("results")
