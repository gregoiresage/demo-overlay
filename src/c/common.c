#include <pebble.h>

void send_tuple(const Tuplet t){
	if(t.type == TUPLE_CSTRING){
		APP_LOG(0, "%p %p %p", &t, &t.cstring, t.cstring.data);
		APP_LOG(0, "%s", t.cstring.data);
	}
	if(t.type == TUPLE_UINT) {
		APP_LOG(0, "%p %ld", &t, t.integer.storage);
	}
	if(t.type == TUPLE_INT) {
		APP_LOG(0, "%p %ld", &t, t.integer.storage);
	}
}
