from __future__ import division
import sys
import collections  # using OrderedDict
from table import *
from where2 import *
from dtree import *
from Abcd import *
import pdb
import random
from base import *


#++++++++++++++++++++++++++++++++++++++++++++++++++++
# Preparing training, testing, data
#++++++++++++++++++++++++++++++++++++++++++++++++++++

def csv2py(f):
  sym2num = {}
  # sym2num hold all the characters with assinged numbers that never seen

  def str2num(t, p=0):
    def bigt():
      if isinstance(tbl, list):
        t = tbl[0]
        for i in range(1, len(tbl)):
          t._rows += tbl[i]._rows
      else:
        t =  tbl
      return t
    t = bigt()
    for r, row in enumerate(t._rows):
      for c, cell in enumerate(row.cells):
        if isinstance(cell, str) and c < t.depen[0].col and isinstance(t.headers[c], Sym):
          if sym2num.get(cell, 0) == 0:
            sym2num[cell] = p
            p += 1
          t._rows[r].cells[c] = sym2num[cell]  # update cell with num
    return t
  if isinstance(f, list):
    tbl = [table(src) for src in f]  # tbl is a list of tables
  else:
    tbl = table(f)
  tbl_num = str2num(tbl)
  x = data(indep=[x.name for x in tbl_num.indep],
           less=[x.name for x in tbl_num.depen],
           _rows=[row.cells for row in tbl_num._rows])
  return x, sym2num


def clustertbl(f, tree, num2sym):
  row = []
  if isinstance(f, list):
    tbl1 = tbl = table(f[0])
  else:
    tbl1 = tbl = table(f)
  newheader = Num()
  newheader.col = len(tbl.headers)
  newheader.name = "=klass"
  tbl1.headers += [newheader]  # tbl1 : the new table with cluster ID
  for k, _ in leaves(tree):
    for j in k.val:
      for i, cell in enumerate(j.cells):
        if isinstance(tbl.headers[i], Sym):
          j.cells[i] = num2sym.get(cell, cell)
      tmp = j.cells
      tmp.append((id(k) % 1000))
      # tmp.append(j.cells[tbl1.depen[0].col])
      # add the FIRST objective into the last cell of the row
      tmp.append(j.cells[tbl1.depen[0].col])
      # j.__dict__.update({'cells': tmp})
      j.update(cells=tmp)
      row.append(j.cells)
  tbl1 = clone(tbl1, row)
  return tbl1, row


def buildtestdata(t, num=1, data=[]):
  data += [t._rows.pop(random.randint(0, len(t._rows) - 1))
           for _ in range(num)]  # take random numbers of testdata
  return data


def buildtestdata1(f):  # build testdata from table
  actual = []
  testdata = []
  tbl = table(f)
  for row in tbl._rows:
    actual += ["Defective" if row.cells[tbl.depen[0].col]
               > 0 else "Non-Defective"]
    testdata += [row]
  return testdata, actual


def makedata(data):
  return data[:-1], data[-1]

#++++++++++++++++++++++++++++++++++++++++++++++++++++
# Leaves related function
#++++++++++++++++++++++++++++++++++++++++++++++++++++


def gotoleaf(testdata, tree, opt=The.tree):
  goleaf = []
  for row in testdata:
    goleaf += [apex(row, tree, opt)]
  return goleaf


def findleaves(tree, leaves=[]):
  for i, leaf in enumerate(dtleaves(tree)):
    leaf.__dict__.update(score=leafscore(leaf), leafid=i)
    leaves += [leaf]
  return leaves


def globalleaf(allleaves, node=None):
  mins = 10 ** 10
  contrastset = collections.OrderedDict()
  for leaf in allleaves:
    if leaf.score < mins:
      node = leaf
      mins = leaf.score
  for i in node.branch:
    contrastset[i[0].name] = i[1]
  contrastset["targetscore"] = mins
  return contrastset, mins


def leafscore(leaf):
  score = []
  # rows = map(lambda x:x.cells, leaf.rows)
  for row in leaf.rows:
    score += [row.cells[-1]]
  n = len(score)
  # p = q = max(0, int(n * 0.5) - 1)
  # if len(score) % 2 == 0:
  #   p = q + 1
  # mymedian = (score[p] + score[q]) * 0.5
  # mymedian = median(score)
  mean = float(sum(score) / n)
  return mean


def majorityscore(test, node):
  def score(neighbors):
    ordered = list(reversed(sorted(neighbors.iteritems())))
    scorelst = [pair[1] for pair in ordered[:The.option.k]]
    # score = sum(sum(scorelst, [])) / len(sum(scorelst, []))  # mean
    score = sum(scorelst, [])
    return score[0]

  neighbors = {}
  for row in node.rows:
    count = 0
    for data, cell in zip(test.cells, row.cells):
      if isinstance(cell, tuple):
        lo, hi = cell
        if lo <= data <= hi:
          count += 1
    neighbors[count] = neighbors.get(count, []) + [row.cells[-1]]
  return score(neighbors)


def apex(test, tree, opt=The.tree):  # from Dr. Menzies
  """apex=  leaf at end of biggest (most supported) 
   branch that is selected by test in a tree"""
  def equals(val, span):
    if val == opt.missing or val == span:
      return True
    else:
      if isinstance(span, tuple):
        lo, hi = span
        return lo <= val <= hi
      else:
        return span == val

  def apex1(cells, tree):
    found = False
    for kid in tree.kids:
      val = cells[kid.f.col]
      if equals(val, kid.val):
        for leaf in apex1(cells, kid):
          found = True
          yield leaf
    if not found:
      yield tree
  leaves = [(len(leaf.rows), leaf)
            for leaf in apex1(opt.cells(test), tree)]
  a = second(last(sorted(leaves)))
  try:
    oldtestdata = a.testdata
  except Exception:
    oldtestdata = []
  newtestdata = oldtestdata + [test]
  # append testdata to nodes in the tree
  a.__dict__.update(testdata=newtestdata)
  return a
#++++++++++++++++++++++++++++++++++++++++++++++++++++
# Find Contrast Set function
#++++++++++++++++++++++++++++++++++++++++++++++++++++


def buildcontrast1(tree, allleaves=[]):
  def addtoleaf(leaf, contrastset):
    thiscontrastset = contrastset[-1]
    for branch in leaf.branch:
      if thiscontrastset.get(branch[0].name, "") == str(branch[1]):
        del thiscontrastset[branch[0].name]
    # add contrast set to this leaf
    leaf.__dict__.update(contrastset=thiscontrastset)
    leaf.__dict__.update(target=thiscontrastset['targetscore'])
    try:
      leaf.__dict__.update(targetleaf=thiscontrastset['targetleaf'])
    except Exception:
      pass
    return leaf

  def br(node, score):
    if not node:
      return
    contrastdic = collections.OrderedDict()  # to track the order of item added
    for b in node.branch:
      # if l.branch[0].name
      contrastdic[b[0].name] = contrastdic.get(b[0].name, "") + str(b[1])
    contrastdic.update({"targetscore": score})
    contrastdic.update({"targeleaf": node.leafid})
    return contrastdic

  def findbetter1(kids, testscore, betternode=None):
    target = testscore
    for bro in kids:
      if bro.kids:
        continue
      if bro.score < target:
        target = bro.score  # find the better brother
        betternode = bro
    return br(betternode, target)

  def findbetter(leavesdic, i, l):
    if not int(i + l.lvl) in leavesdic:
      return
    if len(l.up.kids) > 1:  # priority1: find in brothers/Sisters
      branch = findbetter1(l.up.kids, l.score)
      if branch:
        return branch
    # priority2: find in aunts and uncles
    if l.up.up and len(l.up.up.kids) > 1:
      branch = findbetter1(l.up.up.kids, l.score)
      if branch:
        return branch
    for node in leavesdic[i + l.lvl]:  # priority3: find in cousins
      # tempscore = leafscore(node)
      if node.score < l.score:
        branch = br(node, node.score)
        return branch

  def findset(leavesdic, l, i=0, contrastset=[], branch=None):
    gl, bestscore = globalleaf(allleaves)  # the global best contrast set
    while True:
      if(l.lvl + abs(i) > max(leavesdic) or l.lvl - abs(i) < 0):
        # find the better leaves on the level 0
        branch = findbetter(leavesdic, -l.lvl, l)
        if branch:
          contrastset += [branch]
        elif bestscore == l.score:
          contrastset += [{"This is the best one!":
                           "No Contrast", "targetscore": l.score}]
        else:
          contrastset += [gl]  # not found, give the global best contrast set
        l = addtoleaf(l, contrastset)
        break
      branch = findbetter(leavesdic, -i, l)  # go up level
      if branch:
        contrastset += [branch]
        l = addtoleaf(l, contrastset)
        break
      i = -i  # up
      branch = findbetter(leavesdic, -i, l)  # go down i level
      if branch:
        contrastset += [branch]
        l = addtoleaf(l, contrastset)
        break
      i = abs(i) + 1
    return contrastset
  contrastset = []
  for sub in tree.kids:
    subleaves = [i for i in dtleaves(sub)]
    leavesdic = {}
    for l in subleaves:  # make teh subleaves dic
      # add all leaves under one subroot in to dic, according to lvl
      leavesdic[l.lvl] = leavesdic.get(l.lvl, []) + [l]
      # {1:[leaf1, leaf2,leaf4] 2:[]}
    for l in subleaves:  # build contrast set
      contrastset = findset(leavesdic, l)
  showTdiv(tree)
  printcontrastset(contrastset, allleaves)
  return tree


#++++++++++++++++++++++++++++++++++++++++++++++++++++
# Printing function
#++++++++++++++++++++++++++++++++++++++++++++++++++++
def printcontrastset(contrastset, allleaves):
  if not The.option.showConstrast:
    return
  print "\n" + "+" * 20 + "\nCONSTRAST SET:" + "\n" + "+" * 20
  for k, adit in enumerate(contrastset):
    if "This is the best one!" in adit:
      continue
    out = "leaf #" + str(k) + " score:" + str(round(allleaves[k].score, 2))
    for key, val in adit.iteritems():  # sort dict by key
      out += "  ==>" + str(key) + "=" + str(val)
    print out
    out = ""


def printtogo(nodelst):
  if not The.option.showTogo:
    return
  if not nodelst:
    return
  print "\n" + "+" * 20 + "\nTEST DATA:" + "\n" + "+" * 20
  for i, node in enumerate(nodelst):
    out = "testdata " + str(i) + " will go to"
    try:
      out += " leaf #" + str(node.leafid) + ": "
    except Exception:
      out += " node # " + str(node.mode) + ": "
    for i, b in enumerate(node.branch):
      out += b[0].name + "=" + str(b[1]) + " "
    print out


def showTdiv(n, lvl=-1):
  if not The.option.showDTree:
    return
  if n.f:
    say(('|..' * lvl) + str(n.f.name) + "=" + str(n.val) +
        "\t:" + str(n.mode) + " #" + str(nmodes(n)))
  if n.kids:
    nl()
    for k in n.kids:
      showTdiv(k, lvl + 1)
  else:
    s = classStats(n)
    print ' ' + str(int(100 * s.counts[s.mode()] / len(n.rows))) + '% * ' \
        + str(len(n.rows)) + '  leaf #' + str(n.leafid) + \
        '  score:' + str(round(n.score, 2))


def savetbl(t, fname):
  def writetofile(f, lst):
    f.write(",".join(map(str, lst)) + '\n')
  f = open(fname, 'wb')
  writetofile(f, [i.name for i in t.headers])  # write header
  for i in t._rows:
    writetofile(f, (i.cells))


def summarize(leaves, Dtree, befscore=0, aftscore=0):
  if not The.option.showSummarize:
    return
  for leaf in leaves:
    try:
      leaf.testdata
      befscore += leaf.score * len(leaf.testdata)
      try:
        leaf.contrastset["This is the best one!"]
        aftscore += leaf.score * len(leaf.testdata)
      except Exception:
        aftscore += len(leaf.testdata) * (leaf.contrastset["targetscore"])
    except Exception:
      continue
  print "\n" + "+" * 20 + "\nSummerize:" + "\n" + "+" * 20
  print "before appying contrastset: %s" % str(befscore)
  print "after appying contrastset: %s" % str(aftscore)


def _Abcd(testleaf, testdata, train):
  # train=[]
  test = []
  abcd = Abcd(db='Traing', rx='Testing')

  def isDef(x):
    return "Defective" if x > The.option.threshold else "Non-Defective"
  for leaf, data in zip(testleaf, testdata):
    try:
      test += [isDef(leaf.score)]
      # test +=[isDef(majorityscore(data,leaf))]
    except Exception:  # go to middle points
      # give the median of all rows in this point
      # pdb.set_trace()
      test += [isDef(leafscore(leaf))]
      continue
  for actual, predicted in zip(train, test):
    abcd.tell(actual, predicted)
  abcd.header()
  score = abcd.ask()
  return score


def buildtdiv(tbl):
  row = map(lambda x: x.cells, tbl._rows)
  t = discreteNums(tbl, row)
  tree = tdiv(t)
  # showTdiv(tree)
  return tree

#++++++++++++++++++++++++++++++++++++++++++++++++++++
# We start at hereee!
#++++++++++++++++++++++++++++++++++++++++++++++++++++


def run(train, test):
  # random.seed(1)
  # data = o(src = "data/nasa93train.csv")
  testdata, actual = buildtestdata1(test)
  m, sym2num = csv2py(train)
  num2sym = dict(zip(sym2num.values(), sym2num.keys()))
  Init(m)  # init The class
  tree = where2(m, m._rows)  # tree generated by clustering
  tbl1, row = clustertbl(train, tree, num2sym)  # new table with cluster ID
  # savetbl(tbl1, "data/trainingData")  # write new table to a file
  Dtree = buildtdiv(tbl1)
  leaves = findleaves(Dtree)
  buildcontrast1(Dtree, leaves)
  testleaf = gotoleaf(testdata, Dtree)  # all the leaves the testdata should go
  printtogo(testleaf)
  summarize(leaves, Dtree)
  score = _Abcd(testleaf, testdata, actual)
  return score


def main():
  global The
  if not The.option.tuning:
    print "infoPrune " + str(The.tree.infoPrune)
    print "threshold " + str(The.option.threshold)
    print "prune " + str(The.tree.prune)
    print "predict data:" + str(The.data.predict)
    print "train data:" + str(The.data.train)
  else:
    The.option.count +=1
    sys.stdout.write(">> ")
    sys.stdout.flush()
    if not The.option.count % Settings.de.np:
      print "\n"
  # pdb.set_trace()
    The.option.tuning = False
#   The.option.showDree = True
#   The.option.showTogo= True
  The.data.train =["./data/ant/ant-1.3.csv"]
  The.data.predict ="./data/ant/ant-1.4.csv"
  score = run(The.data.train, The.data.predict)
  return score


# def iteration(para):
#   global The
#   The.option = optionings(showSummarize=False, showDTree=False, showTogo=False)
#   The.tree.infoPrune = para[0]
#   The.option.threshold = para[1]
#   The.tree.prune = para[2]
#   print "infoPrune" + str(The.tree.infoPrune)
#   print "threshold" + str(The.option.threshold)
#   print "prune" + str(The.tree.prune)
#   return main()


if __name__ == "__main__":
  # iteration()
  eval(cmd())
