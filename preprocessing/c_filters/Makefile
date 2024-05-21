# Callum Gran 2024
# See LICENSE for license info

OBJDIR = .obj
SRC = src
DIRS := $(shell find $(SRC) -type d)
SRCS := $(shell find $(SRC) -type f -name "*.c")
OBJS := $(SRCS:%.c=$(OBJDIR)/%.o)

CFLAGS = -Iinclude -Wall -Wextra -Wshadow -std=c11 -O2 -D_POSIX_C_SOURCE=200809L
CFLAGS += -DLOGGING
LDFLAGS = -pthread
LDLIBS = -lm

.PHONY: format clean tags bear $(OBJDIR)
TARGET = main

all: $(TARGET)

$(OBJDIR)/%.o: %.c Makefile | $(OBJDIR)
	@echo [CC] $@
	@$(CC) -c $(CFLAGS) $< -o $@

$(TARGET): $(OBJS)
	@echo [LD] $@
	@$(CC) $(LDFLAGS) -o $@ $^ $(LDLIBS)

$(TARGET-FUZZ): $(OBJS)
	@echo [LD] $@
	@$(CC) $(LDFLAGS) -o $@ $^ $(LDLIBS)

$(OBJDIR):
	$(foreach dir, $(DIRS), $(shell mkdir -p $(OBJDIR)/$(dir)))

debug: CFLAGS += -g -DDEBUG
debug: $(TARGET)

clean:
	rm -rf $(OBJDIR) $(TARGET)

tags:
	@ctags -R

bear:
	@bear -- make

format:
	python format.py
