
//-------------------- GLOBAL PORTS
  input  wire ACLK,
  input  wire ARESETN,
  output wire INTR_LINE_R, 	
	output wire INTR_LINE_W,

//-----------------END GLOBAL PORTS

//-------------------- AXI CONFIGURATION S PORTS
  input  wire [C_S_CTRL_AXI_ADDR_WIDTH-1 : 0] S_AXI_CTRL_AWADDR,
  input  wire [2 : 0]                         S_AXI_CTRL_AWPROT,
  input  wire                                 S_AXI_CTRL_AWVALID,
  output wire                                 S_AXI_CTRL_AWREADY,

  input  wire [C_S_CTRL_AXI-1 : 0]            S_AXI_CTRL_WDATA,
  input  wire [(C_S_CTRL_AXI/8)-1 : 0]        S_AXI_CTRL_WSTRB,
  input  wire                                 S_AXI_CTRL_WVALID,
  output wire                                 S_AXI_CTRL_WREADY,

  output wire [1 : 0]                         S_AXI_CTRL_BRESP,
  output wire                                 S_AXI_CTRL_BVALID,
  input  wire                                 S_AXI_CTRL_BREADY,

  input  wire [C_S_CTRL_AXI_ADDR_WIDTH-1 : 0] S_AXI_CTRL_ARADDR,
  input  wire [2 : 0]                         S_AXI_CTRL_ARPROT,
  input  wire                                 S_AXI_CTRL_ARVALID,
  output wire                                 S_AXI_CTRL_ARREADY,

  output wire [C_S_CTRL_AXI-1 : 0]            S_AXI_CTRL_RDATA,
  output wire [1 : 0]                         S_AXI_CTRL_RRESP,
  output wire                                 S_AXI_CTRL_RVALID,
  input  wire                                 S_AXI_CTRL_RREADY,

//-----------------END AXI CONFIGURATION S PORTS

//-------------------- HARDWARE MODULE PORTS

  input wire         r_start_wire, //: in std_logic;
  input wire         w_start_wire, //: in std_logic;

  input wire         reset_wire,

  //-- base address
  input wire[31 : 0] r_base_addr_wire, //: in std_logic_vector (31 downto 0);
  input wire[31 : 0] w_base_addr_wire, //: in std_logic_vector (31 downto 0);
  //-- num transaction
  input wire[15 : 0] r_num_trans_wire, //: in std_logic_vector(15 downto 0);
  input wire[15 : 0] w_num_trans_wire, //: in std_logic_vector(15 downto 0);

  input wire[7 : 0] r_burst_len_wire,  //: in std_logic_vector(7 downto 0);
  input wire[7 : 0] w_burst_len_wire,  //: in std_logic_vector(7 downto 0);

  input wire        data_val_wire, //: in std_logic;

  //-- output done
  output wire       w_done_wire,  //: out std_logic;
  output wire       r_done_wire,  //: out std_logic;


//-----------------END HARDWARE MODULE PORTS


//-------------------- M OUTPUT INTERFACE PORTS

  output wire [C_M_AXI_ID_WIDTH-1 : 0]        M_AXI_AWID,
  output wire [C_M_AXI_ADDR_WIDTH-1 : 0]      M_AXI_AWADDR,
  output wire [7 : 0]                         M_AXI_AWLEN,
  output wire [2 : 0]                         M_AXI_AWSIZE,
  output wire [1 : 0]                         M_AXI_AWBURST,
  output wire                                 M_AXI_AWLOCK,
  output wire [3 : 0]                         M_AXI_AWCACHE,
  output wire [2 : 0]                         M_AXI_AWPROT,
  output wire [3 : 0]                         M_AXI_AWQOS,
  output wire [C_M_AXI_AWUSER_WIDTH-1 : 0]    M_AXI_AWUSER,
  output wire                                 M_AXI_AWVALID,
  input  wire                                 M_AXI_AWREADY,

  output wire [C_M_AXI_DATA_WIDTH-1 : 0]      M_AXI_WDATA,
  output wire [C_M_AXI_DATA_WIDTH/8-1 : 0]    M_AXI_WSTRB,
  output wire                                 M_AXI_WLAST,
  output wire [C_M_AXI_WUSER_WIDTH-1 : 0]     M_AXI_WUSER,
  output wire                                 M_AXI_WVALID,
  input  wire                                 M_AXI_WREADY,

  input  wire [C_M_AXI_ID_WIDTH-1 : 0]        M_AXI_BID,
  input  wire [1 : 0]                         M_AXI_BRESP,
  input  wire [C_M_AXI_BUSER_WIDTH-1 : 0]     M_AXI_BUSER,
  input  wire                                 M_AXI_BVALID,
  output wire                                 M_AXI_BREADY,

  output wire [C_M_AXI_ID_WIDTH-1 : 0]        M_AXI_ARID,
  output wire [C_M_AXI_ADDR_WIDTH-1 : 0]      M_AXI_ARADDR,
  output wire [7 : 0]                         M_AXI_ARLEN,
  output wire [2 : 0]                         M_AXI_ARSIZE,
  output wire [1 : 0]                         M_AXI_ARBURST,
  output wire                                 M_AXI_ARLOCK,
  output wire [3 : 0]                         M_AXI_ARCACHE,
  output wire [2 : 0]                         M_AXI_ARPROT,
  output wire [3 : 0]                         M_AXI_ARQOS,
  output wire [C_M_AXI_ARUSER_WIDTH-1 : 0]    M_AXI_ARUSER,
  output wire                                 M_AXI_ARVALID,
  input  wire                                 M_AXI_ARREADY,

  input  wire [C_M_AXI_ID_WIDTH-1 : 0]        M_AXI_RID,
  input  wire [C_M_AXI_DATA_WIDTH-1 : 0]      M_AXI_RDATA,
  input  wire [1 : 0]                         M_AXI_RRESP,
  input  wire                                 M_AXI_RLAST,
  input  wire [C_M_AXI_RUSER_WIDTH-1 : 0]     M_AXI_RUSER,
  input  wire                                 M_AXI_RVALID,
  output wire                                 M_AXI_RREADY,

//-----------------END M OUTPUT INTERFACE PORTS

  input  wire i_config,
  output wire [31 : 0] o_data
);

//-------------------- AXI S CONFIGURATION SIGNALS
  reg [C_S_CTRL_AXI_ADDR_WIDTH-1 : 0] axi_awaddr;
  reg                                 axi_awready;
  reg                                 axi_wready;
  reg [1 : 0]                         axi_bresp;
  reg                                 axi_bvalid;
  reg [C_S_CTRL_AXI_ADDR_WIDTH-1 : 0] axi_araddr;
  reg                                 axi_arready;
  reg [C_S_CTRL_AXI-1 : 0]            axi_rdata;
  reg [1 : 0]                         axi_rresp;
  reg                                 axi_rvalid;

  localparam integer ADDR_LSB = (C_S_CTRL_AXI/32)+1;
  localparam integer OPT_MEM_ADDR_BITS = 5;

  reg [C_S_CTRL_AXI-1 : 0] reg00_config;
  reg [C_S_CTRL_AXI-1 : 0] reg01_config;
  reg [C_S_CTRL_AXI-1 : 0] reg02_r_anomaly;
  reg [C_S_CTRL_AXI-1 : 0] reg03_r_anomaly;
  reg [C_S_CTRL_AXI-1 : 0] reg04_w_anomaly;
  reg [C_S_CTRL_AXI-1 : 0] reg05_w_anomaly;
  reg [C_S_CTRL_AXI-1 : 0] reg06_r_config;
  reg [C_S_CTRL_AXI-1 : 0] reg07_r_config;
  reg [C_S_CTRL_AXI-1 : 0] reg08_r_config;
  reg [C_S_CTRL_AXI-1 : 0] reg09_r_config;
  reg [C_S_CTRL_AXI-1 : 0] reg10_r_config;
  reg [C_S_CTRL_AXI-1 : 0] reg11_r_config;
  reg [C_S_CTRL_AXI-1 : 0] reg12_r_config;
  reg [C_S_CTRL_AXI-1 : 0] reg13_r_config;
  reg [C_S_CTRL_AXI-1 : 0] reg14_r_config;
  reg [C_S_CTRL_AXI-1 : 0] reg15_r_config;
  reg [C_S_CTRL_AXI-1 : 0] reg16_r_config;
  reg [C_S_CTRL_AXI-1 : 0] reg17_r_config;
  reg [C_S_CTRL_AXI-1 : 0] reg18_r_config;
  reg [C_S_CTRL_AXI-1 : 0] reg19_r_config;
  reg [C_S_CTRL_AXI-1 : 0] reg20_r_config;
  reg [C_S_CTRL_AXI-1 : 0] reg21_r_config;
  reg [C_S_CTRL_AXI-1 : 0] reg22_w_config;
  reg [C_S_CTRL_AXI-1 : 0] reg23_w_config;
  reg [C_S_CTRL_AXI-1 : 0] reg24_w_config;
  reg [C_S_CTRL_AXI-1 : 0] reg25_w_config;
  reg [C_S_CTRL_AXI-1 : 0] reg26_w_config;
  reg [C_S_CTRL_AXI-1 : 0] reg27_w_config;
  reg [C_S_CTRL_AXI-1 : 0] reg28_w_config;
  reg [C_S_CTRL_AXI-1 : 0] reg29_w_config;
  reg [C_S_CTRL_AXI-1 : 0] reg30_w_config;
  reg [C_S_CTRL_AXI-1 : 0] reg31_w_config;
  reg [C_S_CTRL_AXI-1 : 0] reg32_w_config;
  reg [C_S_CTRL_AXI-1 : 0] reg33_w_config;
  reg [C_S_CTRL_AXI-1 : 0] reg34_w_config;
  reg [C_S_CTRL_AXI-1 : 0] reg35_w_config;
  reg [C_S_CTRL_AXI-1 : 0] reg36_w_config;
  reg [C_S_CTRL_AXI-1 : 0] reg37_w_config;

  wire                     regXX_rden;
  wire                     regXX_wren;
  reg [C_S_CTRL_AXI-1 : 0] reg_data_out;
  integer                  byte_index;
  reg                      aw_en;

  assign S_AXI_CTRL_AWREADY = axi_awready;
  assign S_AXI_CTRL_WREADY  = axi_wready;
  assign S_AXI_CTRL_BRESP   = axi_bresp;
  assign S_AXI_CTRL_BVALID  = axi_bvalid;
  assign S_AXI_CTRL_ARREADY = axi_arready;
  assign S_AXI_CTRL_RDATA   = axi_rdata;
  assign S_AXI_CTRL_RRESP   = axi_rresp;
  assign S_AXI_CTRL_RVALID  = axi_rvalid;

//-----------------END AXI S CONFIGURATION SIGNALS


//-------------------- AXI M INTERNAL SIGNALS
  wire [C_M_AXI_ID_WIDTH-1 : 0]     M_AXI_AWID_wire;
  wire [C_M_AXI_ADDR_WIDTH-1 : 0]   M_AXI_AWADDR_wire;
  wire [7 : 0]                      M_AXI_AWLEN_wire;
  wire [2 : 0]                      M_AXI_AWSIZE_wire;
  wire [1 : 0]                      M_AXI_AWBURST_wire;
  wire                              M_AXI_AWLOCK_wire;
  wire [3 : 0]                      M_AXI_AWCACHE_wire;
  wire [2 : 0]                      M_AXI_AWPROT_wire;
  wire [3 : 0]                      M_AXI_AWQOS_wire;
  wire [C_M_AXI_AWUSER_WIDTH-1 : 0] M_AXI_AWUSER_wire;
  wire                              M_AXI_AWVALID_wire;
  wire                              M_AXI_AWREADY_wire;

  wire [C_M_AXI_DATA_WIDTH-1 : 0]   M_AXI_WDATA_wire;
  wire [C_M_AXI_DATA_WIDTH/8-1 : 0] M_AXI_WSTRB_wire;
  wire                              M_AXI_WLAST_wire;
  wire [C_M_AXI_WUSER_WIDTH-1 : 0]  M_AXI_WUSER_wire;
  wire                              M_AXI_WVALID_wire;
  wire                              M_AXI_WREADY_wire;

  wire [C_M_AXI_ID_WIDTH-1 : 0]     M_AXI_BID_wire;
  wire [1 : 0]                      M_AXI_BRESP_wire;
  wire [C_M_AXI_BUSER_WIDTH-1 : 0]  M_AXI_BUSER_wire;
  wire                              M_AXI_BVALID_wire;
  wire                              M_AXI_BREADY_wire;

  wire [C_M_AXI_ID_WIDTH-1 : 0]     M_AXI_ARID_wire;
  wire [C_M_AXI_ADDR_WIDTH-1 : 0]   M_AXI_ARADDR_wire;
  wire [7 : 0]                      M_AXI_ARLEN_wire;
  wire [2 : 0]                      M_AXI_ARSIZE_wire;
  wire [1 : 0]                      M_AXI_ARBURST_wire;
  wire                              M_AXI_ARLOCK_wire;
  wire [3 : 0]                      M_AXI_ARCACHE_wire;
  wire [2 : 0]                      M_AXI_ARPROT_wire;
  wire [3 : 0]                      M_AXI_ARQOS_wire;
  wire [C_M_AXI_AWUSER_WIDTH-1 : 0] M_AXI_ARUSER_wire;
  wire                              M_AXI_ARVALID_wire;
  wire                              M_AXI_ARREADY_wire;

	wire [C_M_AXI_ID_WIDTH-1 : 0]     M_AXI_RID_wire;
	wire [C_M_AXI_DATA_WIDTH-1 : 0]   M_AXI_RDATA_wire;
	wire [1 : 0]                      M_AXI_RRESP_wire;
	wire                              M_AXI_RLAST_wire;
	wire [C_M_AXI_RUSER_WIDTH-1 : 0]  M_AXI_RUSER_wire;
	wire                              M_AXI_RVALID_wire;
	wire                              M_AXI_RREADY_wire;


	reg [C_M_AXI_ID_WIDTH-1 : 0]      M_AXI_AWID_INT;
	reg [C_M_AXI_ADDR_WIDTH-1 : 0]    M_AXI_AWADDR_INT;
	reg [7 : 0]                       M_AXI_AWLEN_INT;
	reg [2 : 0]                       M_AXI_AWSIZE_INT;
	reg [1 : 0]                       M_AXI_AWBURST_INT;
  reg                               M_AXI_AWLOCK_INT;
	reg [3 : 0]                       M_AXI_AWCACHE_INT;
	reg [2 : 0]                       M_AXI_AWPROT_INT;
	reg [3 : 0]                       M_AXI_AWQOS_INT;
	reg [C_M_AXI_AWUSER_WIDTH-1 : 0]  M_AXI_AWUSER_INT;

	reg [C_M_AXI_ID_WIDTH-1 : 0]      M_AXI_ARID_INT;
	reg [C_M_AXI_ADDR_WIDTH-1 : 0]    M_AXI_ARADDR_INT;
	reg [7 : 0]                       M_AXI_ARLEN_INT;
	reg [2 : 0]                       M_AXI_ARSIZE_INT;
 	reg [1 : 0]                       M_AXI_ARBURST_INT;
  reg                               M_AXI_ARLOCK_INT;
 	reg [3 : 0]                       M_AXI_ARCACHE_INT;
 	reg [2 : 0]                       M_AXI_ARPROT_INT;
	reg [3 : 0]                       M_AXI_ARQOS_INT;
	reg [C_M_AXI_ARUSER_WIDTH-1 : 0]  M_AXI_ARUSER_INT;

//-----------------END AXI M INTERNAL SIGNALS

//-------------------- MEMORY CNTRL LOGIC SIGNALS
  reg AW_ILL_TRANS [MAX_OUTS_TRANS-1 : 0];
  reg [LOG_MAX_OUTS_TRAN-1 : 0] AW_ILL_TRANS_FIL_PTR;
  reg [LOG_MAX_OUTS_TRAN-1 : 0] AW_ILL_DATA_TRANS_SRV_PTR;
  reg [LOG_MAX_OUTS_TRAN-1 : 0] AW_ILL_TRANS_SRV_PTR;
  reg AR_ILL_TRANS [MAX_OUTS_TRANS-1 : 0];
  reg [LOG_MAX_OUTS_TRAN-1 : 0] AR_ILL_TRANS_FIL_PTR;
  reg [LOG_MAX_OUTS_TRAN-1 : 0] AR_ILL_TRANS_SRV_PTR;
  reg                           AW_STATE;
  reg                           AR_STATE;
  reg                           B_STATE;
  reg                           R_STATE;
  reg                           AW_ILLEGAL_REQ;
  reg                           AR_ILLEGAL_REQ;

  wire                          W_DATA_TO_SERVE;
  wire                          W_B_TO_SERVE;
  wire                          W_CH_EN;

  wire                          AW_CH_EN;
  wire                          AR_CH_EN;
    
  reg                           AW_CH_DIS;
  reg                           AR_CH_DIS;
    
  wire                          AW_EN_RST;
  wire                          AR_EN_RST;

  wire [15 : 0]                 AW_ADDR_VALID;
  wire [15 : 0]                 AR_ADDR_VALID;

  wire [15 : 0]                 AW_HIGH_ADDR;
  wire [15 : 0]                 AR_HIGH_ADDR;

  wire                          AW_ADDR_VALID_FLAG;
  wire                          AR_ADDR_VALID_FLAG;
