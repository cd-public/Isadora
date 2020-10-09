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
	
post("aes_tb.out")