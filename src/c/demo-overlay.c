#include <pebble.h>

#include "overlord.h"
#include "overlays.h"

#include "ovl1/ovl1.h"
#include "ovl2/ovl2.h"

int main(void) {

  // load overlay 1
  APP_LOG(0, "Overlay %d loaded", overlay_load(OVL1_OVL));
  // call function from overlay 1
  APP_LOG(0, "number %d", foo(100));

  // load overlay 2
  APP_LOG(0, "Overlay %d loaded", overlay_load(OVL2_OVL));
  // call function from overlay 2
  APP_LOG(0, "number %d", bar());

  app_event_loop();
}
