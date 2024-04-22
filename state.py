DEVICEID = "31514"
APIKEY = "6d5f4be16"

WINDOWS_SPEED = 60           # motor speed 

STATE_CLOSE_FLAG = 0x01      # start to close

STATE_OPEN_FLAG  = 0x02      # start to open

STATE_DONE  = 0x03           # finish the work 

STATE_WINDOWS = 0x00         # present windows state 

WORK = False                 # judge work is done 

IR_OPEN = 69                 # IR control state

IR_CLOSE = 70

IR_STOP = 71


def GET_STATE_WINDOWS():
    global STATE_WINDOWS
    return STATE_WINDOWS


def SET_STATE_WINDOWS(NEW_STATE):
    global STATE_WINDOWS
    STATE_WINDOWS = NEW_STATE
