from pathlib import Path
import re

class ResultAnalyzer:
    def __init__(self):
        # lineNumber, line, counter, branches
        self.tft_library_content = []
        self.tft_library_content_granular = []
        with open("../sut_template/libs/TFT_eSPI_GD32/TFT_eSPI.cpp", "r") as tft_file:
            tft_content = tft_file.readlines()
            for i, tft_line in enumerate(tft_content):
                self.tft_library_content.append([tft_line, 0, [], False, False])
                self.tft_library_content_granular.append([tft_line, 0, [], False, False])
        with open("../results/step5/coverage_original.gcov", "r") as coverable:
            lines = coverable.readlines()
            for line in lines:
                tokens = line.split(":")
                if len(tokens) > 2 and tokens[0].find("#####") != -1:
                    self.tft_library_content[int(tokens[1])-1][4] = True
                    self.tft_library_content_granular[int(tokens[1])-1][4] = True
        
    def Analyze(self):
        directories = [entry for entry in Path("../results/step8_florian").iterdir() if entry.is_dir()]
        for directory in directories:
            print(directory)
            mainResults = [entry for entry in Path(directory.joinpath("testresults")).iterdir() if entry.is_dir()]
            for mainResult in mainResults:
                runs = [entry for entry in Path(mainResult).iterdir() if entry.is_dir()]
                for run in runs:
                    with open(str(run) + "/TFT_eSPI.cpp.gcov1", "r") as gcov_source_file:
                        gcov_source = gcov_source_file.readlines()
                        current_source_line = -1
                        function_flag = False
                        for gcov_line in gcov_source:
                            tokens = gcov_line.split(":")
                            if len(tokens) > 2 and tokens[1].strip() != "0":
                                current_source_line = int(tokens[1].strip()) - 1
                                if function_flag:
                                    self.tft_library_content[int(tokens[1])-1][3] = True
                                    self.tft_library_content_granular[int(tokens[1])-1][3] = True
                                    function_flag = False
                                if tokens[0].strip() != "-" and tokens[0].strip() != "#####":
                                    self.tft_library_content[int(tokens[1])-1][1] += int(tokens[0].strip().replace("*", ""))
                                    self.tft_library_content_granular[int(tokens[1])-1][1] += int(tokens[0].strip().replace("*", ""))
                                elif tokens[0].strip() == "-":
                                    self.tft_library_content[int(tokens[1])-1][1] = -1
                                    self.tft_library_content_granular[int(tokens[1])-1][1] = -1
                            elif len(tokens) == 1:
                                if gcov_line.startswith("branch"):
                                    clean_line = re.sub(r'\s+', ' ', gcov_line)
                                    branch_tokens = clean_line.split(" ")
                                    if len(self.tft_library_content[current_source_line][2])  > int(branch_tokens[1]):
                                        if branch_tokens[2].strip() == "taken" and self.tft_library_content[current_source_line][2][int(branch_tokens[1])] == False:
                                            self.tft_library_content[current_source_line][2][int(branch_tokens[1])] = True
                                    else:
                                        if branch_tokens[2].strip() == "taken":
                                            self.tft_library_content[current_source_line][2].append(True)
                                        else:
                                            self.tft_library_content[current_source_line][2].append(False) 
                                    if len(self.tft_library_content_granular[current_source_line][2])  > int(branch_tokens[1]):
                                        if branch_tokens[2].strip() == "taken" and self.tft_library_content_granular[current_source_line][2][int(branch_tokens[1])] == False:
                                            self.tft_library_content_granular[current_source_line][2][int(branch_tokens[1])] = True
                                    else:
                                        if branch_tokens[2].strip() == "taken":
                                            self.tft_library_content_granular[current_source_line][2].append(True)
                                        else:
                                            self.tft_library_content_granular[current_source_line][2].append(False) 
                                if gcov_line.startswith("function"):
                                    function_flag = True  

                    with open(str(run) + "/TFT_eSPI.cpp.gcov2", "r") as gcov_followup_file:
                        gcov_followup = gcov_followup_file.readlines()
                        current_source_line = 0
                        function_flag = False
                        for gcov_line in gcov_followup:
                            tokens = gcov_line.split(":")
                            if len(tokens) > 2 and tokens[1].strip() != "0":
                                current_source_line = int(tokens[1].strip()) - 1
                                if function_flag:
                                    self.tft_library_content[int(tokens[1])-1][3] = True
                                    self.tft_library_content_granular[int(tokens[1])-1][3] = True
                                    function_flag = False
                                if tokens[0].strip() != "-" and tokens[0].strip() != "#####":
                                    self.tft_library_content[int(tokens[1])-1][1] += int(tokens[0].strip().replace("*", ""))
                                    self.tft_library_content_granular[int(tokens[1])-1][1] += int(tokens[0].strip().replace("*", ""))
                                elif tokens[0].strip() == "-":
                                    self.tft_library_content[int(tokens[1])-1][1] = -1
                                    self.tft_library_content_granular[int(tokens[1])-1][1] = -1
                            elif len(tokens) == 1:
                                if gcov_line.startswith("branch"):
                                    clean_line = re.sub(r'\s+', ' ', gcov_line)
                                    branch_tokens = clean_line.split(" ")
                                    if len(self.tft_library_content[current_source_line][2]) > int(branch_tokens[1]):
                                        if branch_tokens[2].strip() == "taken" and self.tft_library_content[current_source_line][2][int(branch_tokens[1])] == False:
                                            self.tft_library_content[current_source_line][2][int(branch_tokens[1])] = True
                                    else:
                                        if branch_tokens[2].strip() == "taken":
                                            self.tft_library_content[current_source_line][2].append(True)
                                        else:
                                            self.tft_library_content[current_source_line][2].append(False)  
                                    if len(self.tft_library_content_granular[current_source_line][2]) > int(branch_tokens[1]):
                                        if branch_tokens[2].strip() == "taken" and self.tft_library_content_granular[current_source_line][2][int(branch_tokens[1])] == False:
                                            self.tft_library_content_granular[current_source_line][2][int(branch_tokens[1])] = True
                                    else:
                                        if branch_tokens[2].strip() == "taken":
                                            self.tft_library_content_granular[current_source_line][2].append(True)
                                        else:
                                            self.tft_library_content_granular[current_source_line][2].append(False) 
                                if gcov_line.startswith("function"):
                                    function_flag = True
            
            sublines = 0
            subcovered_lines = 0
            subfunctions = 0
            subcovered_functions = 0
            subbranches = 0
            subcovered_branches = 0
            with open(str(directory) + "/sub_coverage.cov", "w") as subcoverage:
                for i, line in enumerate(self.tft_library_content_granular):
                    if line[4] == True:
                        subcoverage.write(str(line) + "\n")
                        if line[1] > 0:
                            subcovered_lines += 1
                        if line[1] != -1:
                            sublines += 1
                        if line[3]:
                            subfunctions += 1
                            if line[1] > 0:
                                subcovered_functions += 1
                        if line[2] != []:
                            subbranches += len(line[2])
                            for branch in line[2]:
                                if branch:
                                    subcovered_branches += 1


                    # subcoverage.write(str(i) + ":")
                    # subcoverage.write(line[])
                    # subcoverage.write(line)

            with open(str(directory) + "/subcoverage_report.txt", "w") as subcoverage_report:
                subcoverage_report.write("Function Coverage: " + str(subcovered_functions) + "/" + str(subfunctions) + " = " + str(subcovered_functions/subfunctions) + "\n")
                subcoverage_report.write("Line Coverage: " + str(subcovered_lines) + "/" + str(sublines) + " = " + str(subcovered_lines/sublines) + "\n")
                subcoverage_report.write("Branch Coverage: " + str(subcovered_branches) + "/" + str(subbranches) + " = " + str(subcovered_branches/subbranches))


            for i, line in enumerate(self.tft_library_content_granular):
                self.tft_library_content_granular[i][1] = 0
                self.tft_library_content_granular[i][2] = []
                self.tft_library_content_granular[i][3] = False   

        lines = 0
        covered_lines = 0
        functions = 0
        covered_functions = 0
        branches = 0
        covered_branches = 0
        with open("../results/step8_florian/coverage_full.cov", "w") as coverage:
            for line in self.tft_library_content:
                if line[4] == True:
                    coverage.write(str(line) + "\n")
                    if line[1] > 0:
                        covered_lines += 1
                    if line[1] != -1:
                        lines += 1
                    if line[3]:
                        functions += 1
                        if line[1] > 0:
                            covered_functions += 1
                    if line[2] != []:
                        branches += len(line[2])
                        for branch in line[2]:
                            if branch:
                                covered_branches += 1
        with open("../results/step8_florian/coverage_report.txt", "w") as coverage_report:
            coverage_report.write("Function Coverage: " + str(covered_functions) + "/" + str(functions) + " = " + str(covered_functions/functions) + "\n")
            coverage_report.write("Line Coverage: " + str(covered_lines) + "/" + str(lines) + " = " + str(covered_lines/lines) + "\n")
            coverage_report.write("Branch Coverage: " + str(covered_branches) + "/" + str(branches) + " = " + str(covered_branches/branches))

