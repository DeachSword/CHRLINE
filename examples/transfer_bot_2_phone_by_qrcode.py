"""
Qrcode migration example.

Line version limit: 12.10.0

Author: YinMo0913
CreatedTime: 2022/09/19
"""
import json
import os
from CHRLINE import *
import axolotl_curve25519 as Curve25519

TOKEN = ""

if __name__ == "__main__":
    assert TOKEN != ""
    cl = CHRLINE(TOKEN, device="ANDROID", version="12.10.0")

    session = cl.createQRMigrationSession()[1]
    qi = os.urandom(32)
    private_key = Curve25519.generatePrivateKey(os.urandom(32))
    public_key = Curve25519.generatePublicKey(private_key)
    print(f"priv key: {private_key}")
    qr_text = json.dumps({"si": session, "qi": qi.hex(), "pk": public_key.hex()})
    qr_img_path = cl.genQrcodeImageAndPrint(qr_text)
    print(f"QrCode image in {qr_img_path}")
    r = input(
        f"Please scan this qrcode with LINE Android/IOS, you will be prompted to wait for verification.\nEnter `Y` if you got `wait for verification` message\nEnter any if you got Error or something."
    )
    if r == "Y":
        cl.sendEncryptedE2EEKey(session, "")
        print(f"Send verification to phone... please check it on phone to login.")
    else:
        print(f"Exit with `{r}`.")
    print(f"EXIT.")
