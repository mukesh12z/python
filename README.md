# python
This project is to collect system usage (memory/cpu) at client machines and raise alert through mail if crosses a limit and to send these statistics irrescpective .
It uses various concepts 
1- Networking with paramiko - socket programming
2- smtplib for mail
3- Postgresql for data entry of usage
4- Pycrypto DES encryption for sending client data back to server
