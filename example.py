from CHRLINE import *

cl = CHRLINE()
#cl = CHRLINE(device="IOSIPAD", version="10.21.3", os_name="iOS", os_ver="11")#with IOSIPAD
#cl = CHRLINE("your email", "your password") #with Email
#cl = CHRLINE(phone="your phone number(0911....)", region="your phone region(TW ,JP, ID..)") #with phone number
token = cl.authToken
print(f"authToken: {token}")

print(cl.profile) # Profile
print(cl.sendMessage('uaff1346eb5adc4928c6b99cda0272226', 'hello world')) # send message

rev = cl.getLastOpRevision()
print(rev)
while True:
    Ops = cl.fetchOps(rev)
    for op in Ops:
        if op and 0 not in op and op[3] != 0: # dont ask why
            rev = max(rev, op[1]) # oh yes
            if op[3] == 26: # 25 = sent messages, 26 = received messages
                msg = op[20]
                if msg[15] == 0: # 0 = text, 1 = image....e.g.
                    if msg[10] == 'ping':
                        cl.sendMessage(msg[2], 'pong!')