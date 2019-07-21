from topology import *

# Here we should consider output links
L={}

for dir in ["East","West","North","South"]:
	for i in [1,2]:
		L[(i,dir)]=link("road",40,15,"road %s %d" %(dir,i))
	L[(3,dir)]=link("sink",1000,15,"road %s %d" %(dir,3))

N=network()
N.links=L.values()

# for l in N.links:
# 	print l
	
N.link2link(L[(1,"North")],L[(2,"North")],1,0.65)
N.link2link(L[(1,"North")],L[(3,"East")],1,0.25)

N.link2link(L[(2,"North")],L[(3,"North")],1,0.65)
N.link2link(L[(2,"North")],L[(2,"West")],1,0.25)

N.link2link(L[(1,"East")],L[(2,"East")],1,0.65)
N.link2link(L[(1,"East")],L[(3,"South")],1,0.25)

N.link2link(L[(2,"East")],L[(3,"East")],1,0.65)
N.link2link(L[(2,"East")],L[(2,"North")],1,0.25)

N.link2link(L[(1,"West")],L[(2,"West")],1,0.65)
N.link2link(L[(1,"West")],L[(3,"North")],1,0.25)

N.link2link(L[(2,"West")],L[(3,"West")],1,0.65)
N.link2link(L[(2,"West")],L[(2,"South")],1,0.25)

N.link2link(L[(1,"South")],L[(2,"South")],1,0.65)
N.link2link(L[(1,"South")],L[(3,"West")],1,0.25)

N.link2link(L[(2,"South")],L[(3,"South")],1,0.65)
N.link2link(L[(2,"South")],L[(2,"East")],1,0.25)

N.antagonistic(L[(1,"North")],L[(2,"East")])
N.antagonistic(L[(2,"North")],L[(1,"West")])
N.antagonistic(L[(1,"East")],L[(2,"South")])
N.antagonistic(L[(2,"East")],L[(1,"North")])
N.antagonistic(L[(1,"West")],L[(2,"North")])
N.antagonistic(L[(2,"West")],L[(1,"South")])
N.antagonistic(L[(1,"South")],L[(2,"West")])
N.antagonistic(L[(2,"South")],L[(1,"East")])

N.update()

D={}
external_demand={}
X={}
Y={}

for l in N.links:
	D[l]=0
	external_demand[l]=0
# Position of the subnetwork in the whole network is important!
# Right now I have it located as NW

# Basis vector for initial and final states
# (want to differentiate initial and final? do it!)
X[L[1,"North"]]=1
X[L[1,"South"]]=1
X[L[1,"East"]]=1
X[L[1,"West"]]=1
X[L[2,"North"]]=1
X[L[2,"South"]]=1
X[L[2,"East"]]=1
X[L[2,"West"]]=1

# Basis vector for inputs from other networks
D[L[1,"North"]]=1
D[L[1,"South"]]=0
D[L[1,"East"]]=0
D[L[1,"West"]]=1

# External demands (from outside of the entire system)
external_demand[L[1,"North"]]=0
external_demand[L[1,"South"]]=5
external_demand[L[1,"East"]]=5
external_demand[L[1,"West"]]=0

# Basis vector for  outputs (100 stands for directions that I don't care)
Y[L[3,"North"]]=100
Y[L[3,"South"]]=1
Y[L[3,"East"]]=1
Y[L[3,"West"]]=100




# for l in N.links:
#	print l, "upstream:",l.up, "downstream:",l.down, "demand vector", D[l]
T=10
gamma=1000
beta_0=30
beta_f=30
state,control,output=N.mine(T,external_demand,X,Y,D,gamma,beta_0,beta_f)

# for l in N.links:
# 	print "\n",l
# 	for t in range(0,T+1):
# 		if l.type!="sink":
# 			print state[l,t],#control[l,t],
# 		if l.type=="sink":
# 			print "output:",output[l,t],"-",
		
		
# for l in N.links:
# 	if l!="sink":
			
