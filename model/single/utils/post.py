from os import system
from os import path
import os
import sys

# convert globs.txt
	# deal with "one of" cases
# look at e.g. 0_119_248_377_541.txt
# take out anything in globs.txt
# group register equalities


def eles_to_consts(eles, consts):
	for const in consts:
		for ele in eles:
			if ele in const:
				const.add(eles[0])
				const.add(eles[1])
				return consts
	consts.append(set(eles))
	return consts
						
def line_to_oneofs(line, oneofs):
	splits = line[1].replace(",","").replace("L","").split()
	vals = [int(s) for s in splits[1:-1]]
	vals.sort()
	for oneof in oneofs:
		if vals == oneof[0]:
			oneof[1].add(line[0])
			return oneofs
	oneofs.append([vals, set([line[0]])])
	return oneofs

# this reads a dout file, ideally from a full trace, to get constants and one of's
def gread():
	gfile = open("globs.txt","r")
	consts = []
	oneofs = []
	for line in gfile:
		if "..tick():::EXIT" in line:
			break
	for line in gfile:
		if " == " in line and "%" not in line and "orig" not in line:
			eles_to_consts(line.strip().split(" == "),consts)
		if " one of " in line:
			line_to_oneofs(line.strip().split(" one of "), oneofs)
	gfile.close()
	consts = [list(const) for const in consts]
	for const in consts:
		const.sort()
	consts = sorted(consts, key=lambda x: x[0])
	oneofs = [[vals,list(regs)] for [vals,regs] in oneofs]
	for oneof in oneofs:
		oneof[1].sort()
	oneofs = sorted(oneofs, key=lambda x: x[0])
	gfile = open("globals.txt","w")
	gfile.write("\"Constants\"\n\n")
	for const in consts:
		gfile.write("!eqset" + const[0] + ": " + str(const).replace("\'","") + "\n")
	gfile.write("\n\nOne of's\n\n")
	for oneof in oneofs:
		gfile.write(str(oneof) + "\n")
	return [consts, oneofs]

# this refs a dout edge vs a dout global
def post(edge, consts, oneofs):
	# Start in EDGES, move to POSTS #
	efile = open(edge, "r")
	for line in efile:
		if "..tick():::EXIT" in line:
			break
	# Let's copy over:
		# non-trivial equalities
		# oneofs with context
	eqs = []
	for line in efile:
		if " == " in line and "%" not in line and "orig" not in line and "ACLK" not in line and "+" not in line and "*" not in line:
			# For equalities, let's use replace to rename, then use sets
			splits = line.strip().split(" == ")
			for const in consts:
				for reg in const:
					for i in [0,1]:
						if splits[i] == reg:
							splits[i] = "!eqset" + const[0]
			eles_to_consts(splits, eqs) # recycle this method
		if " one of " in line and "ACLK" not in line:
			# we'll need to ref vs eqs... eventually
			
	efile.close()
	# clean up struct
	eqs = [list(eq) for eq in eqs]
	for eq in eqs:
		eq.sort()
	eqs = sorted(eqs, key=lambda x: x[0])
	os.chdir(os.getcwd().replace("edges","posts"))
	pfile = open(edge.replace(".txt",".p.txt"), "w")
	os.chdir(os.getcwd().replace("posts","edges"))
	for eq in eqs:
		if len(eq) > 1:
			pfile.write(str(eq).replace("\'","") + "\n")
	pfile.close()
	return
	

def posts():
	# get file pts
	cd_orig = os.getcwd()
	# build the globals struct
	[consts, oneofs] = gread()
	# ref vs edges
	# --- ENTER EDGES DIR --- #
	edges_dir = os.getcwd().replace("utils","outs/edges")
	os.chdir(os.getcwd().replace("utils","outs/edges"))
	os.system("mkdir ../posts")
	files = os.listdir(".")
	edges = list(filter(lambda x: ".txt" in x, files))
	for edge in edges:
		post(edge, consts, oneofs)
	# --- RETURN TO DIR --- #
	os.chdir(cd_orig)

posts()