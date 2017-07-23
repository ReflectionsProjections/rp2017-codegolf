# import user code
from answer import answer
import sys

def test(data):
  arg1 = ord(data[0])
  arg2 = ord(data[1])
  print(answer(arg1, arg2))

if __name__ == "__main__":
  a = sys.stdin.readline()
  test(a)
