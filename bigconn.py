import bigiot,_thread,time
from state import *  
from state import SET_STATE_WINDOWS

class mybig():
    def __init__(self,ID,API_KEY,check=1): #check为1则自检保持重连
        self.ID = ID 
        self.API_KEY = API_KEY
        self.on_conn() #设备上线
        
        if check==1:
            _thread.start_new_thread(self.keep_check_again,())

    def recv(self,msg):
        global STATE_WINDOWS
        print(msg)
        if msg == "play":
            SET_STATE_WINDOWS(STATE_OPEN_FLAG)
        elif msg == "stop":
            SET_STATE_WINDOWS(STATE_CLOSE_FLAG)

    def on_conn(self):
        self.device = bigiot.Device(self.ID, self.API_KEY) 
        self.device.say_callback(self.recv)
        self.device.check_in()

    def keep_check_again(self):
        while 1:
            time.sleep(50)
            try:
                self.device.check_in()
            except:
                self.on_conn() #设备上线