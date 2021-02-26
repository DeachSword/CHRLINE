# LINE TMoreCompact

>What is TMoreCompact?\
It is custom thrift by LINE\
It has more powerful compression than TCompact

## When did it appear?
First appeared in LINE 7.X\
And in the current Android version (11.2.2), it is used in /P5 and /C5\
For two func: **fetchOps** and **sendMessage**

## Why?
They have more powerful compression, and the bytes will be greatly reduced, giving it a faster transmission speed.\
In fetchOps, the effect is more obvious\
If the user has many chat messages, he will get 50 or more Ops at the one time, and this will increase the bytes of a single request and affect its response\
and TMoreCompact is to reduce the situation, it will greatly compress its bytes :p

## How?
Its LINE :D