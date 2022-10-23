import time

import dht
import network
import ntptime
from machine import Pin, Timer
from utime import sleep

from rotary_irq import RotaryIRQ
from tm1637 import TM1637

LOADING_CHARS = [
    [0b00000001, 0x00, 0x00, 0x00],
    [0x00, 0b00000001, 0x00, 0x00],
    [0x00, 0x00, 0b00000001, 0x00],
    [0x00, 0x00, 0x00, 0b00000001],
    [0x00, 0x00, 0x00, 0b00000010],
    [0x00, 0x00, 0x00, 0b00000100],
    [0x00, 0x00, 0x00, 0b00001000],
    [0x00, 0x00, 0b00001000, 0x00],
    [0x00, 0b00001000, 0x00, 0x00],
    [0b00001000, 0x00, 0x00, 0x00],
    [0b00010000, 0x00, 0x00, 0x00],
    [0b00100000, 0x00, 0x00, 0x00],
]

tm = TM1637(clk=Pin(26), dio=Pin(27), brightness=5)
tm.numbers(88, 88)
time.sleep(0.2)
tm.show("")

# Rotary encoder, for setting the operation mode
rotary = RotaryIRQ(
    pin_num_clk=23,
    pin_num_dt=22,
    min_val=0,
    max_val=2,
    reverse=False,
    range_mode=RotaryIRQ.RANGE_WRAP,
    pull_up=False,
    half_step=False,
    invert=False,
)

# DHT sensor for temperature and humidity
dht_sensor = dht.DHT11(Pin(2))
temperature = 0
humidity = 0
try:
    dht_sensor.measure()
    temperature = dht_sensor.temperature()
    humidity = dht_sensor.humidity()
except OSError:
    tm.show("err0")
    sleep(5)

mode = 0

hour = 0
minute = 0
second = 0
colon = True


def is_daylight_saving_time(day, month, dow):
    # January, february, and december are out.
    if month < 3 or month > 11:
        return False
    # April to October are in
    if month > 3 and month < 11:
        return True

    previousSunday = day - dow
    # In march, we are DST if our previous sunday was on or after the 8th.
    if month == 3:
        return previousSunday >= 8
    # In november we must be before the first sunday to be dst.
    # That means the previous sunday must be before the 1st.
    return previousSunday <= 0


def update_time(t):
    global colon

    colon = not colon


def update_temp(t):
    global temperature
    global humidity
    dht_sensor.measure()
    temperature = dht_sensor.temperature()
    humidity = dht_sensor.humidity()


def update_mode():
    global mode
    new_value = rotary.value()
    mode = new_value if new_value is not None else mode


rotary.add_listener(update_mode)

timer_time = Timer(0)
timer_time.init(period=1000, mode=Timer.PERIODIC, callback=update_time)

timer_temp = Timer(1)
timer_temp.init(period=60000, mode=Timer.PERIODIC, callback=update_temp)


def cycle(iterable):
    # cycle('ABCD') --> A B C D A B C D A B C D ...
    saved = []
    for element in iterable:
        yield element
        saved.append(element)
    while saved:
        for element in saved:
            yield element


loading_iter = cycle(LOADING_CHARS)

# enable station interface and connect to WiFi access point
with open("secrets.txt", "r") as f:
    SSID, PASS = f.readline().split(",")

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    wlan.active(True)
    wlan.connect(SSID, PASS)
    while not wlan.isconnected():
        tm.write(next(loading_iter))
        time.sleep(0.2)


# if needed, overwrite default time server
ntptime.host = "1.europe.pool.ntp.org"

no_time = True
while no_time:
    try:
        ntptime.settime()
        no_time = False
    except:
        tm.show("err1")

wlan.disconnect()

t = time.localtime()
day = t[2]
month = t[1]
dow = t[6]

UTC_OFFSET = 1 * 60 * 60
DST_OFFSET = 1 if is_daylight_saving_time(day, month, dow) else 0

while True:
    if mode == 0:
        h, m = time.localtime(time.time() + UTC_OFFSET)[3:5]
        tm.numbers(h + DST_OFFSET, m, colon)

    elif mode == 1:
        tm.temperature(temperature)
    elif mode == 2:
        string = tm.encode_string("{0: >2d}".format(humidity))
        tm.write(string)
        tm.write([0x63, 0x5C], 2)

    sleep(0.2)
