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
	cnt = 0
	for point in ["ppt ..tick():::ENTER\n  ppt-type enter\n","\nppt ..tick():::EXIT0\n  ppt-type subexit\n"]:
		to_write.write(point)
		for reg in key:	
			# only write a single var for each register, regardless of bit length, to decls
			if reg[2] != last:
				to_write.write("  variable " + reg[2] + suffix)
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
				if "[" in reg[2]:
					if "x" in val: # hack for uninitialized values - bit values are always positive
						val = "-1"
				file.write(splits[0] + "\n"+ str(int(val,2)) + "\n1\n")
				val = ""
			elif splits[0] == last:
				val = val + reg[3]
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

def make_spinfo(name):
	to_read = open(name+ "_1.out","r")	
	to_write = open(name + "_1_s.out","w")
	for line in to_read:
		if "shadow_" in line and " == " in line and "orig" not in line:
			to_write.write(line)
	#prefix = "\n\nPPT_NAME ..tick\n"
	#to_write = open(name + ".spinfo","w")
	#to_write.write("\n\nPPT_NAME ..tick\n")

	#		to_write.write("0==orig(" + reg.replace("[","").replace("]","") + ")\n")
	#		last = reg

def clean_up(name):
	# clean up
	system("rm " + name + "_1.out") # first pass temp file full
	system("rm *.dtrace")
	system("rm *.decls")
	system("rm *.spinfo")
	system("rm *.inv.gz")


def do_all(name):
	read(name)
	# For this to work must first do 
	# export JAVA_HOME=${JAVA_HOME:-$(dirname $(dirname $(dirname $(readlink -f $(/usr/bin/which java)))))}
	# export CLASSPATH="/home/mars/radish/daikon-5.7.2/daikon.jar"
	# export DAIKONDIR="/home/mars/radish/daikon-5.7.2"
	system("java daikon.Daikon " + name + ".decls " + name + ".dtrace >" + name + "_1.out")
	make_spinfo(name)
	clean_up(name)
do_all("r_iACW_old")
