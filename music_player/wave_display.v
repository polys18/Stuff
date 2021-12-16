module wave_display (
    input clk,
    input reset,
    input [10:0] x,  // [0..1279]
    input [9:0]  y,  // [0..1023]
    input valid,
    input [7:0] read_value,
    input read_index,
    input [10:0] start_x, end_x,
    input [9:0] start_y, end_y,
    input [2:0] display,
    output reg [8:0] read_address,
    output wire valid_pixel,
    output wire [7:0] r,
    output wire [7:0] g,
    output wire [7:0] b
);
    
    reg valid_x;
    reg [7:0] read_value_adjusted;
    
    always @(*) begin
        case(display)
            3'b000: read_value_adjusted = (read_value >> 6) + 8'b10000000;
            3'b001: read_value_adjusted = (read_value >> 5) + 8'b1110000;
            3'b010: read_value_adjusted = (read_value >> 4) + 8'b1110000;
            3'b011: read_value_adjusted = (read_value >> 3) + 8'b01100000;
            3'b100: read_value_adjusted = (read_value >> 2) + 8'b01110000;
            3'b101: read_value_adjusted = (read_value >> 1) + 8'b01000000;
            default: read_value_adjusted = (read_value >> 6) + 8'b10000000;
        endcase
    end
    //assign read_value_adjusted = (read_value >> 1) + 8'b01000000;
    //assign read_value_adjusted = (read_value >> 1) + 8'b00100000;
    always @(*) begin
        case(x[10:8])
            3'b000: begin 
                read_address = 0;
                valid_x = 0;
            end
            3'b001: begin
                read_address = {read_index, ~x[8], x[7:1]};
                valid_x = 1;
            end
            3'b010: begin
                read_address = {read_index, ~x[8], x[7:1]};
                valid_x = 1;
            end
            3'b011: begin
                read_address = 0;
                valid_x = 0;
            end
            default: begin
                read_address = 0;
                valid_x = 0;
            end
        endcase
    end
    
    assign valid_pixel = (valid_x && ~y[9]);  //if pixel in quadrant 1 or 2
    
    wire [8:0] last_address;
    dffre #(9) addr_dff (.clk(clk), .r(reset), .en(valid), .d(read_address), .q(last_address));
    
    wire en_read = ~(read_address == last_address);
   
    wire [7:0] prev_read_value;
    dffre #(8) RAM_dffre(.clk(clk), .r(reset), .en(en_read), .d(read_value_adjusted), .q(prev_read_value));
    
    //wire [9:0] y_top = {1'b0, y[8:1]};  //y in top half
    
    wire magn_valid, magn_valid1, magn_valid2;
    
    assign magn_valid1 = ((read_value_adjusted >= y[8:1]) && (y[8:1] >= prev_read_value));
    assign magn_valid2 =((read_value_adjusted <= y[8:1]) && (y[8:1] <= prev_read_value));
    assign magn_valid = (magn_valid1 || magn_valid2);     //high if between RAM[x] and RAM[x-1]
    
   
    //assign {r,g,b} = (magn_valid)? 24'h0000f0 : 24'hffffff;
    assign {r,g,b}= (x > start_x && x < end_x && y > start_y && y < end_y) ? (magn_valid ? 24'hffffff : 24'h000000) : 24'hffffff;//

endmodule
