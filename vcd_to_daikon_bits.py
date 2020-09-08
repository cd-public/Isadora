# vcd to daikon

# creates two files - dtrace and decls

prefix = "input-language C/C++\ndecl-version 2.0\nvar-comparability implicit\n\n"

nonce = 1



def make_decls(name,header):
	suffix = "\n	var-kind variable\n	rep-type int\n	dec-type int\n	comparability 1 \n"
	to_write = open(name + ".decls","w")
	to_write.write(prefix)
	# make key
	key = [line.split()[2:5] for line in header]
	for point in ["ppt ..tick():::ENTER\n  ppt-type enter\n","\nppt ..tick():::EXIT0\n  ppt-type subexit\n"]:
		to_write.write(point)
		for reg in key:
			for bit in range(int(reg[0])):
				to_write.write("  variable " + reg[2].split("[")[0] + "_" + str(bit) + "_" + suffix)
	return key

def dump(key,file,nonce):
	if nonce > 0:
		points = ["..tick():::EXIT0\nthis_invocation_nonce\n" + str(nonce) + "\n", "..tick():::ENTER\nthis_invocation_nonce\n" + str(nonce + 1) + "\n"]
	else:
		points = ["..tick():::ENTER\nthis_invocation_nonce\n" + str(nonce + 1) + "\n"]
	for point in points:
		file.write(point)
		for reg in key:
			#prep the bits!
			if "x" in reg[3]:
				bits = ["-1"] * int(reg[0])
			else:
				bits = list(reg[3])
				bits.reverse()
				bits = bits + (int(reg[0]) - len(bits)) * ["0"]
			for bit in range(int(reg[0])):
				file.write(reg[2].split("[")[0] + "_" + str(bit) + "_\n" + bits[bit] + "\n1\n")
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
		if "$var" in line:
			header = header + [line]
	key = make_decls(name,header)
	# now we load the key for the first dump
	line = to_read.readline() # skip first timestamp
	line = to_read.readline() # load first post timestamp line
	while "#" not in line[0]: 
		splits = line.split()
		i = 0
		for index in range(len(key)):
			if key[index][1] in splits[1]:
				i = index
		key[i] = key[i] + [splits[0][1:]]
		line = to_read.readline()
	to_write = open(name + ".dtrace","w")
	to_write.write(prefix)
	nonce = 0
	while len(line) > 0: 
		if "#" in line[0]:
			nonce = dump(key,to_write,nonce)
		else:
			splits = line.split()
			i = 0
			for index in range(len(key)):
				if key[index][1] in splits[1]:
					i = index
			key[i][3] = splits[0][1:]
		line = to_read.readline()
		
read("aes_tb")
