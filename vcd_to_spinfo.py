# vcd to daikon

# creates one file - spinfo

prefix = "\n\nPPT_NAME ..tick\n"

def make_spinfo(name,header):
	to_write = open(name + ".spinfo","w")
	to_write.write(prefix)
	key = [line.split()[4] for line in header]
	key_t = list(filter(lambda x: "_t" in x, key))
	key_t = [reg.split("[")[0] for reg in key_t]
	for reg in key_t: 
		to_write.write("\"1\"==orig(" + reg + ")\n")
	for reg in key_t: 
		to_write.write("\"1\"==orig(" + reg + ")")
		for reg2 in key_t:
			if reg2 != reg:
				to_write.write(" && \"0\"==orig(" + reg + ")")
		to_write.write("\n")
		
def read(name):
	to_read = open(name + ".vcd","r")
	# get header
	header = []
	in_header = True
	# process the headder
	while in_header:
		line = to_read.readline()
		if "dumpvars" in line:
			in_header = False
		if "$var" in line and "clk" not in line:
			header = header + [line]
	key = make_spinfo(name,header)
		
read("aes_tb")
