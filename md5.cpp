#include <cctype>
#include <iostream>
#include <openssl/md5.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>

const char charset[] = "0123456789abcdefghijklmnopqrstuvwxyz";
extern "C" int md5_compute(char *str, unsigned long long difficulty) {
  MD5_CTX c;
  union {
    unsigned char digest[16];
    unsigned long long guard[4];
  };
  MD5_Init(&c);
  MD5_Update(&c, str, 96);
  int count = 1 << 20;
  int seed;
  timeval t;
  gettimeofday(&t, NULL);
  srand(t.tv_usec + (t.tv_sec << 6));
  str[96] = '.';
  while (count-- > 0) {
    MD5_CTX c_copy = c;
    for (int i = 97; i < 120; ++i) {
      // fill nouce with random data
      str[i] = charset[rand() % 32];
    }
    MD5_Update(&c_copy, str + 96, 24);
    MD5_Final(digest, &c_copy);
    unsigned long long current = htobe64(guard[0]);
    if (current < difficulty) {
      return 1;
    }
    // std::cerr << current << "*" << difficulty << std::endl;
  }
  return 0;
}

extern "C" void md5(unsigned char *digest, const char *str) {
  MD5_CTX c;
  MD5_Init(&c);
  MD5_Update(&c, str, 96);
  MD5_Update(&c, str + 96, 24);
  MD5_Final(digest, &c);
  for (int i = 30; i >= 0; i -= 2) {
    digest[i+1] = charset[digest[i/2] >> 4];
    digest[i] = charset[digest[i/2] & 0xF];
  }
}