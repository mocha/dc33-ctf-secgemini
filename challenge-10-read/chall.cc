#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <sys/random.h>

const char *WORDS[50] = {
  "algorithm", "application", "ai", "backup", "binary", "bit", "browser", "bug",
  "byte", "cache", "cpu", "cloud", "coding", "compiler", "computer", "data",
  "database", "debug", "desktop", "device", "digital", "download", "drive",
  "file", "firewall", "folder", "hardware", "hdd", "html", "internet", "input",
  "interface", "keyboard", "laptop", "malware", "memory", "mouse", "network",
  "os", "output", "password", "peripheral", "processor", "program",
  "programmer", "ram", "software", "storage", "system", "virus"
};

static uint8_t g_hash_init;

static uint8_t hash(const char *s) {
  uint8_t v = g_hash_init;
  size_t sz = strlen(s);
  for (size_t i = 0; i < sz; i++) {
    v ^= s[i];
  }
  return v;
}

class HashNode {
 public:
  HashNode *next = nullptr;
  char key[16]{};
  char data[64]{};

  void set(const char *key, const char *data) {
    strlcpy(this->key, key, sizeof(this->key));
    strlcpy(this->data, data, sizeof(this->data));
  }

  uint8_t get_hash() {
    return hash(key);
  }

  HashNode(const char *key, const char *data) {
    set(key, data);
  }
};

class HashList {
 public:
  HashNode *buckets[8]{};

  void add(const char *key, const char *data) {
    HashNode *node = new HashNode(key, data);

    uint8_t idx = node->get_hash() & 0x7;
#ifdef DEBUG_BUILD
    printf("[DEBUG] idx=%i key=%s\n", idx, node->key);
#endif
    node->next = buckets[idx];
    buckets[idx] = node;
  }

  const char *get(const char *key) const {
    uint8_t idx = hash(key) & 0x7;
    HashNode *n = buckets[idx];

    while (n) {
      if (strcmp(key, n->key) == 0) {
        return n->data;
      }
      n = n->next;
    }

    return nullptr;
  }
};

void banner() {
  puts("Welcome to the DATABASE 7.53!");
}

void get_value_from_database(const HashList& hl) {
  puts("Enter key to fetch:");

  char line[16]{};
  if (fgets(line, 16, stdin) == nullptr) {
    return;
  }

  char key[16]{};
  if (sscanf(line, "%15[^\n]", key) != 1) {
    puts("Error: Empty key?");
    return;
  }

  if (strcmp(key, "flag") == 0) {
    puts("Error: Nope, no flag for you.");
    return;
  }

  const char *v = hl.get(key);
  if (v == nullptr) {
    puts("Error: Key not found.");
    return;
  }

  printf("Data: %s\n", v);
}

void get_price_estimate() {
  long pricing[16] = { 1, 1, 2, 3, 4, 5, 5, 6, 7, 7, 7, 7, 7, 8, 8, 8 };

  puts(
    "Thank you for considering our services!\n"
    "How many keys do you think you would store (0-15)?"
  );

  char line[32]{};
  if (fgets(line, 32, stdin) == nullptr) {
    return;
  }

  long key_number{};
  if (sscanf(line, "%ld", &key_number) != 1) {
    puts("Error: Invalid number of keys.");
    return;
  }

  if (key_number > 15) {
    puts("Sorry, our databases can't handle that many keys yet.");
    return;
  }

  printf(
    "Approximate price for %ld keys would be %ld Solarian Credits\n",
    key_number, pricing[key_number]
  );
}

bool menu(const HashList& hl) {
  puts(
    "Menu:\n"
    "  1  Get value from database\n"
    "  2  Get price estimate\n"
    "  3  Quit\n"
    "Choice?"
  );

  char line[16]{};
  if (fgets(line, 16, stdin) == nullptr) {
    return false;
  }

  int choice;
  if (sscanf(line, "%i", &choice) != 1 ||
      choice < 1 || choice > 3) {
    puts("Invalid option, try again.");
    return true;
  }

  switch (choice) {
    case 1: get_value_from_database(hl); return true;
    case 2: get_price_estimate(); return true;
  }

  return false;
}

int main() {
  setbuf(stdout, NULL);
  getrandom(&g_hash_init, 1, GRND_NONBLOCK);

  FILE *f = fopen("flag.txt", "rb");
  if (f == nullptr) {
    puts("TASK ERROR, NOTIFY CTF ADMIN");
    return 1;
  }

  char flag[64]{};
  fread(flag, 1, 64, f);
  fclose(f);

  HashList hl;
  hl.add("flag", flag);
  memset(flag, 0xff, sizeof(flag));

  for (int i = 0; i < 50; i++) {
    hl.add(WORDS[i], "Not a flag.");
  }

  banner();
  while (menu(hl));
  puts("Bye!");
}
