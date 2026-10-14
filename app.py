import os
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from frontend.ui import mulai

if __name__ == "__main__":
    mulai(os.path.join(RAIZ, "data"))
