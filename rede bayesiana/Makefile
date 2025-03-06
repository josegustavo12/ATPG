CC=g++
CFLAGS=-I./include -L./lib
LDFLAGS=-lsmile
SRC=build_circuits_bn.cpp
TARGET=build_circuits_bn

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(SRC) $(CFLAGS) $(LDFLAGS) -o $(TARGET)

clean:
	rm -f $(TARGET)

run:
	./$(TARGET)
