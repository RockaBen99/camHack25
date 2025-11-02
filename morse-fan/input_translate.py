import subprocess
from time import sleep
import threading


# Ensure sudo password check has been done
subprocess.run(["sudo", "echo", "starting"])

# Constants

MORSE_CODE_DICT = { 'A':'.-', 'B':'-...',
                    'C':'-.-.', 'D':'-..', 'E':'.',
                    'F':'..-.', 'G':'--.', 'H':'....',
                    'I':'..', 'J':'.---', 'K':'-.-',
                    'L':'.-..', 'M':'--', 'N':'-.',
                    'O':'---', 'P':'.--.', 'Q':'--.-',
                    'R':'.-.', 'S':'...', 'T':'-',
                    'U':'..-', 'V':'...-', 'W':'.--',
                    'X':'-..-', 'Y':'-.--', 'Z':'--..',
                    '1':'.----', '2':'..---', '3':'...--',
                    '4':'....-', '5':'.....', '6':'-....',
                    '7':'--...', '8':'---..', '9':'----.',
                    '0':'-----', ', ':'--..--', '.':'.-.-.-',
                    '?':'..--..', '/':'-..-.', '-':'-....-',
                    '(':'-.--.', ')':'-.--.-'}

## Morse code controls

DOT_TIME = 1

## never change
DASH_LENGTH = 3
INTRA_CHAR_WAIT = 1
INTER_CHAR_WAIT = 3

## time taken for the fan to start and stop
SPIN_UP_TIME = 0
SPIN_DOWN_TIME = 0

# global variables

__morse_code_queue: list[str] = []
__run_mainloop = True

def __mainloop():
    while __run_mainloop:
        while len(__morse_code_queue) > 0 and __run_mainloop:
            __decode(__morse_code_queue.pop(0))
        sleep(0.01)

mainloop_thread = threading.Thread(target=__mainloop)

def __start_beep():
    subprocess.run(["sudo", "systemctl", "start", "thinkfan"])
    sleep(SPIN_UP_TIME)
    
def __stop_beep():
    subprocess.run(["sudo", "systemctl", "stop", "thinkfan"])
    sleep(SPIN_DOWN_TIME)

def __dot():
    __start_beep()
    sleep(DOT_TIME)
    __stop_beep()
    sleep(INTRA_CHAR_WAIT*DOT_TIME)

def __dash():
    __start_beep()
    sleep(DASH_LENGTH*DOT_TIME)
    __stop_beep()
    sleep(INTRA_CHAR_WAIT*DOT_TIME)

def enqueue_morse_of_char(pressed_key: str):
    if pressed_key in MORSE_CODE_DICT.keys():
        __morse_code_queue.append(MORSE_CODE_DICT[pressed_key])

def __decode(morse: str):
    for beep in morse:
        if beep == '.':
            __dot()
        elif beep == '-':
            __dash()
        else:
            raise ValueError(f"Character {beep} from string {morse} is not a valid morse beep. only '-' and '.' supported.")
    sleep(INTER_CHAR_WAIT * DOT_TIME)
        
def kill():
    global __run_mainloop
    __run_mainloop = False
    mainloop_thread.join()
    __stop_beep()

# keyboard.hook(lambda event: print(event.name), True)

if __name__ == "__main__":
    import keyboard
    
    def __key_pressed(event: keyboard.KeyboardEvent):
        if event.name is not None:
            pressed_key = event.name.upper()
            enqueue_morse_of_char(pressed_key)
            
    keyboard.on_press(__key_pressed, suppress=True)
    __mainloop()
else:
    mainloop_thread.start()