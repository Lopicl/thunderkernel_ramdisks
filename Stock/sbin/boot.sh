#!/sbin/sh

# ThunderKernel Boot setup script
# Based on kissingmylove cyanus.sh
# Modded by Lopicl.00 @ XDA-Developers for ThunderKernel

# chmod
/sbin/busybox chmod -R 755 /sbin

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

# su binary install
if
  /sbin/busybox test -e /system/xbin/su
then
  /sbin/busybox echo "Su binary already installed."
else
  /sbin/busybox echo "Su binary not installed, gonna install it..."
  /sbin/busybox cp /sbin/su-bin /system/xbin/su
  /sbin/busybox chmod 4755 /system/xbin/su
  /sbin/busybox ln -s /system/xbin/su /system/bin/su
  /sbin/busybox echo "Binary installed!!!"
fi

setprop boot.ready 1

exit 1
