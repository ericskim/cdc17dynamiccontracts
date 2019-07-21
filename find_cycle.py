import networkx as nx
from networkx import *
import pickle

# G = nx.DiGraph([(0,1), (0,2), (1,2)])
# print(G)
# s=list(find_cycle(G, orientation='ignore'))
# print(s)




(inv,u)=pickle.load( open( "invaraint_automata.txt", "rb" ) )


G=[]
for s in inv:
    for sprime in u[s]:
        G.append((s,sprime))
G=nx.DiGraph(G)
cycle=find_cycle(G, source=None, orientation='original')
print(list(cycle))
for cycle in list(simple_cycles(G)):
    print(cycle)