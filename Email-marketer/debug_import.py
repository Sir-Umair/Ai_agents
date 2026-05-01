import threading
import sys
import time
import traceback
import os

def f():
    time.sleep(60)
    sys.stderr.write("DUMPING TRACEBACK:\n")
    sys.stderr.write("".join(traceback.format_stack(sys._current_frames()[threading.main_thread().ident])))
    os._exit(1)

threading.Thread(target=f).start()
import app.main
