from __future__ import division
import random, pdb 
from main import *
from base import *
from file import *
# global The

def de():
  def call(i):
    global The
    The.tree.infoPrune = i[0]
    The.option.threshold = i[1]
    # The.option.minSize = i[2]
    The.tree.prune = i[2]
    return main( )

  def generate():
    infoPrune = round(random.uniform(0,Settings.de.limit[0]) ,2)
    threshold = round(random.uniform(0,Settings.de.limit[1]) ,2)
    prune = random.random() <= 0.5
    # prune = False
    # minSize = int(random.uniform(Settings.de.minl, Settings.de.maxl)) 
    return [infoPrune, threshold, prune]

  def evalute(frontier):
    for n, i in enumerate(frontier):
      scores[n] = call(i) # score[i]= [pd,pf,g]
    print scores
    ordered = sorted(scores.items(), key=lambda x: x[1][-1])  # alist of turple
    print ordered
    print(frontier)
    # return  frontier[ordered[-1][0]], ordered
    # pdb.set_trace()
    return scores

  def trim(i, x):
      return max(0.1, min(round(x,2), Settings.de.limit[i]))

  def gen3(n, f, frontier):
    seen = [n]

    def gen1(seen):
      while 1:
        k = random.randint(0, np - 1)
        if k not in seen:
          seen += [k]
          break
      return frontier[k]
    a = gen1(seen)
    b = gen1(seen)
    c = gen1(seen)
    return a, b, c

  def best(scores):
    ordered = sorted(scores.items(), key=lambda x: x[1][-1])  # alist of turple
    bestconf = frontier[ordered[-1][0]]
    bestscore = ordered[-1][1][-1]
    return bestconf, bestscore

  def update(n, old, frontier):
    newf = []
    a, b, c = gen3(n, old, frontier)
    for i in xrange(len(old)):
      if i == len(old) - 1:
        if cr < random.random():
          newf.append(old[i])
        else:
          newf.append(not old[i])  # true of false
      else:
        if cr < random.random():
          newf.append(old[i])
        else:
          # adapt to the Osyzcka model, pass n
          newf.append(trim(i,(a[i] + fa * (b[i] - c[i]))))
    return newf

  scores = {}
  global The  
  The.option.tuning = True
  np = Settings.de.np
  repeats = Settings.de.repeats
  fa = Settings.de.f
  cr = Settings.de.cr
  life = Settings.de.life
  # threshold = Settings.de.threshold
  frontier = [generate() for _ in xrange(np)]
  scores = evalute(frontier)
  bestconf, bestscore = best(scores)
  for k in xrange(repeats):
    if life < 0:
      break
    if bestscore > 80:
      print "bestscore " + str(bestscore)
      print "best conf " + str(bestconf)
      break
    nextgeneration = []
    for n, f in enumerate(frontier):
      new = update(n, f, frontier)
      newscore = call(new)
      if newscore[-1] > scores[n][-1]: # g value
        nextgeneration.append(new)
        scores[n] = newscore
      else:
        nextgeneration.append(f)
    frontier = nextgeneration[:]
    # scores = evalute(frontier)
    newbestconf, newbestscore = best(scores)
    if newbestscore > bestscore:
      bestscore = newbestscore
      bestconf = newbestconf
    else:
      life -= 1
  print "bestscore " + str(bestscore)
  print "best conf " + str(bestconf)
  The.tree.infoPrune = bestconf[0]
  The.option.threshold = bestconf[1]
  The.tree.prune = bestconf[2]
  The.option.tuning = False
  # f = open('myresult','a')
  writefile('bestscore: ' + str(bestscore)) # python will convert \n to os.linesep
  writefile('infoPrune: ' + str(The.tree.infoPrune))
  writefile('threshold: '+ str(The.option.threshold))
  writefile('prune: '+ str(The.tree.prune))
 
  # if scores < 75:
  #   print "mei zhao dao !!!"

if __name__ == "__main__":
  eval(cmd())
