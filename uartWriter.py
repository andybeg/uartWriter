#from _typeshed import Self
import tkinter as tk
from tkinter import ttk
import serial
import threading
import serial.tools.list_ports
import struct
import time
from ftplib import FTP
from pathlib import Path
import json
from array import *
import queue
from tkinter import *
from tkinter import messagebox



class FtpUploadTracker:
    sizeWritten = 0
    totalSize = 0
    lastShownPercent = 0
    
    def __init__(self, totalSize):
        self.totalSize = totalSize
    
    def handle(self, block):
        self.sizeWritten += 1024
        percentComplete = round((self.sizeWritten / self.totalSize) * 100)
        
        if (self.lastShownPercent != percentComplete):
            self.lastShownPercent = percentComplete
            print(str(percentComplete) + " percent complete")


# A simple Information Window
class InformWindow:
    def __init__(self,informStr):
        self.window = tk.Tk()
        self.window.title("Information")
        self.window.geometry("220x60")
        label = tk.Label(self.window, text=informStr)
        buttonOK = tk.Button(self.window,text="OK",command=self.processButtonOK)
        label.pack(side = tk.TOP)
        buttonOK.pack(side = tk.BOTTOM)
        self.window.mainloop()

    def processButtonOK(self):
        self.window.destroy()

def serial_ports():    
    return [p.device for p in serial.tools.list_ports.comports()]

class mainGUI:
    def __init__(self):
        self.condition=0
        self.q = queue.Queue()
        window = tk.Tk()
        window.title("UART rw")
        self.uartState = False # is uart open or not

        # a frame contains COM's information, and start/stop button
        frame_COMinf = tk.Frame(window)
        frame_COMinf.grid(row = 1, column = 1)

        labelCOM = tk.Label(frame_COMinf,text="COMx: ")
        #self.COM = tk.StringVar(value = "/dev/ttyUSB0")
        ports = serial.tools.list_ports.comports()
        tmp_list=[]
        for port, desc, hwid in sorted(ports):
            tmp_list.append(port)
        find_com = serial.tools.list_ports

        comboCOM = ttk.Combobox(frame_COMinf, values=serial_ports())
        comboCOM["state"] = "readonly"
        comboCOM.current(2)
        self.COM = tk.StringVar(value = comboCOM.get())
            
        comboCOM.grid(row = 1, column = 2, padx = 5, pady = 3)

        labelBaudrate = tk.Label(frame_COMinf,text="Baudrate: ")
        comboBaudrate = ttk.Combobox(frame_COMinf, values=[
            "128000",
            "115200", 
            "57600", 
            "38400", 
            "19200", 
            "14400", 
            "9600", 
            "4800", 
            "2400", 
            "1200", 
            "600", 
            "300", 
            "110", 
            ])
        comboBaudrate["state"] = "readonly"
        comboBaudrate.current(1)
        self.Baudrate = tk.StringVar(value = comboBaudrate.get())
        labelBaudrate.grid(row = 1, column = 3, padx = 5, pady = 3)
        comboBaudrate.grid(row = 1, column = 4, padx = 5, pady = 3)

        labelParity = tk.Label(frame_COMinf,text="Parity: ")
        self.Parity = tk.StringVar(value ="NONE")
        comboParity = ttk.Combobox(frame_COMinf, width = 17, textvariable=self.Parity)
        comboParity["values"] = ("NONE","ODD","EVEN","MARK","SPACE")
        comboParity["state"] = "readonly"
        labelParity.grid(row = 2, column = 1, padx = 5, pady = 3)
        comboParity.grid(row = 2, column = 2, padx = 5, pady = 3)

        labelStopbits = tk.Label(frame_COMinf,text="Stopbits: ")
        self.Stopbits = tk.StringVar(value ="1")
        comboStopbits = ttk.Combobox(frame_COMinf, width = 17, textvariable=self.Stopbits)
        comboStopbits["values"] = ("1","1.5","2")
        comboStopbits["state"] = "readonly"
        labelStopbits.grid(row = 2, column = 3, padx = 5, pady = 3)
        comboStopbits.grid(row = 2, column = 4, padx = 5, pady = 3)
        labelStopbits = tk.Label(frame_COMinf,text="Stopbits: ")
        
        self.buttonSS = tk.Button(frame_COMinf, text = "Start", command = self.processButtonSS)
        self.buttonSS.grid(row = 3, column = 4, padx = 5, pady = 3, sticky = tk.E)

#stage 0 старт камеры, заход изменение убут для старта консоли линукс
#stage 1 заход в линукс, добавление ftp
#stage 2 старт камеры, заход в убут, возвращаем обычный старт камеры
#stage 3 дожидаемся старта камеры, удаляем файл веба, 
#stage 4 копируем новый
#stage 5 старт камеры, заход изменение убут для старта консоли линукс
#stage 6 заход в линукс, удаление ftp из загрузки
#stage 7 старт камеры, заход в убут, возвращаем обычный старт камеры 
        stage_frame = tk.Frame(window)
        stage_frame.grid(row = 4, column = 1)
        stageSelect = tk.Frame(stage_frame)
        stageSelect.grid(row = 1, column = 1)

        self.stage0 = tk.BooleanVar()
        self.stage0.set(1)
        self.check0 = tk.Checkbutton(stage_frame, text='stage 0 старт камеры, заход изменение убут для старта консоли линукс',variable=self.stage0, onvalue=1, offvalue=0)#, command=print_selection)
        self.check0.grid(row = 1, column = 1, padx = 10, pady = 1, sticky = tk.W)
        
        self.stage1 = tk.BooleanVar()
        self.stage1.set(1)
        self.check1 = tk.Checkbutton(stage_frame, text='stage 1 заход в линукс, добавление ftp',variable=self.stage1, onvalue=1, offvalue=0)#, command=print_selection)
        self.check1.grid(row = 2, column = 1, padx = 10, pady = 1, sticky = tk.W)

        self.stage2 = tk.BooleanVar()
        self.stage2.set(1)
        self.check2 = tk.Checkbutton(stage_frame, text='stage 2 старт камеры, заход в убут, возвращаем обычный старт камеры',variable=self.stage2, onvalue=1, offvalue=0)#, command=print_selection)
        self.check2.grid(row = 3, column = 1, padx = 10, pady = 1, sticky = tk.W)

        self.stage3 = tk.BooleanVar()
        self.stage3.set(1)
        self.check3 = tk.Checkbutton(stage_frame, text='stage 3.1 дожидаемся старта камеры, удаляем файл веба',variable=self.stage3, onvalue=1, offvalue=0)#, command=print_selection)
        self.check3.grid(row = 4, column = 1, padx = 10, pady = 1, sticky = tk.W)

        self.stage4 = tk.BooleanVar()
        self.stage4.set(1)
        self.check4 = tk.Checkbutton(stage_frame, text='stage 3.2 копируем новый',variable=self.stage4, onvalue=1, offvalue=0)#, command=print_selection)
        self.check4.grid(row = 5, column = 1, padx = 10, pady = 1, sticky = tk.W)

        self.stage5 = tk.BooleanVar()
        self.stage5.set(1)
        self.check5 = tk.Checkbutton(stage_frame, text='stage 4 старт камеры, заход изменение убут для старта консоли линукс',variable=self.stage5, onvalue=1, offvalue=0)#, command=print_selection)
        self.check5.grid(row = 6, column = 1, padx = 10, pady = 1, sticky = tk.W)

        self.stage6 = tk.BooleanVar()
        self.stage6.set(1)
        self.check6 = tk.Checkbutton(stage_frame, text='stage 5 заход в линукс, удаление ftp из загрузки',variable=self.stage6, onvalue=1, offvalue=0)#, command=print_selection)
        self.check6.grid(row = 7, column = 1, padx = 10, pady = 1, sticky = tk.W)

        self.stage7 = tk.BooleanVar()
        self.stage7.set(1)
        self.check7 = tk.Checkbutton(stage_frame, text='stage 6 старт камеры, заход в убут, возвращаем обычный старт камеры',variable=self.stage7, onvalue=1, offvalue=0)#, command=print_selection)
        self.check7.grid(row = 8, column = 1, padx = 10, pady = 1, sticky = tk.W)

        IPSettings = tk.Frame(window)
        IPSettings.grid(row = 5, column = 1)
        #IPLabel =tk.Label(IPSettings,text="IP:")
        #IPLabel.grid(row = 1, column = 1, padx = 3, pady = 2, sticky = tk.W)
        self.camHost = tk.StringVar()
        self.ent = tk.Entry(IPSettings,textvariable = self.camHost,width=18,fg="blue",bd=3,selectbackground='violet')
        self.ent.insert(0,"192.168.0.51")
        self.ent.grid(row = 1, column = 1)
        print(self.camHost.get())

        frameRecv = tk.Frame(window)
        frameRecv.grid(row = 6, column = 1)
        labelOutText = tk.Label(frameRecv,text="Received Data:")
        labelOutText.grid(row = 1, column = 1, padx = 3, pady = 2, sticky = tk.W)
        frameRecvSon = tk.Frame(frameRecv)
        frameRecvSon.grid(row = 2, column =1)
        scrollbarRecv = tk.Scrollbar(frameRecvSon)
        self.OutputText = tk.Text(frameRecvSon, wrap = tk.WORD, width = 60, height = 20, yscrollcommand = scrollbarRecv.set)
        self.showConsole = tk.BooleanVar()
        self.showConsole.set(0)
        self.check8 = tk.Checkbutton(frameRecv, text='отображать вывод консоли',variable=self.showConsole, onvalue=1, offvalue=0)
        self.check8.grid(row = 4, column = 1)
       
        self.OutputText.configure(yscrollcommand=scrollbarRecv.set)
        scrollbarRecv.pack(side = tk.RIGHT, fill = tk.Y)
        self.OutputText.pack(side="left", fill="y", expand=True)
        # serial object
        self.ser = serial.Serial()
        # serial read threading
        self.ReadUARTThread = threading.Thread(target=self.ReadUART)
        self.ReadUARTThread.start()

        frameTrans = tk.Frame(window)
        frameTrans.grid(row = 7, column = 1)
        labelInText = tk.Label(frameTrans,text="To Transmit Data:")
        labelInText.grid(row = 1, column = 1, padx = 3, pady = 2, sticky = tk.W)
        frameTransSon = tk.Frame(frameTrans)
        frameTransSon.grid(row = 2, column =1)
        scrollbarTrans = tk.Scrollbar(frameTransSon)
        scrollbarTrans.pack(side = tk.RIGHT, fill = tk.Y)
        self.InputText = tk.Text(frameTransSon, wrap = tk.WORD, width = 60, height = 5, yscrollcommand = scrollbarTrans.set)
        self.InputText.pack()
        self.buttonSend = tk.Button(frameTrans, text = "Send", command = self.processButtonSend)
        self.buttonSend.grid(row = 3, column = 1, padx = 5, pady = 3, sticky = tk.E)
        window.mainloop()

 
    def processButtonSS(self):
        if (self.ser.isOpen()):
            self.ser.close()
            self.buttonSS["text"] = "Start"
            self.uartState = False
        else:
            # restart serial port
            self.setCondition()
            self.ser.port = self.COM.get()
            self.ser.baudrate = 115200
            print(self.ser.port)
            print(self.ser.baudrate)
            #self.Baudrate.get()
            
            strParity = self.Parity.get()
            if (strParity=="NONE"):
                self.ser.parity = serial.PARITY_NONE
            elif(strParity=="ODD"):
                self.ser.parity = serial.PARITY_ODD
            elif(strParity=="EVEN"):
                self.ser.parity = serial.PARITY_EVEN
            elif(strParity=="MARK"):
                self.ser.parity = serial.PARITY_MARK
            elif(strParity=="SPACE"):
                self.ser.parity = serial.PARITY_SPACE
                
            strStopbits = self.Stopbits.get()
            self.ser.timeout = 1
            if (strStopbits == "1"):
                self.ser.stopbits = serial.STOPBITS_ONE
            elif (strStopbits == "1.5"):
                self.ser.stopbits = serial.STOPBITS_ONE_POINT_FIVE
            elif (strStopbits == "2"):
                self.ser.stopbits = serial.STOPBITS_TWO
            
            try:
                self.ser.open()
            except:
                infromStr = "Can't open "+self.ser.port
                InformWindow(infromStr)
            
            if (self.ser.isOpen()): # open success
                self.buttonSS["text"] = "Stop"
                self.uartState = True

    def processButtonSend(self):
        if (self.uartState):
            strToSend = self.InputText.get(1.0,tk.END)
            bytesToSend = strToSend[0:-1].encode(encoding='ascii')
            self.ser.write(bytesToSend)
            print(bytesToSend)
        else:
            infromStr = "Not In Connect!"
            InformWindow(infromStr)

    def sendData(self, data):
        tmp=""
        tmp=data.encode(encoding='ascii')
        self.ser.write(tmp)
        self.ser.flush()
        #self.OutputText.insert(tk.END,tmp)
        #self.OutputText.see(tk.END)
        #self.OutputText.see(Tkinter.END)


    def warningOut(self,data):
        self.OutputText.insert(tk.END,data+"\n")
        self.OutputText.see(tk.END)

    def setCondition(self):
        while not self.q.empty():
            self.q.get()
        if(self.stage0.get()):
            print("будет выполняться старт камеры, заход изменение убут для старта консоли линукс")
            self.q.put(0)
        if(self.stage1.get()):
            print("будет выполняться заход в линукс, добавление ftp")
            self.q.put(1)
        if(self.stage2.get()):
            print("будет выполняться старт камеры, заход в убут, возвращаем обычный старт камеры")
            self.q.put(2)
        if(self.stage3.get()):
            print("будет выполняться дожидаемся старта камеры, удаляем файл веба")
            self.q.put(3)
        if(self.stage4.get()):
            print("будет выполняться копируем новый")
            self.q.put(4)
        if(self.stage5.get()):
            print("будет выполняться старт камеры, заход изменение убут для старта консоли линукс")
            self.q.put(5)
        if(self.stage6.get()):
            print("будет выполняться заход в линукс, удаление ftp из загрузки")
            self.q.put(6)
        if(self.stage7.get()):
            print("будет выполняться старт камеры, заход в убут, возвращаем обычный старт камеры")
            self.q.put(7)
        self.condition = self.q.get()
        print(self.condition)

    def setColor(self,var,col):
        if (var==0):
            self.check0["fg"] = col
        else:
            if (var==1):
                self.check1["fg"] = col
            else:
                if (var==2):
                    self.check2["fg"] = col
                else: 
                    if (var==3):
                        self.check3["fg"] = col
                    else:
                        if (var==4):
                            self.check4["fg"] = col
                        else:
                            if (var==5):
                                self.check5["fg"] = col
                            else:
                                if (var==6):
                                    self.check6["fg"] = col
                                else:
                                    if (var==7):
                                        self.check7["fg"] = col

    def setColorForAll(self,col):
        for i in range(8):
            self.setColor(i,col)

    def getCondition(self):
        self.condition = self.q.get()

    def getIP(self):
        return self.camHost.get()

    def ReadUART(self):
        print("Threading...")
        
        while True:
            #print(self.getIP())
            if (self.ser.isOpen()):
                try:
#stage 0 старт камеры, заход изменение убут для старта консоли линукс
#stage 1 заход в линукс, добавление ftp
#stage 2 старт камеры, заход в убут, возвращаем обычный старт камеры
#stage 3 дожидаемся старта камеры, удаляем файл веба, 
#stage 4 копируем новый
#stage 5 старт камеры, заход изменение убут для старта консоли линукс
#stage 6 заход в линукс, удаление ftp из загрузки
#stage 7 старт камеры, заход в убут, возвращаем обычный старт камеры 

                    ch = self.ser.readline().decode('ascii', 'ignore')
                    if(self.showConsole.get()):
                        self.OutputText.insert(tk.END,ch)
                        self.OutputText.see(tk.END)

                    self.setColor(self.condition,"green")
                    if( (ch.count("Err:   serial")==1) & ( (self.condition == 0) | (self.condition == 2) | (self.condition == 5) | (self.condition == 7) )) :
                        if( self.stage0.get() | self.stage2.get() | self.stage4.get() | self.stage6.get() ):
                            for i in range(5):
                                self.sendData(chr(17))
                            self.sendData("\n")

                            if ( (self.condition == 0) | (self.condition == 5) ):
                                time.sleep(1)
                                self.sendData("setenv bootargs mem=108M console=ttyAMA0,115200 root=/dev/mtdblock1 rootfstype=jffs2 mtdparts=hi_sfc:3M(boot),13M(rootfs) coherent_pool=2M init=/bin/sh\n")

                            if ( (self.condition == 2) | (self.condition == 7) ):
                                time.sleep(1)
                                self.sendData("setenv bootargs mem=108M console=ttyAMA0,115200 root=/dev/mtdblock1 rootfstype=jffs2 mtdparts=hi_sfc:3M(boot),13M(rootfs) coherent_pool=2M\n")

                            self.sendData("saveenv\n")
                            self.sendData("reset\n")
                        self.condition = self.q.get()
#                        if(self.condition == 7):


                    if( (ch.count("job control turned off")==1) & ((self.condition == 1) | (self.condition==6)) ):
                        self.sendData(" \n")
                        #включение ftp
                        if (self.condition == 1):
                            #self.sendData("echo  'telnetd &'  >> /etc/init.d/rcS\n")
                            self.sendData("echo  'tcpsvd 0.0.0.0 21 ftpd -w -v &'  >> /etc/init.d/rcS\n")
                            #добавление пользователя с правами root для доступа по телнет
                            #self.sendData("adduser -G root -S depadmin\n")
                            #self.sendData("echo -e '$d\nw\nq'| ed /etc/passwd\n")
                            #self.sendData("echo  'depadmin:x:0:0:Linux User,,,:/home/depadmin:/bin/sh'  >> /etc/passwd\n")
                            #self.sendData("echo -e 'depadmin\ndepadmin' | passwd depadmin\n")
                            self.sendData("reboot\n")
                        if (self.condition == 6):
                            #выключение ftp
                            self.sendData("echo -e '$d\nw\nq'| ed /etc/init.d/rcS\n") 
                        self.sendData("reboot -f\n")
                        self.condition = self.q.get()

                    if((ch.count("111111111")==1) & ( (self.condition==3) | (self.condition==4) ) ):
                        self.setColor(self.condition,"green")
                        if( self.condition==3 ):
                            Host=self.getIP()
                            file_path = Path('en.tar')
                            self.OutputText.insert(tk.END,"try to send ftp\n")
                            self.OutputText.see(tk.END)

                            ftpObject = FTP();                                      # Create an FTp instance
                            ftpResponse = ftpObject.connect(host=Host);   # Connect to the host
                            print(ftpResponse);
                            ftpResponse = ftpObject.login();                        # Login anonymously
                            print(ftpResponse);
                            ftpResponse = ftpObject.cwd("/web");                        # Change to a specific folder
                            print(ftpResponse);
                            ftpResponse = ftpObject.delete("en.tar");               # Delete a file
                            print(ftpResponse);
                            self.condition = self.q.get()
                        self.setColor(self.condition,"green")

                        if( self.condition==4 ):
                            sizeWritten = 0
                            file_path='./en.tar'
                            file = open(file_path, 'rb')
                            print ("transfer ended")
                            localfile='./en.tar'
                            remotefile='/web/en.tar'
                            with FTP(Host, "root", "") as ftp, open(localfile, 'rb') as file:
                                    ftp.storbinary(f'STOR {remotefile}', file)

                            self.condition = self.q.get()
                        self.warningOut("необходимо перегрузить камеру по питанию\n")
                        #self.OutputText.insert(tk.END,warn)
                        #self.OutputText.see(tk.END)
                    if(self.q.empty()):
                        self.warningOut("процедура прошивки окончена")
                        self.setColorForAll("black")

                except:
                    infromStr = "Something wrong in receiving."
                    InformWindow(infromStr)
                    self.ser.close() # close the serial when catch exception
                    self.buttonSS["text"] = "Start"
                    self.uartState = False
                   
mainGUI()
