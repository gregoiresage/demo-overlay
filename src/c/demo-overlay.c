#include <pebble.h>

#include "overlord.h"
#include "overlays.h"

#include "ovl1/ovl1.h"
#include "ovl2/ovl2.h"
#include "ovl3/ovl3.h"
#include "ovl4/ovl4.h"

#define DEMO_NUM_MENU_SECTIONS 1

static Window *window;

static SimpleMenuLayer *simple_menu_layer;
static SimpleMenuSection menu_sections[DEMO_NUM_MENU_SECTIONS];
static SimpleMenuItem apps_menu_items[NUM_OVERLAYS];

static void menu_app_select_callback(int index, void *ctx) {
  overlay_load(index);
  switch(index){
    case OVL1_OVL : feature_stdlib_push(); break;
    case OVL2_OVL : app_font_browser_push(); break;
    case OVL3_OVL : show_ovl3(); break;
    case OVL4_OVL : show_ovl4(); break;
  }
}

// This initializes the menu upon window load
static void window_load(Window *window) {
  apps_menu_items[0] = (SimpleMenuItem){
      .title = "Overlay 0",
      .callback = menu_app_select_callback,
    };
  apps_menu_items[1] = (SimpleMenuItem){
      .title = "Overlay 1",
      .callback = menu_app_select_callback,
    };
  apps_menu_items[2] = (SimpleMenuItem){
      .title = "Overlay 2",
      .callback = menu_app_select_callback,
    };
  apps_menu_items[3] = (SimpleMenuItem){
      .title = "Overlay 3",
      .callback = menu_app_select_callback,
    };

  menu_sections[0] = (SimpleMenuSection){
    .num_items = NUM_OVERLAYS,
    .items = apps_menu_items,
    .title = "Demos"
  };

  Layer *window_layer = window_get_root_layer(window);
  GRect bounds = layer_get_frame(window_layer);
  simple_menu_layer = simple_menu_layer_create(bounds, window, menu_sections, DEMO_NUM_MENU_SECTIONS, NULL);
  layer_add_child(window_layer, simple_menu_layer_get_layer(simple_menu_layer));
}

static void window_unload(Window *window) {
  simple_menu_layer_destroy(simple_menu_layer);
}

int main(void) {
  window = window_create();

  window_set_window_handlers(window, (WindowHandlers) {
    .load = window_load,
    .unload = window_unload,
  });

  window_stack_push(window, true);

  app_event_loop();

  window_destroy(window);
}