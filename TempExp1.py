from topology import *
from network_everything import *
import contract_propagation # not needed


T=6
D={}
X_initial={}
for t in range(0,T):
    for link in N[1].links:
        D[link,t]=1.5

for link in N[1].links:
    X_initial[link]=1.5
        

(state,control,output)=N[1].guarantee_miner(T,D,X_initial)
for l in N[1].links:
    print "\n***************",l
    print "\nstates:"
    for t in range(0,T):
        if l.type!="sink":
            print state[l,t],
    print "\ncontrols:"
    for t in range(0,T):
        if l.type!="sink":
            print control[l,t],
    print "\noutput:"
    for t in range(0,T):
        if l.type=="sink":
            print output[l,t],
