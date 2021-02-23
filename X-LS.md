# LINE SESSION (LINE 會話週期)

### What is X-LS
>It is LINE SESSION, It is used to omit user authentication

### How to get the X-LS?
>When you are in a connection, after using X-LINE-ACCESS to request, server will provide X-LS in the header

## LINE Request Example
```
->  POST ga2.line.naver.jp/P5
    Headers:
        X-Line-Application: ANDROID	11.2.1	Android OS	9.0.0
        X-Line-Access: mid:xxxxxxxxx..xxxxxxxxxx=

<-  OK ga2.line.naver.jp/P5
    Headers:
        x-lc: 200
        x-ls: xxxxxxxxxxxxxxx

<-  POST ga2.line.naver.jp/P5
    Headers:
        x-ls: xxxxxxxxxxxxxxx

<-  POST ga2.line.naver.jp/S4
    Headers:
        x-ls: xxxxxxxxxxxxxxx

<-  POST ga2.line.naver.jp/CH4
    Headers:
        x-ls: xxxxxxxxxxxxxxx
......
```

### But what are the benefits?
>Since user checks are omitted, it maybe processed by server faster\
MAYBE...

### The disadvantages outweigh the benefits?
>X-LS must be the same connection, uhh... http/1.1 or... Keep-Alive yea\
So when you create a new connection, X-LS will fail\
You have to schedule all requests, and it is almost impossible to process them at the same time, otherwise you need multiple x-ls for multiple connections 


### Others
另外在回應中也有出現x-lc, 它是status code, 當你的x-lpv為1時, server將始終回應OK(200), 取而代之的是將實際的status code塞進x-lc給你\
Example:
```
->  POST gd2.line.naver.jp/xx/api/xx/xxx
    Headers:
        x-lpv: 1

<-  OK gd2.line.naver.jp/xx/api/xx/xxx
    Headers:
        x-lc: 404
```
