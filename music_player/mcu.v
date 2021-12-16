//`define SWIDTH 2
`define PAUSE 2'b00
`define PLAY 2'b01
`define REWIND 2'b10
`define FF 2'b11

module mcu(
    input clk,
    input reset,
    input play_button,
    input next_button,
    input rewind_button,
    input ff_button,
    output play,
    output reg rewind, 
    output reg ff,
    output reset_player,
    output [1:0] song,
    input song_done
);

    dffre #(.WIDTH(2)) song_reg (
        .clk(clk),
        .r(reset),
        .en(next_button || song_done),
        .d(song + 1'b1),
        .q(song)
    );

    wire [1:0] state;
    reg  [1:0] next_state;

    dffr #(2) playing_reg (
        .clk(clk),
        .r(reset),
        .d(next_state),
        .q(state)
    );

    assign play = (state == `PLAY);
    assign reset_player = next_button || song_done;

    always @* begin
        case (state)
            `PAUSE:
            begin
                next_state = play_button ? `PLAY  : (rewind_button ? `REWIND : (ff_button ? `FF : state));
                rewind = 1'b0;
                ff = 1'b0;
            end 
            `PLAY: next_state =
                (play_button || next_button || song_done) ? `PAUSE : (rewind_button ? `REWIND : (ff_button ? `FF : state));
            `REWIND: 
            begin
                next_state = `PLAY;  
                rewind = 1'b1;
                ff = 1'b0;
            end
            `FF:
            begin
                next_state = `PLAY;
                rewind = 1'b0;
                ff = 1'b1;
            end
            default: 
            begin 
                next_state = `PAUSE;
                rewind = 1'b0;
                ff = 1'b0;
            end 
            
        endcase
    end

endmodule
