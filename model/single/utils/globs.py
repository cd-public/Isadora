from os import system
from os import path
import os
import sys

# times forked to grab globals
# this could be rolled into times

# BEGIN OLD MAIN

def make_decls(key):
	to_write = open("universal.decls","w")
	prefix = "input-language C/C++\ndecl-version 2.0\nvar-comparability implicit\n\n" # this is just how daikon works
	suf_int = "\n	var-kind variable\n	rep-type int\n	dec-type int\n	comparability 1 \n"
	suf_str = "\n	var-kind variable\n	rep-type string\n	dec-type char*\n	comparability 4 \n"
	to_write.write(prefix)
	# make key by cutting up the header
	last = "" # using staggered traversal
	strings = []
	for point in ["ppt ..tick():::ENTER\n  ppt-type enter\n","\nppt ..tick():::EXIT0\n  ppt-type subexit\n"]:
		to_write.write(point)
		for reg in key:	
			# only write a single var for each register, regardless of bit length, to decls
			if reg[2] != last:
				# prevent daikon for looking for relationships between IFT and original design state
				# so this doesn't work because we actually need to remove the shadows from the header
				if "shadow" not in reg[2]:
					suf = suf_int # ususally we encode as int
					if "[" in reg[3] and "]" in reg[3] and ":" not in reg[3]:
						if int(reg[3].replace("[","").replace("]","")) > 31: # but not if we overflow
							suf = suf_str
							strings.append(reg[2])
					to_write.write("  variable " + reg[2] + suf)
				last = reg[2]
	to_write.close()
	for reg in key:
		# continue to store bits separately internally for vcd reading
		if len(reg) > 4:
			reg[2] = reg[2] + " " + reg[3]	
		while len(reg) > 3:
			reg.remove(reg[3])
	for i in range(len(key)):
		# populate starting value as uninitialized
		key[i] = key[i] + ["x"]
	# key a list of 4 tuples
	# one tuple per register or derived value
	# the tuple is size, vcd_name, plaintext name, starting value
	# strings is the list of registers that have to be encoded as strings due to overflow
	return [key, strings]

# little helper to handle string formating
def last_val_to_str(last, val, strings):
	if last == "": # uninitialized case, return nothing
		return ""
	if "x" in val or "z" in val:
		val_str = "-1"
	else:
		val_str = str(int(val,2))
	if last in strings:
		val_str = "\"" + val_str + "\""
	return last + "\n" + val_str + "\n1\n"

# accept a key, build a string for dt
# this does not include the program point prefix
def to_dt(key, strings):
	ret_str = ""
	last = ""
	val = 'x' # default uninitialized value
	for reg in key:
		# figure out how to use strings array in here
		curr = reg[2].split()[0]	
		if curr != last:		
			# new reg, so write last reg
			ret_str = ret_str + last_val_to_str(last, val, strings)
			# save new reg and its value
			last = curr
			val = reg[3]
		elif curr == last:
			# additional bits within the same register, update value
			val = val + reg[3]
	# close out given the offset of one in the loop
	ret_str = ret_str + last_val_to_str(last, val, strings) + "\n"
	return ret_str
	
# given a name, a vcd file pointer (at start of file) and suffix, makes a decls and advances the pointer to trace start	
# also return the key, the internal data struct used to capture state during value dump traversal
	# key a list of 4 tuples
	# one tuple per design register or derived value
	# the tuple is size, vcd_name, plaintext name, starting value
def vcd_to_decls(to_read):
	key = []
	line = to_read.readline()
	# traverse to vars
	while "$var" not in line:
		line = to_read.readline()
	# read in vars
	while "$enddefinitions" not in line:
		if "$var" in line and "shadow" not in line:
			key.append(line.split()[2:])
		line = to_read.readline()
	# read one more line to skip enddef and dumpvar
	# to_read should now point to vcd file at zero timestamp of value dump
	line = to_read.readline() # dumpvars
	line = to_read.readline() # #0
	return make_decls(key)
	
def read_vcd_line(line, key):
	# for a simple value dump line, not a clock tick line
	# split up the line
	splits = line.split()
	if len(splits) == 1:
		# if it can't be split, boolean line, manufacture a split
		splits = [splits[0][0], splits[0][1:]] 
	else: 
		# if it can, multibit line encoding is always boolean, so remove the leading b
		splits[0] = splits[0][1:]
	# "i" will hold the location in key of where we save the line state, if relevant
	i = -1
	for index in range(len(key)):
		if key[index][1] == splits[1]:
			i = index
	# if the line is meaningful, update key
	if i > -1:
		key[i][3] = splits[0]
	# return key as a courtesy
	return key
	
# make a universal decls and a dtrace per time set in the conditions
def read():
	# global values for dt's
	points = ["..tick():::ENTER\nthis_invocation_nonce\n", "..tick():::EXIT0\nthis_invocation_nonce\n"]
	# let's get a vcd
	# --- ENTER VCD DIR --- #
	os.chdir(os.getcwd().replace("utils","vcds"))
	files = os.listdir("../vcds")
	regs = list(filter(lambda x: ".vcd" in x, files))
	to_read = open(regs[0],"r")
	# --- LEAVE VCD DIR --- #
	os.chdir(os.getcwd().replace("vcds","utils"))
	# we can get globs locally then clean
	# --- ENTER DFILES DIR --- #
	# read in vcd header
	[key,strings] = vcd_to_decls(to_read)
	# load key with starting values
	line = to_read.readline()
	while "#" not in line[0]:
		read_vcd_line(line, key)
		line = to_read.readline()
	# in theory, the next # is the first tock
	tick = False # tracks if we're in a tick or a tock
	last_str = to_dt(key, strings)
	# we need to track nonces
	nonce = 1
	# we need a file
	file = open("globs.dtrace","w")
	while len(line) > 0: 
		if "#" in line[0]:
			if "0000" in line: # on a major clock tick
				file.write(points[0] + str(nonce) + "\n" + last_str)
				last_str = to_dt(key, strings)
				file.write(points[1] + str(nonce) + "\n" + last_str)
		else:
			read_vcd_line(line, key)
		line = to_read.readline()
	to_read.close()	
	system("java daikon.Daikon universal.decls globs.dtrace >globs.txt")
	return key

# END OLD MAIN

"""
export JAVA_HOME=${JAVA_HOME:-$(dirname $(dirname $(dirname $(readlink -f $(/usr/bin/which java)))))}
export CLASSPATH="/home/mars/radish/daikon-5.7.2/daikon.jar"
export DAIKONDIR="/home/mars/radish/daikon-5.7.2"
"""

read()