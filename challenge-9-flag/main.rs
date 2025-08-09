use base64::prelude::*;
use sha2::{Digest, Sha256};
use std::fs;
use std::io::{self, Write};
use std::str;

struct GameState {
    clicks: u128,
}

fn show_menu() {
    println!("1. click the flag");
    println!("2. claim the flag");
    println!("3. save game");
    println!("4. load saved game");
    println!("5. quit");
}

fn click_the_flag(state: &mut GameState) {
    state.clicks += 1;
    println!("you clicked the flag {} times", state.clicks);
}

fn claim_the_flag(state: &mut GameState) {
    if state.clicks < 1 || state.clicks > 340282366920938463463374607431768211455 {
        let flag = fs::read_to_string("flag").unwrap();
        println!("{}", flag);
    } else {
        println!("you need more clicks to claim the flag!");
    }
}

fn compute_checksum(clicks_bytes: &[u8]) -> [u8; 8] {
    let mut hasher = Sha256::new();
    hasher.update(clicks_bytes);
    let hash = hasher.finalize();

    let mut checksum: [u8; 8] = [0; 8];
    checksum[0] = (hash[1] ^ hash[0]) | hash[24];
    checksum[2] = (hash[3] ^ hash[2]) | hash[25];
    checksum[4] = (hash[3] ^ hash[4]) | hash[26];
    checksum[6] = (hash[7] ^ hash[6]) | hash[27];
    checksum[1] = (hash[1] | hash[2]) ^ hash[28];
    checksum[3] = (hash[3] | hash[1]) ^ hash[29];
    checksum[5] = (hash[3] | hash[1]) ^ hash[30];
    checksum[7] = (hash[7] | hash[2]) ^ hash[31];

    checksum
}

fn save_game(state: &mut GameState) {
    println!("saving...");

    let clicks = state.clicks.to_string();
    let clicks_bytes = clicks.as_bytes();

    // anti cheat: compute a secure checksum
    let checksum = compute_checksum(clicks_bytes);

    let mut save_state = Vec::new();
    save_state.extend(clicks_bytes);
    save_state.extend(checksum);
    let save_state = BASE64_STANDARD.encode(save_state);

    println!("here's your saved game state: {}", save_state);
}

fn load_game(state: &mut GameState) {
    print!("please enter your saved game state: ");
    io::stdout().flush().unwrap();

    let mut input = String::new();
    io::stdin().read_line(&mut input).unwrap();
    let input = input.trim();

    let save_state = BASE64_STANDARD.decode(input).unwrap();

    let clicks = str::from_utf8(&save_state[..save_state.len() - 8]).unwrap();
    let clicks_bytes = clicks.as_bytes();
    let clicks: u128 = clicks.parse().unwrap();

    // sanity check
    assert!(clicks >= 1);

    // anti cheat: check the secure checksum
    let checksum = compute_checksum(clicks_bytes);
    let saved_checksum = &save_state[save_state.len() - 8..];
    assert_eq!(checksum, saved_checksum);

    state.clicks = clicks;

    println!("success: loaded game from save state");
}

fn main() {
    // the first one is on us...
    let mut state = GameState { clicks: 1 };

    loop {
        show_menu();

        print!("choice: ");
        io::stdout().flush().unwrap();

        let mut input = String::new();
        io::stdin().read_line(&mut input).unwrap();

        let choice: i32 = input.trim().parse().unwrap_or(0);

        match choice {
            1 => {
                click_the_flag(&mut state);
            }
            2 => {
                claim_the_flag(&mut state);
            }
            3 => {
                save_game(&mut state);
            }
            4 => {
                load_game(&mut state);
            }
            5 => {
                println!("thanks for playing!");
                break;
            }
            _ => {
                println!("error: invalid choice!");
                break;
            }
        }
    }
}
