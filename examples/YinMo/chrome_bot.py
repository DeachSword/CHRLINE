# -*- coding: utf-8 -*- 
from CHRLINE import *
import re, time, threading, hashlib, random, sys, json, traceback
import logging
from datetime import datetime
import uuid

cl = CHRLINE(TOKEN, device="ANDROID")

BOTS = [cl]
BOT_MIDS = []
for _bot in BOTS:
    BOT_MIDS.append(_bot.mid)
#cl.updateProfileAttribute(2, "DeadSoup - NotifyBot")
#cl.updateProfileImage(r"./12a934653c06e5b150dea28487ced081.png")
#cl.updateProfileCover(r"./898cf628294dc7ba431dc1f7f2206841.jpeg")
datetime_dt = datetime.now()
datetime_format = datetime_dt.strftime("%Y/%m/%d %H:%M:%S")
for bot in BOTS:
    bot.updateProfileAttribute(16, f"Last Runtime\n{datetime_format}\n\nClient Lib\nCHRLINE (v1.4.1)\n\nProvider\nfacebook.com/DeachSword.tw")

MID_REGEX   = re.compile(r'(?<![a-f0-9])u[a-f0-9]{32}(?![a-f0-9])')
GID_REGEX   = re.compile(r'(?<![a-f0-9])c[a-f0-9]{32}(?![a-f0-9])')
RID_REGEX   = re.compile(r'(?<![a-f0-9])r[a-f0-9]{32}(?![a-f0-9])')
ALLIDS_REGEX= re.compile(r'(?<![a-f0-9])[ucr][a-f0-9]{32}(?![a-f0-9])')
LINETIME_REGEX = re.compile(r'(?<![0-9])(1[56][0-9]{11})(?![0-9])')

# ----- BOT SETTING ------
ADMIN = []
TAGNOTREPLY = {}
TAGNOTREPLY_MIN = 1
ENABLE_ALLID_REGEX = True
ENABLE_LINETIME_REGEX = True
SEND_MESSAGE_COOLING = {}
COOLING_TIME = 5
NOT_COOLING_TEXT = ['sp']
ANNOUNCEMENT_RECORD = []
# ----- ----------- ------

rec_msgs = []
def bot(op, cl):
    opType = op.get(3, 0)
    if opType == 2:
        #友資更新
        pass
    elif opType == 25:
        pass
    elif opType == 26:
        msg = op[20]
        msgId = msg[4]
        msgTime = msg[5]
        msgType = msg[15]
        msgMetadata = msg.get(18, {})
        if msg[3] == 0:
            cl.sendChatChecked(msg[1], msgId)
        elif msg[3] == 1:
            cl.leaveRoom(msg[2])
        elif msg[3] == 2:
            if msg[1] in BOT_MIDS:
                return
            cl = getInGroupBot(msg[2])
            if cl is None:
                return
            if msgId not in rec_msgs:
                rec_msgs.append(msgId)
            else:
                return
            if msgType == 0:
                text = msg[10].lower()
                ids = re.findall(ALLIDS_REGEX, msg[10])
                ttimes = re.findall(LINETIME_REGEX, msg[10])
                metadata = msg.get(18, {})
                if text not in NOT_COOLING_TEXT:
                    chatCooling = {}
                    if msg[2] in SEND_MESSAGE_COOLING:
                        chatCooling = SEND_MESSAGE_COOLING[msg[2]]
                    coolingUUID = f"{msg[1]}_{hashlib.md5(text.encode()).hexdigest()}"
                    if coolingUUID in chatCooling:
                        return
                    else:
                        nowTime = time.time()
                        chatCooling[coolingUUID] = nowTime
                        for _cck in list(chatCooling.keys()):
                            if nowTime - chatCooling[_cck] > COOLING_TIME:
                                del chatCooling[_cck]
                    SEND_MESSAGE_COOLING[msg[2]] = chatCooling
                if 'MENTION' in metadata:
                    key = eval(metadata["MENTION"])
                    tags = key["MENTIONEES"]
                    _tag = {}
                    for tag in tags:
                        _mid = tag['M']
                        if _mid != cl.profile[1]:
                            if _mid not in tag:
                                _tag[_mid] = []
                            _tag[_mid].append([msgId, msgTime])
                    if len(_tag) > 0:
                        if msg[2] not in TAGNOTREPLY:
                            TAGNOTREPLY[msg[2]] = {}
                        for tag in _tag:
                            if tag not in TAGNOTREPLY[msg[2]]:
                                TAGNOTREPLY[msg[2]][tag] = []
                            TAGNOTREPLY[msg[2]][tag] += _tag[tag]
                if len(ttimes) > 0:
                    record = []
                    reply = ''
                    for t in ttimes:
                        if t in record:
                            continue
                        else:
                            record.append(t)
                        _time = str(datetime.fromtimestamp(int(t) / 1000)).split('.', 2)[0]
                        if reply != '':
                            reply += '\n'
                        reply += f"{t}->{_time}"
                    if reply != '':
                        cl.sendMessage(msg[2], reply, relatedMessageId=msg[4])
                if len(ids) > 0:
                    maxSize = 100
                    b = [ids[i:i+maxSize] for i in range(0, len(ids), maxSize)]
                    reply = ""
                    mids = []
                    for _b in b:
                        a = cl.getChatExistence(_b)
                        if 'error' in a:
                            print(f'getChatExistence failed: {len(ids)}')
                        a = a[1]
                        for mid in a.keys():
                            if mid[0] == 'u':
                                if a[mid][1] == 0:
                                    mids.append(mid)
                                    continue
                            reply += f"* {mid[:6]}- "
                            if a[mid][1] == 0:
                                reply += "存在"
                            elif a[mid][1] == 1:
                                reply += "不存在"
                            elif a[mid][1] == 2:
                                reply += "曾經存在(已無成員)"
                            else:
                                reply += "未知?"
                            reply += "\n"
                    if len(mids) > 0 and len(mids) <= 5:
                        for m in mids:
                            cl.sendContact(msg[2], m)
                    if reply != "":
                        reply += f"\n共計 {len(a)}"
                        cl.sendMessage(msg[2], reply)
                if text == "test":
                    _bots = getInGroupBot(msg[2], getAll=True)
                    i = 1
                    for cl in _bots:
                        cl.sendMessage(msg[2], f'pong! - {i}')
                        i += 1
                elif text == 'gid':
                    cl.sendMessage(msg[2], msg[2])
                elif text == 'others':
                    for _bot in BOTS:
                        if msg[2] not in _bot.groups:
                            cl.sendContact(msg[2], _bot.mid)
                elif text == '彥彥好帥':
                    anns = cl.getChatRoomAnnouncements(msg[2])
                    for ann in anns:
                        print(ann)
                        annid = ann[1]
                        annType = ann[2]
                        if annType == 0:
                            annLink = f"line://nv/chatMsg?chatId={msg[2]}&messageId={msgId}"
                        else:
                            annLink = "https://www.deachsword.com/"
                        cl.updateChatRoomAnnouncement(msg[2], annid, annLink, '彥彥好帥')
                elif text == '鴻鴻好暈':
                    anns = cl.getChatRoomAnnouncements(msg[2])
                    for ann in anns:
                        print(ann)
                        annid = ann[1]
                        annType = ann[2]
                        if annType == 0:
                            annLink = f"line://nv/chatMsg?chatId={msg[2]}&messageId={msgId}"
                        else:
                            annLink = "https://www.deachsword.com/"
                        cl.updateChatRoomAnnouncement(msg[2], annid, annLink, '鴻鴻好暈')
                elif text == '鴻':
                    cl.sendMessage(msg[2], '大帥哥')
                elif text == '彥彥':
                    cl.forwardKeepObjectMsg(msg[2], 'linekeep_44415c469d20305174a8884f673d569f_22895235t0bcdfd00', 'zMB5P5Z', 'audio')
                elif text == 'sp':
                    a = time.time()
                    cl.sendMessage(msg[2], '測速中...')
                    b = time.time()
                    cl.sendMessage(msg[2], '%s秒...' % (b-a))
                elif text.startswith("getdata") and msg[3] == 2:
                    try:
                        count = text[7:]
                        if count == '':
                            msgid = msg.get(21)
                            if msgid != None:
                                msgids = cl.getPreviousMessageIds(msg[2], 32767)
                                target_msg = None
                                for i in msgids[1]:
                                    if msgid == str(i[2]):
                                        target_msg = i
                                        break
                                if target_msg is not None:
                                    target_msg = cl.getPreviousMessagesV2(msg[2], target_msg[1], target_msg[2])[0]
                                    target_msg[17] = "fk u bao"
                                    cl.sendMessage(msg[2], target_msg, relatedMessageId=msgid)
                                else:
                                    cl.sendMessage(msg[2], "過期")
                            else:
                                count = 1
                        if count != '':
                            count = int(count)
                            msgids = cl.getPreviousMessageIds(msg[2], count + 10)
                            msgids = msgids[1]
                            msgidc = len(msgids)
                            cl.sendMessage(msg[2], f'找尋{count}')
                            if msgidc >= count:
                                target_msg = msgids[count-1]
                                isFound = False
                                currI = 0
                                for i in msgids:
                                    if str(i[2]) == msg[4]:
                                        isFound = True
                                    else:
                                        if isFound:
                                            currI += 1
                                            if currI == count:
                                                target_msg = i
                                                break
                                target_msgid = target_msg[2]
                                cl.sendMessage(msg[2], '這裡', relatedMessageId=target_msgid)
                                target_msg = cl.getPreviousMessagesV2(msg[2], target_msg[1], target_msg[2])[0]
                                target_msg[17] = "fk u bao" # overwrite content view for image or video...
                                cl.sendMessage(msg[2], target_msg, relatedMessageId=target_msgid)
                            else:
                                cl.sendMessage(msg[2], "過期")
                    except Exception as e:
                        cl.sendMessage(msg[2], f'必須是數字: {count}')
                elif text == 'help':
                    tagnotifytime = cl.custom_data.get('tagnotifytime', {}).get(msg[2], 60 * TAGNOTREPLY_MIN)
                    reply = f"DeachSword Reply Notify Bot v1.1\n\nreviewmsg - 防收回(Text only)\nnotagnotify - not notify if read\nReactNotify - 表情反應通知\n\ntagnotifytime - notify if read time over (curr: {tagnotifytime}sec)"
                    cl.sendMessage(msg[2], reply)
                elif text.startswith('tagnotifytime'):
                    _time = text[14:]
                    reply = f"用法:\n{text[:13]}:time"
                    if _time != '':
                        try:
                            _time = int(_time)
                            if _time >= 5:
                                bots = getInGroupBot(msg[2], getAll=True)
                                for _bot in bots:
                                    if 'tagnotifytime' not in _bot.custom_data:
                                        _bot.custom_data['tagnotifytime'] = {}
                                    _bot.custom_data['tagnotifytime'][msg[2]] = _time
                                    _bot.saveCustomData()
                                reply = f"Success! 相關訊息經 {_time} 秒以上未讀時將被提醒!\n\n※這是該群組的共同設定, 並非個人化設定"
                            else:
                                reply = f"數值不正: {_time}, 應為 5 秒以上"
                        except:
                            reply = f"非法數值: {_time}"
                    cl.sendMessage(msg[2], reply)
                elif text == 'notagnotify':
                    bots = getInGroupBot(msg[2], getAll=True)
                    isFirst = False
                    for _bot in bots:
                        if 'notagnotify' not in _bot.custom_data:
                            _bot.custom_data['notagnotify'] = []
                        if not isFirst:
                            nowset = True if msg[2] in _bot.custom_data['notagnotify'] else False
                            _bot.sendMessage(msg[2], f"當前設置: {nowset}")
                            isFirst = True
                        if nowset:
                            if msg[2] in _bot.custom_data['notagnotify']:
                                _bot.custom_data['notagnotify'].remove(msg[2])
                                _bot.sendMessage(msg[2], f"移除設定")
                        else:
                            if msg[2] not in _bot.custom_data['notagnotify']:
                                _bot.custom_data['notagnotify'].append(msg[2])
                                _bot.sendMessage(msg[2], f"添加設定")
                        _bot.saveCustomData()
                        _bot.sendMessage(msg[2], f"成功{'Removed' if nowset else 'Added'}此群組至標註提醒排除名單")
                elif text == 'testnf':
                    videos = cl.getYouTubeVideosWithQuery()
                    items = videos.get("items", [])
                    reply = f"共 {len(items)} 筆資料"
                    ids = []
                    for item in items:
                        ids.append(item['id']['videoId'])
                    videos2 = cl.getYouTubeVideos(ids)
                    cl.sendMessage(msg[2], reply)
                elif text == 'testnf2':
                    videos = cl.getYouTubeVideos()
                    cl.sendMessage(msg[2], f"{videos}")
                elif text == 'reactnotify':
                    bots = getInGroupBot(msg[2], getAll=True)
                    isFirst = False
                    for _bot in bots:
                        if 'reactnotify' not in _bot.custom_data:
                            _bot.custom_data['reactnotify'] = []
                        if not isFirst:
                            nowset = True if msg[2] in _bot.custom_data['reactnotify'] else False
                            isFirst = True
                        if nowset:
                            if msg[2] in _bot.custom_data['reactnotify']:
                                _bot.custom_data['reactnotify'].remove(msg[2])
                        else:
                            if msg[2] not in _bot.custom_data['reactnotify']:
                                _bot.custom_data['reactnotify'].append(msg[2])
                        _bot.saveCustomData()
                        _bot.sendMessage(msg[2], f"成功{'Removed' if nowset else 'Added'}此群組至表情提醒名單")
                elif text == 'reviewmsg':
                    bots = getInGroupBot(msg[2], getAll=True)
                    isFirst = False
                    for _bot in bots:
                        if 'reviewMsg' not in _bot.custom_data:
                            _bot.custom_data['reviewMsg'] = []
                        if not isFirst:
                            nowset = True if msg[2] in _bot.custom_data['reviewMsg'] else False
                            isFirst = True
                        if nowset:
                            if msg[2] in _bot.custom_data['reviewMsg']:
                                _bot.custom_data['reviewMsg'].remove(msg[2])
                        else:
                            if msg[2] not in _bot.custom_data['reviewMsg']:
                                _bot.custom_data['reviewMsg'].append(msg[2])
                        _bot.saveCustomData()
                        _bot.sendMessage(msg[2], f"成功{'Removed' if nowset else 'Added'}此群組至防收回名單\n目前僅供文字訊息")
                elif text.startswith("cmd:") and msg[1] in ADMIN:
                    reply = execAndWaitOutput(text)
                    cl.sendMessage(msg[2], reply)
                elif msg.get(21) != None and opType == 26:
                    _msgid = msg[21]
                    msgids = cl.getPreviousMessageIds(msg[2], 100)
                    target_msg = None
                    for i in msgids[1]:
                        if _msgid == str(i[2]):
                            target_msg = i
                            break
                    if target_msg is not None:
                        target_msg = cl.getPreviousMessagesV2(msg[2], target_msg[1], target_msg[2])[0]
                        if target_msg[1] not in [msg[1], cl.profile[1]]:
                            if msg[2] not in TAGNOTREPLY:
                                TAGNOTREPLY[msg[2]] = {}
                            if target_msg[1] not in TAGNOTREPLY[msg[2]]:
                                TAGNOTREPLY[msg[2]][target_msg[1]] = []
                            TAGNOTREPLY[msg[2]][target_msg[1]] += [[msgId, msgTime]]
                    else:
                        pass
            elif msgType == 1:
                # {'NOTIFICATION_DISABLED': 'false', 'GTOTAL': '5', 'GID': '14413068866269', 'SRC_SVC_CODE': 'talk', 'OBS_POP': 'kr-1', 'GSEQ': '3'}
                if 'GID' in msgMetadata:
                    if msgMetadata.get('GTOTAL', '999') != msgMetadata.get('GSEQ', '888'):
                        return
                if 'DOWNLOAD_URL' in msgMetadata:
                    return
                tr = cl.trainingImage(msg[4])
                if tr['code'] == 200:
                    if 'words' in tr['result']['OCR']['result']:
                        words = tr['result']['OCR']['result']['words']
                        if words:
                            words = [word['text'] for word in words]
                            reply = None
                            
                            # ARCAEA
                            # ['結果', '同步', 'MimiOuO', '12.83', '194', 'POTENTIAL', '-KEEP-', '4386', '記憶源點', '10', 'MAX RECALL', '1086', 'Future 10', '100', 'Tiferet', 'xi + Sta', 'PUREMEMORY', "10'001'062", 'HIGH SCORE', "10'001'027", 'EX+', 'PURE 108', 'FAR', 'LOST', '+00000035', '夥伴', 'x1.4', '返回', '分享', 'REWARD', '過關10', '精彩展現21', '殘片', '43', '重試']
                            arc_ck = 0
                            for i in range(len(words)):
                                if 'POTENTIAL' in words[i]:
                                    arc_ck = i
                                    break
                            if arc_ck > 0:
                                arc_name = words[arc_ck - 1]
                                if words[:2] == ['結果', '同步'] and arc_ck - 1 != 2:
                                    arc_name = words[2]
                                if arc_name in ['結果', '同步']:
                                    arc_name = None
                                else:
                                    arc_name = f'玩家: {arc_name}\n'
                                arc_pp = words[arc_ck + 1]
                                arc_rank = None
                                if arc_ck - 1 != 2 and arc_ck != 3:
                                    arc_pp = words[3]
                                    if arc_ck != 4:
                                        arc_rank = words[4]
                                if '.' not in arc_pp:
                                    arc_pp = None
                                else:
                                    arc_pp = f'PP: {arc_pp}\n'
                                hs_ck = words.index('HIGH SCORE')
                                hs_str = None
                                pm_type_def = ['PUREMEMORY', 'FULLRECALL', 'TRACKLOST', 'TRACKCOMPLETE']
                                pm_type_name = ['P', 'F', 'L', 'C']
                                if hs_ck > 0:
                                    pm_type = words[hs_ck - 2].replace(' ', '')
                                    hs_now = words[hs_ck - 1]
                                    hs_last = words[hs_ck + 1]
                                    if "'" in hs_now and "'" in hs_last:
                                        hs_now_c = int(hs_now.replace('\'', '').replace(',', ''))
                                        hs_last_c = int(hs_last.replace('\'', '').replace(',', ''))
                                        hs_diff = hs_now_c - hs_last_c
                                        hs_str = f"成績{f'[{pm_type_name[pm_type_def.index(pm_type)]}]' if pm_type in pm_type_def else ''}: {hs_now}({'+' if hs_diff >= 0 else ''}{hs_diff})"
                                reply = f"{arc_name if arc_name is not None else ''}{arc_pp if arc_pp is not None else ''}{hs_str if hs_str is not None else ''}"
                                print(reply)
                            #BGD
                            #['EXPERT', '海色', 'スコア', 'ハイスコア', 'PERFECT', 'GREAT', 'GOOD', 'BAD', 'MISS', 'SS', 'SCORE RANK', 'NEW RECORD!', '0898303', '897957', 'MAX', 'COMBO', '0709', 'ALL PERFECT', 'ガルパ杯ではコンボ数に応じて', '1リズムアイコンあたりのス コアが', '増加しません。', '楽曲レベル', '26', '0709', 'OK']
                            
                            # vtuber
                            vtuber_ck = -1
                            # 歌枠
                            song_ck = -1
                            # youtube comment
                            yt_comment_chinese_re = re.compile(r'以 (.*) 的身分發表留言')
                            # 嘲諷?
                            chinese_lol = re.compile(r'我(.*)就.+了')
                            # group inv?
                            chinese_line_inv = re.compile(r'(.*)已邀請.+加入')
                            # py fine
                            py_fine_name_re = re.compile(r'\/([a-zA-Z0-9_]*).py')
                            # id check
                            id_check_re = re.compile(r'(?<![\w])@[a-zA-Z0-9_.]*')
                            # 需要嗎
                            chinese_need_huh = re.compile(r'需要(.*)嗎')
                            # 日期
                            day_ck_re = re.compile(r'([0-9 ]*年[0-9 ]*月[0-9 ]*日)')
                            # time
                            time_ck_re = re.compile(r'[0-9]{1,2}:[0-9]{2}')
                            # 劍與魔法王國
                            sm_ck_menu = ['装備', '合成', 'ガチャ', 'ショップ', 'その他', 'とじる']
                            sm_ck_my_page = ['ステータス', 'ジョブ', '武器', '補助', 'アバコレ', '総合能力', '装備セット', '覚醒スキル']
                            cm_ck_value = []
                            sm_ck_menu_value = []
                            
                            isMsg = False
                            # check
                            for i in range(len(words)):
                                test_time = re.findall(time_ck_re, words[i])
                                if len(test_time) > 0:
                                    tryCkTimeLen = []
                                    for ii in range(len(words)):
                                        test_time = re.findall(time_ck_re, words[ii])
                                        if len(test_time) > 0:
                                            tryCkTimeLen.append(ii)
                                    if len(tryCkTimeLen) > 1:
                                        tryCkTimeLen = len(tryCkTimeLen)
                                        isMsg = True
                                        reply = ''
                                        leftPosList = {}
                                        backgroundColorList = []
                                        for iiii in tr['result']['OCR']['result']['words']:
                                            bottomLeft = iiii['bounds']['bottomLeft'][0]
                                            if bottomLeft not in leftPosList:
                                                leftPosList[bottomLeft] = 0
                                            leftPosList[bottomLeft] += 1
                                            backgroundColorList.append(iiii['backgroundColor'])
                                        leftPosListIds = sorted(leftPosList)
                                        leftPos = leftPosListIds[2] if len(leftPosListIds) > 2 else leftPosListIds[0]
                                        for iiii in tr['result']['OCR']['result']['words']:
                                            if iiii['backgroundColor'] in [16777215, 2829099, 16777195]:
                                                if tryCkTimeLen <= 0:
                                                    reply = ''
                                                    isMsg = False
                                                    break
                                                tryCkTimeLen -= 1
                                                reply += f"{iiii['text']}\n"
                                        if reply != '':
                                            reply += f"BAO愛你唷"
                                        break
                            for i in range(len(words)):
                                if isMsg:
                                    break
                                if '歌枠' in words[i]:
                                    song_ck = i
                                    break
                                elif 'meme' in words[i].lower():
                                    reply = words[i]
                                    break
                                elif '身分發表留言' in words[i]:
                                    yt_comment_name = re.findall(yt_comment_chinese_re, words[i])
                                    if len(yt_comment_name) > 0:
                                        reply = yt_comment_name[0]
                                        break
                                elif '衝洞' == words[i]:
                                    reply = "先不要衝動BAO, 鴻在看呢"
                                    break
                                elif '信譽積分' in words[i]:
                                    reply = f"{words[i]}很強捏"
                                    break
                                elif 'vtuber' in words[i].lower():
                                    vtuber_ck = i
                                    break
                                elif 'arknights' in words[i].lower():
                                    reply = "明日方舟"
                                    break
                                elif 'made in ' in words[i].lower():
                                    reply = words[i]
                                    break
                                elif 'made with ' in words[i].lower():
                                    reply = words[i]
                                    break
                                elif 'vue' in words[i].lower():
                                    reply = "vue.js"
                                    break
                                elif '原神' in words[i]:
                                    reply = "原神"
                                    break
                                elif '劍與魔法王國' in words[i]:
                                    reply = "劍與魔法王國"
                                    break
                                elif '©' == words[i][0]:
                                    # 版權CC?
                                    reply = words[i]
                                    break
                                else:
                                    test_chinese_lol = re.findall(chinese_lol, words[i])
                                    test_chinese_line_inv = re.findall(chinese_line_inv, words[i])
                                    test_chinese_need_huh = re.findall(chinese_need_huh, words[i])
                                    test_py_fine_name = re.findall(py_fine_name_re, words[i])
                                    test_id_check = re.findall(id_check_re, words[i])
                                    test_day_ck = re.findall(day_ck_re, words[i])
                                    if len(test_day_ck) > 0:
                                        reply = test_day_ck[0]
                                    if len(test_py_fine_name) > 0:
                                        reply = test_py_fine_name[0] + '.py'
                                        break
                                    if len(test_chinese_lol) > 0:
                                        reply = f"我也{test_chinese_lol[0]}啊ww"
                                    if len(test_chinese_line_inv) > 0:
                                        reply = f"{test_chinese_line_inv[0]}又是你"
                                    if len(test_id_check) > 0:
                                        id = test_id_check[0]
                                        if len(id) >= 4:
                                            reply = id
                                            break
                                    if len(test_chinese_need_huh) > 0:
                                        reply = f"{test_chinese_need_huh[0]}? "
                                    if words[i] in sm_ck_my_page and words[i] not in cm_ck_value:
                                        cm_ck_value.append(words[i])
                                        if len(cm_ck_value) >= (len(sm_ck_my_page) - 2):
                                            reply = "劍與魔法王國uwu"
                                            break
                                    if words[i] in sm_ck_menu and words[i] not in sm_ck_menu_value:
                                        sm_ck_menu_value.append(words[i])
                                        if len(sm_ck_menu_value) >= (len(sm_ck_menu) - 2):
                                            reply = "劍與魔法王國?"
                                            break
                            if vtuber_ck > -1:
                                reply = "Korone我婆"
                            if song_ck > -1:
                                reply = "􁜁􀆙KORONE IS MY WAIFE􏿿"
                                
                            # bot reply
                            if reply is not None and reply != '':
                                cl.sendMessage(msg[2], reply, relatedMessageId=msg[4])
                        else:
                            print(tr['result']['OCR']['result'])
    elif op[3] == 30:
        return # for self bot
        gid = op[10]
        seq = op[11]
        update_type = op[12]
        uuid = f"{gid}_{seq}_{update_type}"
        if 'cache' not in ANNOUNCEMENT_RECORD:
            ANNOUNCEMENT_RECORD['cache'] = []
        if uuid not in ANNOUNCEMENT_RECORD['cache']:
            ANNOUNCEMENT_RECORD['cache'].append(uuid)
        else:
            return
        if update_type == 'd' or update_type == 'u':
            reply = f"公告{seq}已被{'取消' if update_type == 'd' else '更新'}"
            relatedMessageId = None
            if gid in ANNOUNCEMENT_RECORD:
                for ann in ANNOUNCEMENT_RECORD[gid]:
                    if str(seq) == str(ann[1]):
                        annData = ann[3]
                        reply += f"\n原內容如下\n`{annData[2]}`\n連結:{annData[3]}"
                        # line://nv/chatMsg?chatId=c13d5e6c1c22464120eef2400407023e0&messageId=14603297007331
                        if '&messageId=' in annData[3]:
                            messageId = annData[3].split('&messageId=')
                            relatedMessageId = messageId[1]
                        break
            cl.sendMessage(gid, reply, relatedMessageId=relatedMessageId)
        ANNOUNCEMENT_RECORD[gid] = cl.getChatRoomAnnouncements(gid)
    elif op[3] == 40:
        # 已讀
        pass
    elif op[3] == 45:
        # NOTIFIED_UPDATE_CONTENT_PREVIEW
        # video message
        cl.react(op[12], random.choice([2, 3, 4, 5, 6]))
    elif op[3] == 48:
        print(f'dummy: {op}')
    elif op[3] == 55:
        # 已讀?
        pass
    elif op[3] == 60:
        # NOTIFIED_JOIN_CHAT
        pass
    elif op[3] == 61:
        # NOTIFIED_LEAVE_CHAT
        pass
    elif op[3] == 65:
        # 收回?
        gid = op[10]
        msgid = op[11]
        return # for self bot
        if gid in cl.custom_data.get('reviewMsg', []):
            msgids = cl.getPreviousMessageIds(gid, 1000)
            target_msg = None
            for i in msgids[1]:
                if msgid == str(i[2]):
                    target_msg = i
                    break
            reply = "找不到相關紀錄Orz"
            contentMetadata = None
            if target_msg is not None:
                target_msg = cl.getPreviousMessagesV2(gid, target_msg[1], target_msg[2])[0]
                # {1: 'ud4045303d1cf300eca5f32fb1ba85376', 2: 'cf2f6416ed319f353bbd26c046c3de3ad', 3: 2, 4: '14409743298380', 5: 1626511223716, 6: 1626511223716, 10: '嗚嗚屋', 14: False, 15: 0, 18: {'UNSENT': 'true', 'seq': '14409743298380'}, 19: 0, 27: []}
                if target_msg[15] == 0:
                    reply = f"@chrline 的原訊息如下:\n{target_msg[10]}"
                    arr = [
                        {
                            "S": str(0),
                            "E": str(8),
                            "M": target_msg[1]
                        }
                    ]
                    contentMetadata = {'MENTION': str('{"MENTIONEES":' + json.dumps(arr) + '}')}
                else:
                    return
            cl.sendMessage(gid, reply, contentMetadata=contentMetadata, relatedMessageId=msgid)
    elif op[3] == 124:
        #被邀請
        if cl.profile[1] in op[12]:
            cl.acceptChatInvitation(op[10])
    elif op[3] == 127:
        #退群組
        if op[10] in cl.groups:
            cl.groups.remove(op[10])
    elif op[3] == 128:
        #NOTIFIED_DELETE_SELF_FROM_CHAT
        #if op[10] in cl.groups:
        #    cl.groups.remove(op[10])
        pass
    elif op[3] == 129:
        #加群組
        cl.groups.append(op[10])
    elif op[3] == 130:
        #別人加群組
        pass
    elif opType == 133:
        if op[12] == cl.profile[1]:
            if op[10] in cl.groups:
                cl.groups.remove(op[10])
    elif opType == 139:
        # SEND_REACTION
        pass
    elif opType == 140:
        # NOTIFIED_SEND_REACTION
        _msgid = op[10]
        _msgTime = op[2]
        _gid = json.loads(op[11])['chatMid']
        _uid = op[12]
        if _gid not in cl.custom_data.get('reactnotify', []):
            return
        msgids = cl.getPreviousMessageIds(_gid, 100)
        target_msg = None
        for i in msgids[1]:
            if _msgid == str(i[2]):
                target_msg = i
                break
        if target_msg is not None:
            target_msg = cl.getPreviousMessagesV2(_gid, target_msg[1], target_msg[2])[0]
            if target_msg[1] not in [_uid, cl.profile[1]]:
                if _gid not in TAGNOTREPLY:
                    TAGNOTREPLY[_gid] = {}
                if target_msg[1] not in TAGNOTREPLY[_gid]:
                    TAGNOTREPLY[_gid][target_msg[1]] = []
                TAGNOTREPLY[_gid][target_msg[1]] += [[_msgid, _msgTime, 'REACTION']]
        else:
            pass
    else:
        print(f"[{opType}]{op}")

def getInGroupBot(gid, getAll=False):
    bs = []
    for b in BOTS:
        if gid in b.groups:
            bs.append(b)
    if bs:
        if getAll:
            return bs
        return random.choice(bs)
    return None

def NotReplyWorking():
    while True:
        botInGroup = {}
        if len(TAGNOTREPLY) > 0:
            for gid in list(TAGNOTREPLY.keys()):
                cl = getInGroupBot(gid)
                if cl is None:
                    print(f'群組未有機器人: {gid}')
                    del TAGNOTREPLY[gid]
                    continue
                if gid in cl.custom_data.get('notagnotify', []) or gid not in cl.groups:
                    del TAGNOTREPLY[gid]
                    continue
                if cl.mid not in botInGroup:
                    botInGroup[cl.mid] = []
                botInGroup[cl.mid].append(gid)
        if botInGroup:
            for bmid in botInGroup.keys():
                for bot in BOTS:
                    if bot.mid == bmid:
                        cl = bot
                        break
                groups = botInGroup[bmid]
                if len(groups) > 0:
                    reads = cl.getMessageReadRange(groups)
                    for gread in reads:
                        gid = gread[1]
                        readRanges = gread.get(2, {})
                        _time = datetime.now()
                        replyedMsgIds = []
                        for mid in list(TAGNOTREPLY[gid].keys()):
                            notReplyDatas = TAGNOTREPLY[gid][mid]
                            delData = []
                            if mid in readRanges:
                                lastReadId = None
                                try:
                                    lastReadId = readRanges[mid][0].get(2, None)
                                except:
                                    delData = notReplyDatas
                                if lastReadId is not None:
                                    for msg in notReplyDatas:
                                        msgid = msg[0]
                                        msgtime = datetime.fromtimestamp(msg[1] / 1000)
                                        msgType = None
                                        if len(msg) > 2:
                                            msgType = msg[2]
                                        if msgid in replyedMsgIds:
                                            delData.append(msg)
                                        elif int(lastReadId) > int(msgid):
                                            delData.append(msg)
                                            replyedMsgIds.append(msgid)
                                            ts = _time - msgtime
                                            minWaitTime = cl.custom_data.get('tagnotifytime', {}).get(gid, 60 * TAGNOTREPLY_MIN)
                                            if ts.total_seconds() > minWaitTime:
                                                days = ts.days
                                                hours, remainder = divmod(ts.seconds, 3600)
                                                minutes, seconds = divmod(remainder, 60)
                                                _profile = cl.getContact(mid)
                                                if msgType is None:
                                                    reply = f"{_profile[22]}, related at {f'{days}天' if days > 0 else ''}{f'{hours}時' if ts.seconds >= 3600 else ''}{f'{minutes}分前' if minutes > 0 else '0分內'}"
                                                elif msgType == 'REACTION':
                                                    reply = f"{_profile[22]}, 有人對你的訊息表達了心情!"
                                                cl.sendMessage(gid, reply, relatedMessageId=msgid)
                                            else:
                                                pass
                                        elif int(lastReadId) == int(msgid):
                                            delData.append(msg)
                                        else:
                                            break
                            if len(delData) > 0:
                                for msg in delData:
                                    TAGNOTREPLY[gid][mid].remove(msg)
                                    cl.react(msg[0], random.choice([2, 3, 4, 5, 6, 7]))
                                if len(TAGNOTREPLY[gid][mid]) == 0:
                                    del TAGNOTREPLY[gid][mid]
                    #except:
                    #    traceback.print_exc()
                    #time.sleep(0.5)
                else:
                    del TAGNOTREPLY[gid]
                time.sleep(1.5)
        time.sleep(1.5)

thread1 = threading.Thread(target=NotReplyWorking)
thread1.daemon = True
thread1.start()

if len(BOTS) > 1:
    for _bot in BOTS[1:]:
        thread1 = threading.Thread(target=_bot.trace, args=(bot, ))
        thread1.daemon = True
        thread1.start()
BOTS[0].trace(bot)