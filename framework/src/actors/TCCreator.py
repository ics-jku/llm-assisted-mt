import os
import re

#from src.llmLibrary.LLMLlama3 import LLMLlama3
from src.llmLibrary.LLMLlama3_1 import LLMLlama3

class TCCreator:
    def __init__(self):
        self.role = "You are the developer of the 'TFT_eSPI' embedded graphics library."
        self.llm = LLMLlama3(self.role, True, 1.0, 1.0, 5)
        self.validAlternatives = []
        self.generatedTC = []

    def Create(self):
        self.lastGenerated = self.GetLastGenerated()
        self.ReadValidAlternatives()
        self.GenerateTC()
        #self.GenerateTCFiles()

    def GetLastGenerated(self):
        highest_number = 0
       
        # List all files in the specified directory
        for filename in os.listdir("../results/step3/"):
            if filename != "output.log":
                number = filename.split("_")[0]
                if int(number) > highest_number:
                    highest_number = int(number)

        return highest_number

    def ReadValidAlternatives(self):
        with open("../results/step2/valid_alternatives.txt", "r") as alternativesFile:
            alternatives = alternativesFile.readlines()
            for alternative in alternatives:
                self.validAlternatives.append(alternative.split("|"))
                #self.methods.append(method.replace("\n", ""))
    
    def GenerateTC(self):
        for i, alternative in enumerate(self.validAlternatives):
            if i > self.lastGenerated:
                print(alternative[0] + "|" + alternative[1].replace("\n", ""))
                prompt = f"""Generate an alternative implementation of the source code: {alternative[0]}
Follow the hard requirement:
- use the '{alternative[1].replace("\n", "")}' method for your implementation
- make sure the same geometrical properties are kept
- the image created on the display stays the same
- output only the C++ code"""
                result = self.llm.Prompt(prompt)
                #print("RESULT: " + result)
                self.generatedTC.append([alternative[0], alternative[1], result])
                with open("../results/step3/" + str(i) + "_" + alternative[0].split("(")[0] + alternative[1].split("(")[0], "w") as tcFile:
                    tcFile.write("--- Source ---\n" + alternative[0] + "\n")
                    tcFile.write("--- Follow-up ---\n" + result)

    # def GenerateTCFiles(self):
    #     for i, tc in enumerate(self.generatedTC):
    #         with open("../results/step3/" + str(i) + tc[0].split("(")[0] + tc[1].split("(")[0], "w") as tcFile:
    #             tcFile.write("--- Source ---\n" + tc[0] + "\n")
    #             tcFile.write("--- Follow-up ---\n" + tc[2])

    # def GenerateSourceUp(self):
    #     lastSource = ""
    #     for alternative in self.validAlternatives:
    #         sourceMethod = alternative[0]
    #         if lastSource != sourceMethod:
    #             prompt = f"""Generate a working C++ example function to demonstrate the functionality of the {sourceMethod} method. Output only the generated C++ code."""
    #             result = self.llm.Prompt(prompt)
    #             clean_alternative = sourceMethod.split("(")[0]
    #             newAlternative = clean_alternative
    #             count = 0
    #             while(newAlternative in self.generatedSources):
    #                 newAlternative = clean_alternative + str(count)
    #                 count += 1 

    #             with open("./Outputs/step3/source/" + newAlternative, "w") as sourceFile:
    #                 sourceFile.write(result)


    #             lastSource = sourceMethod
    #         #print("Source: " + alternative[0])
    #         #print("Follow-Up: " + alternative[1])