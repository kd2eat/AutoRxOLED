import time
import datetime
from autorx.ozimux import OziUploader
from time import gmtime, localtime

dt = datetime.datetime(2019, 12, 29, 20, 03, 04, 79043)
gmt = gmtime()

ozimux = OziUploader(
    ozimux_port = None,
    payload_summary_port = 55673,
    update_rate = 5,
    station='KD2EAT')


packet = {
    'frame' : '1',
    'id' : '1',
    'datetime' : gmt,
    'lat' : 42.4417,
    'lon' : -76.4985,
    'alt' : 22345,
    'temp': 32,
    'type' : 'PAYLOAD_SUMMARY',
    'freq': '1678',
    'freq_float': 1678.0,
    'datetime_dt' : dt,
    }

_short_time = packet['datetime_dt'].strftime("%H:%M:%S")
ozimux.add(  packet )
print "Sent. sleeping 10 to avoid race condition where we shut down before sending the packet."
time.sleep(10)

ozimux.close()
print "Closed"

