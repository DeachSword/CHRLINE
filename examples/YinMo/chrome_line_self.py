from CHRLINE import *
import concurrent.futures
import time
import re
import json
import random

cl = CHRLINE(device="IOSIPAD")
TOKEN = cl.authToken
print(TOKEN)

MID_REGEX = re.compile(r'u[a-f0-9]{32}')
GID_REGEX = re.compile(r'c[a-f0-9]{32}')
RID_REGEX = re.compile(r'r[a-f0-9]{32}')
ALLIDS_REGEX = re.compile(r'[ucr][a-f0-9]{32}')

LAST_CODA = {}


def bot(op, cl):
    if op[3] == 25 or op[3] == 26:
        msg = op[20]
        if msg[3] == 2 or msg[3] == 0:
            if msg[15] == 0 and op[3] == 26:
                metadata = msg.get(18, {})
                if 'MENTION' in metadata:
                    key = eval(metadata["MENTION"])
                    tags = key["MENTIONEES"]
                    isTagMe = False
                    for tag in tags:
                        if tag['M'] == cl.profile[1]:
                            isTagMe = True
                    if isTagMe:
                        oid = random.choice([
                            ['linekeep_1374325027750922ce2955t0d90575a', 'q21Pe18'],
                            ['linekeep_13743262861221229a2074t0d905801', 'l29P0Dp'],
                            ['linekeep_1374330133590122224352t0d905a01', 'A9XMb05'],
                            ['linekeep_1379024163553822903554t0d9b44bb', '1MNbxDq'],
                            ['linekeep_13790235166975224b5861t0d9b444c', 'dKjyNoA']
                        ])
                        #print(cl.forwardKeepObjectMsg(msg[2], oid[0], oid[1], 'audio'))
                        #print(cl.forwardKeepObjectMsg(msg[2], 'linekeep_13743262861221229a2074t0d905801', 'l29P0Dp', 'audio'))
                if msg[10][:5] == '範圍更新：':
                    a = msg[10][5:].split(' ~ ')
                    a1 = int(a[0])
                    a2 = int(a[1])
                    c = int((a2 - a1) / 2) + a1
                    cl.sendMessage(msg[2], f'!coda:{c}')
            if msg[15] == 0 and op[3] == 25:
                text = msg[10].lower()
                FIND_MIDS = re.findall(MID_REGEX, text)
                if text == cl.custom_data.get('cmd_test', 'test') or text == cl.custom_data.get('cmd_ping', 'ping'):
                    cl.sendMessage(msg[2], 'pong!')
                elif text == 'hi':
                    cl.sendMessage('c7bb0199d949fee69dd445eaad321cd2b', msg[2])
                elif text == 'ya':
                    print(cl.forwardKeepObjectMsg(
                        msg[2], 'linekeep_b7f72cfc6b7440a585969a736a77be86_22237459t0d897a85', 'KDv95ox', 'image'))
                elif text == 'peko':
                    print(cl.forwardKeepObjectMsg(
                        msg[2], 'linekeep_132062747076012265326t0d149655', '2nRaD5V', 'video'))
                elif text == 'ok':
                    print(cl.forwardKeepObjectMsg(
                        msg[2], 'linekeep_137564120438671a11522t0d935c82', 'PqodBoy', 'image'))
                elif text == '狗狗':
                    print(cl.forwardKeepObjectMsg(
                        msg[2], 'linekeep_1374325027750922ce2955t0d90575a', 'q21Pe18', 'audio'))
                elif text == 'lct':
                    print(cl.issueChannelToken())
                elif text == 'ccmd' or text[:5] == 'ccmd ':
                    reply = "ccmd (cmd key) (custom cmd)\nccmd reset"
                    if msg[10] != reply:
                        cmds = text.split(" ", 2)
                        print(cmds)
                        if len(cmds) > 1 and cmds[1] == 'reset':
                            resi = 0
                            for i in cl.custom_data.copy().keys():
                                if i.startswith('cmd_'):
                                    print(i)
                                    del cl.custom_data[i]
                                    resi += 1
                            reply = f"ok\nTotal: {resi}"
                            cl.saveCustomData()
                        else:
                            if len(cmds) == 3:
                                if cmds[1] == "fku" and cmds[2].startswith('bao '):
                                    _cmds = cmds[2].split(" ", 1)
                                    print(_cmds)
                                    cmds = [
                                        cmds[0], f"{cmds[1]} {_cmds[0]}", _cmds[1]]
                                old_cmd = cmds[1]
                                if cmds[2] != 'ccmd':
                                    if f'cmd_{cmds[1]}' in cl.custom_data:
                                        old_cmd = cl.custom_data[f'cmd_{cmds[1]}']
                                    cl.custom_data[f'cmd_{cmds[1]}'] = cmds[2]
                                    reply = f"ok\n{old_cmd} -> {cmds[2]}"
                                    cl.saveCustomData()
                                else:
                                    reply = f"'ccmd' is bad idea (|||ﾟдﾟ)"
                        cl.sendMessage(msg[2], reply)
                elif text == '鴻':
                    cl.sendMessage(msg[2], '大帥哥')
                elif text == 'testupimg':
                    id = cl.uploadMultipleImageToTalk([r'./308287559270924288.png', r'./150530084_447564919901294_5636071206788309314_n.jpg',
                                                      r'./683246971536146457.png', r'./150530084_447564919901294_5636071206788309314_n.jpg', r'./1587620544514.jpg'], msg[2])
                    cl.sendMessage(msg[2], f"IMG GID: {id}")
                elif text == 'testkp':
                    print(cl.forwardKeepObjectMsg(
                        msg[2], 'linekeep_136416779593541a0d4945t0d790912', 'e21qpDo', 'audio'))
                elif text == 'testkp2':
                    oid = random.choice([
                        ['linekeep_1374325027750922ce2955t0d90575a', 'q21Pe18'],
                        ['linekeep_13743262861221229a2074t0d905801', 'l29P0Dp'],
                        ['linekeep_1374330133590122224352t0d905a01', 'A9XMb05']
                    ])
                    print(cl.forwardKeepObjectMsg(
                        msg[2], oid[0], oid[1], 'audio'))
                elif text == 'testbao':
                    _tl = cl.getTimelintTab()
                    feedData = _tl['feedData']
                    for feedContent in feedData:
                        indices = feedContent['feedContent']['indices']
                        for story in indices:
                            story = story['data']
                            cl.sendMessage(
                                msg[2], f'[限動活動]\n\n舉辦人: {story["profile"]["displayName"]}\n活動項目: {story["profile"]["label"]}\n\n限動Id: line://story/contentView?contentId={story["storyId"]}')
                    feedList = _tl['feedList']
                    feeds = feedList['feeds']
                    for feed in feeds:
                        if feed['feedInfo']['type'] == 'RECOMMEND_ACCOUNTS':
                            cl.sendMessage(msg[2], '以下為推薦帳號')
                            for account in feed['recommendAccounts']['accounts']:
                                cl.sendContact(
                                    msg[2], account['userInfo']['mid'])
                elif text == cl.custom_data.get('cmd_sp', 'sptest'):
                    a = time.time()
                    cl.sendMessage(msg[2], '測速中...')
                    b = time.time()
                    cl.sendMessage(msg[2], '%s秒...' % (b-a))
                elif text.startswith(cl.custom_data.get('cmd_nk', 'nk')) and msg[3] == 2:
                    name = msg[10][len(
                        cl.custom_data.get('cmd_nk', 'nk')) + 1:]
                    if name:
                        a = cl.getGroup(msg[2])[20]
                        for user in a:
                            if name in user[22]:
                                cl.deleteOtherFromChat(msg[2], user[1])
                        cl.sendMessage(msg[2], '完成')
                    else:
                        cl.sendMessage(msg[2], 'empty string')
                elif text.startswith(cl.custom_data.get('cmd_mk', 'mk')) and msg[3] == 2:
                    metadata = msg[18]
                    reply = msg[1]
                    if 'MENTION' in metadata:
                        key = eval(metadata["MENTION"])
                        tags = key["MENTIONEES"]
                        for tag in tags:
                            cl.deleteOtherFromChat(msg[2], tag['M'])
                        cl.sendMessage(msg[2], '完成')
                    else:
                        cl.sendMessage(msg[2], '沒有目標')
                elif text == cl.custom_data.get('cmd_koa', 'koa') and msg[3] == 2:
                    a = cl.getGroup(msg[2])
                    for b in a[20]:
                        if 34 in b and b[34]:
                            cl.deleteOtherFromChat(msg[2], b[1])
                            time.sleep(0.5)
                    for b in a[22]:
                        if 34 in b and b[34]:
                            cl.cancelChatInvitation(msg[2], b[1])
                            time.sleep(0.5)
                    cl.sendMessage(msg[2], '完成')
                elif text == cl.custom_data.get('cmd_fku bao', 'fku bao') and msg[3] == 2:
                    cl.sendMessage(msg[2], '功能維護中')
                elif text == 'logout':
                    for i in SUB_BOTS.copy():
                        if i == cl:
                            cl.sendMessage(msg[2], 'ok')
                            cl.is_login = False
                            saveSubBots()
                elif text == cl.custom_data.get('cmd_wbm', 'wbm'):
                    if msg[3] == 1:
                        a = cl.getRoomsV2([msg[2]])[0][40]
                    elif msg[3] == 2:
                        a = cl.getGroupsV2([msg[2]])[0][40]
                    else:
                        cl.sendMessage(msg[2], 'not support.')
                        return
                    mids = []
                    for mid in a:
                        res = cl.canReceivePresent(
                            'stickershop', '13965279', mid)
                        if 'code' in res['error']:
                            if res['error']['code'] == 16646:
                                mids.append(mid)
                    if mids:
                        for mid in mids:
                            cl.sendMessage(msg[2], msg[1], 13, {"mid": mid})
                    else:
                        cl.sendMessage(msg[2], 'ないよ')
                elif text == cl.custom_data.get('cmd_tagall', 'tagall'):
                    if msg[3] == 1:
                        a = cl.getRoomsV2([msg[2]])[0][40]
                    elif msg[3] == 2:
                        a = cl.getGroupsV2([msg[2]])[0][40]
                    else:
                        cl.sendMessage(msg[2], 'not support.')
                        return
                    reply = '@n' * 20
                    arr = []
                    i = 0
                    arrs = []
                    for b in a:
                        arr.append({
                            "S": str(i * 2),
                            "E": str(i * 2 + 2),
                            "M": b
                        })
                        i += 1
                        if i == 20:
                            arrs.append(arr)
                            arr = []
                            i = 0
                    if len(arr) > 0:
                        arrs.append(arr)
                    for _arr in arrs:
                        _ri = 10240 - len(reply)
                        reply += 'fku bao' * 142
                        sticonId = random.choice(["008", "009", "011", "021"])
                        contentMetadata = {'MENTION': str('{"MENTIONEES":' + json.dumps(_arr) + '}'), 'REPLACE': '{"sticon":{"resources":[{"S":0,"E":' + str(len(
                            reply)) + ',"version":5,"productId":"5ac1bfd5040ab15980c9b435","sticonId":"' + sticonId + '"}]}}', 'EMTVER': '4', 'STICON_OWNERSHIP': '["5ac1bfd5040ab15980c9b435"]'}
                        _cdi = 10240 - len(str(contentMetadata))
                        contentMetadata['mid'] = 'd'*1000
                        cl.sendMessage(
                            msg[2], reply, contentMetadata=contentMetadata)
                    cl.sendMessage(msg[2], 'hi o/')
                elif text == cl.custom_data.get('cmd_tran', 'tran'):
                    cl.custom_data['tran'] = not cl.custom_data.get(
                        'tran', True)
                    cl.saveCustomData()
                    cl.sendMessage(msg[2], f"ok -> {cl.custom_data['tran']}")
                elif text == cl.custom_data.get('cmd_aj', 'aj'):
                    cl.custom_data['auto_join_chat'] = not cl.custom_data.get(
                        'auto_join_chat', False)
                    cl.saveCustomData()
                    cl.sendMessage(
                        msg[2], f"ok -> {cl.custom_data['auto_join_chat']}")
                elif text == 'groom' and msg[3] == 1:
                    print(cl.getRoomsV2([msg[2]]))
                elif text == cl.custom_data.get('cmd_uo', 'uo') and msg[3] == 2:
                    cl.updateChatPreventedUrl(msg[2], False)
                elif text == cl.custom_data.get('cmd_uc', 'uc') and msg[3] == 2:
                    cl.updateChatPreventedUrl(msg[2], True)
                elif text == cl.custom_data.get('cmd_ut', 'ut') and msg[3] == 2:
                    a = cl.reissueChatTicket(msg[2])
                    if 1 in a:
                        cl.sendMessage(
                            msg[2], "https://line.me/R/ti/g/%s" % a[1])
                elif text == cl.custom_data.get('cmd_jn', 'jn'):
                    cl.custom_data['join_notify'] = not cl.custom_data.get(
                        'join_notify', False)
                    cl.saveCustomData()
                    cl.sendMessage(
                        msg[2], f"ok -> {cl.custom_data['join_notify']}")
                elif text.startswith(cl.custom_data.get('cmd_jnt', 'jnt')):
                    name = msg[10][len(
                        cl.custom_data.get('cmd_jnt', 'jnt')) + 1:]
                    if name:
                        cl.custom_data['join_notify_text'] = name
                        cl.saveCustomData()
                        cl.sendMessage(
                            msg[2], f"設定完成d(`･∀･)b\n\n並且你可以添加 @player ,它將會自動標註")
                    else:
                        cl.sendMessage(msg[2], 'empty string')
                elif text == 'login':
                    a = CHRLINE(device="IOSIPAD", noLogin=True)
                    for b in a.requestSQR():
                        cl.sendMessage(msg[2], b)
                    if a.authToken:
                        #_bot.sendMessage(msg[2], '登入成功')
                        print(a.authToken)
                        _sbot = CHRLINE(a.authToken, device="IOSIPAD")
                        _sbot.sendMessage(msg[2], '登入成功')
                        _sbot.trace(bot)
                elif text == 'help':
                    cl.sendMessage(msg[2], f'''CHRLINE API v1.2.0
*** FREE SELF BOT ***

- {cl.custom_data.get('cmd_sp', 'sp')} : res speed [key:sp]
- {cl.custom_data.get('cmd_test', 'test')} : ping and pong [key:test]
- {cl.custom_data.get('cmd_mk', 'mk')} @ : kick targets [key:mk]
- {cl.custom_data.get('cmd_nk', 'nk')}:(name) : kick users if include that name [key:nk]
- {cl.custom_data.get('cmd_fku bao', 'fku bao')} : kick all [key:fku bao]
- {cl.custom_data.get('cmd_tagall', 'tagall')} : tag all [key:tagall]
- login : share login url
- logout : log out
- {cl.custom_data.get('cmd_tran', 'tran')} : image ocr (def: True) [key:tran]
- {cl.custom_data.get('cmd_aj', 'aj')} : auto join chat (def: False) [key:aj]
- {cl.custom_data.get('cmd_uo', 'uo')} : open group url [key:uo]
- {cl.custom_data.get('cmd_uc', 'uc')} : close group url [key:uc]
- {cl.custom_data.get('cmd_ut', 'ut')} : issue group url [key:ut]
- {cl.custom_data.get('cmd_koa', 'koa')} : kick and cancel OA [key:koa]

- {cl.custom_data.get('cmd_jn', 'jn')} : join notify [key:jn]
- {cl.custom_data.get('cmd_jnt', 'jnt')} : join notify text [key:jnt]

- {cl.custom_data.get('cmd_wbm', 'wbm')} : check who block me on the group [key:wbm]

- ccmd : custom cmd

更多功能請聯繫
https://www.facebook.com/DeachSword.tw/''')
            elif msg[15] == 1:
                if op[3] == 26:
                    if msg[2] in ['c0f98b19ea2a9a7b56571218199efe8c5', 'cae695212dda33bb7b4bd852abebb5c41', 'c82e4b9367f74b23ccaab2d3a4f394b64']:
                        # cl.forwardObjectMsg(DEBUG_GID, msg[4]) # 備份
                        pass
                if cl.custom_data.get('tran', True):
                    tr = cl.trainingImage(msg[4])
                    if tr['code'] == 200:
                        if 'words' in tr['result']['OCR']['result']:
                            words = tr['result']['OCR']['result']['words']
                            if words:
                                words = [word['text'] for word in words]
                                cl.sendMessage(msg[2], '%s' % (
                                    words), relatedMessageId=msg[4])
    elif op[3] == 124 and cl.profile[1] in op[12]:
        if cl.custom_data.get('auto_join_chat', False):
            cl.acceptChatInvitation(op[10])
    elif op[3] == 130:
        if cl.custom_data.get('join_notify', False):
            # 入群體醒
            reply = "那、那個......@player 歡迎加入，女裝大......啊不！主、主人(つд⊂)！"
            if 'join_notify_text' in cl.custom_data:
                reply = cl.custom_data['join_notify_text']
            contentMetadata = None
            if '@player' in reply:
                cs = reply.find('@player')
                arr = [
                    {
                        "S": str(cs),
                        "E": str(cs + 7),
                        "M": op[11]
                    }
                ]
                contentMetadata = {'MENTION': str(
                    '{"MENTIONEES":' + json.dumps(arr) + '}')}
            #_bot.sendMessage(op[10], f"@chrline_api 你怎麼踢我兄弟!", contentMetadata= {'MENTION': str('{"MENTIONEES":' + json.dumps(arr) + '}')})
            cl.sendMessage(op[10], reply, contentMetadata=contentMetadata)


CoolingProcession = {}


def isCoolingTime(to, _from, cType, cTime):
    print(CoolingProcession)
    Cooling = False
    userId = _from
    if userId not in CoolingProcession:
        CoolingProcession[userId] = {}
    cKey = '%s-%s' % (to, cType)
    if cKey in CoolingProcession[userId]:
        if time.time() < CoolingProcession[userId][cKey]:
            Cooling = True
    else:
        CoolingProcession[userId][cKey] = time.time() + cTime
    return Cooling


cl.trace(bot)
