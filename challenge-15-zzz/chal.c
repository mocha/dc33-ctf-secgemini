#include <stdio.h>
#include <stdlib.h>

int main() {
    unsigned char flag[65];

    if (scanf("%64s", flag) < 1) {
        return -1;
    }

    for (int i = 0; i < 64; ++i) {
        flag[i] += 0x77;
    }

    for (int i = 0; i < 64; ++i) {
        flag[i] *= 0x55;
    }

    for (int i = 0; i < 64; ++i) {
        flag[i] ^= 0x33;
    }

    for (int i = 0; i < 64; ++i) {
        flag[i] -= 0x11;
    }

    if (flag[32] != 0x43) {
        puts("nope.");
        return -1;
    }

    if (flag[36] != 0x29) {
        puts("nope.");
        return -1;
    }

    if (flag[40] != 0x76) {
        puts("nope.");
        return -1;
    }

    if (flag[48] != 0x2c) {
        puts("nope.");
        return -1;
    }

    if (flag[8] != 0x70) {
        puts("nope.");
        return -1;
    }

    if (flag[4] != 0x25) {
        puts("nope.");
        return -1;
    }

    if (flag[44] != 0x70) {
        puts("nope.");
        return -1;
    }

    if (flag[16] != 0x40) {
        puts("nope.");
        return -1;
    }

    if (flag[56] != 0x2e) {
        puts("nope.");
        return -1;
    }

    if (flag[20] != 0x7b) {
        puts("nope.");
        return -1;
    }

    if (flag[12] != 0xe2) {
        puts("nope.");
        return -1;
    }

    if (flag[0] != 0xe0) {
        puts("nope.");
        return -1;
    }

    if (flag[60] != 0x25) {
        puts("nope.");
        return -1;
    }

    if (flag[24] != 0x23) {
        puts("nope.");
        return -1;
    }

    if (flag[28] != 0x40) {
        puts("nope.");
        return -1;
    }

    if (flag[52] != 0x2c) {
        puts("nope.");
        return -1;
    }

    if ((flag[48] ^ flag[49]) != 0x5c) {
        puts("nope.");
        return -1;
    }

    if ((flag[32] ^ flag[33]) != 0x1e) {
        puts("nope.");
        return -1;
    }

    if ((flag[0] ^ flag[1]) != 0xa3) {
        puts("nope.");
        return -1;
    }

    if ((flag[28] ^ flag[29]) != 0x3c) {
        puts("nope.");
        return -1;
    }

    if ((flag[12] ^ flag[13]) != 0xcb) {
        puts("nope.");
        return -1;
    }

    if ((flag[60] ^ flag[61]) != 0x60) {
        puts("nope.");
        return -1;
    }

    if ((flag[36] ^ flag[37]) != 0x0a) {
        puts("nope.");
        return -1;
    }

    if ((flag[56] ^ flag[57]) != 0x41) {
        puts("nope.");
        return -1;
    }

    if ((flag[24] ^ flag[25]) != 0x13) {
        puts("nope.");
        return -1;
    }

    if ((flag[52] ^ flag[53]) != 0x5c) {
        puts("nope.");
        return -1;
    }

    if ((flag[4] ^ flag[5]) != 0x60) {
        puts("nope.");
        return -1;
    }

    if ((flag[8] ^ flag[9]) != 0x5f) {
        puts("nope.");
        return -1;
    }

    if ((flag[16] ^ flag[17]) != 0x9f) {
        puts("nope.");
        return -1;
    }

    if ((flag[44] ^ flag[45]) != 0x5c) {
        puts("nope.");
        return -1;
    }

    if ((flag[40] ^ flag[41]) != 0x0c) {
        puts("nope.");
        return -1;
    }

    if ((flag[20] ^ flag[21]) != 0x39) {
        puts("nope.");
        return -1;
    }

    if ((flag[37] ^ flag[38] ^ flag[39]) != 0x7f) {
        puts("nope.");
        return -1;
    }

    if ((flag[9] ^ flag[10] ^ flag[11]) != 0x05) {
        puts("nope.");
        return -1;
    }

    if ((flag[61] ^ flag[62] ^ flag[63]) != 0x46) {
        puts("nope.");
        return -1;
    }

    if ((flag[13] ^ flag[14] ^ flag[15]) != 0x11) {
        puts("nope.");
        return -1;
    }

    if ((flag[25] ^ flag[26] ^ flag[27]) != 0x6f) {
        puts("nope.");
        return -1;
    }

    if ((flag[21] ^ flag[22] ^ flag[23]) != 0x78) {
        puts("nope.");
        return -1;
    }

    if ((flag[29] ^ flag[30] ^ flag[31]) != 0x25) {
        puts("nope.");
        return -1;
    }

    if ((flag[57] ^ flag[58] ^ flag[59]) != 0x31) {
        puts("nope.");
        return -1;
    }

    if ((flag[17] ^ flag[18] ^ flag[19]) != 0xc6) {
        puts("nope.");
        return -1;
    }

    if ((flag[33] ^ flag[34] ^ flag[35]) != 0x1d) {
        puts("nope.");
        return -1;
    }

    if ((flag[49] ^ flag[50] ^ flag[51]) != 0x70) {
        puts("nope.");
        return -1;
    }

    if ((flag[1] ^ flag[2] ^ flag[3]) != 0xfa) {
        puts("nope.");
        return -1;
    }

    if ((flag[45] ^ flag[46] ^ flag[47]) != 0x6a) {
        puts("nope.");
        return -1;
    }

    if ((flag[5] ^ flag[6] ^ flag[7]) != 0x4c) {
        puts("nope.");
        return -1;
    }

    if ((flag[41] ^ flag[42] ^ flag[43]) != 0x62) {
        puts("nope.");
        return -1;
    }

    if ((flag[53] ^ flag[54] ^ flag[55]) != 0x1b) {
        puts("nope.");
        return -1;
    }

    if (((flag[20] - flag[21] + flag[23]) & 0xff) != 0xb3) {
        puts("nope.");
        return -1;
    }

    if (((flag[52] - flag[53] + flag[55]) & 0xff) != 0xec) {
        puts("nope.");
        return -1;
    }

    if (((flag[60] - flag[61] + flag[63]) & 0xff) != 0x06) {
        puts("nope.");
        return -1;
    }

    if (((flag[16] - flag[17] + flag[19]) & 0xff) != 0xd0) {
        puts("nope.");
        return -1;
    }

    if (((flag[40] - flag[41] + flag[43]) & 0xff) != 0x2c) {
        puts("nope.");
        return -1;
    }

    if (((flag[48] - flag[49] + flag[51]) & 0xff) != 0xeb) {
        puts("nope.");
        return -1;
    }

    if (((flag[36] - flag[37] + flag[39]) & 0xff) != 0x32) {
        puts("nope.");
        return -1;
    }

    if (((flag[32] - flag[33] + flag[35]) & 0xff) != 0x20) {
        puts("nope.");
        return -1;
    }

    if (((flag[44] - flag[45] + flag[47]) & 0xff) != 0x74) {
        puts("nope.");
        return -1;
    }

    if (((flag[28] - flag[29] + flag[31]) & 0xff) != 0x34) {
        puts("nope.");
        return -1;
    }

    if (((flag[56] - flag[57] + flag[59]) & 0xff) != 0xeb) {
        puts("nope.");
        return -1;
    }

    if (((flag[24] - flag[25] + flag[27]) & 0xff) != 0x1f) {
        puts("nope.");
        return -1;
    }

    if (((flag[4] - flag[5] + flag[7]) & 0xff) != 0x0c) {
        puts("nope.");
        return -1;
    }

    if (((flag[8] - flag[9] + flag[11]) & 0xff) != 0xb2) {
        puts("nope.");
        return -1;
    }

    if (((flag[0] - flag[1] + flag[3]) & 0xff) != 0xf5) {
        puts("nope.");
        return -1;
    }

    if (((flag[12] - flag[13] + flag[15]) & 0xff) != 0xe5) {
        puts("nope.");
        return -1;
    }

    puts("correct.");

    return 0;
}
