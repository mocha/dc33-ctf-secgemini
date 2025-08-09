#!/usr/bin/env runhaskell

import Data.Char (ord)
import System.IO (hFlush, stdout)
import Data.Bits ((.&.), (.|.), shiftL)
import System.Exit (exitSuccess, exitFailure)

main :: IO ()
main = do
    putStr "Enter the flag: "
    hFlush stdout
    flag <- getLine -- Read flag from stdin


    let passed = if length flag >= 29 then checkConditions flag else 0

    if passed == 5 
        then exitSuccess
        else exitFailure


checkConditions :: String -> Int
checkConditions flag = sum [
    if (ord (flag !! 6) .&. 0xf) == 0x5 && (ord (flag !! 21) .&. 0xf0) == 0x60 then 1 else 0,
    if (ord (flag !! 10) .&. 0xf0) == (2 `shiftL` 4) + (2 `shiftL` 3) && (ord (flag !! 19) .&. 0xf) == (1 `shiftL` 2) * 3 then 1 else 0,
    if (ord (flag !! 25) .&. 0xf) == 0x1 && (ord (flag !! 6) .&. 0xf0) == (11^2 - 9) then 1 else 0,
    if (ord (flag !! 21) .&. 0xf) == 7 `mod` 14 && (ord (flag !! 10) .&. 0xf) == 3 then 1 else 0,
    if (ord (flag !! 25) .&. (255 - 15)) == 2^5 && (ord (flag !! 19) .&. (128 + 112)) == (0x50 + 0x10) then 1 else 0
    ]

