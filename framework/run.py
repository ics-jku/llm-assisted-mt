from src.main import main

import time

if __name__ == "__main__":
    print("-----------------------------------------------")
    print("-- Starting Program")
    print("-----------------------------------------------")
    start_time = time.time()
    main()
    execution_time = time.time() - start_time
    print("-----------------------------------------------")
    print(f"-- Execution time: {execution_time} seconds")
    print("-----------------------------------------------")