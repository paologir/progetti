CC = gcc
CFLAGS = -O3 -Wall -Wextra -std=c99
LDFLAGS = -lm
TARGET = bond_duration
SOURCE = bond_duration.c

.PHONY: all clean debug release

all: release

release: CFLAGS += -DNDEBUG
release: $(TARGET)

debug: CFLAGS = -g -O0 -Wall -Wextra -Wformat=2 -Wconversion -Wshadow -std=c99
debug: $(TARGET)

$(TARGET): $(SOURCE)
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

clean:
	rm -f $(TARGET)

install: $(TARGET)
	install -m 755 $(TARGET) ~/bin/

test: $(TARGET)
	./$(TARGET) -p 950,50 -f 1000 -c 0,05 -m 10 -q 2