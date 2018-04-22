#music recognition: https://www.tensorflow.org/versions/master/tutorials/audio_recognition

import telnetlib
import time
import radio_identifier
import music_identifier
import tableTest
def foo(msg):
    tn = telnetlib.Telnet('127.0.0.1', 7356)
    tn.write(('%s\n' % msg).encode('ascii'))
    response = tn.read_some().decode('ascii').strip()
    tn.write('c\n'.encode('ascii'))
    return response

from tkinter import Tk, Label, Button

class MyFirstGUI:
    def __init__(self, master):
        self.master = master
        master.title("A simple GUI")

        self.label = Label(master, text="This is our first GUI!")
        self.label.pack()

        self.greet_button = Button(master, text="Connect", command=self.scan_music)
        self.greet_button.pack()

        self.close_button = Button(master, text="Close", command=master.quit)
        self.close_button.pack()

    def scan_music(self):
        fm_list = radio_identifier.get_radio_list()
        for fm in fm_list:
            foo('F ' + str(fm * 1000000))
            foo('AOS')              #send start recording signal
            print('start recording')
            time.sleep(5)           #record for 5 sec
            print('stop recording')
            foo('LOS')              #send stop recording signal
            if music_identifier.is_music('newfile'):
                print("This is music!")
            else:
                print("This is not music!")


root = Tk()
my_gui = MyFirstGUI(root)
root.mainloop()
