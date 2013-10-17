#!/sbin/sh

# mount
	/sbin/busybox mount -o remount,rw / /;
	/sbin/busybox mount -o remount,rw /dev/block/stl9 /system;

# modules
/sbin/insmod /system/lib/modules/bcm_headsetsw.ko
/sbin/insmod /system/lib/modules/brcm_headsetsw.ko
/sbin/insmod /system/lib/modules/brcm-headsetsw.ko
/sbin/insmod /system/lib/modules/memalloc.ko
/sbin/insmod /system/lib/modules/hx170dec.ko
/sbin/insmod /system/lib/modules/h6270enc.ko
/sbin/insmod /system/lib/modules/gememalloc.ko    
/sbin/insmod /system/lib/modules/ge_drv.ko   
/sbin/insmod /system/lib/modules/brcm_switch.ko
/sbin/insmod /system/lib/modules/bcm_switch.ko


/sbin/busybox chmod 755 /sbin
/sbin/busybox chmod 755 /sbin/busybox

setprop boot.ready 1

exit 1
