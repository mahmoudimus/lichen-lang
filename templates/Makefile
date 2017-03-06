include native.mk
include modules.mk
include options.mk

SRC += calls.c exceptions.c main.c ops.c progops.c progtypes.c
OBJ = $(SRC:.c=.o)
CFLAGS += -Wall -I. -finput-charset=UTF-8 -O2
LDFLAGS += -lm -lgc

ifdef ARCH
CC := $(ARCH)-$(CC)
endif

all: main

clean:
	rm -f main $(OBJ)

main: $(OBJ)
	$(CC) $(LDFLAGS) $(OBJ) -o $@

.c.o:
	$(CC) -c $(CFLAGS) $< -o $@
