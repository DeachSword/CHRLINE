"""
TEST SEND_MESSAGE BY /PUSH ENDPOINT.

DIED.
"""
import time
from CHRLINE import *

TEST_GROUP_MID = ''

if __name__ == '__main__':
    assert TEST_GROUP_MID != ''
    cl = CHRLINE(device="IOSIPAD")

    send_message_req_data = {
        "to": TEST_GROUP_MID,
    }
    a = time.time()
    send_message_req_data['text'] = 'okok...'
    cl.legyPushers.SendAndReadSignOnRequest('sendMessage',
                                            **send_message_req_data)
    b = time.time() - a
    send_message_req_data['text'] = f'speed: {b}s'
    cl.legyPushers.SendAndReadSignOnRequest('sendMessage',
                                            **send_message_req_data)
