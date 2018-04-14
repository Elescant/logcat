import tkinter as tk
from tkinter import *
from tkinter import Menu
from logcat import *
from tkinter.scrolledtext import ScrolledText
import threading

port = '/dev/ttyACM0'

class Application(Frame):
    def __init__(self,master= None):
        Frame.__init__(self,master)

        self.pack(expand=YES,fill=BOTH)#把自己放入父组件(即master)
        self.createWidgets()
        self.master.protocol('WM_DELETE_WINDOW',self.closewin)

        # self.testlayout()

    def testlayout(self):
        
         frame = Frame(self,bg='red')

         btn1 = Button(frame,text='one',width=5,height=5).pack(side=TOP, anchor=NW)
         btn2 = Button(frame,text='two',width=5,height=5).pack(side=TOP,anchor=NW)
         btn3 = Button(frame,text='three',width=5,height=5).pack(side=TOP, anchor=NW)

         frame.pack(side=LEFT,anchor=NW)

         frame2 = Frame(self,bg='green')
         btn4 = Button(frame2,text='four',width=15,height=15).pack(side=LEFT,fill=BOTH,expand=YES)
         frame2.pack(side=LEFT,expand=YES,fill=BOTH)


    def testmenu(self):
        menuBar = Menu(self)
        self.master.config(menu=menuBar)

        fileMenu = Menu(menuBar,tearoff = 0)
        menuBar.add_cascade(label='File',menu=fileMenu)

        fileMenu.add_command(label='New')
        fileMenu.add_command(label='Exit',command=self._quit)

        helpMenu = Menu(menuBar,tearoff = 0)
        menuBar.add_cascade(label='Help',menu=helpMenu)

        helpMenu.add_command(label='about')

    def createWidgets(self):
        # self.text = ScrolledText(self,background='#ffffff')
        # self.text.pack(expand=1, fill="both")

        menuBar = Menu(self)
        self.master.config(menu=menuBar)

        fileMenu = Menu(menuBar,tearoff = 0)
        menuBar.add_cascade(label='File',menu=fileMenu)

        fileMenu.add_command(label='New')
        fileMenu.add_command(label='Exit',command=self._quit)

        helpMenu = Menu(menuBar,tearoff = 0)
        menuBar.add_cascade(label='Help',menu=helpMenu)

        helpMenu.add_command(label='about')

        #Checkbutton
        fmbtn = Frame(self)

        self.ckbtn_debugvar = BooleanVar()
        self.checkbtn_debug = Checkbutton(fmbtn,text='Debug',variable = self.ckbtn_debugvar,command = self.ckbtnchange)
        self.checkbtn_debug.grid(row=0,column=0)
        self.checkbtn_debug.select()

        self.ckbtn_warnvar = BooleanVar()
        self.checkbtn_warn = Checkbutton(fmbtn,text='Warn',variable = self.ckbtn_warnvar,command = self.ckbtnchange)
        self.checkbtn_warn.grid(row=0,column=1)

        self.ckbtn_infovar = BooleanVar()
        self.checkbtn_info = Checkbutton(fmbtn,text='Info',variable = self.ckbtn_infovar,command = self.ckbtnchange)
        self.checkbtn_info.grid(row=0,column=2)

        self.ckbtn_pidvar = BooleanVar()
        self.checkbtn_pid = Checkbutton(fmbtn,text='Pid',variable = self.ckbtn_pidvar,command = self.ckbtnchange)
        self.checkbtn_pid.grid(row=0,column=3)

        self.spinbox = Spinbox(fmbtn,from_ = 0,to = 0xFF,command=self.spincmd,width=5)
        self.spinbox.grid(row=0,column=4,sticky='EW')

        self.uartety = Entry(fmbtn)
        self.uartety.grid(row=1,column=0,rowspan=1,columnspan=4,sticky='EW')
 
        self.uartbtntxt = StringVar()
        self.uartbtntxt.set('open uart')
        self.uartbtn = Button(fmbtn,textvariable=self.uartbtntxt,command=self.openuart)
        self.uartbtn.grid(row=1,column=4,sticky='EW')

        self.fileety = Entry(fmbtn)
        self.fileety.grid(row=2,column=0,rowspan=1,columnspan=4,sticky='EW')
        filebtn = Button(fmbtn,text='load file',command=self.loadfile)
        filebtn.grid(row=2,column=4,sticky='EW')
        #Entry
        fmbtn.pack(side=LEFT,anchor= NW)

        #文本框
        fmtext = Frame(self)
        self.text = Text(fmtext)
        self.text.pack(side = LEFT,fill=BOTH,expand=YES,anchor=NE)
        self.scrollbar = Scrollbar(fmtext)
        self.scrollbar.pack(side=LEFT,fill=Y,anchor=NW)

        # self.scrollbar.config(command=self.scrollcall)        
        self.scrollbar.config(command=self.text.yview)
        self.text.config(yscrollcommand = self.scrollbar.set)
        fmtext.pack(side=LEFT,expand=YES,fill=BOTH)

        self.logcat = Logcat()
        self.logcat.start()

        self.timer = threading.Timer(1,self.fun_timer)
        self.timer.start()
        
    def ckbtnchange(self):
        if self.ckbtn_debugvar.get() == 1:
            self.logcat.set_grade(DEBUG,True)
        else:
            self.logcat.set_grade(DEBUG,False)
        if self.ckbtn_infovar.get() == 1:
            self.logcat.set_grade(INFO,True)
        else:
            self.logcat.set_grade(INFO,False)
        if self.ckbtn_warnvar.get() == 1:
            self.logcat.set_grade(WARN,True)
        else:
            self.logcat.set_grade(WARN,False)
        if self.ckbtn_pidvar.get() == 1:
            self.logcat.set_grade(PID,True)
        else:
            self.logcat.set_grade(PID,False)

    def set_filtergrade(self,*args):
        pass

    # def scrollcall(self,*args):
    #     print(self.scrollbar.get())
    #     self.text.yview(*args)

    def openuart(self):
        if not self.logcat.uartisopen():
            uartname = self.uartety.get()
            try:
                self.logcat.openuart(port=uartname)
            except serial.serialutil.SerialException as e:
                pass
            if self.logcat.uartisopen():
                self.uartbtntxt.set('close uart')
        else:
            self.logcat.closeuart()
            self.uartbtntxt.set('open uart')

    def loadfile(self):
        opensucess = True
        filename = self.fileety.get()

        self.textclr()
        try:
            msglist = self.logcat.readfile(filename)
        except FileNotFoundError as e:
            opensucess = False

        if opensucess:
            for item in msglist:
                self.text.insert(END,item.format())
            self.text.see(END)

    def textclr(self):
        self.text.delete(0.0,len(self.text.get(0.0,END))-1.0)

    def textupdate(self):
        endfile = False
        msglist = self.logcat.get_dislist()
        if self.scrollbar.get()[1] == 1:
            endfile =True
        if len(msglist) > 0:
            for item in msglist:
                self.text.insert(END,item.format())
            self.logcat.dislistclr()
        if endfile:
            self.text.see(END)

    def spincmd(self):
        self.logcat.set_dispid(int(self.spinbox.get()))

    def fun_timer(self):
        self.textupdate()
        self.timer = threading.Timer(0.05,self.fun_timer)
        self.timer.start()
    def closewin(self):
        self._quit()
    def _quit(self):
        if self.timer:
            self.timer.cancel()
        self.logcat.end()
        self.quit()
        self.master.destroy()
        exit()

window = tk.Tk()
window.title('Logcat')

app = Application(window)
app.mainloop()