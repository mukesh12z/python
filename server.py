#!/usr/bin/python

import sys,paramiko,xml.etree.ElementTree as ET,re,psycopg2 as ps,smtplib
from datetime import datetime
from Crypto.Cipher import DES

from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
import smtplib
import sys

from Crypto import Random
random_generator = Random.new().read

#read client details from client config xml on server side
e=ET.parse('client1.xml').getroot()
hostname = e.get('ip')
username= 'nikki'
password= 'nikki@123'
port    = e.get('port')

#read cpu and mem usage alert from client xml
alert_list = []
for type1 in e.findall('alert'):
    alert_list.append(type1.get('limit'));


list_read = []
#generate key for paramiko  
key1 = '/home/nikki/.ssh/id_rsa'

#command to execute on client side - put script in temp and execute it
com1 = "cp /home/nikki/nikki/python/pythonnetworking/unixcmd.py /var/tmp \n python /var/tmp/unixcmd.py "

#DB connection detail, used postgresql here
conn = ps.connect(database="testpython",user="nikki",password="nikki",host="localhost",port="5432")
cur = conn.cursor()

#Encryption details - used DES here
key='abcd1234'
des = DES.new(key, DES.MODE_ECB)

try:
#Connect to paramiko to execute client script
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    rsa_key = paramiko.RSAKey.from_private_key_file(key1)
    client.connect(hostname,port=port,username=username,password=password)
    stdin,stdout,stderr = client.exec_command(com1)

#read the encrypted output from client side output  , rstrip removes the extra space added
    result1 = stdout.read().rstrip()

    output1 = des.decrypt(result1) 

#write the decrypted data to a file 
    output = '\n'.join(item for item in output1.splitlines())
    outfile = open("outfile","w")
    outfile.write(output)
    outfile.close()
    client.close()
#    print("connection closed")

except (RuntimeError, TypeError, NameError):
    print("error executing Paramiko client")

#read the decrypted file 
infile = open("outfile","r")
x = []

for line in infile.readlines():
    x=re.sub(' +',' ',line).rstrip().split(" ")    
    list_read.append(x)

#read mem_usage and cpu_usage from decrypted values
mem_usage = (float(list_read[2][6])/float(list_read[2][1]))

cpu_usage = (float(100-float(list_read[8][12])))

date1 = datetime.now()

#insert values into table
try:
    cur.execute('insert into usage values(%s,%s,%s,%s)',(hostname,date1,mem_usage*100,cpu_usage))
    cur.close()
except psycopg2.DatabaseError as error:
    print(error)

#convert 50% into float 50 value for comparison purpose
mem_alert = alert_list[0].replace("%","")
cpu_alert = alert_list[1].replace("%","")
mem_alert1 = float(mem_alert)

#Mail sending part

#assumption- the event log is the output of commands run at client
gmail_user = "mukeshp12z@gmail.com"
gmail_pwd= "clement_12z"
FROM = "mukeshp12z@gmail.com"
TO = "mukesh.pusola@gmail.com"

message = "PFA the event log"

if ((mem_usage*100 > mem_alert) and (cpu_usage > cpu_alert)):
    message = message + " \n mem exceeded :" + str(mem_usage*100) + "\n cpu exceeded:" + str(cpu_usage)
if mem_usage*100 > mem_alert:
    message = message + "\n mem exceeded :" + str(mem_usage*100)
if cpu_usage > cpu_alert:
    message = message + "\n cpu exceeded :" + str(cpu_usage)
try:
    content = MIMEText(message, "plain")
    msg = MIMEMultipart('mixed')
    msg["From"] = "mukeshp12z@gmail.com"
    msg["To"] = "mukesh.pusola@gmail.com"
    msg["Subject"] = "System statistics"
    msg.attach(content)
    filename1 = "outfile"
    f = open(filename1,"r")
    attachment = MIMEText(f.read())
    attachment.add_header("Content-Disposition","attachment",filename=filename1)
    msg.attach(attachment)
    s = smtplib.SMTP("smtp.gmail.com",587)
    s.starttls()
    s.login(gmail_user,gmail_pwd)
    s.sendmail(FROM,TO,msg.as_string())

    s.close()
except:
    print("failed to send mail")



