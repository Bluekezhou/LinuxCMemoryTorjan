all: backdoor.c
	gcc -o backdoor backdoor.c -lpthread -g 
	gcc -o backdoor_x86 backdoor.c -m32 -lpthread -g
	strip backdoor
	strip backdoor_x86

debug: backdoor.c
	gcc -o backdoor backdoor.c -lpthread -g -DDEBUG
	gcc -o backdoor_x86 backdoor.c -m32 -lpthread -g -DDEBUG

run: all
	./backdoor
