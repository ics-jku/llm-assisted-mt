SUT_BASE = <ENV_FOLDER>

PATHS = {
    "TFT": SUT_BASE + "libs/TFT_eSPI_GD32/",
    "SDK": SUT_BASE + "libs/nuclei_sdk/",
    "GCC": "riscv64-unknown-elf-gcc",
    "GCOV": "riscv64-unknown-elf-gcov",
    "GUI": SUT_BASE + "riscv-vp-plusplus/env/gd32/vp-breadboard/build/vp-breadboard",
    "VP": SUT_BASE + "riscv-vp-plusplus/vp/build/bin/gd32-vp",
    "TESTCASES": SUT_BASE + "testresults/"
}
BUILD = {
    "COMPILE":  "-c " \
                "-g3 " \
                "-Wall " \
                "-ffunction-sections " \
                "-fdata-sections " \
                "-fno-common " \
                "-march=rv32imac " \
                "-mabi=ilp32 " \
                "-mcmodel=medlow " \
                "--coverage " \
                "-DPLATFORMIO=60105 " \
                "-DDOWNLOAD_MODE=DOWNLOAD_MODE_FLASHXIP " \
                "-DNO_RTOS_SERVICE " \
                "-I. " \
                "-I"+PATHS['TFT']+" " \
#                "-I"+PATHS['SDK']+"NMSIS/Include " \
                "-I"+PATHS['SDK']+"NMSIS/Core/Include " \
#                "-I"+PATHS['SDK']+"NMSIS/DSP/Include " \
#                "-I"+PATHS['SDK']+"NMSIS/NN/Include " \
                "-I"+PATHS['SDK']+"SoC/gd32vf103/Common/Include " \
                "-I"+PATHS['SDK']+"SoC/gd32vf103/Board/gd32vf103v_vp/Include",
    "LINK": "-T "+PATHS['SDK']+"SoC/gd32vf103/Board/gd32vf103v_vp/Source/GCC/gcc_gd32vf103_flashxip.ld " \
            "-Os " \
            "-ffunction-sections " \
            "-fdata-sections " \
            "-fno-common " \
            "-Wl,--gc-sections " \
            "-march=rv32imac " \
            "-mabi=ilp32 " \
            "-mcmodel=medlow " \
            "-lgcov " \
            "--coverage " \
            "-nostartfiles " \
            "-Wl,--no-relax " \
            "-L. " \
            "-L"+PATHS['TFT'] + " " \
            "-L"+PATHS['SDK'] + " " \
            "-L"+PATHS['SDK']+"NMSIS/Library/DSP/GCC " \
            "-L"+PATHS['SDK']+"NMSIS/Library/NN/GCC " \
            "-Wl,--start-group "+SUT_BASE+"libs/nuclei_sdk/libsoc_gd32vf103.a "+SUT_BASE+"libs/TFT_eSPI_GD32/libTFT_eSPI_GD32.a " \
            "-lgcc " \
            "-lm " \
            "-lstdc++ " \
            "-Wl,--end-group",
}
