#include <pebble.h>

static uint8_t hhhh[20000];

int bar(){
	int res = 0;
	for(int i=0; i<20000; i++){
		hhhh[i] = time(NULL);
		res += hhhh[i];
	}
	return res;
}