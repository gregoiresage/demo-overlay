# demo-overlay

Work in progress, a Pebble package will come

# Usage

`pebble build && pebble build` (twice, I will explain later)

`pebble install --emulator aplite --logs`

You should see :

```
Installing app...
App install succeeded.
[01:38:40] overlord.c:14> App: demo-overlay Version 1.0 size:21248
[01:38:40] overlord.c:23> app:0 size:20090
[01:38:40] demo-overlay.c:13> Overlay 0 loaded
[01:38:42] ovl1.c:11> HELLO1
[01:38:42] demo-overlay.c:15> number 2542933
[01:38:42] overlord.c:23> app:1 size:20040
[01:38:42] demo-overlay.c:18> Overlay 1 loaded
[01:38:44] demo-overlay.c:20> number 2587018
[01:38:44] ocess_manager.c:417> Heap Usage for App <demo-overl: Total Size <2884B> Used <24B> Still allocated <24B>
```
