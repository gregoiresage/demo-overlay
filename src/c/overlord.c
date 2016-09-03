#include <pebble.h>
#include "overlays.h"

#include "pebble_process_info.h"
extern const PebbleProcessInfo __pbl_app_info;

extern uint32_t _ovly_table[][2]; // values set in the ldscript

static uint8_t *s_pbl_app_info_address = NULL; // can't use &__pbl_app_info directly... don't know why
static uint16_t s_current_ovl = -1;

uint16_t overlay_load(uint16_t overlay_id)
{	
	// APP_LOG(APP_LOG_LEVEL_INFO, "App: %s Version %d.%d size:%d", __pbl_app_info.name, __pbl_app_info.process_version.major, __pbl_app_info.process_version.minor, __pbl_app_info.load_size);
	if (overlay_id < NUM_OVERLAYS && s_current_ovl != overlay_id){
		if(s_pbl_app_info_address == NULL){
			s_pbl_app_info_address = (uint8_t *)&__pbl_app_info;
		}
		size_t size = resource_load_byte_range(
			resource_get_handle(RESOURCE_ID_OVL_FULL), 
			_ovly_table[overlay_id][0], 
			s_pbl_app_info_address + 0x82 + 0x26, // size of .header + size of .note.gnu.build-id
			_ovly_table[overlay_id][1]);
		if(size == _ovly_table[overlay_id][1]){
			APP_LOG(APP_LOG_LEVEL_INFO, "app:%d size:%d",overlay_id, size);
			s_current_ovl = overlay_id;
		}
	} 
	return s_current_ovl;
}
