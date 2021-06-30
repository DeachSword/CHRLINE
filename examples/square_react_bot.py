import random
from CHRLINE import *

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
                reactId = random.choice([2, 3, 4, 5, 6, 7])
                cl.reactToMessage(message[2], message[4], reactId)