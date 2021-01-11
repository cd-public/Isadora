from os import system

# vcd to daikon

# creates two files - dtrace and decls

prefix = "input-language C/C++\ndecl-version 2.0\nvar-comparability implicit\n\n"

nonce = 1

def make_decls(name,header):
	prefix = "input-language C/C++\ndecl-version 2.0\nvar-comparability implicit\n\n"
	suffix = "\n	var-kind variable\n	rep-type int\n	dec-type int\n	comparability 1 \n"
	to_write = open(name + ".decls","w")
	to_write.write(prefix)
	# make key
	key = [line.split()[2:] for line in header]
	last = ""
	for point in ["ppt ..tick():::ENTER\n  ppt-type enter\n","\nppt ..tick():::EXIT0\n  ppt-type subexit\n"]:
		to_write.write(point)
		for reg in key:	
			# only write a single var for each register, regardless of bit length, to decls
			if reg[2] != last:
				to_write.write("  variable " + reg[2] + suffix)
				last = reg[2]
		# add delay length
		to_write.write("  variable " + "delay" + suffix)
	for reg in key:
		# continue to store bits separately internally
		if len(reg) > 4:
			reg[2] = reg[2] + " " + reg[3]	
		while len(reg) > 3:
			reg.remove(reg[3])
	# add delay slot to key
	out_key = key
	out_key = out_key + [[0, "", "delay", "0"]]
	return out_key

def make_spinfo(name,header):
	prefix = "\n\nPPT_NAME ..tick\n"
	to_write = open(name + ".spinfo","w")
	to_write.write(prefix)
	key = [line.split()[4] for line in header]
	key_t = list(filter(lambda x: "reg" not in x and "_tnt" not in x and "_old" not in x and "_ctr" not in x and "_or" not in x, key)) # capture original regs and relevant shadow
	key_t = [reg for reg in key_t]
	last = ""
	for reg in key_t: 
		if reg != last:
			#to_write.write("\"1\"==orig(" + reg.replace("[","").replace("]","") + ")\n")
			to_write.write("0==orig(" + reg.replace("[","").replace("]","") + ")\n")
			last = reg

def dump(key,file,nonce):
	if nonce > 0:
		points = ["..tick():::EXIT0\nthis_invocation_nonce\n" + str(nonce) + "\n", "..tick():::ENTER\nthis_invocation_nonce\n" + str(nonce + 1) + "\n"]
	else:
		points = ["..tick():::ENTER\nthis_invocation_nonce\n" + str(nonce + 1) + "\n"]
	for point in points:
		file.write(point)
		# handle the differing bits
		last = ""
		val = ""
		first = True
		for reg in key:
			splits = reg[2].split()
			if splits[0] != last:
				if not first:
					if "x" in val: # hack for uninitialized values - bit values are always positive
						val = "-1"
					file.write(str(int(val,2)))
					file.write("\n1\n")
					val = ""
				else:
					first = False
				file.write(splits[0] + "\n") #.replace("]","") + "\n")
				val = val + reg[3]
				last = splits[0]
			elif splits[0] == last:
				val = val + reg[3]
		file.write(str(int(val,2)))
		file.write("\n1\n")
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
				if key[index][1] in splits[1] and splits[1] in key[index][1]:
					i = index
		if i > -1:
			key[i] = key[i] + [splits[0].replace('b','')]
		if i == -1:
			print(key[i])
			print(line)
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
					if key[index][1] in splits[1] and splits[1] in key[index][1]:
						i = index
			if i > -1:
				key[i][3] = splits[0].replace('b','')
				change = True
		line = to_read.readline() #.replace("[","").replace("]","")
	

def post(name):
	# need to remove globals
	in_prefix = True
	in_point = False
	in_global = False
	title = ""
	titled = False
	point_info = []
	global_struct = []
	one_ofs = []
	for_out = open("post_" + name, "w")
	for line in open(name, "r"):
		if "===" in line:
			in_prefix = False
			if in_point: 
				# print here
				titled = False
				for s in point_info[0]:
					if set(s) not in global_struct:
						if not titled:
							for_out.write(title)
							titled = True
						l = list(s)
						l.sort()
						text = str(l).replace("zzorig","orig").replace("[","").replace("]","").replace("\'","")
						#text = text.replace("shadow_M_AXI_","") # just for the AAC
						for_out.write("==: " + text + "\n")
				for line in point_info[2]:
					if line not in one_ofs:
						if not titled:
							for_out.write(title)
							titled = True
						for_out.write(line + "\n")
				if in_global:
					global_struct = [set(s) for s in point_info[0]]
					one_ofs = point_info[2]
					in_global = False
			in_point = False
		elif in_prefix:
			1 == 1
		elif "..tick():::EXIT;" in line:
			title = line.strip().replace("\"","").replace("..tick():::EXIT;condition=","\nGiven \"") + "\":\n\n"
			in_point = True
			in_global = False
			point_info = [[],[],[]]
		elif "..tick():::EXIT" in line:
			title = "Global conditions:\n\n"
			in_point = True
			point_info = [[],[],[]]
			in_global = True
		elif in_point: # property case
			# we can have (1) equalities (2) inequalities (3) one of's (4) implication (5) bi-implication
			# implication and bi-implication only occur in global case - not implemented
			# inequalities are one of (1) > (2) < (3) <= (4) >= (5) !=
			# inequalities likely aren't interesting - not implemented
			line = line.strip().replace("\"","")
			if " <==> " in line or " ==> " in line:
				1 == 1
			elif " == " in line:
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
			elif "one of" in line:
				point_info[2] += [line.strip().replace("(","").replace(")","") ]
	# last conditional
	if in_point: 
		titled = False
		for s in point_info[0]:
			if set(s) not in global_struct:
				if not titled:
					for_out.write(title)
					titled = True
				l = list(s)
				l.sort()
				text = str(l).replace("zzorig","orig").replace("[","").replace("]","").replace("\'","")
				#text = text.replace("shadow_M_AXI_","") # just for the AAC
				for_out.write("==: " + text + "\n")
		for line in point_info[2]:
			if line not in one_ofs:
				if not titled:
					for_out.write(title)
					titled = True
				for_out.write(line + "\n")#.replace("shadow_M_AXI_","") + "\n")


def do_all(name):
	read(name)
	# For this to work must first do 
	# export JAVA_HOME=${JAVA_HOME:-$(dirname $(dirname $(dirname $(readlink -f $(/usr/bin/which java)))))}
	# export CLASSPATH="/home/mars/radish/daikon-5.7.2/daikon.jar"
	# export DAIKONDIR="/home/mars/radish/daikon-5.7.2"
	system("java daikon.Daikon " + name + ".decls " + name + ".dtrace " + name + ".spinfo >" + name + ".out")
	post(name + ".out")

		
do_all("r_iACW")
