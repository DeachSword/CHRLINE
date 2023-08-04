from CHRLINE import *


# cl = CHRLINE(IOS_TOKEN, device='IOS', version="13.11.0", os_name="iPadOS", os_model="iPad5,1", os_version="15.7.2")
cl = CHRLINE()

SQ_CHAT_MID = "m..."
LIVE_TALK_TITLE = "Hi -BAO-!"

# create
LV = cl.acquireLiveTalk(SQ_CHAT_MID, LIVE_TALK_TITLE)
LiveTalk = cl.checkAndGetValue(LV, "liveTalk", 1)
squareChatMid = cl.checkAndGetValue(LiveTalk, "squareChatMid", 1)
sessionId = cl.checkAndGetValue(LiveTalk, "sessionId", 2)

# join
JoinLiveTalkResponse = cl.joinLiveTalk(squareChatMid, sessionId, False)

# voip
# todo by yourself
