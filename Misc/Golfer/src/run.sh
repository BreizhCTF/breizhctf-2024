#!/bin/bash
cd "$1";
HOME="$1";
export PATH=/opt/rust/bin:$PATH;
export RUSTUP_HOME=/opt/rust;
export CARGO_HOME=/opt/rust;
port=$(comm -23 <(seq 10000 65535 | sort) <(ss -Htan | awk '{print $4}' | cut -d':' -f2 | sort -u) | shuf | head -n 1);
rustc main.rs;
 ./main $port &
 echo $2 | base64 -d | nc localhost $port;