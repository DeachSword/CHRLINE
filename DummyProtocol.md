# Dummy Protocol

## How to write DummyProtocol?
Its code like: 
```
params = [
        [10, 2, revision],
        [8, 3, count],
        [10, 4, self.globalRev],
        [10, 5, self.individualRev]
    ]
sqrd = self.generateDummyProtocol('fetchOps', params, 4)
```

### How do I know the args of these requests?
that is very easy if u can decompilation.

![](/examples/assets/2021-08-24_145129.png)

u can see args of fetchOps: `localRev, count, globalRev and individualRev`

and u can see the name, type & fid `("localRev", (byte) 10, 2)`