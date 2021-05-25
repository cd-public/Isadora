from os import system
from os import path
import os
import sys

# reg family:
# GLOBAL PORTS := ACLK | ARESETN | INTR_LINE_*
# AXI CONFIGURATION S PORTS := S_AXI_*
# HARDWARE MODULE PORTS := *_wire
# M OUTPUT INTERFACE PORTS := M_AXI_* / M_AXI_*_wire / M_AXI_*_INT
# AXI S CONFIGURATION SIGNALS := axi_* | reg* | byte_index | aw_en
# AXI M INTERNAL SIGNALS  := M_AXI_*_wire | M_AXI_*_INT
# MEMORY CNTRL LOGIC SIGNALS := AW_* | AR_* | B_* | R_* | W_*

# given a register, figure out group it's in
def reg_to_group(reg):
	reg = reg.replace(',','').replace(']','')
	for port in ['ACLK', 'ARESETN', 'INTR_LINE_R', 'INTR_LINE_W']:
		if reg == port:
			return 'GLOBAL PORT'
	if 'S_AXI_' in reg:
		return 'AXI CONFIGURATION S PORTS'
	if 'M_AXI_' in reg:
		if '_wire' in reg or '_INT' in reg:
			return 'AXI M INTERNAL SIGNALS'
		else:
			return 'M OUTPUT INTERFACE PORTS'
	if '_wire' in reg:
		return 'HARDWARE MODULE PORTS'
	for prefix in ['AW_', 'AR_', 'B_', 'R_', 'W_']:
		if prefix in reg[0:3]:
			return 'MEMORY CNTRL LOGIC SIGNALS'
	if 'axi_' in reg[0:4] or 'reg' in reg[0:3] or reg == 'byte_index' or reg == 'aw_en':
		return 'AXI S CONFIGURATION SIGNALS'
	return 'unknown flow relation family'

# read a single cond line
def line_to_groups(line, groups):
	splits = line.strip().split(' =?=> [')
	src = reg_to_group(splits[0])
	for dst in splits[1].split():	
		groups.add(src + ' ==> ' + reg_to_group(dst))
	

# when reading a cond, find group flow cases within that cond
def cond_to_groups():
	conds = open('conditions.txt','r')
	struct = [] # entries will be [<case>,<groups>]
	case = ''
	groups = set()
	for line in conds:
		if 'case' in line:
			if case != '':
				struct.append([case,groups])
			case = line.strip()
			groups = set()
		else:
			line_to_groups(line, groups)
	conds.close()
	# conds by groupflow:
	by_group = open('conds_by_group.txt','w')
	for cond in struct:
		l = list(cond[1])
		by_group.write('\n' + cond[0] + ' has flows')
		l.sort()
		last = ''
		for ele in l:
			splits = ele.split(' ==> ')
			if last == splits[0]:
				by_group.write(', ' + splits[1])
			else:
				by_group.write('\n\t' + ele)
				last = splits[0]
	by_group.close()
	# groupflow by cond - basically transpose
	transpose = []
	for cond in struct:
		for pair in cond[1]:
			added = False
			for ele in transpose:
				if ele[0] == pair:
					ele[1].append(cond[0])
					added = True
			if not added:
				transpose.append([pair,[cond[0]]])
	by_cond = open('groups_by_cond.txt','w')
	for group in transpose:
		by_cond.write(group[0] + ' flows in ' + str(len(group[1])) + ' cases\n')
		for case in group[1]:
			by_cond.write('\t' + case.split()[1] + '\n')
	by_cond.close()
	csv = open('case_distro.csv','w')
	names = ['GLOBAL PORT', 'AXI CONFIGURATION S PORTS', 'HARDWARE MODULE PORTS', 'M OUTPUT INTERFACE PORTS', 'AXI S CONFIGURATION SIGNALS', 'AXI M INTERNAL SIGNALS', 'MEMORY CNTRL LOGIC SIGNALS']
	# src on top, dst down the side
	csv.write('src_on_top,' + str(names).replace("\'","")[1:-1] + '\n')
	for name in names:
		csv.write(name + ',')
		for src in names:
			# looking for src ==> name in transpose
			cnt = 0
			for group in transpose:
				if src + ' ==> ' + name == group[0]:
					cnt = len(group[1])
			csv.write(str(cnt) + ',')
		csv.write('\n')
	
cond_to_groups()