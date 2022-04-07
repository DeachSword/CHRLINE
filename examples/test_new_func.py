# -*- coding: utf-8 -*- 
from CHRLINE import *

cl = CHRLINE(token, device="IOS")

test_step = 0

if test_step == 0:
    res = cl.testRequest("sync", [
        [12, 1, [
            [10, 1, 1814143],
            [8, 2, 2],
            [10, 4, 14128]
        ]]
    ], "/SYNC5", 4, 5)
    print(res)
elif test_step == 1:
    res = cl.sync(0)
    print(res)
