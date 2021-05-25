from os import system
from os import path
import os
import sys

# forked from main to handle times

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
def read(times):
	# global values for dt's
	points = ["..tick():::ENTER\nthis_invocation_nonce\n1\n", "..tick():::EXIT0\nthis_invocation_nonce\n1\n"]
	# let's get a vcd, we can work in that directory and rm *.decls on the way out
	# --- ENTER VCD DIR --- #
	os.chdir(os.getcwd().replace("utils","vcds"))
	files = os.listdir("../vcds")
	regs = list(filter(lambda x: ".vcd" in x, files))
	to_read = open(regs[0],"r")
	# --- LEAVE VCD DIR --- #
	os.chdir(os.getcwd().replace("vcds","utils"))
	# make sure theres a dfiles directory in outs
	system("mkdir ../outs")
	system("mkdir ../outs/dfiles")
	# --- ENTER DFILES DIR --- #
	os.chdir(os.getcwd().replace("utils","outs/dfiles"))
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
	# deal with special zero case
	if 0 in times:
		open("0.dtrace","w").write(points[0] + last_str + points[1] + last_str)
	while len(line) > 0: 
		if "#" in line[0]:
			if "0000" in line: # on a major clock tick
				time = int(line[1:-5])
				if time in times:
					file = open(str(time) + ".dtrace","w")
					file.write(points[0] + last_str)
					last_str = to_dt(key, strings)
					file.write(points[1] + last_str)
					file.close()
		else:
			read_vcd_line(line, key)
		line = to_read.readline()
	to_read.close()	
	# --- LEAVE DFILES DIR --- #
	os.chdir(os.getcwd().replace("outs/dfiles", "utils"))
	return key

# END OLD MAIN

# BEGIN GET TIMES

# LIST of [TUPLES of REG_NAME(str) and LIST of [TUPLES of VCD_NAME(str) and BIT_VALUE(str)]] and LIST of TIMES(int)
def build_struct(vcd):
	struct = []
	last_reg = "" # traversal aid for the last reg we saw
	last_ele = [] # list element corresponding to last_reg
	for line in vcd:
		if "$dumpvars" in line: # finished building
			return struct
		if "$var" in line and "shadow_" in line: # shadow reg case
			# may have a new reg or a new bit of an old reg
			# fortunately the regs are sorted - lets use "last" technology
			# split it up
			splits = line.split()
			# we want REG_NAME @ 4, VCD_NAME @ 3
			reg_name = splits[4].replace("shadow_","")
			vcd_name = splits[3]
			if reg_name == last_reg:
				# TUPLES of VCD_NAME and BIT_VALUE (with initial bit value "x", the standard Tortuga case)
				last_ele[1].append([vcd_name, "0"])
			else:
				last_reg = reg_name # cache this for the loop
				# TUPLE of [STRING of REG_NAME and LIST of TUPLES of VCD_NAME and BIT_VALUE and LIST of TIMES
				last_ele = [reg_name, [[vcd_name, "0"]], []] 
				struct.append(last_ele)

# helper to find out if a register's tuple list of bit values is currently zeroed out
def is_zero(reg1):
	for bit in reg1:
		if bit[1] != "0":
			return False
	return True

def walk(vcd, struct):
	# hold time
	time = 0
	for line in vcd:
		# 3 cases - new time, relevant value change, other
		# new time - major ticks begin with # and contain "0000"
		if line[0] == '#' and "0000" in line:
			time = int(line[1:-5]) # get the relevant bits
		elif " " not in line: # all shadow regs are bitwise
			# cut the line
			val = line[0]
			vcd_name = line.strip()[1:]
			# use the struct
			for reg in struct:
				for bit in reg[1]:
					if bit[0] == vcd_name:
						# two things - update the value and check for flow
						if val != "0" and is_zero(reg[1]):
							reg[2].append(time)
						bit[1] = val			

# comma separate the flow relation, with a label
# cases instead of bool values?
def csv_line(name, struct):
	ts = [name] + [int(not is_zero(reg[1])) for reg in struct]
	return str(ts)[1:-1].replace('\'','') + "\n"

# subroutine to use return
def add_reg_to_times(reg, times):
	for time in times:
		if time[0] == reg[2]:
			return time[1].append(reg[0])
	return times.append([reg[2],[reg[0]]])
	

# LIST of [TUPLES of LIST of TIMES(int) and LIST of REG_NAMES(str)]
def build_times(struct):
	times = []
	for reg in struct:
		if reg[2] != []:
			add_reg_to_times(reg, times)
	return times

# provide the name of a register that has a corresponding source vcd
# returns a line for the flow relation csv and a time struct in a tuple
def one_src(name):
	vcd = open(name, "r")
	struct = build_struct(vcd) # get regs
	walk(vcd,struct) # get times
	line = csv_line(name.split(".")[0], struct) # get line for csv
	times = build_times(struct) # get timing info for this src
	return [line, times]

# take an arbitrary vcd to get the csv first line
def csv_labels(name):
	vcd = open(name, "r")
	struct = build_struct(vcd) # overloading this a bit
	vcd.close()
	labels = [] + [reg[0] for reg in struct]
	return str(labels)[1:-1].replace('\'','') + "\n"
	
# subroutine to use return
def add_time_to_conds(reg, time, conds):
	for cond in conds:
		if cond[0] == time[0]:
			return cond[1].append([reg.split(".")[0],time[1]])
	return conds.append([time[0],[[reg.split(".")[0],time[1]]]])
	
def conds_to_file(conds):
	# wonder if I want an xml here
	# or to sort
	con = open("conditions.txt","w")
	#maybe timestamps, single indent source =?=> sink list
	for time in conds:
		con.write("case: " + str(time[0])[1:-1].replace(", ","_") + "\n")
		for src in time[1]:
			line = "\t" + src[0] + " =?=> " + str(src[1]) + "\n"
			con.write(line.replace('\'',''))
	con.close()
	return

# build a csv and a time struct for all vcds in a directory
# this reads every bit in hundreds of vcds so it takes some time
def all_srcs():
	csv = open("relations.csv","w") # boolean values of flow relations, sources are columns
	# LIST of [TUPLES of LIST of TIMES(int) and LIST of [TUPLES of REG_NAMES(str, src) and LIST of REG_NAMES(str, sinks)]]
	conds = []
	# --- ENTER VCD DIR --- #
	os.chdir(os.getcwd().replace("utils","vcds")) # this should work even if the cd is already vcds
	files = os.listdir(".")
	regs = list(filter(lambda x: ".vcd" in x, files))
	csv.write(csv_labels(regs[0]))
	for reg in regs:
		if ".vcd" in reg:
			[line, times] = one_src(reg)
			csv.write(line)
			for time in times:
				add_time_to_conds(reg, time, conds)
	csv.close()
	# --- LEAVE VCD DIR --- #
	os.chdir(os.getcwd().replace("vcds","utils"))
	conds_to_file(conds)
	return conds
	
# END GET TIMES

# BEGIN NEW CODE

# take the output of all_srcs
# LIST of [TUPLES of LIST of TIMES(int) and LIST of [TUPLES of REG_NAMES(str, src) and LIST of REG_NAMES(str, sinks)]]
# and make input to read
# LIST of TIMES
def conds_to_times(conds):
	# lets make a new struct in case we want to keep the old one
	times = set()
	for cond in conds:
		for time in cond[0]:
			times.add(time)
	return times

"""
export JAVA_HOME=${JAVA_HOME:-$(dirname $(dirname $(dirname $(readlink -f $(/usr/bin/which java)))))}
export CLASSPATH="/home/mars/radish/daikon-5.7.2/daikon.jar"
export DAIKONDIR="/home/mars/radish/daikon-5.7.2"
"""
# run Daikon for all conditions
def conds_to_dcall(conds):
	# do this in outs/dfiles
	# --- ENTER DFILES DIR --- #
	os.chdir(os.getcwd().replace("utils","outs/dfiles"))
	# make sure we have and outs/edges
	system("mkdir ../edges")
	for time in conds:
		dcall = "java daikon.Daikon universal.decls "
		dts = "".join([str(tick) + ".dtrace " for tick in time[0]])
		out_loc = ">../edges/" + str(time[0])[1:-1].replace(", ","_")  + ".txt"
		system(dcall + dts + out_loc)
	# --- LEAVE DFILES DIR --- #
	os.chdir(os.getcwd().replace("outs/dfiles", "utils"))
	return

# END NEW CODE

# BEGIN OLD EXAMINE

def add_to_eq(eqs, in_splits):
	splits = [ele.strip() for ele in in_splits]
	for eq in eqs:
		if splits[0] in eq:
			eq.append(splits[1])
			return eqs
	# new set case
	eqs.append(splits)
	return eqs

def dout_to_zs(case):
	# get file pts
	cd_orig = os.getcwd()
	# --- ENTER EDGES DIR --- #
	os.chdir(os.getcwd().replace("utils","outs/edges"))
	dout = open(case + ".txt","r")
	# --- ENTER ZS DIR --- #
	os.chdir(os.getcwd().replace("edges","zs"))
	zout = open(case + ".zs.txt","w")
	# --- RETURN TO DIR --- #
	os.chdir(cd_orig)
	# get to relevant dout region
	for line in dout:
		if "..tick():::EXIT" in line:
			break
	# find equalities
	# LIST of LISTS of REG_NAMES(str)
	eqs = []
	for line in dout:
		if " == " in line and "%" not in line and "orig" not in line:
			eqs = add_to_eq(eqs, line.split(" == "))
	dout.close()
	# eqs to zs
	nzs = []
	zs = []
	for eq in eqs:
		eq.sort()
		if eq[0].strip().isdigit(): # reasonably confident digits always sort first
			# either zs, nzs. uninits dont pass isdigit
			if eq[0].strip() == '0':
				zs = eq[1:]
			else:
				nzs = nzs + eq[1:]
	
	zout.write("0 == _r_ in {" + str(zs).replace("[","").replace("]","").replace("\'","") + "}\n")
	nzs.sort()
	zout.write("0 != _r_ in {" + str(nzs).replace("[","").replace("]","").replace("\'","") + "}\n")

# get all cases
def conds_to_cases():
	con = open("conditions.txt","r")
	cases = []
	for line in con:
		if "case: " in line:
			cases.append(line.replace("case: ","").strip())
	return cases
		
# lets just do all of them
# this is probably going in times at some point
def douts_to_zs():
	for case in conds_to_cases():
		dout_to_zs(case)
		
# END OLD EXAMINE

# run this in /utils with vcds for each relevant source in /vcd
def make_spec():
	conds = all_srcs() # find iflow times, relations
	read(conds_to_times(conds)) # create iflow traces
	conds_to_dcall(conds) # mine iflow invariants
	douts_to_zs() # get regs equal to zero etc

make_spec()