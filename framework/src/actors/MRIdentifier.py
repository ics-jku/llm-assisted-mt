#from src.llmLibrary.LLMLlama3 import LLMLlama3
from src.llmLibrary.LLMLlama3_1 import LLMLlama3

class MRIdentifier:
    def __init__(self):
        self.role = "You are the developer of the 'TFT_eSPI' embedded graphics library."
        self.llm = LLMLlama3(self.role, True, 1.0, 1.0, 4000)
        self.methods = []
        self.validAlternatives = []
        self.invalidAlternatives = []


    def Identify(self):
        self.ReadMethods()
        self.CheckAlternatives()
        self.GenerateMethodFiles()

        print("*** Valid Alternatives: " + str(len(self.validAlternatives)) )
        print("*** Invalid Alternatives: " + str(len(self.invalidAlternatives)) )

    def ReadMethods(self):
        with open("../results/step1/selected_methods.txt", "r") as selectedMethodsFile:
            methods = selectedMethodsFile.readlines()
            for method in methods:
                self.methods.append(method.replace("\n", ""))

    def CheckAlternatives(self):
        notGeneratables = []
        with open("../results/step2/not_generatable.txt", "r") as notGenerateableFile:
            notGeneratableList = notGenerateableFile.readlines()
            for notGeneratable in notGeneratableList:
                notGeneratables.append(notGeneratable.split("|"))
        for method in self.methods:
            for alternative_method in self.methods:
                prompt = f"""For all possible parameters, can a working alternative of the following source code be generated: {method} 
Follow the hard requirements:
- the functionality should be implemented using the {alternative_method} api method 
- the same geometrical properties and the colors need to be kept for the generated display output
- make sure not only the outline of the objects matches but also the infill
Answer only with 'Yes' or 'No'"""
                result = self.llm.Prompt(prompt).replace(".","")
                #print(result)
                alternative = method + "|" + alternative_method
                if result=="Yes":
                    generatable = True
                    for notGeneratable in notGeneratables:
                        if method == notGeneratable[0] and alternative_method == notGeneratable[1].replace("\n", ""):
                            generatable = False
                    if generatable:
                        self.validAlternatives.append(alternative)
                elif result=="No":
                    self.invalidAlternatives.append(alternative)
                else:
                    print("!!! ERROR: " + alternative + " " + result)
                    

    def GenerateMethodFiles(self):
        with open("../results/step2/valid_alternatives.txt", "w") as validAlternativesFile:
            for method in self.validAlternatives:
                validAlternativesFile.write(method + "\n")
        with open("../results/step2/invalid_alternatives.txt", "w") as invalidAlternativesFile:
            for method in self.invalidAlternatives:
                invalidAlternativesFile.write(method + "\n")     
        