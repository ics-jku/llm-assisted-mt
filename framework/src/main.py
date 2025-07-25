from src.actors.LibraryExplorer import LibraryExplorer
from src.actors.MRIdentifier import MRIdentifier
from src.actors.TCCreator import TCCreator
from src.actors.TCImplementor import TCImplementor
from src.actors.TCRunner import TCRunner
from src.actors.ResultAnalyzer import ResultAnalyzer
from src.actors.Reviser import Reviser

import sys
import time

import os


def main():

    step = int(sys.argv[1])

    if step == 1:
        print("*** Step 1: Understand the Library ***")
        start_time = time.time()
        LibraryExplorer().Understand()
        execution_time = time.time() - start_time
        print(f"*** Finished Step 1 in {execution_time} seconds ***" )
    elif step == 2:
        print("*** Step 2: Identify Metamorphic Relations ***")
        start_time = time.time()
        MRIdentifier().Identify()
        execution_time = time.time() - start_time
        print(f"*** Finished Step 2 in {execution_time} seconds ***" )
    elif step == 3:
        print("*** Step 3: Create Test Cases ***")
        start_time = time.time()
        TCCreator().Create()
        execution_time = time.time() - start_time
        print(f"*** Finished Step 3 in {execution_time} seconds ***" )
    elif step == 4:
        print("*** Step 4: Implement Test Cases ***")
        start_time = time.time()
        TCImplementor().Implement()
        execution_time = time.time() - start_time
        print(f"*** Finished Step 4 in {execution_time} seconds ***" )
    elif step == 5:
        print("*** Step 5: Run Test Cases ***")
        start_time = time.time()
        TCRunner().Run()
        execution_time = time.time() - start_time
        print(f"*** Finished Step 5 in {execution_time} seconds ***" )
    elif step == 6:
        print("*** Step 6: Analyze Results ***")
        start_time = time.time()
        ResultAnalyzer().Analyze()
        execution_time = time.time() - start_time
        print(f"*** Finished Step 6 in {execution_time} seconds ***" )
    elif step == 7:
        print("*** Step 7: Repeat and Refine ***")
        start_time = time.time()
        Reviser().RepeatAndRefine()
        execution_time = time.time() - start_time
        print(f"*** Finished Step 7 in {execution_time} seconds ***" )
    else:
        print(step)

