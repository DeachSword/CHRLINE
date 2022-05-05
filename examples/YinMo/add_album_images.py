# -*- coding: utf-8 -*-
from CHRLINE import *


cl = CHRLINE()

# Group ID: str
groupId = None

# Album ID: str, u can get it from getAlbums or create a new album.
albumId = None

# Image's path: list<str>
images = []

for i in images:
    print(f"--> Try to Upload {i}")
    oid = cl.updateImageToAlbum(groupId, albumId, i)
    print(f"<-- OID: {oid}")
    cl.addImageToAlbum(groupId, albumId, oid)

print(f"Done.")
