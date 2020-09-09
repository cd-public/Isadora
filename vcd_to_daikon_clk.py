# vcd to daikon

# creates two files - dtrace and decls

prefix = "input-language C/C++\ndecl-version 2.0\nvar-comparability implicit\n\n"

nonce = 1



def make_decls(name,header):
	suffix = "\n	var-kind variable\n	rep-type string\n	dec-type char*\n	comparability 1 \n"
	to_write = open(name + ".decls","w")
	to_write.write(prefix)
	# make key
	key = [line.split()[2:5] for line in header]
	for point in ["ppt ..tick():::ENTER\n  ppt-type enter\n","\nppt ..tick():::EXIT0\n  ppt-type subexit\n"]:
		to_write.write(point)
		for reg in key: 
			to_write.write("  variable " + reg[2].split("[")[0] + suffix)
		# add delay length
		to_write.write("  variable " + "delay" + suffix)
	# add delay slot to key
	out_key = key
	out_key = out_key + [[0, "", "delay", "0"]]
	return out_key

def dump(key,file,nonce):
	if nonce > 0:
		points = ["..tick():::EXIT0\nthis_invocation_nonce\n" + str(nonce) + "\n", "..tick():::ENTER\nthis_invocation_nonce\n" + str(nonce + 1) + "\n"]
	else:
		points = ["..tick():::ENTER\nthis_invocation_nonce\n" + str(nonce + 1) + "\n"]
	for point in points:
		file.write(point)
		for reg in key:
			file.write(reg[2].split("[")[0] + "\n\"" + reg[3] + "\"\n1\n")
		file.write("\n")
	return nonce + 1
			

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
	key = make_decls(name,header)
	# now we load the key for the first dump
	line = to_read.readline() # skip first timestamp
	line = to_read.readline() # load first post timestamp line
	regs = len(header)
	while "#" not in line[0]: 
		splits = line.split()
		i = -1
		for index in range(regs):
			if (len(splits) > 1):
				if key[index][1] in splits[1]:
					i = index
		if i > -1:
			key[i] = key[i] + [splits[0][1:]]
		line = to_read.readline()
	to_write = open(name + ".dtrace","w")
	to_write.write(prefix)
	nonce = 0
	last = 0
	curr = 0
	change = False
	while len(line) > 0: 
		if "#" in line[0]:		
			curr = nonce
			key[len(key)-1][3] = str(curr - last)
			if change:
				last = curr
			nonce = dump(key,to_write,nonce)
			change = False
		else:
			splits = line.split()
			i = -1
			for index in range(regs):
				if (len(splits) > 1):
					if key[index][1] in splits[1]:
						i = index
			if i > -1:
				key[i][3] = splits[0][1:]
				change = True
		line = to_read.readline()
		
read("aes_clk")
