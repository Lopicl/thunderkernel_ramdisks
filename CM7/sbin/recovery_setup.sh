#!/sbin/sh

# ThunderKernel Recovery setup script
# Based on kissingmylove cyanus_recovery.sh
# Modded by Lopicl.00 @ XDA-Developers for ThunderKernel

/sbin/busybox chmod -R 755 /sbin
/sbin/busybox chmod 755 /res/recovery.fstab

# make some folder
/sbin/busybox mkdir /etc
/sbin/busybox mkdir /sd-ext

# symlinking fstab file
/sbin/busybox ln -s /res/recovery.fstab /sbin/recovery.fstab
/sbin/busybox ln -s /res/recovery.fstab /etc/recovery.fstab

# Unlock BML partition
/sbin/bmlunlock

# Mounting /data
/sbin/busybox mount /data
# Unmounting /data
/sbin/busybox umount /data

# Final things
/sbin/busybox rm /cache/recovery/command
/sbin/busybox rm /cache/update.zip
/sbin/busybox touch /tmp/.ignorebootmessage

setprop recovery.ready 1 

exit 1
