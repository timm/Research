from __future__ import division
import sys
import random
import math
import datetime
import time
import re
import pdb

sys.dont_write_bytecode = True


class Options:

  def __init__(i, **d):
    i.__dict__.update(d)

Settings = Options(de=Options(np=10,
                              repeats=1000,
                              f=0.75,
                              cr=0.85,
                              threshold=0.0001,
                              limit=[1,2],
                              life=5,
                              k = 0
                              ))
