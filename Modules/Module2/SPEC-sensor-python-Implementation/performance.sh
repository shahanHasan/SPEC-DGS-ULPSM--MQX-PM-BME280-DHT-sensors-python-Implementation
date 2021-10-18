#!/bin/sh
# performance.sh

###clock speed / frequency
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq
###Returns the throttled state of the system. This is a bit pattern - a bit being set
vcgencmd get_throttled
vcgencmd measure_temp
vcgencmd measure_clock arm
vcgencmd measure_clock core
vcgencmd measure_volts core
vcgencmd measure_volts sdram_c
vcgencmd measure_volts sdram_i
vcgencmd measure_volts sdram_p