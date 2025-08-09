#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>

// bump allocator.
uint8_t *bump_ptr;

void* malloc(size_t sz) {
  void *tmp = bump_ptr;
  sz = (sz + 15) & ~0xfULL; // alignment to 16 bytes.
  bump_ptr += sz;
  return tmp;
}

void free(void* ptr) {
  // do nothing, there's no free in bump allocs.
  (void)ptr;
}

typedef struct note_t {
  uint8_t buffer[1];
} note_t;

note_t* notes[128];
int note_sz[128];

void setup() {
  setbuf(stdin, NULL);
  setbuf(stdout, NULL);
  setbuf(stderr, NULL);
}

int menu() {
  puts("1. make a new note");
  puts("2. write to a note");
  puts("3. read from a note");
  puts("4. destroy a note");
  puts("5. exit");
  puts("what do you want to do?");

  int choice = 0;
  scanf("%d", &choice);
  getchar();

  return choice;
}

void win() {
  FILE* flag = fopen("flag", "rb");

  if (flag == NULL) {
    puts("flag missing - contact admin!");
    return;
  }

  char buffer[128];
  fread(buffer, 1, 128, flag);
  fclose(flag);

  puts(buffer);
}

void note_create() {
  int idx = -1;
  for (int i = 0; i < 128; i++) {
    if (notes[i] == NULL) {
      idx = i;
      break;
    }
  }

  if (idx == -1) {
    puts("no more notes allowed!");
    return;
  }

  puts("how big should the note be? choose from 1 to 1024 bytes.");

  int sz = 64;
  scanf("%d", &sz);
  getchar();

  if (sz < 1 || sz > 1024) {
    puts("invalid size!");
    return;
  }

  note_t* note = (note_t*)malloc(sz);

  notes[idx] = note;
  note_sz[idx] = sz;

  printf("allocated %d bytes at index %d\n", sz, idx);
}

void note_write() {
  puts("which note do you want to write to?");

  int idx = -1;
  scanf("%d", &idx);
  getchar();

  if (idx < 0 || idx >= 128) {
    puts("invalid index!");
    return;
  }

  note_t* note = notes[idx];

  if (note == NULL) {
    puts("note at this index not created yet!");
    return;
  }

  puts("what do you want to write?");

  int sz = note_sz[idx];

  fgets(note->buffer, sz, stdin);
}

void note_read() {
  puts("which note do you want to read from?");

  int idx = -1;
  scanf("%d", &idx);
  getchar();

  if (idx < 0 || idx >= 128) {
    puts("invalid index!");
    return;
  }

  note_t* note = notes[idx];

  if (note == NULL) {
    puts("note at this index not created yet!");
    return;
  }

  puts(note->buffer);
}

void note_destroy() {
  puts("which note do you want to destroy?");

  int idx = -1;
  scanf("%d", &idx);
  getchar();

  if (idx < 0 || idx >= 128) {
    puts("invalid index!");
    return;
  }

  note_t* note = notes[idx];

  if (note == NULL) {
    puts("note at this index not created yet!");
    return;
  }

  free(note);

  notes[idx] = NULL;
  notes[idx] = 0;
}

int main(int argc, char *argv[]) {
  setup();

  uint8_t buffer[64 * 1024] = {}; // 64KB should be enough.
  bump_ptr = buffer;

  for ( ; ; ) {
    switch (menu()) {
      case 1:
      {
        note_create();
        continue;
      }
      case 2:
      {
        note_write();
        continue;
      }
      case 3:
      {
        note_read();
        continue;
      }
      case 4:
      {
        note_destroy();
        continue;
      }
    }

    puts("bye");
    break;
  }

  return 0;
}
