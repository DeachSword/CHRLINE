

class LineCube():

    def __init__(self):
        self.CWA_Headers = {
            'X-Line-CWA-Token': self.approveChannelAndIssueChannelToken('1570623124')[1]
        }

    def issueBillSplitId(self):
        url = "https://cube.line.me/bill-split/api/splits/id/issue"
        # POST
        # {"id":"45bc09b354950892f8e815ce2cd91ea2"}
    
    def getBillSplitShareLink(self, split_id):
        url = "https://cube.line.me/bill-split/api/public/share/url?split_id=" + split_id
        # GET
    
    def getBillSplitSurvey(self, split_id):
        url = "https://cube.line.me/bill-split/api/survey/" + split_id
        # GET
    
    def getBillSplitBills(self, split_id):
        url = "https://cube.line.me/bill-split/api/bills/" + split_id
        # GET
    
    def putBillSplitBills(self, split_id):
        url = "https://cube.line.me/bill-split/api/bills/" + split_id
        # PUT
    
    def snedBillSplitBills(self, split_id, mids):
        url = "https://cube.line.me/bill-split/api/message/send"
        data = {
            "id": split_id,
            "tos": mids
        }
        print(self.CWA_Headers)
        r = self.server.postContent(url, json=data, headers=self.CWA_Headers)
        return r.json()