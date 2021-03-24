from os import system
from os import path
import sys

# fork from 2pass.py, changes

def make_decls(name,header,suffix):
	to_write = open(name + suffix + ".decls","w")
	derived = []
	# only use derived state functionality if observing some target register
	if suffix != "_1":
		# this introduces a name space collision risk
		# hard code off of this in taint_cnt
		derived = ["DERIVED_taint_reg_count","DERIVED_taint_reg_delta","DERIVED_vcd_timestamp"] # derived values
	prefix = "input-language C/C++\ndecl-version 2.0\nvar-comparability implicit\n\n" # this is just how daikon works
	suffix = "\n	var-kind variable\n	rep-type int\n	dec-type int\n	comparability " # overloading suffix
	to_write.write(prefix)
	# make key by cutting up the header
	key = [line.split()[2:] for line in header]
	last = "" # using staggered traversal
	for point in ["ppt ..tick():::ENTER\n  ppt-type enter\n","\nppt ..tick():::EXIT0\n  ppt-type subexit\n"]:
		to_write.write(point)
		for reg in key:	
			# only write a single var for each register, regardless of bit length, to decls
			if reg[2] != last:
				# prevent daikon for looking for relationships between IFT and original design state
				if "shadow" in reg[2]:
					suf = suffix + "2 \n"
				else:
					suf = suffix + "1 \n"
				to_write.write("  variable " + reg[2] + suf)
				last = reg[2]
		for reg in derived:
			suf = suffix + "3 \n" # we don't want IFT or original design registers interacting with derived values
			to_write.write("  variable " + reg + suf)
	for reg in key:
		# continue to store bits separately internally for vcd reading
		if len(reg) > 4:
			reg[2] = reg[2] + " " + reg[3]	
		while len(reg) > 3:
			reg.remove(reg[3])
	for i in range(len(key)):
		# populate starting value as uninitialized
		key[i] = key[i] + ["x"]
	for reg in derived:
		# Have to think about typing on derived reg[3]
		key = key + [["", "", reg, "0"]]
	# key a list of 4 tuples
	# one tuple per register or derived value
	# the tuple is size, vcd_name, plaintext name, starting value
	return key

# little helper to handle string formating
def last_val_to_str(last, val):
	if last == "": # uninitialized case, return nothing
		return ""
	if "x" in val:
		val_str = "-1"
	else:
		val_str = str(int(val,2))
	return last + "\n" + val_str + "\n1\n"

# accept a key, build a string for dt
# this does not include the program point prefix
def to_dt(key):
	ret_str = ""
	last = ""
	val = 'x'
	for reg in key:
		curr = reg[2].split()[0]	
		if curr != last:		
			# new reg, so write last reg to file
			ret_str = ret_str + last_val_to_str(last, val)
			# save new reg and its value
			last = curr
			val = reg[3]
		elif curr == last:
			# additional bits within the same register, update value
			val = val + reg[3]
	# close out given the offset of one in the loop
	ret_str = ret_str + last_val_to_str(last, val) + "\n"
	return ret_str
	
# given a name, a vcd file pointer (at start of file) and suffix, makes a decls and advances the pointer to trace start	
# also return the key, the internal data struct used to capture state during value dump traversal
	# key a list of 4 tuples
	# one tuple per design register or derived value
	# the tuple is size, vcd_name, plaintext name, starting value
def vcd_to_decls(name, to_read, suffix, ban_list):
	header = []
	line = to_read.readline()
	# process the header
	# traverse to vars
	while "$var" not in line:
		line = to_read.readline()
	# read in vars
	while "$enddefinitions" not in line:
		splits = line.split()
		if splits[4] not in ban_list and "$var" in line:
			header = header + [line]
		line = to_read.readline()
	# read one more line to skip enddef and dumpvar
	# to_read should now point to vcd file at just past zero timestamp of value dump
	line = to_read.readline()
	line = to_read.readline()
	return make_decls(name,header,suffix)
	
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
	
# see if a register is tainted
def reg_tainted(tar_reg, key):
	ret = False
	for reg in key:
		if "shadow_" + tar_reg in reg[2] and "1" in reg[3]:
			ret = True
	return ret
	
# calculate derived values
def derived(key, line):
	# staggered traversal
	last = key[0][2].split()[0]
	curr_bool = False
	cnt = 0
	# walk through regs, see if unique named shadow regs are nonzero
	for reg in key:
		if "shadow_" in reg[2]:
			curr = reg[2].split()[0]
			if curr != last:
				if curr_bool == True:
					cnt = cnt + 1
				last = curr
				curr_bool = False
				if "1" in reg[3]:
					curr_bool = True
			elif curr == last and "1" in reg[3]:
				curr_bool = True
	if curr_bool == True:
		cnt = cnt + 1
	# count is in len - 3, delta is in len - 2
	l = len(key)
	# deal with types
	prev = int(key[l-3][3],2)
	key[l-1][3] = bin(int(line[1:-5])) 
	key[l-2][3] = bin(cnt - prev)
	key[l-3][3] = bin(cnt)
	return cnt
	
def nxt_file(name, suffix, hi_curr, file_cnt):
	cnt_str = "%02d" % file_cnt
	if hi_curr:
		file = open(name + suffix + "_hi" + cnt_str + ".dtrace","w")
	else:
		file = open(name + suffix + "_lo" + cnt_str + ".dtrace","w")
	file.write("input-language C/C++\ndecl-version 2.0\nvar-comparability implicit\n\n")
	return [0, file]
				
# turns a vcd file into a decls and either a dtrace or a few dtraces cut on tar_reg
def read(name, ban_list, tar_reg):
	# set up some variables
	suffix = "_" + tar_reg
	prefix = "input-language C/C++\ndecl-version 2.0\nvar-comparability implicit\n\n"
	points = ["..tick():::ENTER\nthis_invocation_nonce\n", "..tick():::EXIT0\nthis_invocation_nonce\n"]
	if tar_reg == "":
		# this introduces a namespace collision risk
		suffix = "_1"
		to_write = [0, open(name + suffix + ".dtrace","w")]
		to_write[1].write(prefix)
	to_read = open(name + ".vcd","r")
	
	# read in vcd header
	key = vcd_to_decls(name, to_read, suffix, ban_list)
	
	# load key with starting values
	line = to_read.readline()
	
	while "#" not in line[0]:
		read_vcd_line(line, key)
		line = to_read.readline()
	# in theory, the next # is the first tock
	tick = False # tracks if we're in a tick or a tock
	last_str = to_dt(key)
	# now we start keeping track of files
	if tar_reg != "":
		# we want to keep track of 
			# where shadow_tar_reg is
			# how many high and low dts there have been
			# the edge dt
		file_cnt = 1
		rise_file = [0, open(name + suffix + "_rise.dtrace","w")]
		rise_file[1].write(prefix)
		fall_file = [0, open(name + suffix + "_fall.dtrace","w")]
		fall_file[1].write(prefix)
		hi_curr = reg_tainted(tar_reg, key)
		to_write = nxt_file(name, suffix, hi_curr, 0)
		
	while len(line) > 0: 
		if "#" in line[0]:
			# do the derived stuff
			if tick:
				if tar_reg != "":
					derived(key, line)
					hi_last = hi_curr
					hi_curr = reg_tainted(tar_reg, key)
					# if hi_curr == hi_last, write to to_write
					# if not, write to edge and open a new to_write
					if hi_curr == hi_last:
						curr_write = to_write
					else:
						if hi_curr:
							curr_write = rise_file
						else:
							curr_write = fall_file
						to_write = nxt_file(name, suffix, hi_curr, file_cnt)
						file_cnt = file_cnt + 1
				else:
					curr_write = to_write
				# use last_str to do enter, get new str, use it to do exit
				curr_write[1].write(points[0] + str(curr_write[0]) + "\n" + last_str)
				last_str = to_dt(key)
				curr_write[1].write(points[1] + str(curr_write[0]) + "\n" + last_str)
				curr_write[0] = curr_write[0] + 1
			tick = not tick
		else:
			read_vcd_line(line, key)
		line = to_read.readline()
	return key

# basically find redundant registers
def get_bans(name):
	to_read = open(name+ "_1.out","r")	
	to_write = open(name + ".ts.txt","w")
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
			# ban all but one elements but equal not to a constant
			# output to file
			ts.sort()
			nts.sort()
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
				
def no_secondaries(ban_list, key):
	s = set()
	for reg in key:
		if "S_AXI_" in reg[2]:
			s.add(reg[2].split()[0]) 
	return ban_list + list(s)

def bans_to_file(name, ban_list):
	to_write = open(name + ".bans.txt","w")
	for reg in ban_list:
		to_write.write(reg + "\n")
	return
	
def file_to_bans(name):
	to_read = open(name + ".bans.txt","r")
	ban_list = []
	for line in to_read:
		ban_list = ban_list + [line.strip()]
	return ban_list
	
# 2->multi, TODO none
def get_shadows(name, key, ban_list):
	last = ""
	to_ret = []
	for reg in key:
		splits = reg[2].split()
		if splits[0] != last:
			last = splits[0]
			if "shadow_" in last:
				unbanned = True
				for ban in ban_list:
					if ban in last:
						unbanned = False
				if unbanned:
					to_ret += [last]
	cts = []
	for reg in to_ret:
		cts = cts + [reg]
	cts = [reg.replace("shadow_","") for reg in cts] 
	cts.sort()
	open(name + ".ts.txt","a").write("CONDTAINT REGS: " + str(cts) + "\n")
	return to_ret

def clean_up(name):
	# clean up
	system("rm *.dtrace >/dev/null")
	system("rm *.decls >/dev/null")
	system("rm *.spinfo >/dev/null")
	system("rm *.inv.gz >/dev/null")

# analyzes a vcd cross register:
	# For command to work to work must first do 
	# export JAVA_HOME=${JAVA_HOME:-$(dirname $(dirname $(dirname $(readlink -f $(/usr/bin/which java)))))}
	# export CLASSPATH="/home/mars/radish/daikon-5.7.2/daikon.jar"
	# export DAIKONDIR="/home/mars/radish/daikon-5.7.2"
# output
	# _full 	== globals post ban
	# _<reg>_	== props related to that reg
	# _lo/_hi	== when reg taint is low or high
	# _rise/_fall	== when reg taint changes, low to high or high to low
	# _base		== when reg taint doesn't change
if __name__ == "__main__":
	# read arguments
	
	name = ""
	tar_reg = ""
	
	# total arguments
	n = len(sys.argv)
	# get vcd name
	if (n == 1):
		exit()
	else:
		name = sys.argv[1]
			
	# if necessary, generate a ban_list from a naive pass
	
	if not path.exists(name + ".bans.txt"):
		
		# naive decls, dtrace, if needed
		key = read(name, [], "") # minimal read

		# this is the first pass, into _1
		system("java daikon.Daikon " + name + "_1.decls " + name + "_1.dtrace >" + name + "_1.out")

		# develop the ban list - vcd terms that are uninteresting, and save it
		ban_list = get_bans(name)
		ban_list = no_secondaries(ban_list, key) # ban S_AXI_* from Andy, "S_AXI Signals..."
		ban_list = ban_list + ["ACLK"]
		shadows = get_shadows(name, key, ban_list) # we do this for the side effect on *_ts
		bans_to_file(name, ban_list)
		
		# clean temp files
		system("rm *_1*")
		key = read(name, ban_list, "")
		system("java daikon.Daikon " + name + "_1.decls " + name + "_1.dtrace >" + name + "_full.txt")
		
	else:
		
		ban_list = file_to_bans(name)
	
	# get reg name
	if (n > 2):
		tar_reg = sys.argv[2]
	else:
		# arbitrary if unspecified
		to_read = open(name + ".ts.txt","r")
		to_read.readline()
		tar_reg = to_read.readline().replace("CONDTAINT REGS: [","").split()[0].replace(",","").replace("'","") # read CONDTAINT 1st element
		
	# begin multipass
	key = read(name, ban_list, tar_reg)
	local = name + "_" + tar_reg
	system("java daikon.Daikon " + local + ".decls " + local + "_rise.dtrace >" + local + "_rise.txt")
	system("java daikon.Daikon " + local + ".decls " + local + "_fall.dtrace >" + local + "_fall.txt")
	system("java daikon.Daikon " + local + ".decls " + local + "_lo*.dtrace >" + local + "_lo.txt")
	system("java daikon.Daikon " + local + ".decls " + local + "_hi*.dtrace >" + local + "_hi.txt")
	system("java daikon.Daikon " + local + ".decls " + local + "_lo*.dtrace " + local + "_hi*.dtrace >" + local + "_base.txt")
	# clean temp files
	#clean_up(name)
