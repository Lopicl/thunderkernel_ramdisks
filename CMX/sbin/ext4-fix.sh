#!/sbin/busybox sh

/sbin/busybox chmod 755 /sbin/tune2fs
/sbin/busybox chmod 755 /sbin/e2fsck
/sbin/busybox ln -s /sbin/busybox /sbin/grep
/sbin/busybox touch /etc/mtab

if [ "$(tune2fs -l /dev/block/mmcblk0p2 | grep huge_file)" != "" ]; then
    tune2fs -O ^huge_file /dev/block/mmcblk0p2
    e2fsck -pf /dev/block/mmcblk0p2
fi;
sync

if [ "$(tune2fs -l /dev/block/stl9 | grep huge_file)" != "" ]; then
    tune2fs -O ^huge_file /dev/block/stl9
    e2fsck -pf /dev/block/stl9
fi;
sync

if [ "$(tune2fs -l /dev/block/stl10 | grep huge_file)" != "" ]; then
    tune2fs -O ^huge_file /dev/block/stl10
    e2fsck -pf /dev/block/stl10
fi;
sync

if [ "$(tune2fs -l /dev/block/stl11 | grep huge_file)" != "" ]; then
    tune2fs -O ^huge_file /dev/block/stl11
    e2fsck -pf /dev/block/stl11
fi;
sync

if [ "$(tune2fs -l /dev/stl9 | grep huge_file)" != "" ]; then
    tune2fs -O ^huge_file /dev/stl9
    e2fsck -pf /dev/stl9
fi;
sync

if [ "$(tune2fs -l /dev/stl10 | grep huge_file)" != "" ]; then
    tune2fs -O ^huge_file /dev/stl10
    e2fsck -pf /dev/stl10
fi;
sync

if [ "$(tune2fs -l /dev/stl11 | grep huge_file)" != "" ]; then
    tune2fs -O ^huge_file /dev/stl11
    e2fsck -pf /dev/stl11
fi;
sync

/sbin/busybox rm -f /etc/mtab

exit 1
