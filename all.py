from os import system

# vcd to daikon

# creates two files - dtrace and decls

prefix = "input-language C/C++\ndecl-version 2.0\nvar-comparability implicit\n\n"

nonce = 1

def make_decls(name,header):
	prefix = "input-language C/C++\ndecl-version 2.0\nvar-comparability implicit\n\n"
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

def make_spinfo(name,header):
	prefix = "\n\nPPT_NAME ..tick\n"
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
	make_spinfo(name,header)
	key = make_decls(name,header)
	# now we load the key for the first dump
	line = to_read.readline() # skip first timestamp
	line = to_read.readline() # load first post timestamp line
	regs = len(header)
	while "#" not in line[0]: 
		splits = line.split()
		if len(splits) == 1:
			splits = [splits[0][0], splits[0][1:]]
		i = -1
		for index in range(regs):
			if (len(splits) > 1):
				if key[index][1] in splits[1]:
					i = index
		if i > -1:
			key[i] = key[i] + [splits[0].replace('b','')]
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
			if len(splits) == 1:
				splits = [splits[0][0], splits[0][1:]] 
			i = -1
			for index in range(regs):
				if (len(splits) > 1):
					if key[index][1] in splits[1]:
						i = index
			if i > -1:
				key[i][3] = splits[0].replace('b','')
				change = True
		line = to_read.readline()

def post(name):
	in_prefix = True
	in_point = False
	point_info = []
	for_out = open("post_" + name, "w")
	for line in open(name, "r"):
		if "===" in line:
			in_prefix = False
			if in_point: 
				# print here
				for s in point_info[0]:
					l = list(s)
					l.sort()
					text = str(l).replace("zzorig","#-1 ").replace("[","").replace("]","").replace("\'","")
					for_out.write("==: " + text + "\n")
				for line in point_info[2]:
					for_out.write(line + "\n")
			in_point = False
		elif in_prefix:
			1 == 1
		elif "..tick():::EXIT;" in line:
			for_out.write(line.strip().replace("\"","").replace("..tick():::EXIT;condition=","\nGiven \"") + "\":\n\n")
			in_point = True
			point_info = [[],[],[]]
		elif "..tick():::EXIT" in line:
			#for_out.write("global condition\n")
			# not implemented
			in_point = False
			# point_info = [[],[],[],[],[]]
		elif in_point: # property case
			# we can have (1) equalities (2) inequalities (3) one of's (4) implication (5) bi-implication
			# implication and bi-implication only occur in global case - not implemented
			# inequalities are one of (1) > (2) < (3) <= (4) >= (5) !=
			# inequalities likely aren't interesting - not implemented
			line = line.strip().replace("\"","")
			if "==" in line:
				regs = line.split(" == ")
				regs = [reg.strip().replace("orig","zzorig").replace("(","").replace(")","") for reg in regs]
				added = False
				for s in point_info[0]:
					for reg in regs:
						if reg in s:
							for reg in regs:
								s.add(reg)
								added = True
				if not added:
					point_info[0] += [set(regs)]
			if "one of" in line:
				point_info[2] += [line.strip().replace("orig","#-1 ").replace("(","").replace(")","") ]

def do_all(name):
	read(name)
	# For this to work must first do 
	# export JAVA_HOME=${JAVA_HOME:-$(dirname $(dirname $(dirname $(readlink -f $(/usr/bin/which java)))))}
	# export CLASSPATH="/home/mars/radish/daikon-5.7.2/daikon.jar"
	# export DAIKONDIR="/home/mars/radish/daikon-5.7.2"
	system("java daikon.Daikon " + name + ".decls " + name + ".dtrace " + name + ".spinfo >" + name + ".out")
	post(name + ".out")

		
do_all("aes_tb")
