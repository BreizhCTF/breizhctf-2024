use cve_rs::construct_fake_string;

use std::io::{stdin, stdout, Write};
use std::{io, mem, fs::File};
use std::io::Read;

fn flag() {
    let mut file = File::open("flag.txt").expect("Flag not found please contact an admin if this is remote.");

    let mut contents = String::new();
    let _ = file.read_to_string(&mut contents);

    println!("Here is your flag: {contents}");
}


fn main() -> io::Result<()> {
    use std::hint::black_box;

    #[repr(C)]
    #[derive(Default)]
    struct Authentication {
        name_buf: [u8; 16],
        password: [u8; 16],
        is_admin: i64
    }

    let mut auth = black_box(Authentication::default());

    let mut name = construct_fake_string(auth.name_buf.as_mut_ptr(), 1024usize, 0usize);

    println!("Welcome to the BreizhCTF !");
    println!("Will you be able to reach the top :-)");
    println!("First, enter your username > ");
    stdout().flush()?;
    stdin().read_line(&mut name)?;

    mem::forget(name);
    let username = &auth.name_buf[0..16];

    if "adminthelionking" == String::from_utf8_lossy(username) {
        let is_admin = &auth.is_admin;
        if *is_admin != 0 {
            flag();
        } else {
            println!("No flag sadmiaou");
        }
    } else {
        println!("Wrong username.");
    }

    Ok(())
}
