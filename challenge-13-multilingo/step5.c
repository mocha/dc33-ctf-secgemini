#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int mod_inverse(int a, int m) {
    for (int i = 1; i < m; i++) {
        if ((a * i) % m == 1) {
            return i;
        }
    }
    return -1;
}

int main() {
    char flag[30]; 
    char encrypted_values[] = {'Z', 'r', 'o', '\\','4'}; 
    int a = 7;
    int b = 3;
    int m = 95;
    int a_inverse = mod_inverse(a, m);
    int expected_indices[] = {0, 1, 2, 22, 23};

    printf("Enter the flag: ");
    fgets(flag, 30, stdin); 
    
    size_t len = strlen(flag);
    if (len > 0 && flag[len - 1] == '\n') {
        flag[len - 1] = '\0'; 
    }
    
    if (strlen(flag) != 29){
      exit(1);
    }

    for (int i = 0; i < 5; i++) {
        int encrypted_value = encrypted_values[i] - 32;
        int decrypted_value = (a_inverse * (encrypted_value - b)) % m;
        char expected_char = decrypted_value + 32; 

        if (flag[expected_indices[i]] != expected_char) {
            exit(1);
        }
    }

    exit(0);
}
