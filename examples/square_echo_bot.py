from CHRLINE.CHRLINE import *

cl = CHRLINE(device="IOSIPAD")
print(cl.authToken)

events = cl.fetchMyEvents()
while True:
    events = cl.fetchMyEvents(syncToken=events[3])
    for e in events[2]:
        print(e)
        if e[3] == 29:
            message = e[4][30][2][1]
            if not cl.squareMemberIdIsMe(message[1]):
                if message.get(10) is not None:
                    cl.sendSquareMessage(message[2], message[10])