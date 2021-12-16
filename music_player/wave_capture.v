`define STATE_ARMED 2'b00
    `define STATE_ACTIVE 2'b01
    `define STATE_WAIT 2'b10
    
module wave_capture (
    input clk,
    input reset,
    input new_sample_ready,
    input [15:0] new_sample_in,
    input wave_display_idle,

    output wire [8:0] write_address,
    output reg write_enable,
    output wire [7:0] write_sample,
    output wire read_index
);
    
    // need to switch audio sample from signed to unsigned
    
    
    reg [1:0] next_state;
    wire [1:0] state;
    wire [7:0] count;
    reg [7:0] next_count;
    reg [8:0] next_write_address;
    wire next_read_index;
    wire [15:0] previous_new_sample_in;
    wire [7:0] write_sample_temp;
    
    
    dffr #(2) states(.clk(clk), .r(reset), .d(next_state), .q(state));
    dffr #(8) counter(.clk(clk), .r(reset), .d(next_count), .q(count));
    dffr #(9) addresses(.clk(clk), .r(reset), .d(next_write_address), .q(write_address));
    dffr #(1) read(.clk(clk), .r(reset), .d(next_read_index), .q(read_index));
    dffr #(16) samples(.clk(clk), .r(reset), .d(new_sample_in), .q(previous_new_sample_in));
    

    
    always @(*) begin
        casex({reset, state})
            3'b1xx: begin
                next_state = `STATE_ARMED;
                next_count = 8'b0;
                write_enable = 1'b0;
            end 
            // Armed state
            3'b000: begin
                next_state = ((previous_new_sample_in[15] == 1'b1) && (new_sample_in[15] == 1'b0)) ? `STATE_ACTIVE : `STATE_ARMED;
                next_count = 8'b0;
                write_enable = 1'b0;
            end 
            // Active state
            3'b001: begin
                next_state = (count == 8'b11111111) ? `STATE_WAIT : `STATE_ACTIVE;
                next_count = (new_sample_ready) ? count + 8'b1 : count;
                write_enable = 1'b1;
            end 
            // Wait state
            3'b010: begin
                next_state = wave_display_idle ? `STATE_ARMED : `STATE_WAIT;
                next_count = 8'b0;
                write_enable = 1'b0;
            end 
        default: begin 
        next_state = 2'b00;
        next_count = 8'b0;
        end
        endcase 
    end 

     
     always @(*) begin
        case (new_sample_ready) 
            1'b1: next_write_address = reset ? 9'b0 : {~read_index, count};
            default: next_write_address = write_address;
        endcase 
     end 

    assign write_sample_temp = (state == `STATE_ACTIVE) ? new_sample_in[15:8] : 8'b0;
    assign write_sample = 8'b0 - (write_sample_temp + 8'b10000000 + 1);
    assign next_read_index = reset ? 1'b0 : ((wave_display_idle && (state == 2'b10)) ? ~read_index : read_index);
    
endmodule
