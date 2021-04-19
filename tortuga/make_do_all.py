from os import system

#regs = ['M_AXI_ARADDR', 'M_AXI_ARADDR_INT']

regs = ['M_AXI_ARADDR', 'M_AXI_ARADDR_INT', 'M_AXI_ARADDR_wire', 'M_AXI_ARBURST', 'M_AXI_ARBURST_INT', 'M_AXI_ARBURST_wire', 'M_AXI_ARCACHE', 'M_AXI_ARCACHE_INT', 'M_AXI_ARCACHE_wire', 'M_AXI_ARID', 'M_AXI_ARID_INT', 'M_AXI_ARID_wire', 'M_AXI_ARLEN', 'M_AXI_ARLEN_INT', 'M_AXI_ARLEN_wire', 'M_AXI_ARLOCK', 'M_AXI_ARLOCK_INT', 'M_AXI_ARLOCK_wire', 'M_AXI_ARPROT', 'M_AXI_ARPROT_INT', 'M_AXI_ARPROT_wire', 'M_AXI_ARQOS', 'M_AXI_ARQOS_INT', 'M_AXI_ARQOS_wire', 'M_AXI_ARREADY', 'M_AXI_ARREADY_wire', 'M_AXI_ARSIZE', 'M_AXI_ARSIZE_INT', 'M_AXI_ARSIZE_wire', 'M_AXI_ARUSER', 'M_AXI_ARUSER_INT', 'M_AXI_ARUSER_wire', 'M_AXI_ARVALID', 'M_AXI_ARVALID_wire', 'M_AXI_AWADDR', 'M_AXI_AWADDR_INT', 'M_AXI_AWADDR_wire', 'M_AXI_AWBURST', 'M_AXI_AWBURST_INT', 'M_AXI_AWBURST_wire', 'M_AXI_AWCACHE', 'M_AXI_AWCACHE_INT', 'M_AXI_AWCACHE_wire', 'M_AXI_AWID', 'M_AXI_AWID_INT', 'M_AXI_AWID_wire', 'M_AXI_AWLEN', 'M_AXI_AWLEN_INT', 'M_AXI_AWLEN_wire', 'M_AXI_AWLOCK', 'M_AXI_AWLOCK_INT', 'M_AXI_AWLOCK_wire', 'M_AXI_AWPROT', 'M_AXI_AWPROT_INT', 'M_AXI_AWPROT_wire', 'M_AXI_AWQOS', 'M_AXI_AWQOS_INT', 'M_AXI_AWQOS_wire', 'M_AXI_AWREADY', 'M_AXI_AWREADY_wire', 'M_AXI_AWSIZE', 'M_AXI_AWSIZE_INT', 'M_AXI_AWSIZE_wire', 'M_AXI_AWUSER', 'M_AXI_AWUSER_INT', 'M_AXI_AWUSER_wire', 'M_AXI_AWVALID', 'M_AXI_AWVALID_wire', 'M_AXI_BID', 'M_AXI_BID_wire', 'M_AXI_BREADY', 'M_AXI_BREADY_wire', 'M_AXI_BRESP', 'M_AXI_BRESP_wire', 'M_AXI_BUSER', 'M_AXI_BUSER_wire', 'M_AXI_BVALID', 'M_AXI_BVALID_wire', 'M_AXI_RDATA', 'M_AXI_RDATA_wire', 'M_AXI_RID', 'M_AXI_RID_wire', 'M_AXI_RLAST', 'M_AXI_RLAST_wire', 'M_AXI_RREADY', 'M_AXI_RREADY_wire', 'M_AXI_RRESP', 'M_AXI_RRESP_wire', 'M_AXI_RUSER', 'M_AXI_RUSER_wire', 'M_AXI_RVALID', 'M_AXI_RVALID_wire', 'M_AXI_WDATA', 'M_AXI_WDATA_wire', 'M_AXI_WLAST', 'M_AXI_WLAST_wire', 'M_AXI_WREADY', 'M_AXI_WREADY_wire', 'M_AXI_WSTRB', 'M_AXI_WSTRB_wire', 'M_AXI_WUSER', 'M_AXI_WUSER_wire', 'M_AXI_WVALID', 'M_AXI_WVALID_wire']

indent = "    "
out_file = open("do_all.txt","w")
out_file.write("newgrp hyperflogen\ncd /data/cd\nsource setup_radixs\ntouch start_time.txt\ncd iterative_build\n") # setup
for reg in regs:
	out_file.write("cp " + reg + ".as iACW_sps.as\n") # set new source
	out_file.write("./clean.sh\nradixs_shell -s iACW_explore.script\n./run_questa_explore\n") # run tortuga
	out_file.write("cd /data/cd\ncp iterative_build/iACW.vcd .\npython refine_vcd.py\nmv r_iACW.vcd " + reg + ".vcd\ncd iterative_build\n")
out_file.write("cd data/cd\nrm *ACW.vcd\ntouch end_time.txt\nls -al")