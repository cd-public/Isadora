from os import system

# vcd to daikon

# creates two files - dtrace and decls

prefix = "input-language C/C++\ndecl-version 2.0\nvar-comparability implicit\n\n"

nonce = 1

def make_decls(name,header,suffix):
	to_write = open(name + suffix + ".decls","w")
	prefix = "input-language C/C++\ndecl-version 2.0\nvar-comparability implicit\n\n"
	suffix = "\n	var-kind variable\n	rep-type int\n	dec-type int\n	comparability "
	to_write.write(prefix)
	# make key
	key = [line.split()[2:] for line in header]
	last = ""
	cnt = 0
	for point in ["ppt ..tick():::ENTER\n  ppt-type enter\n","\nppt ..tick():::EXIT0\n  ppt-type subexit\n"]:
		to_write.write(point)
		for reg in key:	
			# only write a single var for each register, regardless of bit length, to decls
			if reg[2] != last:
				if "shadow" in reg[2]:
					suf = suffix + "2 \n"
				else:
					suf = suffix + "1 \n"
				to_write.write("  variable " + reg[2] + suf)
				last = reg[2]
				cnt = 1
	for reg in key:
		# continue to store bits separately internally
		if len(reg) > 4:
			reg[2] = reg[2] + " " + reg[3]	
		while len(reg) > 3:
			reg.remove(reg[3])
	out_key = key
	return out_key

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
				val = val + reg[3]
				last = splits[0]
				if "x" in val: # hack for uninitialized values - bit values are always positive
					val = "-1"
				file.write(splits[0] + "\n"+ str(int(val,2)) + "\n1\n")
				val = ""
			elif splits[0] == last:
				val = val + reg[3]
		file.write("\n")
	return nonce + 1
			

def read(name, banlist,suffix):
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
			splits = line.split()
			if splits[4] not in banlist:
				header = header + [line]
	key = make_decls(name,header,suffix)
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
			1 == 1
		line = to_read.readline()
	to_write = open(name + suffix + ".dtrace","w")
	to_write.write(prefix)
	nonce = 0
	while len(line) > 0: 
		if "#" in line[0]:		
			nonce = dump(key,to_write,nonce)
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
		line = to_read.readline() #.replace("[","").replace("]","")
	return key

def get_bans(name):
	to_read = open(name+ "_1.out","r")	
	to_write = open(name + "_ts.out","w")
	struct = [] # hold sets of regs of the same value
	for line in to_read:
		if "EXIT" in line:
			to_ret = [] # returned struct of relevant regs
			ts = []
			nts = []
			for ele in struct:
				l = list(ele)
				l.sort()
				valid = l
				valid = list(filter(lambda x: "shadow_" in x or x.replace("-","").isdigit(), l))
				if len(l) > 1:
					valid = list(filter(lambda x: "shadow_" in x or x.replace("-","").isdigit(), l))
					valid = [reg.replace("shadow_","") for reg in valid] 
					if len(valid) > 1 and valid[0].replace("-","").isdigit():
						if (valid[0] != "0"):
							ts += valid[1:]
						else:
							nts += valid[1:]
					to_ret += l[1:]
			# ban all elements equal to constant
			# ban all elements but first not equal to constant
			# output taints and not taints to file
			ts.sort()
			nts.sort()
			to_write.write("TAINTED   REGS: " + str(ts) + "\n")
			to_write.write("UNTAINTED REGS: " + str(nts) + "\n")
			return to_ret
		if " == " in line and "%" not in line: # get equalities
			splits = line.split()
			must_add = True			
			for ele in struct:
				if splits[0] in ele:
					ele.add(splits[2])
					must_add = False
			if must_add:
				struct += [set([splits[0],splits[2]])]

def get_shadows(name, key):
	last = ""
	to_ret = []
	for reg in key:
		splits = reg[2].split()
		if splits[0] != last:
			last = splits[0]
			if "shadow_" in last:
				to_ret += [last]
	return to_ret

def make_spinfo(name, key):
	shadows = get_shadows(name,key)
	to_write = open(name + ".spinfo","w")
	to_write.write("\n\nPPT_NAME ..tick\n")
	# for each register in key that contains shadow that is not on the ban list:
	for reg in shadows:
		to_write.write("0==orig(" + reg + ") && 0!=" + reg + "\n")
	return shadows

def make_a_spinfo(reg):
	to_write = open(reg + ".spinfo","w")
	to_write.write("\n\nPPT_NAME ..tick\n")
	to_write.write("0==orig(" + reg + ") && 0!=" + reg + "\n")

def clean_up(name):
	# clean up
	system("rm " + name + "_1.out") # first pass temp file
	system("rm *.dtrace")
	system("rm *.decls")
	system("rm *.spinfo")
	system("rm *.inv.gz")


def do_all(name):

	# naive decls, dtrace
	key = read(name, [], "_1")

	# For command to work to work must first do 
	# export JAVA_HOME=${JAVA_HOME:-$(dirname $(dirname $(dirname $(readlink -f $(/usr/bin/which java)))))}
	# export CLASSPATH="/home/mars/radish/daikon-5.7.2/daikon.jar"
	# export DAIKONDIR="/home/mars/radish/daikon-5.7.2"

	# this is the first pass, into _1
	system("java daikon.Daikon " + name + "_1.decls " + name + "_1.dtrace >" + name + "_1.out")

	# develop the ban list - vcd terms that are uninteresting
	ban_list = get_bans(name)
	
	# reduced decls, dtrace, and a candidate spinfo (unuseable, but can be editted)
	key = read(name, ban_list, "_2")
	shadows = make_spinfo(name, key)

	# test on single split
	make_a_spinfo(shadows[0])
	
	system("java daikon.Daikon " + name + "_2.decls " + name + "_2.dtrace " + shadows[0] + ".spinfo >" + name + "_" + shadows[0] + ".out")
	#clean_up(name)

do_all("r_iCTreply37")
