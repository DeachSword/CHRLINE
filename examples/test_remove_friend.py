from CHRLINE import *

mid = '' # user mid
if len(mid) == 0 or cl.getToType(mid) != 0:
    raise Exception('Invalid mid')

print(cl.updateContactSetting(mid, 16, "true"))