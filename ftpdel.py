# Example Python program that deletes a file
# from an FTP server
from ftplib import FTP

ftpObject = FTP(); 										# Create an FTp instance
ftpResponse = ftpObject.connect(host="192.168.0.51");	# Connect to the host
print(ftpResponse);
ftpResponse = ftpObject.login("root");						# Login anonymously
print(ftpResponse);
ftpResponse = ftpObject.cwd("/web");						# Change to a specific folder
print(ftpResponse);
ftpResponse = ftpObject.delete("en.tar");				# Delete a file
print(ftpResponse);