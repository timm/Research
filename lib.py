from __future__ import division
import sys,re,random,math
sys.dont_write_bytecode = True

from demos    import *
from settings import *

def prefer(pairs1,pairs2,key = lambda x:x):
  out = {}
  for k,val in pairs1:
    k = key(k)
    out[k] = val
  for k,val1 in pairs2:
    k = key(k)
    if k in out:
      val2=out[k]
      if val1 == val2:
        del out[k]
  return out

def overlap(xs,ys):
  n = 0
  for x,y in zip(xs,ys):
    if x == y:
      n += 1
  return n / len(xs)

def shuffle(lst):
  random.shuffle(lst)
  return lst

rand = random.random
any  = random.choice
def seed(n = The.math.seed): random.seed(n)

def first(x): return x[0]
def second(x): return x[1]
def third(x): return x[2]
def fourth(x): return x[3]
def fifth(x): return x[4]
def last(x): return x[-1]

### printing

def g1(x)    : return round(x,1)
def g2(x)    : return round(x,2)
def g3(x)    : return round(x,3)
def gs1(lst) : return map(g1,lst)
def gs2(lst) : return map(g2,lst)
def gs3(lst) : return map(g3,lst)

def saysln(*lst):
  say(','.join(map(str, lst))); nl()
def says(*lst):
  say(','.join(map(str, lst)))
def say(x): 
  sys.stdout.write(str(x))
  sys.stdout.flush()
def nl(): print ""

def rprintln(x):  return rprint1(x,'\n')
def rprint(x)  :  return rprint1(x), nl()

def rprint1(x, end=None, dpth=-1):
  if end : space='  '
  else   : dpth,end,space = 1,'',' '
  tabs = lambda n : space * n
  q = lambda z : '\"%s\"'%z if isa(z,str) else str(z)
  def what2show(keys):
    return [k for k in sorted(keys) if not "_" == str(k)[0]]
  if callable(x):
    say(tabs(dpth) + 'function' + end)
  elif x==None or isa(x,str) or nump(x)   or isa(x,bool):
    say(tabs(dpth) + q(x) + end)
  elif isa(x,dict):
    for key in what2show(x.keys()):
      value = x[key]
      say(tabs(dpth) + (':%s' % key))
      if isa(value,str) or nump(value):
        say(( ' %s' % q(value))+ end)
      else: 
        say(end)
        rprint1(value, end, dpth + 1)
  elif listp(x):
    if len(x) == 0:
      say(tabs(dpth) + '[]' + end)
    else:
      for something in x:
        rprint1(something, end, dpth+1)
  elif x == None:
    say(tabs(dpth)+ 'None' + end)
  else:
    left,right,name = '{','}',x.__class__.__name__
    name = "" if name == None else name
#    if isa(x,Thing):
 #     left,right,name='{','}',''
    say(tabs(dpth) + name + left + end)
    rprint1(x.__dict__, end, dpth+1)
    say(tabs(dpth) + right + end)

def align(lsts,sep=' '):
  "Print, filled to max width of each column."
  width = {}
  for lst in lsts: # pass1- find column max widths
    for n,x in enumerate(lst):
      width[n] = max(widths.get(n,0),len('%s' % x))
  for lst in lsts: # pass2- print to max width
    for n,x in enumerate(lst):
      say(('%s' % x).rjust(width[n],' ')+sep)
    print ""
  print ""

### typings

isa  = isinstance
               
def nump(x)  : return isa(x,(int,long,float,complex))          
def listp(x) : return isa(x,(list,tuple))


def atoms(str,sep=',', bad=The.string.white):
  str = re.sub(bad,"",str)
  if str:
    return map(atom,str.split(sep))

def log2(x): return math.log(x,2)
def oddp(x): return (x % 2) == 1
def median(lst, ordered=False):
  if not ordered: lst=sorted(lst)
  n=len(lst)
  if n==1: return lst[0]
  if n==2: return (lst[0]+lst[1])*0.5
  mid = int(n/2)
  if oddp(n):
    return lst[mid]
  else:
    return (lst[mid] + lst[mid+1]) * 0.5

def ditto(lst,old,mark="."):
  "Show 'mark' if an item of  lst is same as old."
  out = []
  for i,now in enumerate(lst):
    before = old.get(i,None) # get old it if exists
    out   += [mark if  before == now else now]
    old[i] = now # next time, 'now' is the 'old' value
  return out # the lst with ditto marks inserted


if __name__ == '__main__': eval(cmd())
