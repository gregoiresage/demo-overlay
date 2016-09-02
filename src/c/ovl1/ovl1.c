#include <pebble.h>

static uint8_t gggg[20000];

int foo(int i){
	int res = 0;
	for(int i=0; i<20000; i++){
		gggg[i] = time(NULL);
		res += gggg[i];
	}
	APP_LOG(0, "HELLO1");
	return res + i;
}