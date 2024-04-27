use std::f64::consts::PI;
// use std::net::UdpSocket;
use std::io;
// use rand::Rng;

const NUM_SAMPLES:usize = 4096;

fn main() -> io::Result<()> {

    //Variables
    let frequency:f64 = 10000.0; //Hz
    let sampling_freq:f64 = 30.0 * ((1000000) as f64);

    //Test Signal Generated
    let signal_buffer = sine_array(sampling_freq, frequency);
    //println!("{:?}",signal_buffer);

    //We have succesfully recieved an array, but it contains floating point values
    //We convert them to 16 bit hex values, and then send them as bytes on 127.0.0.1:5006

    let quantized_buffer = convert2hex_16bit(signal_buffer);
    println!("{:?}",quantized_buffer);
    
    //We have Converted the signal to 16 bit values
    //To send this as a packet, we need to send this as bytes (u8), So we split the packets




    // let mut rng = rand::thread_rng();
    // Connect to the server (replace with the server's IP address and port)
    // let server_address = "127.0.0.1:5006";
    // let socket = UdpSocket::bind("0.0.0.0:0")?;
    // socket.connect(server_address)?;
    // let buffer: Vec<u32> = (0..1024).collect();

    /*
    loop{
        let noise: Vec<u8> = (0..16384).map(|_| rng.gen()).collect();
        println!("{:?}",buffer);
        let slice_data: &[u32] = buffer.as_slice();
        // Send the message to the server
        //socket.send(slice_data)?;

    } 
    */
    Ok(())
}



fn sine_array(fs:f64, freq:f64) -> [f64; NUM_SAMPLES]{
//Assume all to be in Mhz, This is just a test function
//Can try 30.72 Mhz as fs
    let mut buffer = [0.0 as f64; NUM_SAMPLES];
    let w = 2.0 * PI * freq;
    let mut t:f64;
    let dt = 1.0/fs;
    for index in 0..NUM_SAMPLES{
        t = (index as f64) * dt;
        let i = index as usize; 
        buffer[i] = f64::sin(w*t);
    }
    return buffer;
}

fn convert2hex_16bit(buffer:[f64; NUM_SAMPLES]) -> [i16; NUM_SAMPLES]{
    //MIN = -32768 and MAX = 32767
    let min:i32 = -32768;
    let max:i32 = 32767;
    let mut quantized_buffer = [0 as i16; NUM_SAMPLES];

    for i in 0..NUM_SAMPLES{
       let quantized1:i32 = (buffer[i] * (max as f64)) as i32;
       let quantized2:i32 = if quantized1 > max {max} else {quantized1};
       let quantized3:i16 = if quantized2 < min {min as i16} else {quantized2 as i16};
       quantized_buffer[i] = quantized3;

    } 
    return quantized_buffer;
}


