all: main.c
	gcc -o main main.c -lpthread -g 
	gcc -o main_x86 main.c -m32 -lpthread -g
	strip main
	strip main_x86

debug: main.c
	gcc -o main main.c -lpthread -g -DDEBUG
	gcc -o main_x86 main.c -m32 -lpthread -g -DDEBUG

run: all
	./main
