from src.llmLibrary.CodeGen import CodeGen

class LibraryExplorer:
    def __init__(self):
        self.debug = False
        
        self.libraryFolder = "../sut_template/libs/TFT_eSPI_GD32/"
        self.libraryPath = self.libraryFolder + "TFT_eSPI.cpp"
        self.libraryHeaderPath = self.libraryFolder + "TFT_eSPI.h"
        
        self.role = "You are the developer of the 'TFT_eSPI' embedded graphics library."
        self.llm  = CodeGen(self.role, True, 1.0, 1.0, 200)
        
        self.methods = []
        self.prefiltered = []
        self.selectedMethods = []
        self.deselectedMethods = []

        
    def Understand(self):
        self.ExtractMethods()
        self.FilterVisibility()
        self.FilterDisplayOutputMethods()
        self.GenerateMethodFiles()

        print("*** Identified methods: " + str(len(self.methods)) )
        print("*** Prefiltered methods: " + str(len(self.prefiltered)) )
        print("*** Graphical methods: " + str(len(self.selectedMethods)) )
        print("*** Nongraphical methods: " + str(len(self.deselectedMethods)) )

    def ExtractMethods(self):
        with open(self.libraryPath , "r") as sourceCodeFile:
            sourceCode = sourceCodeFile.read()
            sourceCode = sourceCode.replace("\n", "")
            bracketCount = 0
            for i, char in enumerate(sourceCode):
                if char == "{":
                    if bracketCount == 0:
                        startPos = sourceCode.rfind("TFT_eSPI::", 0, i)
                        endPos = sourceCode.rfind(")", 0, i) + 1
                        signatureTokens = sourceCode[startPos:endPos].split()
                        signature = " ".join(signatureTokens)
                        signature = signature.replace("TFT_eSPI::", "")
                        self.methods.append(signature)
                    bracketCount += 1
                elif char == "}":
                    bracketCount -= 1
        remove = [""]
        self.methods = [x for x in self.methods if x not in remove]
        

    def FilterVisibility(self):
        with open(self.libraryHeaderPath, "r") as headerFile:
            headerCode = headerFile.read()
            headerCode.replace("\n", "")
            public_section_start = headerCode.find("public:")
            private_section_start = headerCode.find("private:")
            protected_section_start = headerCode.find("protected:")
                
            if public_section_start < private_section_start:
                if private_section_start < protected_section_start:
                    public_section_end = private_section_start
                else:
                    public_section_end = protected_section_start
            elif public_section_start < protected_section_start:
                if protected_section_start < private_section_start:
                    public_section_end = protected_section_start
                else:
                    public_section_end = private_section_start
            if self.debug:
                print("Public: " + str(public_section_start) + " - " + str(public_section_end))
                print("Private: " + str(private_section_start))
                print("Protected: " + str(protected_section_start))

        for method in self.methods:
            result = self.StudyVisibility(method, public_section_start, public_section_end)
            if result == True:
                self.prefiltered.append(method)
            else:
                self.deselectedMethods.append(method)

    def StudyVisibility(self, method, public_start, public_end):
        with open(self.libraryHeaderPath, "r") as headerFile:
            headerCode = headerFile.read()
            headerCode.replace("\n", "")
            method_position = headerCode.find(method.split("(")[0].strip())
            if method_position > public_start and method_position < public_end:
                return True
            else:
                return False

            
    def FilterDisplayOutputMethods(self):
        for method in self.prefiltered:
            result = self.StudyMethod(method)
            if result == True:
                self.selectedMethods.append(method)
            else:
                self.deselectedMethods.append(method)


    def StudyMethod(self, method):
        # role, reproducible, temperature, top_p, reload_after 
        #print(method)
        prompt = \
f"""There are multiple methods within your library. Take a closer look at the definition of the {method} method. 
For the following questions answer only with 'Yes' or 'No'.
Q: Calling the {method} method generates a graphical object on the display?
A: """
        result = self.llm.Prompt(prompt)
        
        if self.debug:
            print("Q: " + prompt)
            print("A: " + result)
        
        if result=="Yes":
            return True
        elif result=="No":
            return False
        else:
            print("ERROR:" + result)
        
    def GenerateMethodFiles(self):
        with open("../results/step1/prefiltered_methods.txt", "w") as prefilteredMethodsFile:
            for method in self.prefiltered:
                prefilteredMethodsFile.write(method + "\n")
        with open("../results/step1/selected_methods.txt", "w") as selectedMethodsFile:
            for method in self.selectedMethods:
                selectedMethodsFile.write(method + "\n")
        with open("../results/step1/deselected_methods.txt", "w") as deselectedMethodsFile:
            for method in self.deselectedMethods:
                deselectedMethodsFile.write(method + "\n")

        
