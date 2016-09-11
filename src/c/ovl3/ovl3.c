#include <pebble.h>

#include "../common.h"

void show_ovl3(void) {
	Tuplet t = TupletCString(103, "PIN");
	send_tuple(t);
	// send_tuple(TupletCString(103, "PIN")); // craching... don't know why yet
}
