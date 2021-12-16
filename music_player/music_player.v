//
//  music_player module
//
//  This music_player module connects up the MCU, song_reader, note_player,
//  beat_generator, and codec_conditioner. It provides an output that indicates
//  a new sample (new_sample_generated) which will be used in lab 5.
//

//
//  music_player module
//
//  This music_player module connects up the MCU, song_reader, note_player,
//  beat_generator, and codec_conditioner. It provides an output that indicates
//  a new sample (new_sample_generated) which will be used in lab 5.
//

module music_player(
    // Standard system clock and reset
    input clk,
    input reset,

    // Our debounced and one-pulsed button inputs.
    input play_button,
    input next_button,
    
    // Playback control 
    input rewind_button, 
    input ff_button, 
    
    // The raw new_frame signal from the ac97_if codec.
    input new_frame,

    // This output must go high for one cycle when a new sample is generated.
    output wire new_sample_generated,

    // Our final output sample to the codec. This needs to be synced to
    // new_frame.
    output wire [15:0] sample_out
    //, sample_out_one, sample_out_two, sample_out_three
   
);
    // The BEAT_COUNT is parameterized so you can reduce this in simulation.
    // If you reduce this to 100 your simulation will be 10x faster.
    //parameter BEAT_COUNT = 1000;
    parameter BEAT_COUNT = 1000;


//
//  ****************************************************************************
//      Master Control Unit
//  ****************************************************************************
//   The reset_player output from the MCU is run only to the song_reader because
//   we don't need to reset any state in the note_player. If we do it may make
//   a pop when it resets the output sample.
//
 
    wire play;
    wire reset_player;
    wire [1:0] current_song;
    wire song_done;
    wire rewind;
    wire ff;
    mcu mcu(
        .clk(clk),
        .reset(reset),
        .play_button(play_button),
        .next_button(next_button),
        .rewind_button(rewind_button),
        .ff_button(ff_button),
        .play(play),
        .rewind(rewind),
        .ff(ff),
        .reset_player(reset_player),
        .song(current_song),
        .song_done(song_done)
    );

//
//  ****************************************************************************
//      Song Reader
//  ****************************************************************************
//
    wire beat;
    wire note_done, note_done_one, note_done_two, note_done_three;
    wire [17:0] notes_out;
    wire [17:0] durations_out;
    wire new_note;
 
    assign note_done = note_done_one && note_done_two && note_done_three;
    song_reader song_reader(
        .clk(clk),
        .reset(reset | reset_player),
        .play(play),
        .rewind(rewind),
        .ff(ff),
        .beat(beat),
        .song(current_song),
        .song_done(song_done),
        .note_done(note_done),
        .notes_out(notes_out),
        .durations_out(durations_out),
        .new_note(new_note)
    );

//   
//  ****************************************************************************
//      Note Player
//  ****************************************************************************
//  
    wire [5:0] note_one, note_two, note_three;
    wire [5:0] duration_one, duration_two, duration_three;
    
    assign {note_one, note_two, note_three} = notes_out;
    assign {duration_one, duration_two, duration_three} = durations_out;
    
    wire generate_next_sample;
    wire [15:0] note_sample_one, note_sample_two, note_sample_three;
    wire note_sample_ready_one, note_sample_ready_two, note_sample_ready_three;
    
    note_player note_player_one(
        .clk(clk),
        .reset(reset),
        .play_enable(play),
        .note_to_load(note_one),
        .duration_to_load(duration_one),
        .load_new_note(new_note),
        .done_with_note(note_done_one),
        .beat(beat),
        .generate_next_sample(generate_next_sample),
        .sample_out(note_sample_one),
        .new_sample_ready(note_sample_ready_one)
    );
    
    note_player note_player_two(
        .clk(clk),
        .reset(reset),
        .play_enable(play),
        .note_to_load(note_two),
        .duration_to_load(duration_two),
        .load_new_note(new_note),
        .done_with_note(note_done_two),
        .beat(beat),
        .generate_next_sample(generate_next_sample),
        .sample_out(note_sample_two),
        .new_sample_ready(note_sample_ready_two)
    );
      
      note_player note_player_three(
        .clk(clk),
        .reset(reset),
        .play_enable(play),
        .note_to_load(note_three),
        .duration_to_load(duration_three),
        .load_new_note(new_note),
        .done_with_note(note_done_three),
        .beat(beat),
        .generate_next_sample(generate_next_sample),
        .sample_out(note_sample_three),
        .new_sample_ready(note_sample_ready_three)
    );
      
//   
//  ****************************************************************************
//      Beat Generator
//  ****************************************************************************
//  By default this will divide the generate_next_sample signal (48kHz from the
//  codec's new_frame input) down by 1000, to 48Hz. If you change the BEAT_COUNT
//  parameter when instantiating this you can change it for simulation.
//  
    beat_generator #(.WIDTH(10), .STOP(BEAT_COUNT)) beat_generator(
        .clk(clk),
        .reset(reset),
        .en(generate_next_sample),
        .beat(beat)
    );

//  
//  ****************************************************************************
//      Codec Conditioner
//  ****************************************************************************
//  
    wire note_sample_ready;
    assign note_sample_ready = note_sample_ready_one && note_sample_ready_two && note_sample_ready_three;
    assign new_sample_generated = generate_next_sample;
    
    wire [15:0] note_sample;
//    wire [15:0] sample_one_shifted, sample_two_shifted, sample_three_shifted;
//    assign sample_one_shifted = note_sample_one >> 2;
//    assign sample_two_shifted = note_sample_two >> 2;
//    assign sample_three_shifted = note_sample_three >> 2;
    
    wire [15:0] sample_one_f, sample_two_f, sample_three_f;
    
//    assign sample_out_one = note_sample_one;
//    assign sample_out_two = note_sample_two;
//    assign sample_out_three = note_sample_three;
    
    assign sample_one_f = (note_sample_one[15]) ? {2'b11, note_sample_one[15:2]} : {2'b00, note_sample_one[15:2]};
    assign sample_two_f = (note_sample_two[15]) ? {2'b11, note_sample_two[15:2]} : {2'b00, note_sample_two[15:2]};
    assign sample_three_f = (note_sample_three[15]) ? {2'b11, note_sample_three[15:2]} : {2'b00, note_sample_three[15:2]};
   

    assign note_sample = sample_one_f + sample_two_f + sample_three_f;
    
    codec_conditioner codec_conditioner(
        .clk(clk),
        .reset(reset),
        .new_sample_in(note_sample),
        .latch_new_sample_in(note_sample_ready),
        .generate_next_sample(generate_next_sample),
        .new_frame(new_frame),
        .valid_sample(sample_out)
    );

endmodule
