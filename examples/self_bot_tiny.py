from CHRLINE.CHRLINE import *

cl = CHRLINE(device="IOSIPAD") # first login for get AuthToken
#cl = CHRLINE("authToken", device="IOSIPAD") # type the AuthToken
print(f"AuthToken: {cl.authToken}") # AuthToken, save it, and use CHRLINE(authToken, device="IOSIPAD")

cl.custom_data['admin'] = cl.custom_data.get('admin', []) # init the admin data

def bot(op, cl):
    if op[3] == 25:
        # SEND MESSAGE
        msg = op[20]
        to = msg[2]
        if msg[15] == 0:
            # TEXT MESSAGE
            text = msg[10].lower()
            if text == 'setting':
                cl.sendMessage(to, f"[CHRLINE SELF BOT]\nAdmin: {len(cl.custom_data.get('admin', []))}人\nAuto Join: {'On' if cl.custom_data.get('auto_join_chat', False) else 'Off'}")
            elif text == 'aj':
                cl.custom_data['auto_join_chat'] = not cl.custom_data.get('auto_join_chat', False)
                cl.saveCustomData()
                cl.sendMessage(msg[2], f"ok -> {cl.custom_data['auto_join_chat']}")
        elif msg[15] == 1:
            # IMAGE MESSAGE
            objId = msg[4] # this is msgId = objId, u can use it to dl the image
            cl.sendMessage(to, 'IMAGE!')
        # 2 = VIDEO
        # 3 = AUDIO...
    elif op[3] == 26:
        # RECEIVE MESSAGE
        msg = op[20]
        sender = msg[1]
        if msg[15] == 0:
            text = msg[10]
            if sender in cl.custom_data.get('admin', []):
                if text == "test":
                    cl.sendMessage(to, 'pong! this is admin only!')
            else:
                if text == "dearsakura":
                    cl.custom_data['admin'].append(sender)
                    cl.saveCustomData() #save the data
                    cl.sendMessage(to, 'You are now admin!')
    elif op[3] == 124:
        # INVITE NOTIFY
        if cl.profile[1] in op[12]:
            if cl.custom_data.get('auto_join_chat', False):
                cl.acceptChatInvitation(op[10]) # auto join chat

cl.trace(bot) # BOT 使動