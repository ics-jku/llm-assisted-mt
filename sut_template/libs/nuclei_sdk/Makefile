RISCV_PREFIX ?= riscv64-unknown-elf-

override CC = $(RISCV_PREFIX)gcc
override CXX = $(RISCV_PREFIX)g++
override LD = $(RISCV_PREFIX)g++
override AR = $(RISCV_PREFIX)ar

ASFLAGS ?= $(CFLAGS)


#-Wall -g -Os -s -z norelro -Wl,--gc-sections \

BUILD_FLAGS = \
	-g3 -march=rv32imac -mabi=ilp32 -ffunction-sections -fdata-sections -fno-common -mcmodel=medlow \
	-Wall -mno-relax --coverage \
	-I include \
	-ISoC/gd32vf103/Common/Include \
	-INMSIS/Core/Include \
	-ISoC/gd32vf103/Board/gd32vf103v_vp/Include

CFLAGS += $(BUILD_FLAGS)
CXXFLAGS += $(BUILD_FLAGS) #-std=c++2a

LIBRARY = libsoc_gd32vf103.a
ASMSOURCES := $(wildcard SoC/gd32vf103/Common/Source/GCC/*.S)
CSOURCES := $(wildcard SoC/gd32vf103/Common/Source/*.c) \
		$(wildcard SoC/gd32vf103/Common/Source/Drivers/*.c) \
		$(wildcard SoC/gd32vf103/Board/gd32vf103v_vp/Source/*.c)
OBJECTS := $(patsubst %.S,%.o,$(ASMSOURCES)) $(patsubst %.c,%.o,$(CSOURCES))

########################################################################

all: $(LIBRARY)

$(LIBRARY): $(OBJECTS)
	$(AR) ru $@ $^
	ranlib $@

%.o: %.S
	$(CC) $(CPPFLAGS) $(ASFLAGS) -c $< -o $@
%.o: %.c
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@
%.o: %.cpp
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@

########################################################################

clean:
	rm -f $(OBJECTS) $(LIBRARY)
	find . -name \*.gcda -exec rm {} \;
	find . -name \*.gcov -exec rm {} \;
	find . -name \*.gcno -exec rm {} \;

clean-coverage:
	find . -name \*.gcda -exec rm {} \;
	find . -name \*.gcov -exec rm {} \;
	
.PHONY: all clean

