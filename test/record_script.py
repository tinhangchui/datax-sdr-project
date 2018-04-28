import telnetlib
import time
def sendMsg(msg):
    """
    Send msg to gqrx, assume gqrx has opened the server
    """
    tn = telnetlib.Telnet('127.0.0.1', 7356)
    tn.write(('%s\n' % msg).encode('ascii'))
    response = tn.read_some().decode('ascii').strip()
    tn.write('c\n'.encode('ascii'))
    return response

for i in range(200):
    sendMsg('AOS')              #send start recording signal
    print('start recording' + str(i))
    time.sleep(1)           #record for 5 sec
    print('stop recording' + str(i))
    sendMsg('LOS')              #send stop recording signal
