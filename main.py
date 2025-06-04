import serial
import serial.tools.list_ports
import tkinter as tk
from pynput.keyboard import Key, Controller as KeyController
from pynput.mouse import Button, Controller as ButtonController
import time
import sys

def select_port():
    root = tk.Tk()
    root.title("手势控制教具")
    root.geometry("267x200")
    root.resizable(False, False)
    root.iconbitmap("icon.ico")

    ports = serial.tools.list_ports.comports()
    if not ports:
        text = tk.Label(root, text = '未检测到可用串口')
        text.pack(pady = (10, 10))
        root.mainloop()
        sys.exit()

    text = tk.Label(root, text = '可用端口：')
    text.pack(pady = (7, 5))
    
    listbox = tk.Listbox(root, width = 30, height = 6, selectmode = tk.SINGLE)
    listbox.selection_set(0)
    listbox.pack()

    for i, port in enumerate(ports, start = 1):
        listbox.insert(tk.END, f"{i}. {port.description}")
    
    choice = -1
    def submit_selection():
        nonlocal choice
        choice = listbox.curselection()[0]
        root.destroy()

    submit_button = tk.Button(root, text = "   确认   ", command = submit_selection)
    submit_button.pack(pady = 12)
    
    root.wait_window()
    root.mainloop()
    if choice == -1:
        sys.exit()
    return ports[choice].device

def show_action():
    keyboard = KeyController()
    mouse = ButtonController()
    func, interval = '空', 0
    global ser

    def update():
        nonlocal action, func, interval
        THRESHOLD, EPS = 3, 0.001

        line = ser.readline().decode('utf-8', errors='replace').strip()
        ax = float(line.split('aX:')[1].split(',')[0])
        ay = float(line.split('aY:')[1].split(',')[0])
        az = float(line.split('aZ:')[1]) - 10.7
        print(f'{ax}  {ay}  {az}')

        if abs(ax - 0.00) < EPS and abs(ay - 39.39) < EPS and abs(az - 5.85) < EPS:
            #print(func)
            match func:
                case '空':
                    root.after(10, update)
                    return
                case '上':
                    keyboard.tap(Key.up)
                case '下':
                    keyboard.tap(Key.down)
                case '右':
                    keyboard.tap(Key.right)
                case '左':
                    keyboard.tap(Key.left)
                case '上左':
                    keyboard.press(Key.shift)
                    keyboard.tap(Key.f5)
                    keyboard.release(Key.shift)
                case '上右':
                    keyboard.tap(Key.esc)
                case '下左':
                    mouse.click(Button.right)
                    keyboard.tap('z')
                    time.sleep(0.3)
                    mouse.click(Button.left)
                case '下右':
                    keyboard.press(Key.alt)
                    keyboard.tap(Key.tab)
                    keyboard.release(Key.alt)
            action.set(f'当前动作：{func}')
            func = '空'
        elif interval == 0:
            if az > THRESHOLD and abs(ax) < THRESHOLD and func == '空':
                func = '上'
                interval = 3
            elif az < -THRESHOLD and abs(ax) < THRESHOLD and func == '空':
                func = '下'
                interval = 3
            elif ax < -THRESHOLD and abs(az) < THRESHOLD:
                match func:
                    case '下':
                        func = '下右'
                    case '上':
                        func = '上右'
                    case '空':
                        func = '右'
                interval = 3
            elif ax > THRESHOLD and abs(az) < THRESHOLD:
                match func:
                    case '上':
                        func = '上左'
                    case '下':
                        func = '下左'
                    case '空':
                        func = '左'
                interval = 3
        else:
            interval -= 1
        
        root.after(1, update)

    root = tk.Tk()
    root.title("手势控制教具")
    root.geometry("267x200")
    root.resizable(False, False)
    root.iconbitmap("icon.ico")

    text1 = tk.Label(root, text = '连接成功')
    text1.pack(pady= (20, 5))

    text2 = tk.Label(root, text = '上/左：向前翻页\n下/右：向后翻页\n上左/上右：播放/退出PPT\n下左：放大局部\n下右：切换窗口')
    text2.pack(pady= (5, 5))

    action = tk.StringVar()
    disp_action = tk.Label(root, textvariable = action)
    disp_action.pack(pady = 5)
    update() 

    root.mainloop()
    
def error():
    root = tk.Tk()
    root.title("手势控制教具")
    root.geometry("267x200")
    root.resizable(False, False)
    root.iconbitmap("icon.ico")

    text = tk.Label(root, text = '串口打开/读取失败')
    text.pack(pady = (80, 10))
    
    root.wait_window()
    root.mainloop()
    sys.exit()
    
port = select_port()
#print(port)
try:
    ser = serial.Serial(port, 9600, timeout = 1)
except:
    error()
    
if len(ser.readline().decode('utf-8', errors='replace').strip()) < 9:
    ser.close()
    error()

show_action()
ser.close()
