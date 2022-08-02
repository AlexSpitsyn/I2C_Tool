from cProfile import label

import dearpygui.dearpygui as dpg
import I2Ctool

def get_reg_addr():
    if dpg.get_value(burst_reg_addr_input) == '':
        print_log_line('Wrong reg address')
        return False
    reg_addr = int(dpg.get_value(burst_reg_addr_input), 16)
    if tool.mem_addr_size_16bit:
        if reg_addr > 65535:
            print_log_line('Wrong reg address')
            return False
    else:
        if reg_addr > 255 or reg_addr < 0:
            print_log_line('Wrong reg address')
            return False
    return [reg_addr // 256, reg_addr % 256]

def button_scan_callback():
    tool.scan()
    l=[]
    for i in tool.devices:
        l.append(hex(i))
    dpg.configure_item(comdo_addres_select, items=l , default_value = '')
    tool.set_dev = None
    print_log_line('     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f')
    for i in range(8):
        s = str(i) + '0: '
        for a in range(16):
            if i*16+a in tool.devices:
                s+=hex(i*16+a)[2:] + ' '
            else:
                s+='-- '
        print_log_line(s)


def i2c_addr_select(sender, app_data, user_data):
    print_log_line(f"Device status: {tool.set_addr(int(app_data, 0))}")

def button_write_callback(sender, app_data, user_data):
    if tool.set_dev == None:
        print_log_line('I2C address not set')
        return

    if sender == wr_single:
        in_str = dpg.get_value(singl_byte_input)
        if in_str == '':
            print_log_line('Value not set')
            return
        else:
            if dpg.get_value(rb_single) == 'hex':
                wr_val = int(dpg.get_value(singl_byte_input), 16)
            else:
                wr_val = int(dpg.get_value(singl_byte_input), 10)
            if wr_val< 0 or wr_val > 255:
                print_log_line('Wrong Value')
                return
            else:
                tool.write_nbytes(1, [wr_val])
                print_log_line(f'Write: {wr_val}\t {hex(wr_val)}\t {bin(wr_val)}')
                print_log_line(f'Write to {hex(tool.set_dev)} status: {tool.get_status()}')

    if sender == wr_burst:
        print(dpg.get_value(cb_skip_addr))
        if not dpg.get_value(cb_skip_addr):
            reg_addr_list = get_reg_addr()
            if reg_addr_list == False:
                return

        in_str = dpg.get_value(burst_input)
        if in_str == '':
            print_log_line('Value not set')
            return
        else:
            if dpg.get_value(rb_burst) == 'hex' or dpg.get_value(rb_burst) == 'dec':
                in_str = in_str.strip(';')
                in_str = in_str.replace(' ', '')
                for symb in in_str:
                    if dpg.get_value(rb_burst) == 'hex':
                        if symb.upper() not in '0123456789ABCDEF;':
                            print_log_line(f'Wrong character: {symb}')
                            return
                    if dpg.get_value(rb_burst) == 'dec':
                        if symb.upper() not in '0123456789;':
                            print_log_line(f'Wrong character: {symb}')
                if len(in_str.split(';')) > 32:
                    print_log_line('Byte count > 32')
                    return
                count = len(in_str.split(';'))
                wr_list = []
                for v in in_str.split(';'):
                    if dpg.get_value(rb_burst) == 'hex':
                        v_int = int(v, 16)
                    if dpg.get_value(rb_burst) == 'dec':
                        v_int = int(v, 10)
                    if v_int > 255:
                        print_log_line(f'Wrong Value: {v}')
                        return
                    else:
                        wr_list.extend([v_int])

            if dpg.get_value(rb_burst) == 'char':
                count = len(in_str)
                for v in in_str:
                    wr_list.extend([int(v.encode('utf-8').hex(), 16)])

            if dpg.get_value(cb_skip_addr):
                tool.write_nbytes(count, wr_list)
            else:
                tool.write_reg_nbytes(reg_addr_list, count, wr_list)
            print_log_line(f'Write to {hex(tool.set_dev)} status: {tool.get_status()}')




def button_read_callback(sender, app_data, user_data):
    h = dpg.get_value(cb_hex)
    c = dpg.get_value(cb_char)
    d = dpg.get_value(cb_dec)

    if tool.set_dev == None:
        print_log_line('I2C address not set')
        return

    if sender == rd_single:
        tool.write([4])
        ret = tool.read()
        print_log_line(f'Read device {hex(tool.set_dev)} status: {tool.get_status()}')
        #if int(ret[0]) == 0:
        print_log_line(f'Read: {ret[1]}\t {hex(ret[1])}\t {bin(ret[1])}')

    if sender == rd_burst:
        print(dpg.get_value(cb_skip_addr))
        if not dpg.get_value(cb_skip_addr):
            reg_addr_list = get_reg_addr()
            if reg_addr_list == False:
                return

        count = dpg.get_value(burst_byte_cnt)

        if dpg.get_value(cb_skip_addr):
            ret = tool.read_nbytes(count)
        else:
            ret = tool.read_reg_nbytes(reg_addr_list, count)

        print_log_line('\n')
        print_log_line(f'Read device {hex(tool.set_dev)} status: {tool.get_status()}')
        if ret:
            print_bytes(ret, h , c , d)

def button_clear_callback():
    dpg.set_value(out_log, '')


def cb_2byte_addr_callback(sender, app_data, user_data):

    if app_data:
        dpg.configure_item(burst_reg_addr_input,label='0-FFFF')
        tool.set_mem_addr_size('16BIT')
    else:
        dpg.configure_item(burst_reg_addr_input, label='0-FF  ')
        tool.set_mem_addr_size('8BIT')

    if app_data != tool.mem_addr_size_16bit:
        print_log_line('Set memory address size FAIL')

def cb_skip_addr_callback(sender, app_data, user_data):
    if app_data:
        dpg.configure_item(burst_reg_addr_input, enabled=False)
        dpg.configure_item(cb_2byte_addr, enabled=False)
        dpg.bind_item_theme(burst_reg_addr_input,disabled_theme)
        dpg.bind_item_theme(cb_2byte_addr, disabled_theme)

    else:
        dpg.configure_item(burst_reg_addr_input, enabled=True)
        dpg.configure_item(cb_2byte_addr, enabled=True)
        dpg.bind_item_theme(burst_reg_addr_input,global_theme)
        dpg.bind_item_theme(cb_2byte_addr, global_theme)



def radio_btn_hex_dec_char(sender, app_data, user_data):
    if sender == rb_single:
        dpg.set_value(singl_byte_input, '')
        if app_data == 'hex':
           dpg.configure_item(singl_byte_input, label='0-FF', hexadecimal=True, decimal=False)
        if app_data == 'dec':
           dpg.configure_item(singl_byte_input, label='0-255', hexadecimal=False, decimal=True)
    if sender == rb_burst:
        dpg.set_value(burst_input, '')
        if app_data == 'hex':
           dpg.configure_item(burst_input, hint='hex;hex;...')
        if app_data == 'dec':
           dpg.configure_item(burst_input, hint='dec;dec;...')
        if app_data == 'char':
           dpg.configure_item(burst_input, hint='charchar...')


def print_log_line(msg):
    dpg.configure_item(out_log, default_value=dpg.get_value(out_log)+msg+'\r\n')


def print_bytes(bts, h=True, c=True, d=True):
    if bts == b'':
        return
    lenght = len(bts)
    mux_h = 24
    mux_d = 32
    mux_c = 8
    lines = lenght//8
    if lenght%8:
        lines+=1

    chr_str=''
    hex_str=''
    dec_str=''
    header='\t'

    for i in range(len(bts)):
        # print(int(i))
        if int(bts[i]) > 122 or int(bts[i]) < 32:
            chr_str += '.'
        else:
            chr_str += chr(int(bts[i]))
        hex_str += bts.hex()[i * 2:i * 2 + 2] + ' '
        dec_str += str(int(bts[i])).rjust(3,'0') + ' '
    chr_str = chr_str.ljust(lines*mux_c + 1, ' ')
    hex_str = hex_str.ljust(lines*mux_h + 1, ' ')
    dec_str = dec_str.ljust(lines*mux_d + 1, ' ')

    cnt = 4
    for l in range(lines):
        msg = str(chr(l).encode('utf-8').hex()) + ': '
        if h:
            header = header + '00 01 02 03 04 05 06 07 | '
            cnt+=25
            msg += hex_str[l*mux_h:l*mux_h+mux_h] + '| '
        if c:
            header = header + '01234567 | '
            cnt += 10
            msg += chr_str[l * mux_c:l * mux_c + mux_c] + ' | '
        if d:
            header = header + ' 0   1   2   3   4   5   6   7  '
            cnt += 33
            msg += dec_str[l * mux_d:l * mux_d + mux_d]
        if h or c or d:
            if l == 0:
                print_log_line(header.strip(' | '))
                print_log_line(''.ljust(cnt,'-'))
            print_log_line(msg.strip(' | '))
    return

def key_handler (sender, data):
    tool.write([10])
    ret = tool.read()
    print_log_line('I2C state: ' + tool.I2C_STATE[hex(int(ret[0]))])
    print(hex(int(ret[0])))


dpg.create_context()
#dpg.configure_app(manual_callback_management=True) #for debug




with dpg.window(tag="main"):
    with dpg.group(horizontal=True, horizontal_spacing=10):
        dpg.add_text("I2C Address select")
        # dpg.add_spacer(width=100)
        dpg.add_text("Address:")
        comdo_addres_select = dpg.add_combo(callback=i2c_addr_select, width=100)
        dpg.add_button(label="Scan", callback=button_scan_callback, enabled=True)

    dpg.add_spacer(height=10)
    dpg.add_separator()
    dpg.add_spacer(height=10)

    with dpg.group(horizontal=True, horizontal_spacing=50):
        with dpg.tab_bar() as tb:
            with dpg.tab(label="Singl Byte Reg"):
                dpg.add_spacer(height=10)
                rb_single = dpg.add_radio_button(("hex", "dec"),  default_value='hex', horizontal=True, callback=radio_btn_hex_dec_char)
                dpg.add_spacer(height=10)
                with dpg.group(horizontal=True, horizontal_spacing=10):
                    wr_single = dpg.add_button(label="Write", callback=button_write_callback, user_data='single')
                    dpg.add_text("Value:")
                    singl_byte_input = dpg.add_input_text(label="00-FF", hexadecimal=True, uppercase=True, width=50)
                    #onereg_instr = dpg.add_input_text(label="00-FF", hexadecimal=True, uppercase=True, width=100, callback=lambda s, a: dpg.set_value(s, a[0:2]))

                with dpg.group(horizontal=True, horizontal_spacing=10):
                    rd_single = dpg.add_button(label="Read ", callback=button_read_callback,  user_data="single")
                    #dpg.add_text("Value:")
                    #dpg.add_input_text( hexadecimal=True, uppercase=True, width=100, enabled=False, tag='it')


            with dpg.tab(label="Burst Reg"):
                dpg.add_spacer(height=10)
                cb_skip_addr = dpg.add_checkbox(label="skip address", default_value=False, callback=cb_skip_addr_callback)
                with dpg.group(horizontal=True, horizontal_spacing=8):
                    dpg.add_spacer(width=2)
                    dpg.add_text("Reg address: ")
                    burst_reg_addr_input = dpg.add_input_text(label="0-FF  ", hexadecimal=True, uppercase=True, width=70 )
                    dpg.add_spacer(width=5)
                    cb_2byte_addr = dpg.add_checkbox(label="2-byte address", default_value=True, callback=cb_2byte_addr_callback)
                dpg.add_separator()
                dpg.add_spacer(height=10)
                with dpg.group(horizontal=True, horizontal_spacing=10):
                    dpg.add_text("data format")
                    dpg.add_spacer(width=5)
                    rb_burst = dpg.add_radio_button(("hex", "dec", 'char'), default_value='hex', horizontal=True,
                                                callback=radio_btn_hex_dec_char)
                dpg.add_spacer(height=10)
                with dpg.group(horizontal=True, horizontal_spacing=10):
                    wr_burst = dpg.add_button(label="Write", callback=button_write_callback,width=100,  user_data='burst')
                    #dpg.add_spacer(width=1)
                    burst_input = dpg.add_input_text(label="max 32 byte", width=300, hint='hex;hex;...')
                dpg.add_spacer(height=10)
                with dpg.group(horizontal=True, horizontal_spacing=10):
                    rd_burst = dpg.add_button(label="Read", callback=button_read_callback,width=100, user_data="burst")
                    #dpg.add_spacer(width=1)
                    burst_byte_cnt = dpg.add_input_int(label='byte count', default_value=1, min_value=1, max_value=32, width=100, min_clamped=True, max_clamped=True)



            with dpg.tab(label="Memory"):
                dpg.add_spacer(height=10)

                dpg.add_spacer(height=10)

                with dpg.group(horizontal=True, horizontal_spacing=10):



                    dpg.add_button(label="Show File Selector", user_data=dpg.last_container(),
                               callback=lambda s, a, u: dpg.configure_item(u, show=True))



            with dpg.tab(label="SMBus"):
                dpg.add_text("This is the tab 4!")

    # LOG WINDOW
    with dpg.group( pos=(550, 10)):
        with dpg.group(horizontal=True, horizontal_spacing=10):
            dpg.add_text("View mode:")
            cb_hex=dpg.add_checkbox(label="hex", default_value=True)
            cb_char=dpg.add_checkbox(label="char", default_value=True)
            cb_dec=dpg.add_checkbox(label="dec", default_value=True)
            dpg.add_spacer(width=150)
            dpg.add_button(label='Clear Log', callback=button_clear_callback)
        out_log=dpg.add_input_text(multiline=True, width=550, height=400,  readonly=True, tracked=True )

    with dpg.handler_registry():
        k_down = dpg.add_key_press_handler(key=dpg.mvKey_S)
        dpg.set_item_callback(k_down, key_handler)
#dpg.bind_item_handler_registry('it',"widget handler")

with dpg.theme() as disabled_theme:
    with dpg.theme_component(dpg.mvAll, enabled_state=False):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, [25, 25, 99, 255], category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Text, [0, 0, 0, 255], category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1, category=dpg.mvThemeCat_Core)
        # dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 20, 10, category=dpg.mvThemeCat_Core)

with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, [25, 25, 99, 255], category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Text,[255,255,255,255], category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 20,3, category=dpg.mvThemeCat_Core)




view = dpg.create_viewport(title='I2C Tool', width=1120, height=480, resizable=False)

dpg.bind_theme(global_theme)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("main", True)


tool = I2Ctool.I2C_tool()
tool.dbg = True
tool.inf()

if tool.error_messages:
    for m in tool.error_messages:
        print_log_line(m)

if tool.mem_addr_size_16bit:
    dpg.configure_item(burst_reg_addr_input,label='0-FFFF')
else:
    dpg.configure_item(burst_reg_addr_input, label='0-FF  ')



while dpg.is_dearpygui_running():
    if tool.device_search():
        if tool.init_state == False:
            tool.__init__()

        dpg.set_viewport_title('I2C tool: connected')
        for i in dpg.get_all_items():
            if dpg.get_item_type(i) == "mvAppItemType::mvButton":
                dpg.enable_item(i)
        dpg.bind_theme(global_theme)
    else:
        dpg.set_viewport_title('I2C tool: disconnected')

        for i in dpg.get_all_items():
            if dpg.get_item_type(i) == "mvAppItemType::mvButton":
                dpg.disable_item(i)
        dpg.bind_theme(disabled_theme)

        #dpg.stop_dearpygui()
            # dpg.disable_item(i)
# insert here any code you would like to run in the render loop
# you can manually stop by using stop_dearpygui()
    dpg.render_dearpygui_frame()
#dpg.start_dearpygui()
#dpg.destroy_context()


# In terminal
# pyinstaller --onefile --name I2Ctool --noconsole main.py