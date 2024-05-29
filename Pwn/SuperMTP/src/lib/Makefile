CC=clang
CFLAGS = -shared -fPIC -lssl -lcrypto
INCLUDES = -I/usr/include/python3.11/ -I.
SOURCES = smtp.c
#OBJECTS = $(SOURCES:.c=.o)

LIBRARY = smtp.so

all: $(LIBRARY)

$(LIBRARY): smtp.c
	$(CC) $(CFLAGS) $(INCLUDES) $(SOURCES) -o $(LIBRARY)

clean:
	rm -f $(LIBRARY)

test:
	python3 test.py
