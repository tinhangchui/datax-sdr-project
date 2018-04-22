import telnetlib
import time
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

        self.greet_button = Button(master, text="Connect", command=self.greet)
        self.greet_button.pack()

        self.close_button = Button(master, text="Close", command=master.quit)
        self.close_button.pack()

    def greet(self):
        foo('AOS')
        print('start recording')
        time.sleep(5)
        print('stop recording')
        result = foo('LOS')
        print(result)


root = Tk()
my_gui = MyFirstGUI(root)
root.mainloop()
