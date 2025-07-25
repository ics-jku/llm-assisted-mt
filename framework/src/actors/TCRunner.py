import os
import shutil
from multiprocessing import Pool

class TCRunner:
    def __init__(self):
        self.operationList = []

    def searchOperationalCases(self):
        count_dev = 0
        with open("../results/step5/to_be_verified_filled.csv", "r") as to_be_verified_file:
            toBeVerified = to_be_verified_file.readlines()
            for i, mtc in enumerate(toBeVerified):
                tokens = mtc.split(";")
                if tokens[0] != "Source":
                    source = tokens[0]
                    followUp = tokens[1]
                    operational = tokens[4]
                    if operational == "y":
                        self.operationList.append(str(i) + "|" + source + "|"+ followUp)
                        # if count_dev >= 0:
                        #     break
                        # count_dev += 1

    def poolFunction(self, operational):
        print("!!!" + operational)
        tokens = operational.split("|")
        idx = tokens[0]
        src = tokens[1]
        fup = tokens[2]
        if os.path.exists("../results/step8/" + idx):
            shutil.rmtree("../results/step8/" + idx)
        shutil.copytree("../sut_template/", "../results/step8/" + idx)

        with open("../results/step8/" + idx + "/Main.py", "w") as mainFile:
            mainFile.write("from test_runner import TestRunner\n")
            mainFile.write("\n")
            mrName = "mtc_" + idx + "_" + src.split("(")[0] + fup.split("(")[0]
            mainFile.write("from Generators.LLM." + mrName + " import " + mrName + "\n")
            mainFile.write("TestRunner(" + mrName + "()).run(1000)\n\n")
            #mainFile.write("TestRunner(" + mrName + "()).run(10)\n\n")

        with open("../results/step8/" + idx + "/config_template.py", "r") as configTemplateFile:
            with open("../results/step8/" + idx + "/config.py", "w") as configFile:
                configs = configTemplateFile.readlines()
                for config in configs:
                    if config.startswith("SUT_BASE = "):
                        configFile.write('SUT_BASE = "' + os.path.abspath("../results/step8/" + idx) + '/"\n')
                    else:
                        configFile.write(config)
        shutil.move("../results/step8/" + idx + "/riscv-vp-plusplus/vp/src/platform/gd32/gpio/gpiocommon.hpp", "../results/step8/" + idx + "/riscv-vp-plusplus/vp/src/platform/gd32/gpio/gpiocommon_del.hpp")
        with open("../results/step8/" + idx + "/riscv-vp-plusplus/vp/src/platform/gd32/gpio/gpiocommon_del.hpp", "r") as gpio_del_file:
            with open("../results/step8/" + idx + "/riscv-vp-plusplus/vp/src/platform/gd32/gpio/gpiocommon.hpp", "w") as gpio_wr_file:
                gpio_common = gpio_del_file.readlines()
                for gpio_common_line in gpio_common:
                    gpio_common_line = gpio_common_line.replace("A = 1400,", "A = " + str(40000+(int(idx)*10)) + ",")
                    #gpio_common_line = gpio_common_line.replace("A = 1400,", "A = " + str(1400) + ",")
                    gpio_wr_file.write(gpio_common_line)
        os.remove("../results/step8/" + idx + "/riscv-vp-plusplus/vp/src/platform/gd32/gpio/gpiocommon_del.hpp")
        os.chdir("../results/step8/" + idx + "/riscv-vp-plusplus/")
        os.system("make clean && make")
        #os.system("make clean && make -j")
        os.chdir("./env/gd32/vp-breadboard")
        os.system("cd build && rm -rf * && cmake .. && make -j3")
        #os.system("cd build && rm -rf * && cmake .. && make -j")
        os.chdir("../../../../libs/nuclei_sdk/")
        os.system("make clean && make -j3")
        os.chdir("../TFT_eSPI_GD32")
        os.system("make clean && make")
        os.chdir("../../../../../framework")
        os.system("python3 ../results/step8/" + idx + "/Main.py")


    def Run(self):
        self.searchOperationalCases()
        with Pool(processes=30) as pool:
            pool.map(self.poolFunction, self.operationList)
