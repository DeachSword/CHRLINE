# -*- coding: utf-8 -*-

def loggedIn(func):
    def checkLogin(*args, **kwargs):
        if args[0].can_use_cube:
            return func(*args, **kwargs)
        else:
            raise Exception("can't use Line Cube")

    return checkLogin


class LineCube:

    def __init__(self):
        self.can_use_cube = False
        try:
            self.CWA_Headers = {
                'X-Line-CWA-Token': self.checkAndGetValue(self.approveChannelAndIssueChannelToken('1570623124'), 1,
                                                          'val_1')
            }
            self.can_use_cube = True
        except:
            self.log(f"can't use Line Cube")

    @loggedIn
    def issueBillSplitId(self):
        url = "https://cube.line.me/bill-split/api/splits/id/issue"
        # POST
        # {"id":"45bc09b354950892f8e815ce2cd91ea2"}

    @loggedIn
    def getBillSplitShareLink(self, split_id):
        url = "https://cube.line.me/bill-split/api/public/share/url?split_id=" + split_id
        # GET

    @loggedIn
    def getBillSplitSurvey(self, split_id):
        url = "https://cube.line.me/bill-split/api/survey/" + split_id
        # GET

    @loggedIn
    def getBillSplitBills(self, split_id):
        url = "https://cube.line.me/bill-split/api/bills/" + split_id
        # GET

    @loggedIn
    def putBillSplitBills(self, split_id):
        url = "https://cube.line.me/bill-split/api/bills/" + split_id
        # PUT

    @loggedIn
    def snedBillSplitBills(self, split_id, mids):
        url = "https://cube.line.me/bill-split/api/message/send"
        data = {
            "id": split_id,
            "tos": mids
        }
        print(self.CWA_Headers)
        r = self.server.postContent(url, json=data, headers=self.CWA_Headers)
        return r.json()
