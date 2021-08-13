from ftplib import FTP
import os.path

# Init
sizeWritten = 0
file_path='./en.tar'
print('Total file size : ' + str(round(os.path.getsize(file_path) / 1024 / 1024 ,1)) + ' Mb')

# Open FTP connection
ftp = FTP('192.168.0.51')
ftp.login('root','')

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

uploadTracker = FtpUploadTracker(int(os.path.getsize(file_path)))
file = open(file_path, 'rb')
ftp.storbinary('STOR /web/en.tar', file, 1024, uploadTracker.handle)
print ("transfer ended")