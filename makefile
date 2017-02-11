all: main.c
	gcc -o main main.c -g -lpthread
run: all
	./main
