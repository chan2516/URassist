 
import multiprocessing
import subprocess
import sys
import os

ENABLE_HOTWORD = False

# To run Jarvis
def startJarvis():
        # Code for process 1
        print("Process 1 is running.")
        from main import start
        start()

# To run hotword
def listenHotword():
        # Code for process 2
        print("Process 2 is running.")
        from engine.features import hotword
        hotword() 


# Start both processes
if __name__ == '__main__':
        # Set multiprocessing start method to spawn for Windows
        multiprocessing.set_start_method('spawn', force=True)
        
        p1 = multiprocessing.Process(target=startJarvis)
        p2 = multiprocessing.Process(target=listenHotword) if ENABLE_HOTWORD else None
        p1.start()
        # subprocess.call([r'device.bat'])
        if p2 is not None:
            p2.start()
        p1.join()

        if p2 is not None and p2.is_alive():
            p2.terminate()
            p2.join()

        print("system stop")