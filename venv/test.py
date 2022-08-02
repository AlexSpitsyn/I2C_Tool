import serial
import serial.tools.list_ports
from tkinter import *
from tkinter import ttk
import time



window_height = 800
window_width = 800


class I2C_tool:
    I2C_STATUS = {b'\x00':'OK',
                  b'\x01':'ERROR',
                  b'\x02':'BUSY',
                  b'\x03':'TIMEOUT'}

    I2C_MEMADD_SIZE = {'8BIT':b'\x01',
                        '16BIT':b'\x10'}

    def __init__(self):
        self.devices = []
        self.set_dev = None
        self.scm = False
        self.mem_addr_size = None
        ports = serial.tools.list_ports.comports()

        for p in ports:
            if p.pid == 4805 and p.vid == 1156:
                # print('PID',port.pid)#4805
                # print('VID', port.vid)#1156
                # print(port.device)  # 1156
                self.port = serial.Serial(p.device, 115200, timeout=1)
                self.swich_to_scm()
                if self.scm:
                    self.get_mem_addr_size()
                    if self.mem_addr_size == None:
                        print('Cant get Mem addr size')
                break
            else:
                self.port = None
        if self.port is None:
            print("I2C tool not found")

    def inf(self):
        print(f"Port: {self.port} ")
        print(f"SCM: {self.scm} ")
        print(f"DEVICES: {self.devices} ")
        print(f"Mem Size: {self.mem_addr_size} ")

    def write(self, int_list):
        #print(int_list, bytearray(int_list))
        self.port.write(bytearray(int_list))

    def read(self):
        return self.port.readline()

    def swich_to_scm(self):
        self.port.write(b'scm\r\n')
        for i in range(5):
            ret = self.read()
            if ret == b'scm!\r\n':
                self.scm = True
                self.read()#to remove last messages
                break

    def get_mem_addr_size(self):
        self.write([33])
        ret = self.read()
        print(ret)
        if ret == self.I2C_MEMADD_SIZE['8BIT']:
            self.mem_addr_size = False
        if ret == self.I2C_MEMADD_SIZE['16BIT']:
            self.mem_addr_size = True


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
        if self.I2C_STATUS[ret] == 'OK':
            self.set_dev = dev
        return self.I2C_STATUS[ret]


def print_bytes(bts):
    if bts == b'':
        return
    l = len(bts)
    print(f'Lenght: {l}')
    #print(dpg.get_value(cb_hex), dpg.get_value(cb_char), dpg.get_value(cb_dec))
    h = dpg.get_value(cb_hex)
    c = dpg.get_value(cb_char)
    d = dpg.get_value(cb_dec)

    #print_log_line('\t00 01 02 03 04 05 06 07 | 01234567')
    msg=''
    chr_str=''
    hex_str=''
    dec_str=''
    header='\t'
    cnt=4
    if h:
        header = header + '00 01 02 03 04 05 06 07 | '
        cnt+=25
    if c:
        header = header + '01234567 | '
        cnt += 10
    if d:
        header = header + ' 0   1   2   3   4   5   6   7  '
        cnt += 33
    if h or c or d:
        print_log_line(header.strip(' | '))
        print_log_line(''.ljust(cnt,'-'))
    i=0
    line=0
    for b in bts:
        chr_str = chr_str + chr(b)
        hex_str = hex_str + str(chr(b).encode('utf-8').hex()) + ' '
        dec_str = dec_str + str(int(b)).rjust(3,'0') + ' '
        i+=1
        print(chr(b).encode('utf-8').hex(), chr(b) , str(int(b)).rjust(3,'0'))
        if i%8==0:
            msg=str(chr(line).encode('utf-8').hex()) + ': '
            if h:
                msg = msg + hex_str.strip() + ' | '
            if c:
                msg = msg + chr_str + ' | '
            if d:
                msg = msg + dec_str + ' | '
            print_log_line(msg.strip(' | '))
            chr_str = ''
            hex_str = ''
            line+=1
            l-=8
    if l:
        if h or c or d:
            msg = str(chr(line).encode('utf-8').hex()) + ': '
        if h:
            msg = msg + hex_str.ljust(23) + ' | '
        if c:
            msg = msg + chr_str.ljust(8) + ' | '
        if d:
            msg = msg + dec_str.ljust(32) + ' | '
        print_log_line(msg.strip(' | '))

def str_to_bytes(s):
    byte_s = bytearray(len(s))
    i = 0
    for c in s:
        byte_s[i] = int(c.encode('utf-8').hex(), 16)
        i = i + 1
    return byte_s

def int_to_bytes(int_list):
    byte_s = bytes(len(s))
    i = 0
    for c in s:
        byte_s[i] = int(c.encode('utf-8').hex(), 16)
        i = i + 1
    print(byte_msg)

#print(serial.to_bytes(cmd['scan']))
#print((cmd['scan']).to_bytes(1, 'big'))

        #com.write(b'scm\r\n')
        #print(com.readline())
        #time.sleep(3)
        #com.write(b'\x02')

        #com.write((2).to_bytes(1, byteorder='big'))

        #a = com.readline()
# a=b'QD'
# print(int.from_bytes(a, 'big'))
# for i in a:
#     print(int(i))



#tool = I2C_tool()
#tool.swich_to_scm()
#tool.inf()


b= 7
d = [1,2,1]
d+=[b]
print(d)




# for c in int_s:
#     print(int(c.encode('utf-8').hex(), 16))




# str
# for c in s:
#     print(c, c.encode('utf-8'), c.encode('utf-8').hex(), int(c.encode('utf-8').hex(),16), bytes(c, 'utf-8'))

# int
# print(i, bytes([i]), hex(i))
# cmd[0]=int(hex(i), 16)
# print(cmd)

#for i in int_list:
#    bts2 = bytearray()

# n=257
#
# print((n).to_bytes(2,'big'))
# print(n//255)
# print(bytes([n//256, n%256]))



# bts = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x00\x31\xAB'
# print(f'hex: {bts[1]}', hex(bts[1]), bin(bts[1]))

# print(int(bts[11]))
#
# for c in range(len(bts)):
#     print(bts.hex()[c*2:c*2+2])

# bts_s= bts.decode("utf-8")
# print(bts_s)


# s=''
# print(s)
# for i in range(len(bts)):
#     #print(int(i))
#     if int(bts[i])>122 or int(bts[i])<32:
#         s+='.'
#     else:
#         s+=chr(int(bts[i]))






    #print(chr(b).encode('utf-8').hex(), chr(b), str(int(b)).rjust(3, '0'))
#str_to_bytes(s)

#bts
#print(str(bts))
# for b in bts:
#     #print(chr(b))
#     print(str(b).rjust(3,'0'))



#cmd=bytearray(len(s))
# print(f">>> {bytes(str(i), 'utf-8')+d}")
# print(hex(int.from_bytes(d, 'big')))
# print (i.to_bytes(1, 'big'))
# print (bytearray.fromhex(str(i)))

#index = d.index(b'\x51')
#index = d.index(int(h,0))
# int.from_bytes(a, 'big')
#print(index)

# tool.swich_to_scm()
#
# tool.scan()
# tool.inf()
exit()






def Scan_btn_click():
    tool.scan()
    l=[]
    for i in tool.devices:
        l.append(hex(i))
    combo_i2c_dev_sel['values']=l
    #combo_i2c_dev_sel['values'] = tool.devices


def combo_i2c_dev_select():
    print(combo_i2c_dev_sel.get())

def select_i2c_device(event):
    tool.set_addr(tool.devices.index(int(combo_i2c_dev_sel.get(),0)))


window = Tk()
window.title("I2C Scanner")
window.geometry(str(window_height)+'x'+str(window_width))
window.minsize(window_height,window_width)
window.maxsize(window_height,window_width)

frame_status = Frame(window, relief=RIDGE)
frame_top = LabelFrame(window, relief=RIDGE)
frame_bot = LabelFrame(window, relief=RIDGE)

frame_status.grid(column=0, row=1, sticky='ew')
frame_top.grid(column=0, row=2, sticky='ew')
frame_bot.grid(column=0, row=3)

#==================== FRAME STATUS ===================================
lbl_status = Label(frame_status, text="Status: connected")
lbl_status.grid(column=0, row=0)

#==================== FRAME TOP ===================================
lbl1 = Label(frame_top, text="I2C Address select:")
lbl2 = Label(frame_top, text="Address: ")
btn_scan = Button(frame_top, text="Scan", command=Scan_btn_click)
combo_i2c_dev_sel = ttk.Combobox(frame_top,width = 27, postcommand=combo_i2c_dev_select, state="readonly")

lbl1.grid(column=0, row=0)
lbl2.grid(column=0, row=1)
btn_scan.grid(column=3, row=1)
combo_i2c_dev_sel.grid(column=2, row=1)

#==================== FRAME BOT ===================================

tab_control = ttk.Notebook(frame_bot)
tab_control.grid(column=0, row=0)
tab1 = ttk.Frame(tab_control, width=400, height=400)
tab2 = ttk.Frame(tab_control)
tab3 = ttk.Frame(tab_control)
tab4 = ttk.Frame(tab_control)

tab_control.add(tab1, text='1-Reg')
tab_control.add(tab2, text='multi-reg')
tab_control.add(tab3, text='memory')
tab_control.add(tab4, text='SMBus')






combo_i2c_dev_sel.bind("<<ComboboxSelected>>", select_i2c_device)

window.mainloop().mainloop()