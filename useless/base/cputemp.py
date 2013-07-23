import time
import subprocess

def set_cpu_max_speed(speed):
    cmd = ['sudo', 'cpufreq-set', '--max', speed]
    subprocess.check_call(cmd)

def get_temperature(device='temp1', hwmon='hwmon0'):
    filename = '/sys/class/hwmon/%s/%s_input' % (hwmon, device)
    contents = file(filename).read().strip()
    degC = int(contents) / 1000
    return degC


# FIXME: no hardcoded speeds
def set_speed_per_temperature(hot, cold_enough, hwmon, devices,
                              speed='unset'):
    is_hot = False
    top_temp = 0
    for device in devices:
        degC = get_temperature(device=device, hwmon=hwmon)
        if degC > hot:
            is_hot = True
        if degC > top_temp:
            top_temp = degC
    prior_speed = speed
    if is_hot:
        # go slow
        speed = '800M'
    elif top_temp < cold_enough:
        # go fast
        speed = '2G'
    else:
        # go medium
        speed = '1.6G'
    if speed != prior_speed:
        set_cpu_max_speed(speed)
    return speed

def keep_cool():
    while True:
        speed = set_speed_per_temperature(args)
        time.sleep(1)
        
