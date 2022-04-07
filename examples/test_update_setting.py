# -*- coding: utf-8 -*- 
from CHRLINE import *

cl = CHRLINE()

def testUpdatePrivacyReceiveMessagesFromNotFriend(cl, enabled=True):
    set = {}
    set[26] = enabled
    cl.updateSettingsAttributes2(set, [25])