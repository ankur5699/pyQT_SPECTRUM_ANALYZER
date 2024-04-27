use std::f64::consts::PI;
// use std::net::UdpSocket;
use std::io;
// use rand::Rng;

const NUM_SAMPLES:usize = 4096;

fn main() -> io::Result<()> {

    //Variables
    let frequency:f64 = 10000.0; //Hz

    let sampling_freq:f64 = 30.0 * ((1000000) as f64);
    let signal_buffer = sine_array(sampling_freq, frequency);
    println!("{:?}",signal_buffer);




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
