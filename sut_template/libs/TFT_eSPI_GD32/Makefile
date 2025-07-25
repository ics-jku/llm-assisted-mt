RISCV_PREFIX ?= riscv64-unknown-elf-

override CC = $(RISCV_PREFIX)gcc
override CXX = $(RISCV_PREFIX)g++
override LD = $(RISCV_PREFIX)g++
override AR = $(RISCV_PREFIX)ar

ASFLAGS ?= $(CFLAGS)

# ISA Version 2.2 is the last version where zicsr is still
# supported as part of the base ISA. Use that for now until
# _zicsr is widely supported by existing cross-compilers.
SUPPORTS_MISA ?= $(shell echo "typedef int dont_be_pedantic;" | $(RISCV_PREFIX)gcc -march=rv32imac -mabi=ilp32 -misa-spec=2.2 -E - > /dev/null 2>&1 && echo 1 || echo 0)
ifeq (1,$(SUPPORTS_MISA))
  CFLAGS += -misa-spec=2.2
  CXXFLAGS += -misa-spec=2.2
endif


#-Wall -g -Os -s -z norelro -Wl,--gc-sections \

BUILD_FLAGS = \
	-march=rv32imac -mabi=ilp32 -mcmodel=medlow --coverage -fno-use-cxa-atexit \
	-Wall -g3 -ffunction-sections -fdata-sections -fno-common \
	-DTF_LITE_USE_GLOBAL_CMATH_FUNCTIONS \
	-DTF_LITE_STATIC_MEMORY -DTF_LITE_DISABLE_X86_NEON \
	-DTF_LITE_MCU_DEBUG_LOG -DTF_LITE_USE_GLOBAL_CMATH_FUNCTIONS \
	-DTF_LITE_USE_GLOBAL_MIN -DTF_LITE_USE_GLOBAL_MAX \
	-I. \
	-I ../nuclei_sdk/SoC/gd32vf103/Common/Include \
	-I ../nuclei_sdk/NMSIS/Core/Include \

CFLAGS += $(BUILD_FLAGS)
CXXFLAGS += $(BUILD_FLAGS) #-std=c++2a

LIBRARY = libTFT_eSPI_GD32.a
CPPSOURCES := $(wildcard *.cpp) $(wildcard Processors/GD32/*.cpp) \
				$(wildcard Processors/GD32/*.cpp) \
				$(wildcard Processors/GD32/EXMC/*.cpp)
OBJECTS := $(patsubst %.cpp,%.o,$(CPPSOURCES)) $(patsubst %.c,%.o,$(CSOURCES))

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

