use std::net::UdpSocket;
use std::io;
use rand::Rng;


fn main() -> io::Result<()> {

    //Variables
    let sample_size = 1024;
    let frequency = 10000; //Hz

    let sampling_freq:f64 = 30.0 * ((1000000) as f64);
    println!("{:?}",sampling_freq);


    let mut rng = rand::thread_rng();
    // Connect to the server (replace with the server's IP address and port)
    let server_address = "127.0.0.1:5006";
    let socket = UdpSocket::bind("0.0.0.0:0")?;
    socket.connect(server_address)?;
    let buffer: Vec<u32> = (0..1024).collect();

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