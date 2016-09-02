ENTRY(main)

MEMORY
{
  STRT (rwx) : ORIGIN = $STRT_ORIGIN, LENGTH = $STRT_LENGTH
  APP (rwx) : ORIGIN = $APP_ORIGIN, LENGTH = $APP_LENGTH
}

SECTIONS
{
	.header :
	{
		KEEP(*(.pbl_header))
	} > STRT

	/* -- DO NOT ADD ANY NEW SECTIONS HERE AND DO NOT CHANGE THE ALIGNMENT -- */
    /* The GNU build ID is tacked to the end of the PebbleProcessInfo struct: */
    .note.gnu.build-id ALIGN(1) : {
        PROVIDE(BUILD_ID = .);
        KEEP(*(.note.gnu.build-id))
    } > STRT

	OVERLAY : NOCROSSREFS AT ($OVERLAY_AT)
	{
$OVL_CONTENT
	} > STRT

	.text2 : 
	{
		*(.text)
		*(.text.*)
		*(.rodata)
		*(.rodata*)
	} > APP

	.data :
	{
		KEEP(*(.data))
		*(.data.*)
		_ovly_table = .; 
$OVL_TABLE
			
	} > APP

	.bss :
	{
		*(.bss)
		*(.bss.*)
	} > APP

	DISCARD :
	{
		libc.a ( * )
		libm.a ( * )
		libgcc.a ( * )
		*(.eh_frame)
	}
}