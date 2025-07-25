#from src.llmLibrary.LLMLlama3 import LLMLlama3
from src.llmLibrary.LLMLlama3_1 import LLMLlama3

class TCImplementor:
    def __init__(self):
        self.role = "You are the developer of the 'TFT_eSPI' embedded graphics library."
        self.llm = LLMLlama3(self.role, True, 1.0, 1.0, 100)
        self.prefilteredMethods = []
        with open ("../results/step1/prefiltered_methods.txt", "r") as prefilteredFile:
            prefiltered = prefilteredFile.readlines()
            for method in prefiltered:
                self.prefilteredMethods.append(method.split("(")[0])


    def Implement(self):
        #self.ExportCSVList()
        #self.GenerateConstraints()
        #self.GenerateMain()
        self.ImplementTCGenerators()
        
    def GenerateConstraints(self):
        with open("../results/step1/selected_methods.txt", "r") as selectedMethodsFile:
            methods = selectedMethodsFile.readlines()
            with open("../sut/Generators/Util/constraints.py", "w") as constraintsFile:
                for i, method in enumerate(methods):
                    constraintsFile.write(method.split("(")[0] + " = {\n")
                    prompt = f"Assuming you have a display with 320x240, for each parameter of the {method} method, name a possible range for each parameter to execute random testing. Do not add additional text and answer only with the parameters in the form of: - '<parameter>' : [start_range, end_range]"
                    result = self.llm.Prompt(prompt)
                    #print(result)
                    parameters = result.split("\n")
                    param_count = 0
                    for i, parameter in enumerate(parameters):
                        if parameter.startswith("-"):
                            if param_count != 0:
                                constraintsFile.write(",\n")
                            constraintsFile.write(parameter.replace("-", "   ").replace("`", "'").replace(".0", "").replace(".1", "").split("(")[0])
                            param_count += 1
                    constraintsFile.write("\n}\n\n")
                    #self.generatedTC.append([alternative[0], result])
    
    def GenerateMain(self):
        with open("../sut/Main.py", "w") as mainFile:
            mainFile.write("from test_runner import TestRunner\n")
            mainFile.write("\n")
            with open("../results/step2/valid_alternatives.txt", "r") as validAlternativesFile:
                validAlternatives = validAlternativesFile.readlines()
                for i, validAlternative in enumerate(validAlternatives):
                    alternatives = validAlternative.split("|")
                    mrName = "mtc_" + str(i + 1) + "_" + alternatives[0].split("(")[0] + alternatives[1].split("(")[0]
                    mainFile.write("from Generators.LLM." + mrName + " import " + mrName + "\n")
                    mainFile.write("TestRunner(" + mrName + "()).run(1)\n\n")

    def ExportCSVList(self):
        with open("../results/step4/to_be_verified.csv", "w") as csvFile:
            csvFile.write("Source;Follow-Up;Compileable;Executable;Operational\n")
            with open("../results/step2/valid_alternatives.txt", "r") as validAlternativesFile:
                validAlternatives = validAlternativesFile.readlines()
                for validAlternative in validAlternatives:
                    alternatives = validAlternative.split("|")
                    csvFile.write(alternatives[0].replace(" ", "") + ";" + alternatives[1].replace("\n", "").replace(" ", "") + ";;;\n")

    def ImplementTCGenerators(self):
        with open("../results/step2/valid_alternatives.txt", "r") as validAlternativesFile:
            validAlternatives = validAlternativesFile.readlines()
            for i, validAlternative in enumerate(validAlternatives):
                alternatives = validAlternative.split("|")
                mrName = "mtc_" + str(i + 1) + "_" + alternatives[0].split("(")[0] + alternatives[1].split("(")[0]
                #print(mrName)
                parameters = []

                signature = alternatives[0].split("(")[1]
                signature = signature.split(",")
                
                for sourceParameter in signature:
                    sourceParameter = sourceParameter.strip().replace(")", "")
                    parameters.append(sourceParameter.split(" ")[1])
                    #print("    " + sourceParameter.split(" ")[1])
                with open("../sut/Generators/LLM/" + mrName + ".py", "w") as generator:
                    generator.write('import random\n')
                    generator.write('import Generators.Util.constraints\n')
                    generator.write('from Generators.Util.mtc_generator import MTCGenerator\n')
                    generator.write('\n')
                    generator.write(f'class {mrName}(MTCGenerator):\n')
                    generator.write(f'    def __init__(self, path="", name = "{mrName}"):\n')
                    generator.write(f'       super({mrName}, self).__init__(path,name)\n')
                    generator.write('\n')
                    generator.write('    def source_testcase(self,cpp):\n')
                    generator.write(f'        cpp(f"tft.{alternatives[0].split("(")[0]}(')
                    for j, parameter in enumerate(parameters):
                        if j != 0:
                            generator.write(", ")
                        generator.write("{self.args['" + parameter + "']}")
                    generator.write(');")\n')
                    generator.write('\n')
                    generator.write('    def followup_testcase(self, cpp):\n')
                    cpp_support = False
                    with open("../results/step3/" + str(i+1) + "_" + alternatives[0].split("(")[0] + alternatives[1].split("(")[0], "r") as mrFile:
                        mr = mrFile.readlines()
                        followup_found = False
                        cpp_found = False
                        cpp_possible_support = False
                        first_support = True
                        for line in mr:
                            if line.startswith("--- Follow-up ---"):
                                
                                followup_found = True
                            if followup_found: 
                                if line.find(alternatives[0].split("(")[0] + "Alt") != -1:
                                    line = line.replace(alternatives[0].split("(")[0] + "Alternative", alternatives[0].split("(")[0])
                                    line = line.replace(alternatives[0].split("(")[0] + "Alt", alternatives[0].split("(")[0])
                                if cpp_found and not cpp_possible_support and line.find(alternatives[0]) == -1 and line != "}\n" and not line.startswith("```"):
                                    line = line.replace("{", "{{").replace("}", "}}")
                                    line = line[:line.find("//")]
                                    line = line.replace(alternatives[1].split("(")[0], "tft." + alternatives[1].split("(")[0])
                                    for method in self.prefilteredMethods:
                                        if line.find(method) != -1 and line.find("tft." + method) == -1:
                                            line = line.replace(method, "tft." + method)
                                    line = line.replace("TFT_eSPI::", "tft.")
                                    line = line.replace('"', '\\"')
                                    for parameter in parameters:
                                        line = line.replace(" " + parameter + ", ", " {self.args['" + parameter + "']}, ")
                                        line = line.replace(" " + parameter + " + ", " {self.args['" + parameter + "']} + ")
                                        line = line.replace(" " + parameter + " - ", " {self.args['" + parameter + "']} - ")
                                        line = line.replace(" " + parameter + " / ", " {self.args['" + parameter + "']} / ")
                                        line = line.replace(" " + parameter + " * ", " {self.args['" + parameter + "']} * ")
                                        line = line.replace(" " + parameter + " && ", " {self.args['" + parameter + "']} && ")
                                        line = line.replace(" " + parameter + " == ", " {self.args['" + parameter + "']} == ")
                                        line = line.replace("(" + parameter + " > ", "({self.args['" + parameter + "']} > ")
                                        line = line.replace("(" + parameter + " < ", "({self.args['" + parameter + "']} < ")
                                        line = line.replace("(" + parameter + " == ", "({self.args['" + parameter + "']} == ")
                                        line = line.replace("(" + parameter + "!= ", "({self.args['" + parameter + "']}!= ")
                                        line = line.replace("(" + parameter + " % ", "({self.args['" + parameter + "']} % ")
                                        line = line.replace(" " + parameter + ")", " {self.args['" + parameter + "']})")
                                        line = line.replace("(" + parameter + ", ", "({self.args['" + parameter + "']}, ")
                                        line = line.replace("(" + parameter + " + ", "({self.args['" + parameter + "']} + ")
                                        line = line.replace("(" + parameter + " - ", "({self.args['" + parameter + "']} - ")
                                        line = line.replace("(" + parameter + " / ", "({self.args['" + parameter + "']} / ")
                                        line = line.replace("(" + parameter + " * ", "({self.args['" + parameter + "']} * ")
                                        line = line.replace("(" + parameter + " & ", "({self.args['" + parameter + "']} & ")
                                        line = line.replace("(" + parameter + " << ", "({self.args['" + parameter + "']} << ")
                                        line = line.replace("(" + parameter + ")", "({self.args['" + parameter + "']})")
                                        line = line.replace("(" + parameter + " >>", "({self.args['" + parameter + "']} >>")
                                        line = line.replace("(" + parameter + " <=", "({self.args['" + parameter + "']} <=")
                                        line = line.replace("(" + parameter + " &&", "({self.args['" + parameter + "']} &&")
                                        line = line.replace("(!" + parameter + ") ", "(!{self.args['" + parameter + "']}) ")
                                        line = line.replace(")" + parameter + ";", "){self.args['" + parameter + "']};")
                                        line = line.replace(")" + parameter + " *", "){self.args['" + parameter + "']} *")
                                        line = line.replace(")" + parameter + " +", "){self.args['" + parameter + "']} +")
                                        line = line.replace(")" + parameter + " /", "){self.args['" + parameter + "']} /")
                                        line = line.replace("[" + parameter + "]", "[{self.args['" + parameter + "']}]")
                                        line = line.replace("[" + parameter + " * ", "[{self.args['" + parameter + "']} * ")
                                        line = line.replace("[" + parameter + " + ", "[{self.args['" + parameter + "']} + ")
                                        line = line.replace("[" + parameter + " - ", "[{self.args['" + parameter + "']} - ")
                                        line = line.replace("[" + parameter + " * ", "[{self.args['" + parameter + "']} * ")
                                        line = line.replace(" * " + parameter + "]", " * {self.args['" + parameter + "']}]")
                                        line = line.replace(" * " + parameter + ";", " * {self.args['" + parameter + "']};")
                                        line = line.replace("*" + parameter + "+", "*{self.args['" + parameter + "']}+")
                                        line = line.replace("*" + parameter + " +", "*{self.args['" + parameter + "']} +")
                                        line = line.replace("{" + parameter + ", ", "{{self.args['" + parameter + "']}, ")
                                        line = line.replace(", " + parameter + "}", ", {self.args['" + parameter + "']}}")
                                        line = line.replace(", " + parameter + ",", ", {self.args['" + parameter + "']},")
                                        line = line.replace(", " + parameter + " &", ", {self.args['" + parameter + "']} &")
                                        line = line.replace(", " + parameter + "? ", ", {self.args['" + parameter + "']}? ")
                                        line = line.replace(", " + parameter + " >>", ", {self.args['" + parameter + "']} >>")
                                        line = line.replace(", &" + parameter + ")", ", {self.args['" + parameter + "']})")
                                        line = line.replace("= " + parameter + ";", "= {self.args['" + parameter + "']};")
                                        line = line.replace("= " + parameter + " &", "= {self.args['" + parameter + "']} &")
                                        line = line.replace("= " + parameter + " >>", "= {self.args['" + parameter + "']} >>")
                                        line = line.replace("= " + parameter + "? ", "= {self.args['" + parameter + "']}? ")
                                        line = line.replace("= " + parameter + " %", "= {self.args['" + parameter + "']} %")
                                        line = line.replace("= -" + parameter + ";", "= -{self.args['" + parameter + "']};")
                                        line = line.replace("= -" + parameter + " *", "= -{self.args['" + parameter + "']} *")
                                        line = line.replace("- " + parameter + ";", "- {self.args['" + parameter + "']};")
                                        line = line.replace("-" + parameter + " /", "-{self.args['" + parameter + "']} /")
                                        line = line.replace("-" + parameter + " &&", "-{self.args['" + parameter + "']} &&")
                                        line = line.replace("-" + parameter + ",", "-{self.args['" + parameter + "']},")
                                        line = line.replace("- " + parameter + ",", "- {self.args['" + parameter + "']},")
                                        line = line.replace("+ " + parameter + ";", "+ {self.args['" + parameter + "']};")
                                        line = line.replace("+ " + parameter + "]", "+ {self.args['" + parameter + "']}]")
                                        line = line.replace("+ " + parameter + " >", "+ {self.args['" + parameter + "']} >")
                                        line = line.replace("+ " + parameter + ",", "+ {self.args['" + parameter + "']},")
                                        line = line.replace("+ " + parameter + " +", "+ {self.args['" + parameter + "']} +")
                                        line = line.replace("* " + parameter + " *", "* {self.args['" + parameter + "']} *")
                                        line = line.replace("/ " + parameter + ";", "/ {self.args['" + parameter + "']};")
                                        line = line.replace("< " + parameter + ";", "< {self.args['" + parameter + "']};")
                                        line = line.replace("> " + parameter + ";", "> {self.args['" + parameter + "']};")
                                        line = line.replace("? " + parameter + " : ", "? {self.args['" + parameter + "']} : ")
                                        line = line.replace(": " + parameter + ";", ": {self.args['" + parameter + "']};")
                                        line = line.replace("% " + parameter + ";", "% {self.args['" + parameter + "']};")
                                        line = line.replace("| " + parameter + ";", "| {self.args['" + parameter + "']};")
                                        line = line.replace("!= " + parameter + " ||", "!= {self.args['" + parameter + "']} ||")
                                        line = line.replace("!= " + parameter + " ||", "!= {self.args['" + parameter + "']} ||")
                                        line = line.replace("== " + parameter + " ||", "== {self.args['" + parameter + "']} ||")
                                        line = line.replace(">= " + parameter + " ||", ">= {self.args['" + parameter + "']} ||")
                                        line = line.replace("<= " + parameter + " ||", "<= {self.args['" + parameter + "']} ||")
                                        line = line.replace("|| " + parameter + " >=", "|| {self.args['" + parameter + "']} >=")
                                        line = line.replace("|| " + parameter + " <", "|| {self.args['" + parameter + "']} <")
                                        line = line.replace("|| " + parameter + " &", "|| {self.args['" + parameter + "']} &")
                                        line = line.replace("|= " + parameter + " &", "|= {self.args['" + parameter + "']} &")
                                        line = line.replace("&& " + parameter + " >", "&& {self.args['" + parameter + "']} >")
                                        line = line.replace("(uint16_t*)&" + parameter + ")", "(uint16_t*)({self.args['" + parameter + "']}))")
                                        line = line.replace("(uint8_t*)&" + parameter + ",", "(uint8_t*)({self.args['" + parameter + "']}),")
                                        line = line.replace("(uint16_t *)&" + parameter + ")", "(uint16_t *)({self.args['" + parameter + "']}))")
                                        line = line.replace("(uint8_t *)&" + parameter + ",", "(uint8_t *)({self.args['" + parameter + "']}),")
                                        line = line.replace("(uint8_t *)" + parameter + ",", "(uint8_t *)({self.args['" + parameter + "']}),")
                                        line = line.replace("(uint8_t*)" + parameter + ",", "(uint8_t*)({self.args['" + parameter + "']}),")
                                        line = line.replace("(const uint8_t *)&" + parameter + ",", "(const uint8_t *)({self.args['" + parameter + "']},")
                                        line = line.replace("(const uint16_t *)&" + parameter + ",", "(const uint16_t *)({self.args['" + parameter + "']}),")
                                        line = line.replace("(const uint16_t *)&" + parameter + ")", "(const uint16_t *)({self.args['" + parameter + "']}))")
                                        line = line.replace("(const uint16_t *) &" + parameter + ")", "(const uint16_t *)({self.args['" + parameter + "']}))")
                                        line = line.replace("(uint16_t *)&" + parameter + ",", "(uint16_t *)({self.args['" + parameter + "']}),")
                                        line = line.replace("(uint16_t *) &" + parameter + ")", "(uint16_t *)({self.args['" + parameter + "']}))")
                                        line = line.replace("(float)" + parameter + ",", "(float)({self.args['" + parameter + "']}),")
                                        line = line.replace("(float)" + parameter + ")", "(float)({self.args['" + parameter + "']}))")
                                        line = line.replace("(int)" + parameter + " -", "(int)({self.args['" + parameter + "']}) -")
                                        line = line.replace("(int32_t)" + parameter + ",", "(int32_t)({self.args['" + parameter + "']}),")
                                        line = line.replace("(int32_t)" + parameter + " &&", "(int32_t)({self.args['" + parameter + "']}) &&")
                                        line = line.replace("(int16_t)" + parameter + ",", "(int16_t)({self.args['" + parameter + "']}),")
                                        line = line.replace("(int32_t)" + parameter + ")", "(int32_t)({self.args['" + parameter + "']}))")
                                        line = line.replace("(int32_t)" + parameter + " -", "(int32_t)({self.args['" + parameter + "']}) -")
                                        #line = line.replace(parameter + " += ", "int32_t " + parameter + " = {self.args['" + parameter + "']}; " + parameter + " += ")
                                    generator.write('        cpp(f"' + line.replace("\n", "")[4:] + '")\n')
                                if cpp_possible_support and not line.startswith("```"):
                                    line = line.replace("{", "{{").replace("}", "}}")
                                    if first_support:
                                        cpp_support = True
                                        generator.write("\n")
                                        generator.write('    def support_functions(self, cpp):\n')
                                        first_support = False
                                    generator.write('        cpp(f"' + line.replace("\n", "") + '")\n')
                                if cpp_found and line == "}\n":
                                    cpp_possible_support = True
                                if line.startswith("```cpp"):
                                    cpp_found = True
                                elif cpp_found and line.startswith("```"):
                                    break
                    generator.write("\n")
                    if not cpp_support:
                        generator.write('    def support_functions(self, cpp):\n')
                        generator.write('        pass\n')
                    generator.write('\n')
                    generator.write(f'    def random_args(self):\n')
                    generator.write(f'        constraints = Generators.Util.constraints.{alternatives[0].split("(")[0]}\n')
                    generator.write(f'        self.args = {{ }}\n')
                    generator.write(f'        for val in constraints:\n')
                    generator.write(f'            if isinstance(constraints[val][0],bool):\n')
                    generator.write(f'                if random.randrange(0,10,1) >= 5:\n')
                    generator.write(f'                    self.args[val] = "true"\n')
                    generator.write(f'                else:\n')
                    generator.write(f'                    self.args[val] = "false"\n')
                    generator.write(f'            else:\n')
                    generator.write(f'                self.args[val] = random.randrange(*constraints[val])\n')
                                

                                