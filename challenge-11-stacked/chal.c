#include <stdlib.h>
#include <stdio.h>

void vuln() {
  char buf[128];
  printf("buf: %p\n", buf);
  fgets(buf, 0x128, stdin);
}

void setup() {
  setbuf(stdin, NULL);
  setbuf(stdout, NULL);
  setbuf(stderr, NULL);
}

int main(int argc, char *argv[]) {
  setup();
  vuln();
  return 0;
}
