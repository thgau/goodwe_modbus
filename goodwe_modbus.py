import sys
import logging
import asyncio
import time
import concurrent.futures
import goodwe

from pymodbus.datastore import ModbusBaseSlaveContext
from pymodbus.datastore import ModbusServerContext
from pymodbus.server import StartAsyncTcpServer

class Entry:
    """ help class to define mapping between modbus and the udp api"""
    offset: int # modbus offset
    id_: str    # name in the api
    size_: int  # modbus size in halfwords
    factor: int # scaling factor to adjust between api and modbus

    def __init__(self, off, idstr, anz, f):
        self.offset = off
        self.id_ = idstr
        self.size = anz
        self.factor = f

class GoodweContext(ModbusBaseSlaveContext):
    """ the modbus api handler """

    map : tuple[Entry, ...] = (
        #grid
        Entry(36025, 'active_power_total', 2, 1), #int32
        Entry(36017, 'meter_e_total_imp', 2, 1), #float32

        # pv
        Entry(35105, 'ppv1', 2, 1), #uint32
        Entry(35109, 'ppv2', 2, 1), #uint32
        Entry(35113, 'ppv3', 2, 1), #uint32
        Entry(35117, 'ppv4', 2, 1), #uint32
        Entry(35191, 'e_total', 2, 1), #uint32

        #battery
        Entry(35183, 'pbattery1', 1, 1 ),  #int16
        Entry(37007, 'battery_soc', 1, 1 ),  #int16
        Entry(35209, 'e_bat_discharge_total', 2, 1 ),  #uint32

    )

    # needed for a async call from a sync method 
    pool = concurrent.futures.ThreadPoolExecutor()

    # timestamp of last call to goodwe
    last = 0.0

    def __init__(self):
        logging.debug("init")

    async def addInverter(self, ip_address):
        #print("addInverter")
        self.inverter = await goodwe.connect(ip_address)

    def findSensor(self, address) -> Entry:
        for e in self.map:
            if e.offset == address:
               return e

        log.error(f"offset {address} not found in mapping")
        raise ValueError()


    def reset(self):
        logging.debug("reset")

    def decode(self, fx):
         #print(f"decode {fx}")
         ModbusBaseSlaveContext.decode(self,fx)

    def validate(self, fx, address, count=1):
         logging.debug(f"validate {fx} {address} {count}")
         entry = self.findSensor(address)
         #print(entry.id_)
         return True

    def getValues(self, fx, address, count=1):
         logging.debug(f"getValues {fx} {address} {count}")
         entry = self.findSensor(address)
         #print(entry.id_)
         # avoid a round trip to goodwe for every single value
         if self.last < time.time() - 3:
             self.runtime_data = self.pool.submit(asyncio.run, self.inverter.read_runtime_data()).result()
             logging.debug ("new data fetched")
             self.last = time.time()
         if entry.id_ in self.runtime_data:
             value = self.runtime_data[entry.id_]
             logging.debug(f"{entry.id_} value: {value}")
             value = int(value) // entry.factor;
             if count == 1:
                value &= 0xffff
                #print(value)
                return [ value ]
             (a,b) = divmod( value, 65536)
             a &= 0xffff
             b &= 0xffff
             #print(f"{a},{b}")
             ret = [ a, b]
             #ret = int.to_bytes(int(value / entry.factor), length=2, byteorder="big", signed=True)
             #print(type(ret))
             #print(ret.hex('-'))
             return ret
         else:
            #print("does not exist")
            if count == 1:
                return [0]
            return [0, 0]

    def setValues(self, fx, address, values):
         logging.debug(f"setValues {fx} {address} {values}")

async def run_server(ip_address):
    store = GoodweContext()
    await store.addInverter(ip_address)
    #store.findSensor(36025)
    #store.getValues(3, 36025,2)
    context = ModbusServerContext(slaves=store, single=True)
    await StartAsyncTcpServer(context=context, address=("localhost", 8899))

if __name__ == "__main__":
    #logging.basicConfig( level=logging.DEBUG )
    if len(sys.argv) <= 1:
       print("argument <ip-address> missing")
    else:
      ip_address = sys.argv[1]
      logging.info(f"starting {ip_address}")
      asyncio.run(run_server(ip_address))
