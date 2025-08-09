#!/usr/bin/env perl

use strict;
use warnings;
print "Enter the flag: ";
chomp(my $flag = <STDIN>);

sub transform {
    my ($c, $offset) = @_;
    my $n = ord($c);
    my $rotated = (($n << 3) & 0xFF) | ($n >> 5);
    my $res = $rotated + $offset;
    return $res;
}

my $a5 = substr($flag, 5, 1);
my $a18 = substr($flag, 18, 1);
my $a20 = substr($flag, 20, 1);

my $a7 = substr($flag, 7, 1);
my $a26 = substr($flag, 26, 1);

my $offset1 = 50;
my $offset2 = 35;
my $offset3 = 66;
my $offset4 = 64;
my $offset5 = 56;

my $passed = 0;

if (transform($a5, $offset1) == 179) {
  $passed += 1;
}

if (transform($a18, $offset2) == 164) {
  $passed += 1;
}

if (transform($a20, $offset3) == 269) {
  $passed += 1;
}

if (transform($a7, $offset4) == 314) {
  $passed += 1;
}

if (transform($a26, $offset5) == 65) {
  $passed += 1;
}

if($passed == 5){
  print "Correct!\n";
  exit(0);
} 

exit(1)

