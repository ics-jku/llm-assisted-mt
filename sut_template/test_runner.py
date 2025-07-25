import numpy as np
import cv2
import os
import json
import time
import socket
import datetime
import config
import shutil
from subprocess import Popen, TimeoutExpired
from pathlib import Path
from Generators.Util.mtc_generator import MTCGenerator

class TestRunner():
    def __init__(self, generator: MTCGenerator):
        self.generator = generator
        self.main1 = "main1.cpp"
        self.main2 = "main2.cpp"
        self.firmware1 = "main1"
        self.firmware2 = "main2"
        self.screenshot1 = "screenshot_1.png"
        self.screenshot2 = "screenshot_2.png"
        self.diff = "diff.png"

    def storeInResults(self, sourceFolder, filename, idx, srcFup = None):
        if os.path.exists(config.PATHS["TESTCASES"] + self.generator.name+'/'+str(idx) + "/" + filename):
            os.remove(config.PATHS["TESTCASES"] + self.generator.name+'/'+str(idx) + "/" + filename)
        if filename == "TFT_eSPI.cpp.gcov":
            shutil.move(sourceFolder + filename, config.PATHS["TESTCASES"] + self.generator.name+'/'+str(idx) + "/" + filename + srcFup)
        else:
            shutil.move(sourceFolder + filename, config.PATHS["TESTCASES"] + self.generator.name+'/'+str(idx) + "/" + filename)

    def cleanCoverage(self):
        os.chdir(config.PATHS['SDK'])
        os.system("make clean-coverage")
        os.chdir(config.PATHS['TFT'])
        os.system("make clean-coverage")
        os.chdir(config.SUT_BASE)

    def generateCoverage(self):
        os.chdir(config.PATHS['TFT'])
        os.system(config.PATHS["GCOV"] + " -b TFT_eSPI.cpp")

    def run(self, generate, ignore_fail = True):
        
        print("--- RUNNING TEST: " + self.generator.name, flush=True)
        timeout = 200
        timeout_counter = 0
        
        tests = []
        idx = 0
        failed_cases = []
        passed_cases = []
        timedout = True
        startdate = datetime.datetime.now()
        start = time.time()
        generated_tests = 0
        while generated_tests < generate:
            idx += 1
            path = config.PATHS['TESTCASES']+self.generator.name+'/'+str(idx)
            
            Path(path).mkdir(parents=True, exist_ok=True)
            os.chdir(config.SUT_BASE)
            
            self.generator.generate_mtc()
            runtime = time.time()
            try:
                #compiletime = time.time()
                self.cleanCoverage()
                self.compile(self.main1, self.firmware1)
                self.run_vp(self.firmware1, self.screenshot1, timeout)
                self.generateCoverage()
                self.storeInResults(config.SUT_BASE, self.firmware1, idx)
                self.storeInResults(config.SUT_BASE, self.main1, idx)
                self.storeInResults(config.SUT_BASE, self.main1.replace(".cpp", ".o"), idx)
                self.storeInResults(config.SUT_BASE, self.main1.replace(".cpp", ".gcno"), idx)
                self.storeInResults(config.SUT_BASE, self.main1.replace(".cpp", ".gcda"), idx)
                self.storeInResults(config.PATHS['TFT'], "TFT_eSPI.cpp.gcov", idx, "1")

                self.cleanCoverage()
                self.compile(self.main2, self.firmware2)
                self.run_vp(self.firmware2, self.screenshot2, timeout)
                self.generateCoverage()
                self.storeInResults(config.SUT_BASE, self.firmware2, idx)
                self.storeInResults(config.SUT_BASE, self.main2, idx)
                self.storeInResults(config.SUT_BASE, self.main2.replace(".cpp", ".o"), idx)
                self.storeInResults(config.SUT_BASE, self.main2.replace(".cpp", ".gcno"), idx)
                self.storeInResults(config.SUT_BASE, self.main2.replace(".cpp", ".gcda"), idx)
                self.storeInResults(config.PATHS['TFT'], "TFT_eSPI.cpp.gcov", idx, "2")
            except RuntimeError as error:
                print('[ERROR] An error occured while compiling test {}: {}! A new test will be generated.'.format(idx, error))
                idx -= 1 # generate test again with same id
                break
            except TimeoutError as error:
                
                # OS takes up to 60 seconds till port is released after terminate
                time.sleep(70)
                timeout_counter += 1
                if timeout_counter == 10:
                    print('[ERROR] Test ran 10 times in a row in a timeout! stopping execution!')
                    break
                else:
                    continue
            runtime = time.time() - runtime

            equal = self.analyze()
            self.storeInResults(config.SUT_BASE, self.screenshot1, idx)
            self.storeInResults(config.SUT_BASE, self.screenshot2, idx)
            self.storeInResults(config.SUT_BASE, self.diff, idx)

            passed = not (equal ^ self.generator.should_be_equal)
            
            tests.append({
                "id": idx,
                "passed": passed,
                #"compiletime": round(compiletime, 2),
                "runtime": round(runtime, 2)
            })
            if not passed:
                failed_cases.append(idx)
                if not ignore_fail:
                    timedout = False
                    break
            else:
                passed_cases.append(idx)
            generated_tests += 1
            timeout_counter = 0
        runtime = time.time() - start
        if len(tests) > 0:
            results = {
                "relation": self.generator.name,
                "should_be_equal" : self.generator.should_be_equal,
                "host": socket.gethostname(),
                "starttime": startdate.isoformat(),
                "endtime": datetime.datetime.now().isoformat(),
                "total_runtime": str(datetime.timedelta(seconds=runtime)),
                #"avg_compiletime_pc": round(sum(d['compiletime'] for d in tests) / len(tests), 2),
                "avg_runtime_pc": round(sum(d['runtime'] for d in tests) / len(tests), 2),
                "timeout": timedout,
                "ignore_fail": ignore_fail,
                "number_of_tests": idx,
                "number_failed": len(failed_cases),
                "number_passed": idx - len(failed_cases),
                "failed_cases": str(failed_cases), # cast to str in order to avoid indentation - a bit ugly
                "test": tests
            }

            with open(config.PATHS['TESTCASES']+self.generator.name+".json", "w") as outfile:
                outfile.write(json.dumps(results, indent=4))


    def compile(self, code_file, firmware_file):
        compile = [config.PATHS['GCC'], '-o', code_file.replace(".cpp", '.o'), code_file]
        compile.extend(config.BUILD['COMPILE'].split())
        print(compile)
        compile_p = Popen(compile)
        compile_p.communicate()[0]
        compile_p.wait()
        if compile_p.returncode:
            raise RuntimeError('unable to compile firmware')

        link = [config.PATHS['GCC'], '-o', firmware_file, code_file.replace(".cpp", '.o')]
        link.extend(config.BUILD['LINK'].split())

        link_p = Popen(link)
        link_p.communicate()[0]
        link_p.wait()
        if link_p.returncode:
            raise RuntimeError('unable to link firmware')


    def run_vp(self, firmware_file, screenshot_file, timeout):
        successs = True
        screenshot = Path(screenshot_file)
        if screenshot.is_file():
            screenshot.unlink()

        start_time = time.time()
        vp = Popen([config.PATHS['VP'], '--intercept-syscalls', '--wait-for-gpio-connections',  firmware_file])
        gui = Popen([config.PATHS['GUI'], '--platform', 'offscreen'])

        try:
            vp.wait(timeout=timeout)
        except TimeoutExpired:
            vp.terminate()
            vp.wait()
            gui.terminate()
            gui.wait()
            raise TimeoutError('Unable to simulate firmware')
        gui.terminate()
        gui.wait()

    def analyze(self) -> bool:
        """Load two RGBA images. For each pixel: 
        if there is a difference in one or more channels, output 255 else 0. 
        In the final image white pixels indicate a difference."""
        img1 = cv2.imread(config.SUT_BASE + self.screenshot1, cv2.IMREAD_UNCHANGED)
        img2 = cv2.imread(config.SUT_BASE + self.screenshot2, cv2.IMREAD_UNCHANGED)

        diff = np.where(img1[:, ..., [0, 1, 2, 3]] != img2[:, ..., [0, 1, 2, 3]], 255, 0)
        diff = np.where(np.sum(diff, axis=2) > 0, 255, 0)
        cv2.imwrite(config.SUT_BASE + self.diff, diff)

        return bool(np.all(np.equal(img1, img2)))
