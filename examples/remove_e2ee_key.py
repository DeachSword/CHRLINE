# -*- coding: utf-8 -*- 
from CHRLINE import *

cl = CHRLINE(TOKEN, device="ANDROID")

pks = cl.getE2EEPublicKeys()
for pk in pks:
    print(f"try remove key id: {pk[2]}")
    cl.removeE2EEPublicKey(pk[1], pk[2], pk[4])