#!/usr/bin/env node

const readline = require("readline");

const crypto = require("crypto");

const rl = readline.createInterface({
  input: process.stdin,
  output: null,
});

function computeMD5(data) {
  return crypto.createHash("md5").update(data).digest("hex");
}

rl.question("Enter flag: ", (answer) => {
  let flagLen = answer.length;
  if (flagLen < 29) {
    process.exit(1);
  }
  let passed = 0;
  let a4 = answer[4];
  let a8 = answer[8];
  let a17 = answer[17];
  let a27 = answer[27];
  let a24 = answer[24];
  let a3 = answer[3];
  let a28 = answer[28];

  if (computeMD5(a4 + a17) == "b4d2241315ae63ff5c54388456f8d5c7") {
    passed += 1;
  }

  if (computeMD5(a8 + a27) == "3416a75f4cea9109507cacd8e2f2aefc") {
    passed += 1;
  }
  if (computeMD5(a24 + a3 + a28) == "493a97c8ea1bc749c1063cd9bb0b6923") {
    passed += 1;
  }

  if (passed === 3) {
    process.exit(0);
  } else {
    process.exit(1);
  }
});
