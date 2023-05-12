# goodwe_modbus
Bridge for GoodWe ET between EVCC modbus protocol and GoodWe WiFi access procotol 

# Summary
I want to connect [EVCC](https://github.com/evcc-io/evcc) with my GoodWe inverter, but the GoodWe does not support the modbus protocol with its WiFi adapter.

The GoodWe inverter talks UDP on port 8899 as used by the smartphone app, and I can access it with the python library [GoodWe](https://github.com/marcelblijleven/goodwe).

So I created a small bridge which serves as modbus server and fetches the needed information from the GoodWe via the this library.

For the modbus protocol I use the library from [pymodbus](https://github.com/pymodbus-dev/pymodbus)

# Installation
Install goodwe `pip install goodwe` and the pymodbus `pip install -U pymodbus` (as described on their pages)
To test, if the UDP port works, run the sample program as described in [GoodWe](https://github.com/marcelblijleven/goodwe)

Download the goodwe_modbus.py from this repository and run `phyton goodwe_modbus.py <ip-address of your goodwe>`

Edit your evcc.yaml file and replace
```
  template: goodwe-hybrid
  modbus: tcpip
  host: <ip-address of the goodwe>
  port: 502
```
with 
```
  template: goodwe-hybrid
  modbus: tcpip
  host: localhost
  port: 8899
```

If all works you can run the program as service. Download goodwe_modbus.service and adopt to your username and file location and store it as /etc/systemd/system/goodwe_modbus.service.
Enable automatic start after reboot with `sudo systemctl enable goodwe_modbus` and immediate start with `sudo systemctl start goodwe_modbus`

# Limitations
Currently only the few modbus registers needed by EVCC [goodwe-hybrid.yaml](https://github.com/evcc-io/evcc/blob/master/templates/definition/meter/goodwe-hybrid.yaml) are supported.
To add more registers, look up the name in the [GoodWe Spec](https://github.com/evcc-io/evcc/files/10417348/Goodwe_Modbus_Protocol_Hybrid_ET_EH_BH_BT__ARM205.HV__V1.7._.Read.Only_20200226.1.pdf) and find the corresponding name in the [GoodWe libarary](https://github.com/marcelblijleven/goodwe/blob/master/goodwe/et.py). You will notice that the lists are very similar but not identical. Then add the missing register as Entry in goodwe_modbus.py
