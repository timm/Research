from __future__ import division
import sys
from os import listdir
from table import *
from os.path import isfile, join
from settings import *
from de import *
from sk import *
from time import strftime

def myrdiv(d):
	def pre(dist):
		l=dist.items()[0][-1]
		k = dist.items()[0][0]
		return [k].extend(l)
	stat = []
	for key,val in d.iteritems():
		val.insert(0,key)
		stat.append(val)
	# pdb.set_trace()
	return stat

def createfile():
	f = open('myresult','w').close()

def writefile(s):
	f = open('myresult', 'a')
	f.write(s+'\n')
	f.close()

def file(path="./data"):
  random.seed(10)
  createfile()
  folders = [f for f in listdir(path) if not isfile(join(path, f))]
  pd = {}
  pf = {}
  g = {}
  for one in folders[0:1]:
    nextpath = join(path, one)
    data = [join(nextpath, f)
            for f in listdir(nextpath) if isfile(join(nextpath, f))]
    predict = data.pop(-1)
    t_predict = data.pop(-1)
    t_train = data
    global The
    The.data.predict = t_predict
    The.data.train = t_train
    writefile("time :" +strftime("%Y-%m-%d %H:%M:%S"))
    writefile("dataset: "+one)
    for i in xrange(20):
#       de()
      The.data.predict = predict
      score = main()
      # pdb.set_trace()
      pd[str(one)] =pd.get(str(one),[]) + [float(score[0]/100)]
      pf[str(one)] = pf.get(str(one),[]) + [float(score[1]/100)]
      g[str(one)]= g.get(str(one),[]) + [float(score[2]/100)]
  # pdb.set_trace()
  print "*"*10+"pd"+"*"*10
  rdivDemo(myrdiv(pd))
  print "*"*10+"pf"+"*"*10
  rdivDemo(myrdiv(pf))
  print "*"*10+"g"+"*"*10
  rdivDemo(myrdiv(g))
  # f = open('myresult','a')
  # f.write('bestscore: ' + str(bestscore)+'\n') # python will convert \n to os.linesep
  # f.write('infoPrune: ' + str(he.tree.infoPrune)+'\n' )
  # f.write('threshold: '+ str(The.option.threshold)+'\n')
  # f.write('prune: '+ The.tree.prune + '\n')
  # f.close() 



if __name__ =="__main__":
	eval(cmd()) 