import serial.tools.list_ports
import time
class I2C_tool:




    def __init__(self):
        self.devices = []
        self.set_dev = None
        self.scm = False
        self.mem_addr_size_16bit = None
        self.port= None
        self.comport=None
        self.init_state = False
        self.error_messages = []
        self.dbg = False
        self.last_operation_status_code=None
        self.I2C_STATUS = {0: 'OK',
                      1: 'ERROR',
                      2: 'BUSY',
                      3: 'TIMEOUT'}
        self.I2C_STATE = {
                    '0x00': 'Peripheral is not yet Initialized',
                    '0x20': 'Peripheral Initialized and ready for use',
                    '0x24': 'An internal process is ongoing',
                    '0x21': 'Data Transmission process is ongoing',
                    '0x22': 'Data Reception process is ongoing',
                    '0x28': 'Address Listen Mode is ongoing',
                    '0x29': 'Address Listen Mode and Data Transmission process is ongoing',
                    '0x2A': 'Address Listen Mode and Data Reception process is ongoing',
                    '0x60': 'Abort user request ongoing',
                    '0xA0': 'Timeout state',
                    '0xE0': 'Error'
        }


        self.I2C_MEMADD_SIZE = {'8BIT': b'\x01',
                           '16BIT': b'\x10'}

        if self.device_search():
            self.port = serial.Serial(self.comport.device, 115200, timeout=0.1)
            self.swich_to_scm()
            if self.scm:
                self.init_state = True
                self.get_mem_addr_size()
                if self.mem_addr_size_16bit == None:
                    self.error_messages.append('Cant get Mem addr size')
        else:
            self.error_messages.append("I2C tool not found")


    def device_search(self):
        for p in serial.tools.list_ports.comports():
            if p.pid == 4805 and p.vid == 1156:
                self.comport = p
                return True
        self.init_state = False
        return False

    def print_dbg(self, *args, **kwargs):
        if self.dbg:
            print(*args, **kwargs)

    def inf(self):
        self.print_dbg(f"Port: {self.port} ")
        self.print_dbg(f"SCM: {self.scm} ")
        self.print_dbg(f"DEVICES: {self.devices} ")
        self.print_dbg(f"Mem 16bit addr size: {self.mem_addr_size_16bit} ")
        for msg in self.error_messages:
            self.print_dbg(f"Error: {msg} ")

    def write_nbytes(self, count, int_list):
        self.write([7] + [len(int_list)] + int_list)
        self.last_operation_status_code = int(self.read()[0])

    def read_nbytes(self, count):
        self.write([6, count])
        ret = self.read()
        self.last_operation_status_code = int(ret[0])
        return ret [1:]

    def write_reg_nbytes(self, reg_list, count, int_list):
        self.write([9]+reg_list+[count]+int_list)
        self.last_operation_status_code = int(self.read()[0])

    def read_reg_nbytes(self, reg_list, count):
        self.write([8]+reg_list+[count])
        ret = self.read()
        self.last_operation_status_code = int(ret[0])
        return ret [1:]

    def write(self, int_list):
        self.print_dbg(f"Write: {int_list}")
        self.port.write(bytearray(int_list))

    def read(self):
        ret = self.port.readline()
        self.print_dbg(f"Return: {ret} ")
        return ret

    def swich_to_scm(self):
        self.port.write(b'scm\r\n')
        for i in range(5):
            ret = self.read()
            if ret == b'scm!\r\n':
                self.scm = True
                self.read()#to remove last messages
                break

    def set_mem_addr_size(self, size):
        if size == '8BIT':
            self.write([3, 1])
        if size == '16BIT':
            self.write([3, 16])
        time.sleep(0.5)
        self.get_mem_addr_size()

    def get_status(self):
        return self.I2C_STATUS[self.last_operation_status_code]


    def get_mem_addr_size(self):
        self.write([4])
        ret = self.read()
        if ret == self.I2C_MEMADD_SIZE['8BIT']:
            self.mem_addr_size_16bit = False
        if ret == self.I2C_MEMADD_SIZE['16BIT']:
            self.mem_addr_size_16bit = True


    def scan(self):
        self.devices.clear()
        self.write([2])
        for dev in self.read():
            self.devices.append(dev)
        #print(f"devices: {self.devices}")

    def set_addr(self, dev):
        self.set_dev = dev
        self.write([1,dev])
        ret = self.read()
        if self.I2C_STATUS[int(ret[0])] == 'OK':
            self.set_dev = dev
        return self.I2C_STATUS[int(ret[0])]

