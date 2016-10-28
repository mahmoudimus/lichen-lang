SRC = exceptions.c progops.c progtypes.c ops.c $(wildcard src/*.c)
OBJ = $(SRC:.c=.o)
CFLAGS = -I.

all: main

clean:
	rm -f main $(OBJ)

main: $(OBJ)
	$(CC) $(LDFLAGS) $(OBJ) -o $@

.c.o:
	$(CC) -c $(CFLAGS) $< -o $@
