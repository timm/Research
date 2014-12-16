from __future__ import division
from lib    import *
from demos  import *
from counts import *
from fi     import *

import sys
sys.dont_write_bytecode = True

def rows(file, 
          sep= The.reader.sep,
          bad= The.reader.bad):
  """Read comma-seperated rows that might be split 
  over many lines.  Finds strings that can compile 
  to nums.  Kills comments and white space."""
  n,kept = 0,""
  ins = open(file)
  for line in ins:
    now   = re.sub(bad,"",line) # kill white space
    kept += now
    if kept:
      if not now[-1] == sep:
        yield n, map(atom,kept.split(sep))
        n += 1
        kept = "" 
  ins.close()

def row(file,skip= The.reader.skip):
  "Leaps over any columns marked 'skip'."
  todo = None
  for n,line in rows(file): # line is a list including elements of  one row
    todo = todo or [col for col,name in enumerate(line) 
                    if not skip in name]
    yield n, [ line[col] for col in todo ]

## Read Headers and Rows
def table(source, rows = True, contents = row):
  t = table0(source) # Thing object
  for n,cells in contents(source): # cells is a list including one row elements
    if n == 0 : head(cells,t) 
    else      : body(cells,t,rows) 
  #print ">>>>", t.headers
  return t

def centroid(tbl,selections=False):
  return [h.centroid() for h in tbl.headers if (not selections or h.selected)]

## Create Table 
def table0(source):
  return Thing(source = source,
    depen=[], indep=[], nums =[], syms=[], 
    more =[], less =[], klass=[], headers=[], 
    _rows=[], at   ={}, patterns= The.reader.patterns)

def head(cells,t,numc=The.reader.numc):
  for col,cell in enumerate(cells): # col is # of col, cell is the element in col, cells are just headers
    this   = Num if numc in cell else Sym #
    this.rank = 0 # rank is the arribute of instance this?
    header = this() # header is Sym or Num instance
    header.col, header.name = col,cell
    t.at[cell] = header # t.at?????
    for pattern,val in t.patterns.items():
      if re.search(pattern,cell):
        where  = val(t)  ### where is a lamda function :t.indep or t.depen etc....
        where += [header]## put header into t.indep or t.depen  
  return t

def body(cells,t,keep=True):
  #print "LEN?",len(t._rows)
  for n,header in enumerate(t.headers):
    cell = cells[header.col]# cells is one row, cell is the element of col
    #print n,"!",cell,"!"
    if not cell == The.reader.missing:
      header + cell # 
  if keep: 
    new = Row(cells)
    t._rows += [new] # put new in to t._rows 

class Row(Thing):
  def __init__(i,cells):# keep one row
    i.newId() # get the new ID from Thing
    i.id = Row.id = Row.id +1
    i.cells = cells
    i.pos = []
    i.x0,i.y0= 0,0
  def addCells(i, cells):
    i.cells += [cells]


def discreteTable(f,contents=lambda x: row(x)):
  rows, t = [],  table0(f)
  for n,cells in contents(f):  
    if n==0 : head(cells,t) 
    else    : rows += [cells]
  return discreteNums(t,rows)

def discreteNums(tbl,therows):
  for num in tbl.indep:
    if isinstance(num,Num) and not num in tbl.depen:
      edivresults = ediv(therows,
                       num=lambda x:x[num.col], # change Dr. Menzies' code style
                       sym=lambda x:x[tbl.klass[0].col]) # classify each column according to entropy
      for cut in edivresults:
      #print num.name, cut.at
        for row in cut._has:  #
          row[num.col] = cut.range # update each cell with the range value of that cluster.
  return clone(tbl, discrete=True, rows=therows)


def clone(tbl1,rows=[],discrete=False,keepSelections=False) :
  def ok(x):
    if x[-1]=="/":  return x # what does "/" mean?
    return x.replace("$",'') if discrete else x
  tbl2= head([ok(h.name) for h in tbl1.headers],
             table0('copy of '+tbl1.source)) 
  if keepSelections:
    for h in tbl1.headers:
      tbl2.headers[h.col].selected = h.selected
  for cells in rows:  body(cells,tbl2,True)
  return tbl2


@demo
def tabled(f='data/weather.csv'):
  t=table(f)
  for x in  t.indep: rprintln(x)
  #rprintln(t)

@demo
def tableCopied(f='data/weather.csv'):
  t0=table(f)
  t1=copyTable(t0)
  rprintln([t0.nums,t1.nums]); 

if __name__ == '__main__': eval(cmd())
