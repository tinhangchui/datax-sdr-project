import telnetlib
import time
import radio_identifier
import music_identifier
import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
import os
"""
App Class
The main app to identify signals!
"""
class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        #self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        #data
        self.frequency_list = []
        self.report = dict()

        self.frames = {}
        for F in [ScanWindow, ConnectWindow, Report]:
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        #when started, show ScanWindow
        self.show_frame("ScanWindow")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        #if frame is Report frame, call LoadTable() to update the result
        if page_name == "Report":
            frame.LoadTable()
        frame.tkraise()

"""
Scan window
The first window that prompts user to enter min and max frequency.
Then the program will scan the fm station in this range.
After that, open connect window
"""
class ScanWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.parent = parent
        self.controller.title("DataX alien project!")

        self.label = Label(self, text="Please enter the min and max scanning frequency.")
        self.label.pack()

        self.min_label = Label(self, text="minimum Hz")
        self.min_label.pack()
        self.min_input = Entry(self)
        self.min_input.pack()

        self.max_label = Label(self, text="maximum Hz")
        self.max_label.pack()
        self.max_input = Entry(self)
        self.max_input.pack()

        self.scan_button = Button(self, text="Scan", command=self.scan_frequency)
        self.scan_button.pack()

        self.close_button = Button(self, text="Close", command=self.controller.quit)
        self.close_button.pack()

    def scan_frequency(self):
        min = int(self.min_input.get())
        print("Debug(start.py): received min value = {}".format(min))
        max = int(self.max_input.get())
        print("Debug(start.py): received max value = {}".format(max))

        #check if data is valid
        if not self.is_frequency_valid(min, max):
            messagebox.showinfo("Error", "Invalid frequency!")
            return

        #call get_radio_list to scan frequency
        frequency_list = radio_identifier.get_radio_list(min, max)
        print("Debug(start.ypy): result frequency list : {}".format(frequency_list))

        #save the frequency to my controller.frequency_list
        self.controller.frequency_list = frequency_list

        #move to connect window
        self.controller.show_frame("ConnectWindow")

    def is_frequency_valid(self, min, max):
        #check if the user's frequency is valid
        if min < 0 or min > max:
            return False
        return True

"""
Send Message function
helper function to send message to gqrx server
"""
def sendMsg(msg):
    """
    Send msg to gqrx, assume gqrx has opened the server
    """
    tn = telnetlib.Telnet('127.0.0.1', 7356)
    tn.write(('%s\n' % msg).encode('ascii'))
    response = tn.read_some().decode('ascii').strip()
    tn.write('c\n'.encode('ascii'))
    return response

"""
Connect Window
prompts user to open gqrx and its tcp server.
Then it goes through every fm station and see if it is playing music.
"""
class ConnectWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.controller.title("DataX alien project!")

        self.label = Label(self, text="Please open gqrx and tcp server.\n Start DSP and set the record address to the folder where data_alien.py is in.")
        self.label.pack()

        self.greet_button = Button(self, text="Connect", command=self.scan_music)
        self.greet_button.pack()

        self.close_button = Button(self, text="Close", command=self.controller.quit)
        self.close_button.pack()

    def scan_music(self):
        #try to send some message to check if gqrx is really opened
        try:
            tn = telnetlib.Telnet('127.0.0.1', 7356)
            tn.write('c\n'.encode('ascii'))
        except:
            messagebox.showinfo("Error", "Failed to connect to gqrx. Make sure you have opened gqrx and its tcp server.")
            return

        fm_list = self.controller.frequency_list
        for fm in fm_list:
            sendMsg('F ' + str(fm * 1000000))
            sendMsg('AOS')              #send start recording signal
            print('start recording')
            time.sleep(1)           #record for 5 sec
            print('stop recording')
            sendMsg('LOS')              #send stop recording signal

            #open the file in ./tmp
            if os.listdir('./tmp') == []:
                raise 'Please set gqrx wav output to ./tmp'
            path = ''
            for file in os.listdir('./tmp'):
                if file.endswith(".wav"):
                    path = './tmp/' + file

            if music_identifier.is_music(path):
                print("Debug: This is music!")
                self.controller.report[fm] = True
            else:
                print("Debug: This is not music!")
                self.controller.report[fm] = False

            os.remove(path)

        #in controller, construct report frame
        self.controller.show_frame("Report")

"""
Report Table
After identified which fm station is playing music, report
in a tkinter table.
"""
class Report(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.CreateUI()
        self.grid(sticky = (N,S,W,E))
        parent.grid_rowconfigure(0, weight = 1)
        parent.grid_columnconfigure(0, weight = 1)

    def CreateUI(self):
        tv = Treeview(self)
        tv['columns'] = ('frequency', 'status')
        tv.heading("#0", text='Sources', anchor='w')
        tv.column("#0", anchor="w")
        tv.heading('frequency', text='Start Time')
        tv.column('frequency', anchor='center', width=100)
        tv.heading('status', text='Status')
        tv.column('status', anchor='center', width=100)
        tv.grid(sticky = (N,S,W,E))
        self.treeview = tv
        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)

    def LoadTable(self):
        report = self.controller.report
        i = 1
        for fm in report:
            frequency = str(fm)
            if report[fm] == True:  #is music
                self.treeview.insert('', 'end', text="fm station " + str(i), values=(frequency, 'music'))
            else:   #not music
                self.treeview.insert('', 'end', text="fm station " + str(i), values=(frequency, 'not music'))
            i += 1
"""
The program starts here.
"""
if __name__ == "__main__":
    app = App()
    app.mainloop()
