#include <pebble.h>
#include "overlays.h"

#include "pebble_process_info.h"
extern const PebbleProcessInfo __pbl_app_info;

extern unsigned long _ovly_table[][2];

static uint8_t * OVL_P = NULL;
static uint16_t s_current_ovl = -1;

void overlay_init()
{
	APP_LOG(APP_LOG_LEVEL_INFO, "App: %s Version %d.%d size:%d", __pbl_app_info.name, __pbl_app_info.process_version.major, __pbl_app_info.process_version.minor, __pbl_app_info.load_size);
	OVL_P = (void *) & __pbl_app_info;
	OVL_P+=0x82+0x26;
}

uint16_t overlay_load(uint16_t overlay_id)
{
	if (OVL_P && overlay_id < NUM_OVERLAYS && s_current_ovl != overlay_id){
		size_t size = resource_load_byte_range(resource_get_handle(RESOURCE_ID_OVL_FULL), _ovly_table[overlay_id][0], OVL_P, _ovly_table[overlay_id][1]);
		APP_LOG(APP_LOG_LEVEL_INFO, "app:%d size:%d",overlay_id, size);
		s_current_ovl = overlay_id;
	} 
	return s_current_ovl;
}