module wf_limits(
  input clk,
  input rst,
  input btn0,
  input btn1,
  input btn2,
  output reg [10:0] start_x,
  output reg [10:0] end_x,
  output reg [9:0] start_y,
  output reg [9:0] end_y,
  output wire [2:0] display
);
  
  `define DEFAULT_DISPLAY 3'b000
  //`define MAX_WIDTH 3'b001
  //`define MAX_HEIGHT 3'b011
  `define STAGE1 3'b001
  `define STAGE2 3'b010
  `define STAGE3 3'b011
  `define STAGE4 3'b100
  `define FULL_SCREEN 3'b101
  
  
  wire [10:0] default_start_x, default_end_x;
  wire [9:0] default_start_y, default_end_y;
  wire [10:0] max_start_x, max_end_x;
  wire [9:0] max_start_y, max_end_y;
    
  //new default display
  assign default_start_x  = 11'd380;
  assign default_end_x = 11'd640;
  assign default_start_y = 10'd92;
  assign default_end_y = 10'd452;
  
  //max display
  assign max_start_x = 11'd88;
  assign max_end_x = 11'd888;
  assign max_start_y = 10'd30;
  assign max_end_y = 10'd512;
 
  reg [2:0] next_state;
  wire [2:0] state;
  
  dffr #(3) states(.clk(clk), .r(rst), .d(next_state), .q(state));
  
  wire [2:0] btns;
  assign btns = {btn0, btn1, btn2};
  
  assign display = state;
  
  always @(*) begin
    casex({rst, state})
      4'b1xxx: begin     //Reset
        next_state = `DEFAULT_DISPLAY;
        start_x = default_start_x;
        end_x = default_end_x;
        start_y = default_start_y;
        end_y = default_end_y;
      end
      4'b0000: begin    //Default display
        next_state = (btns == 3'b100) ? `FULL_SCREEN : ((btns == 3'b010) ? `STAGE1 :  `DEFAULT_DISPLAY);
        start_x = default_start_x;
        end_x = default_end_x;
        start_y = default_start_y;
        end_y = default_end_y;
      end
      4'b0001: begin    //Stage1
        next_state = (btns == 3'b010) ? `STAGE2 : ((btns == 3'b100 || btns == 3'b001) ? `DEFAULT_DISPLAY : `STAGE1);
        start_x = 11'd360;
        end_x = 11'd660;
        start_y = 10'd80;
        end_y = 10'd464;
      end
      4'b0010: begin   //Stage 2
        next_state = (btns == 3'b010) ? `STAGE3 : ((btns == 3'b001) ? `STAGE1 : ((btns == 3'b100) ? `DEFAULT_DISPLAY : `STAGE2));
        start_x = 11'd340;
        end_x = 11'd680;
        start_y = 10'd68;
        end_y = 10'd476;
      end
      4'b0011: begin    //Stage 3
        next_state = (btns == 3'b010) ? `STAGE4 : ((btns == 3'b001) ? `STAGE2 : ((btns == 3'b100) ? `DEFAULT_DISPLAY : `STAGE3));
        start_x = 11'd320;
        end_x = 11'd700;
        start_y = 10'd56;
        end_y = 10'd488;
      end
      4'b0100: begin   //Stage 4
        next_state = (btns == 3'b010) ? `FULL_SCREEN : ((btns == 3'b001) ? `STAGE3 : ((btns == 3'b100) ?`DEFAULT_DISPLAY : `STAGE4));
        start_x = 11'd300;
        end_x = 11'd720;
        start_y = 10'd44;
        end_y = 10'd500;
      end
      4'b0101: begin  //Full Screen
        next_state = (btns == 3'b010 || btns == 3'b100) ? `DEFAULT_DISPLAY : ((btns == 3'b001) ? `STAGE4 : `FULL_SCREEN);
        start_x = max_start_x;
        end_x = max_end_x;
        start_y = max_start_y;
        end_y = max_end_y;
      end
      default: begin
        next_state = `DEFAULT_DISPLAY;
        start_x = default_start_x;
        end_x = default_end_x;
        start_y = default_start_y;
        end_y = default_end_y;
      end
    endcase
  end
endmodule
