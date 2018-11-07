import threading
import time
import sys
import random

i = 0
def printit():
  test = random.randint(0, 2)
  threading.Timer(3.0, printit).start()
  if (test == 1):
    print("1")
  elif (test == 2):
    print("-1")
  else:
    print("1")

  sys.stdout.flush()

printit()