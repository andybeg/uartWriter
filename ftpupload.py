from ftplib import FTP
from pathlib import Path
import ftplib
import os

# FTP server credentials
FTP_HOST = "192.168.0.51"
FTP_USER = "root"
FTP_PASS = ""

#file_path = Path('/media/data/dev/python/uartWriter/en.tar')


#ftp = ftplib.FTP(FTP_HOST)
#ftp.set_pasv(False)
#ftp.login("root", "")
localfile='./en.tar'
remotefile='/web/en.tar'
#with open(localfile, "rb") as file:
#    ftp.storbinary('STOR %s' % remotefile, file)

with FTP("192.168.0.51", "root", "") as ftp, open(localfile, 'rb') as file:
        ftp.storbinary(f'STOR {remotefile}', file)
 
