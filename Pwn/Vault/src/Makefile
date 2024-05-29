

all:
	#gcc -s src/main.c -lpthread -o out/vault 
	gcc src/main.c -Wl,-z,relro,-z,now -lpthread -o out/vault 

clean:
	rm out/vault
