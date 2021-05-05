from os import system
from os import path
import os
import sys

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
	#os.chdir(os.getcwd().replace("utils","vcds")) # this should work even if the cd is already vcds
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
	#os.chdir(os.getcwd().replace("vcds","utils"))
	conds_to_file(conds)
	return conds
	
# BEGIN OLD EXAMINE


all_srcs()