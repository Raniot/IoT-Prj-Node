import threading
import time
import sys
import random

i = 0
def printit():
  test = random.randint(0, 2)
  threading.Timer(3.0, printit).start()
  if (test == 1):
    print("Hello, World!")
  elif (test == 2):
    print("Hello, Python!")
  else:
    print("test2")

  sys.stdout.flush()

printit()