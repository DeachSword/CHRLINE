# -*- coding: utf-8 -*-
from ..CHRLINE import *

class Qrcode():
    def login_chrome():
        cl = CHRLINE(device="CHROMEOS")

    def login_iosipad():
        cl = CHRLINE(device="IOSIPAD")

    def login_watchos():
        cl = CHRLINE(device="WATCHOS")

    def login_wear():
        cl = CHRLINE(device="WEAROS")

    def login_desktop_win():
        cl = CHRLINE(device="DESKTOPWIN")

    def login_desktop_mac():
        cl = CHRLINE(device="DESKTOPMAC")

class Email():
    def login_web():
        e = input('Email: ')
        p = input('Password: ')
        cl = CHRLINE(e, p, device="WEB")

class Token():
    def login_bot():
        token = input('Token: ')
        cl = CHRLINE(token, device="BOT")

    def login_wap():
        token = input('Token: ')
        cl = CHRLINE(token, device="WAP")

    def login_tizen():
        token = input('Token: ')
        cl = CHRLINE(token, device="TIZEN")

    def login_virtual():
        token = input('Token: ')
        cl = CHRLINE(token, device="VIRTUAL")

    def login_dummy_primary():
        token = input('Token: ')
        cl = CHRLINE(token, device="DUMMYPRIMARY")

    def login_channel_cp():
        token = input('Token: ')
        cl = CHRLINE(token, device="CHANNELCP")

    def login_channel_gw():
        token = input('Token: ')
        cl = CHRLINE(token, device="CHANNELGW")

class Pwless():
    def login_android():
        phone = input('Phone: ')
        region = input('Region: ')
        cl = CHRLINE(phone=phone, region=region, device="ANDROID")

    def login_ios():
        phone = input('Phone: ')
        region = input('Region: ')
        cl = CHRLINE(phone=phone, region=region, device="IOS")