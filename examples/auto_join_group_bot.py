from CHRLINE.CHRLINE import *

cl = CHRLINE()
print(cl.authToken)

def bot(op):
    if op[3] == 124 and cl.profile[1] in op[12]:
        # op[10] group id
        # op[11] inviter mid
        # op[12] invitee mids
        cl.acceptChatInvitation(op[10])

cl.trace(bot)