import serial
import re
import time,sys,threading
from enum import Enum
from collections import OrderedDict
import json
import unittest
from datetime import datetime
import time

usartport = '/dev/ttyACM0'
bps = 9600
timeout = 0.02

DEBUG = 0x01
INFO = 0x02
WARN = 0x04
PID = 0x08
NONE = 0x00

class DisGrade(Enum):
    debug = 'DEBUG'
    info = 'INFO'
    warn = 'WARN'
    pid = 'PID'

class Message(object):
    def __init__(self,grade,pid,info,time = 0):
        self.grade = grade
        self.pid = pid
        self.info = info
        self.time = time
    def __str__(self):
        return str(self.__dict__)
    def set_curtime(self):
        self.time = int(time.time())
    def format(self):
        time_local = time.localtime(self.time)
        dt = time.strftime("%Y-%m-%d %H:%M:%S",time_local)
        return '{0}:\t{1},{2}:\t{3}\n'.format(dt,self.grade,self.pid,self.info)

class Logcat(object):
    def __init__(self):
        self.dev = NONE
        self.dislist = []
        self.dislen = 500
        self.curdisgrade = DEBUG
        self.curdispid = 0
        self.curdisdependchange = False
        self.msgsourceisuart = False
        self.running = False

    def openuart(self,port,baudrate=9600,timeout=0.2):
        self.dev = serial.Serial(port = port,baudrate=baudrate,timeout=timeout)

    def uartisopen(self):
        return self.dev != NONE

    def closeuart(self):
        if self.dev:
            self.dev.close()
            self.dev=NONE
        
    def uartwrite(self,*args,**kw):
        if self.dev:
            if len(args)>0:
                content = str(args)
                if len(args) == 1:
                    content = content[1:len(content)-2]
                else:
                    content = content[1:len(content)-1]
                self.dev.write(bytes(content,encoding = 'utf8'))

    def uartreadline(self):
        if self.dev:
            dat= self.dev.readline()
            return str(dat,'utf-8')
        else:
            time.sleep(0.2)
            return ''

    def start(self):
        self.running = True
        self.t = threading.Thread(target=self.loopread_uart,name = 'LoopReadThread')
        self.t.start()

    def end(self):
        self.running = False
        self.t.join()
        if self.dev:
            self.dev.close()
            self.dev = None
        

    def loopread_uart(self):
        #read
        while self.running:
            s = self.uartreadline()
            if s == '':
                pass
            else:
                msglist = self.parseline(s)
                self.savemsg('log.txt',msglist)
                for msg in msglist:
                   if self.disfilter(msg):
                       self.dislist.append(msg)

    def readfile(self,filename):
        filelist = []
        with open(filename,'r') as f:
            for line in f.readlines():
                msg = self.json2msg(line)
                if self.disfilter(msg):
                    filelist.append(msg)
        return filelist

    def savemsg(self,filename,msglist):
        with open(filename,'a') as f:
            for msg in msglist:
                f.write(self.msg2json(msg))
                f.write('\r\n')

    def disfilter(self,msg):
        if self.curdisgrade & DEBUG:
            if msg.grade == DisGrade.debug.value:
                return True
        if self.curdisgrade & INFO:
            if msg.grade == DisGrade.info.value:
                return True
        if self.curdisgrade & WARN:
            if msg.grade == DisGrade.warn.value:
                return True
        if self.curdisgrade & PID:
            if msg.pid == self.curdispid or self.curdispid == 0xFF:
                return True    
        return False        

    def parseline(self,line):
        dwi = line.split('\r\n')
        dwi = list(filter(lambda s:s and s.strip(),dwi))
        msglist = []
        for s in dwi:
            msg = self.pickupmsg(s)
            if msg:
                msglist.append(msg)
        return msglist

    def pickupmsg(self,s):
        result = re.match(r'([a-zA-Z]*):PID\s([0-9]+):(.*)',s)
        if result:
            #              grade            pid             info
            msg = Message(result.group(1),int(result.group(2)),result.group(3))
            msg.set_curtime()
            return msg
        else:
            return None

    def dislistclr(self):
        self.dislist.clear()

    def dislistappend(self,somthing):
        if(len(self.dislist) >= self.dislen):
            self.dislist.pop(0)
        self.dislist.append(somthing)
    def get_dislist(self):
        return self.dislist

    def msg2json(self,msg):
        return json.dumps(msg,default = lambda obj:obj.__dict__)

    def json2msg(self,jsstr):
        try:
           return json.loads(jsstr,object_hook=self.dict2msg)     
        except json.decoder.JSONDecodeError as e:
            print('catch except:',e)
        # finally:
        #     print('finally...')

    def dict2msg(self,msg):
        return Message(msg['grade'],msg['pid'],msg['info'],msg['time'])

    def set_grade(self,grade,onoff):
        self.curdisdependchange = True
        if onoff:
            self.curdisgrade =self.curdisgrade | grade
        else:
            self.curdisgrade &=(~grade)
                
                
    def get_grade(self):
        return self.curdisgrade

    def set_dispid(self,pid):
        self.curdispid = pid

    def get_dispid(self):
        return self.curdispid

    def get_gradechange(self):
        return self.curdisdependchange

    def set_gradechange(self,bl):
        self.curdisdependchange = bl

    def set_dislen(self,len):
        assert(len > 0)
        self.dislen = len 
    def get_dislen(self):
        return self.dislen

    def set_msgsourceisuart(self):
        self.msgsourceisuart = True
    
    def get_msgsourceisuart(self):
        return self.msgsourceisuart
def main():
        log = Logcat(usartport)
        log.set_grade(DisGrade.pid)
        log.set_dispid(3)
        log.start()

class TestLogcat(unittest.TestCase):
    def test_init(self):
        pass
    # def test_json2msg(self):
    #     log = Logcat(usartport)
    #     js = '{"time": 1514941761.4127579, "grade": "INFO", "pid": "3", "info": "Will exit in 2048 sec!"}'
    #     msg = log.json2msg(js)
    #     print(msg)
    # def test_parseline(self):
    #     s = 'DEBUG:PID 3:Thismessage comes from DEBUG!\n'+'WARN:PID 3:This is Warning!\n'+'INFO:PID 3:Will exit in 2048 sec!'
    #     log = Logcat(usartport)
    #     msglist = log.parseline(s)
    #     for msg in msglist:
    #         print(msg)
    # def test_readfile(self):
    #     log = Logcat()
    #     log.set_grade(DEBUG,True)
    #     log.set_grade(DEBUG,False)
    #     msglist = log.readfile('log.txt')
    #     for msg in msglist:
    #             print(msg)
    # def test_savemsg(self):
    #     s = 'DEBUG:PID 3:Thismessage comes from DEBUG!\n'+'WARN:PID 3:This is Warning!\n'+'INFO:PID 3:Will exit in 2048 sec!'
    #     log = Logcat(usartport)
    #     msglist = log.parseline(s)
    #     log.savemsg('log.txt',msglist)
    def test_filter(self):
        s = 'DEBUG:PID 3:Thismessage comes from DEBUG!\r\n'+'WARN:PID 4:This is Warning!\r\n'+'INFO:PID 5:Will exit in 2048 sec!'
        log = Logcat()
        log.set_grade(DEBUG,False)
        log.set_grade(INFO,False)
        log.set_grade(WARN,False)
        log.set_grade(PID,True)
        log.set_dispid(0xFF)
        msglist = log.parseline(s)
        for msg in msglist:
           if log.disfilter(msg):
               print(msg)




if __name__ == '__main__':
   unittest.main()
    # main()

