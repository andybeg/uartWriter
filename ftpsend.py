from ftplib import FTP            
import sys,getpass,os.path    

import tkinter as Tkinter
from tkinter import ttk
import time
import threading


HOST = '192.168.0.51'  # ftp address
PORT = 21
TIMEOUT = 60  # overtime time
USER_NAME = 'root'  # ftp account
PASS_WORD = ''    # ftp password
BLOCK_SIZE = 1       # Data size uploaded per frame

file_name = ''          # Uploaded file name, for ui part display
file_size = 0           # Total file size, used when calculating progress
upload_size = 0         # Uploaded data size, used when calculating progress
bar = None              # Progress bar object

 
class PopupProgressBar:
    def __init__(self, title):
        self.title = title
        self.root = None
        self.bar = None
        self.bar_lock = threading.Lock()
        self.thread = None
        self.thread_upd = None
        self.is_stop_thread_upd = False
        self.value = 0
        self.text = ""
        self.labelText = None # Tkinter.StringVar()
        if not self.title:
            self.title = "PopupProgressBar"
 
    def start(self):
        print("start")
        self.thread = threading.Thread(target=PopupProgressBar._run_, args=(self,))
        self.thread.start()
    
    def _run_(self):
        root = Tkinter.Tk()
        root.geometry('500x80+500+200')
        root.title(self.title)
 
        self.labelText = Tkinter.StringVar()
        self.labelText.set(self.text)
 
        ft = ttk.Frame()
        ft.pack(expand=True, fill=Tkinter.BOTH, side=Tkinter.TOP)
 
        label1 = Tkinter.Label(ft, textvariable=self.labelText)
        label1.pack(fill=Tkinter.X, side=Tkinter.TOP)
 
        pb_hD = ttk.Progressbar(ft, orient='horizontal',length = 300, mode='determinate')
        pb_hD.pack(expand=True, fill=Tkinter.BOTH, side=Tkinter.TOP)
        
        self.root = root
        self.bar = pb_hD
        self.bar["maximum"] = 100
        self.bar["value"] = 0
    
        self.thread_upd = threading.Thread(target=PopupProgressBar._update_, args=(self,))
        self.thread_upd.start()

        self.root.mainloop()

 
    def _update_(self):
        while not self.is_stop_thread_upd:

            self.update_data(self.value)
            self.labelText.set(self.text)
            time.sleep(0.01)

        
 
    def update_data(self, value):
        if not self.bar:
            return
        if self.bar_lock.acquire():
            self.bar["value"] = value
            self.bar_lock.release()
 
    def stop(self):
        if self.thread_upd:
            self.is_stop_thread_upd = True

        
        self.thread_upd.join()

        self.root.quit()




# localfile Local file and path to be uploaded
# remotepath The path of the ftp server (ftp://192.168.1.8/xxx)
def upload_file(localfile, remotepath):
    global file_size
    global bar
    bar = PopupProgressBar('ftp upload file: ' + localfile)
    bar.start()

    cur_ftp = FTP()
    cur_ftp.connect(HOST, PORT, TIMEOUT)  # Connect to ftp server
    cur_ftp.login(USER_NAME, PASS_WORD)     # Log in to the ftp server
    cur_ftp.cwd(remotepath)                      # Set the path of the FTP server
    cur_file = open(localfile,'rb')             # Open local file
    file_size = os.path.getsize(localfile)
    cur_ftp.storbinary('STOR %s' % os.path.basename(localfile), cur_file, blocksize = BLOCK_SIZE, callback = upload_file_cb)  # Upload file to ftp server
    print('upload_file done')
    cur_file.close()             # Close local file
    cur_ftp.quit()                    # drop out
    

def upload_file_cb(block):
    global upload_size
    upload_size = upload_size + len(block)
    bar.value = upload_size/file_size *100
    bar.text = format(upload_size / file_size*100, '.2f') + '%'
    if bar.value >= 100:
        time.sleep(0.2)
        bar.stop()


if '__main__' == __name__:
    upload_file('./en.tar', '/web')
    print('ok')