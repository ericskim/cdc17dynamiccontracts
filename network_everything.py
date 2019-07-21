from topology import *
import contract_propagation as cp

# Here we should consider output links
L={} # the dict of all links (entire network_wide)
N={} # the dict of networks (we have N[1],N[2],N[3],N[4] and N[4] is a freeway)

# for network_index in [1,2,3]:
#   N[network_index]=network()
#   N[network_index].links=L.values()
		
	
for network_index in [1,2,3]: 
	for dir in ["East","West","North","South"]:
		for i in [1,2]:
			L[network_index,i,dir]=link("road",40,15,"network %d road %s %d" %(network_index,dir,i))
		L[network_index,3,dir]=link("sink",1000,15,"network %d road %s %d" %(network_index,dir,3))

# Now the freeway
for i in [1,2,3]:
	L[4,i,"East"]=link("freeway",60,25,"freeway East %d" %(i))
L[4,4,"East"]=link("freeway",60,25,"freeway East %d" %(4))
for j in [1,2,3,4]:
	L[4,j,"West"]=link("freeway",60,25,"freeway West %d" %(j))
L[4,5,"West"]=link("freeway",60,25,"freeway West %d" %(5))
# Off-Ramps:
for i in [1,3,5]:
	L[4,i,"West Ramp"]=link("sink",60,25,"off-ramp West %d" %(i))
	L[4,i+1,"East Ramp"]=link("sink",60,25,"off-ramp East %d" %(i+1))
# On-Ramps:
for i in [2,4,6]:
	L[4,i,"West Ramp"]=link("on-ramp",30,15,"on-ramp West %d" %(i))
for i in [1,3,5]:
	L[4,i,"East Ramp"]=link("on-ramp",30,15,"on-ramp East %d" %(i))

for network_index in [1,2,3,4]:
	N[network_index]=network()
	for key in L.keys():
		if key[0]==network_index:
			N[network_index].links.append(L[key])
			

for i in [1,2,3]:
	
	N[i].link2link(L[(i,1,"North")],L[(i,2,"North")],1,0.50)
	N[i].link2link(L[(i,1,"North")],L[(i,3,"East")],1,0.20)

	N[i].link2link(L[(i,2,"North")],L[(i,3,"North")],1,0.50)
	N[i].link2link(L[(i,2,"North")],L[(i,2,"West")],1,0.20)

	N[i].link2link(L[(i,1,"East")],L[(i,2,"East")],1,0.50)
	N[i].link2link(L[(i,1,"East")],L[(i,3,"South")],1,0.20)

	N[i].link2link(L[(i,2,"East")],L[(i,3,"East")],1,0.50)
	N[i].link2link(L[(i,2,"East")],L[(i,2,"North")],1,0.20)

	N[i].link2link(L[(i,1,"West")],L[(i,2,"West")],1,0.50)
	N[i].link2link(L[(i,1,"West")],L[(i,3,"North")],1,0.20)

	N[i].link2link(L[(i,2,"West")],L[(i,3,"West")],1,0.50)
	N[i].link2link(L[(i,2,"West")],L[(i,2,"South")],1,0.20)

	N[i].link2link(L[(i,1,"South")],L[(i,2,"South")],1,0.50)
	N[i].link2link(L[(i,1,"South")],L[(i,3,"West")],1,0.20)

	N[i].link2link(L[(i,2,"South")],L[(i,3,"South")],1,0.50)
	N[i].link2link(L[(i,2,"South")],L[(i,2,"East")],1,0.20)

	N[i].antagonistic(L[(i,1,"North")],L[(i,2,"East")])
	N[i].antagonistic(L[(i,2,"North")],L[(i,1,"West")])
	N[i].antagonistic(L[(i,1,"East")],L[(i,2,"South")])
	N[i].antagonistic(L[(i,2,"East")],L[(i,1,"North")])
	N[i].antagonistic(L[(i,1,"West")],L[(i,2,"North")])
	N[i].antagonistic(L[(i,2,"West")],L[(i,1,"South")])
	N[i].antagonistic(L[(i,1,"South")],L[(i,2,"West")])
	N[i].antagonistic(L[(i,2,"South")],L[(i,1,"East")])

for i in [1,2,3]:
	N[4].link2link(L[(4,i,"East")],L[(4,i+1,"East")],1,0.7)
for j in [1,2,3,4]:
	N[4].link2link(L[(4,j,"West")],L[(4,j+1,"West")],1,0.7)

# East Off ramps
N[4].link2link(L[(4,1,"East")],L[(4,2,"East Ramp")],1,0.1)
N[4].link2link(L[(4,2,"East")],L[(4,4,"East Ramp")],1,0.1)
N[4].link2link(L[(4,3,"East")],L[(4,6,"East Ramp")],1,0.1)
# East On ramps
N[4].link2link(L[(4,1,"East Ramp")],L[(4,2,"East")],1,1)
N[4].link2link(L[(4,3,"East Ramp")],L[(4,3,"East")],1,1)
N[4].link2link(L[(4,5,"East Ramp")],L[(4,4,"East")],1,1)
# West Off ramps
N[4].link2link(L[(4,1,"West")],L[(4,1,"West Ramp")],1,0.1)
N[4].link2link(L[(4,2,"West")],L[(4,3,"West Ramp")],1,0.1)
N[4].link2link(L[(4,3,"West")],L[(4,5,"West Ramp")],1,0.1)
# West On ramps
N[4].link2link(L[(4,2,"West Ramp")],L[(4,3,"West")],1,1)
N[4].link2link(L[(4,4,"West Ramp")],L[(4,4,"West")],1,1)
N[4].link2link(L[(4,6,"West Ramp")],L[(4,5,"West")],1,1)


for network_index in [1,2,3,4]:
	N[network_index].update()

# for l in L.values():
# 	print l, "down:",l.down, "up:",l.up
	
def propogate_demand(D_downstream,Y_upstream,T):
	upstream_index=Y_upstream.keys()[0][0] # link index
	downstream_index=D_downstream.keys()[0][0] #
	for t in range(0,T):
		if upstream_index==1 and downstream_index==2:
			D_downstream[L[2,1,"East"],t]+=Y_upstream[L[1,3,"East"],t]
		if upstream_index==2 and downstream_index==1:
			D_downstream[L[1,1,"West"],t]+=Y_upstream[L[2,3,"West"],t]
		if upstream_index==2 and downstream_index==3:
			D_downstream[L[3,1,"East"],t]+=Y_upstream[L[2,3,"East"],t]
		if upstream_index==3 and downstream_index==2:
			D_downstream[L[2,1,"West"],t]+=Y_upstream[L[3,3,"West"],t]

		# Ramps
		
		if downstream_index==1 and upstream_index==4:
			D_downstream[L[1,3,"North"],t]+=Y_upstream[L[4,2,"East Ramp"],t]
			D_downstream[L[1,3,"North"],t]+=Y_upstream[L[4,5,"West Ramp"],t]            
		if downstream_index==4 and upstream_index==1:
			D_downstream[L[4,6,"West Ramp"],t]+=Y_upstream[L[1,3,"South"],t]
			D_downstream[L[4,1,"East Ramp"],t]+=Y_upstream[L[1,3,"South"],t]

		if downstream_index==2 and upstream_index==4:
			D_downstream[L[2,3,"North"],t]+=Y_upstream[L[4,4,"East Ramp"],t]
			D_downstream[L[2,3,"North"],t]+=Y_upstream[L[4,3,"West Ramp"],t]
		if downstream_index==4 and upstream_index==2:
			D_downstream[L[4,4,"West Ramp"],t]+=Y_upstream[L[2,3,"South"],t]
			D_downstream[L[4,3,"East Ramp"],t]+=Y_upstream[L[2,3,"South"],t]
				
		if downstream_index==3 and upstream_index==4:
			D_downstream[L[3,3,"North"],t]+=Y_upstream[L[4,6,"East Ramp"],t]
			D_downstream[L[3,3,"North"],t]+=Y_upstream[L[4,1,"West Ramp"],t]
		if downstream_index==4 and upstream_index==3:
			D_downstream[L[4,2,"West Ramp"],t]+=Y_upstream[L[3,3,"South"],t]
			D_downstream[L[4,5,"East Ramp"],t]+=Y_upstream[L[3,3,"South"],t]
	return D_downstream


# N_whole=network()
# N_whole.links=L.values()
# 
# for i in [1,2,3]:
# 	
# 	N_whole.link2link(L[(i,1,"North")],L[(i,2,"North")],1,0.50)
# 	N_whole.link2link(L[(i,1,"North")],L[(i,3,"East")],1,0.20)
# 
# 	N_whole.link2link(L[(i,2,"North")],L[(i,3,"North")],1,0.50)
# 	N_whole.link2link(L[(i,2,"North")],L[(i,2,"West")],1,0.20)
# 
# 	N_whole.link2link(L[(i,1,"East")],L[(i,2,"East")],1,0.50)
# 	N_whole.link2link(L[(i,1,"East")],L[(i,3,"South")],1,0.20)
# 
# 	N_whole.link2link(L[(i,2,"East")],L[(i,3,"East")],1,0.50)
# 	N_whole.link2link(L[(i,2,"East")],L[(i,2,"North")],1,0.20)
# 
# 	N_whole.link2link(L[(i,1,"West")],L[(i,2,"West")],1,0.50)
# 	N_whole.link2link(L[(i,1,"West")],L[(i,3,"North")],1,0.20)
# 
# 	N_whole.link2link(L[(i,2,"West")],L[(i,3,"West")],1,0.50)
# 	N_whole.link2link(L[(i,2,"West")],L[(i,2,"South")],1,0.20)
# 
# 	N_whole_whole.link2link(L[(i,1,"South")],L[(i,2,"South")],1,0.50)
# 	N_whole.link2link(L[(i,1,"South")],L[(i,3,"West")],1,0.20)
# 
# 	N_whole.link2link(L[(i,2,"South")],L[(i,3,"South")],1,0.50)
# 	N_whole.link2link(L[(i,2,"South")],L[(i,2,"East")],1,0.20)
# 
# 	N_whole.antagonistic(L[(i,1,"North")],L[(i,2,"East")])
# 	N_whole.antagonistic(L[(i,2,"North")],L[(i,1,"West")])
# 	N_whole.antagonistic(L[(i,1,"East")],L[(i,2,"South")])
# 	N_whole.antagonistic(L[(i,2,"East")],L[(i,1,"North")])
# 	N_whole.antagonistic(L[(i,1,"West")],L[(i,2,"North")])
# 	N_whole.antagonistic(L[(i,2,"West")],L[(i,1,"South")])
# 	N_whole.antagonistic(L[(i,1,"South")],L[(i,2,"West")])
# 	N_whole.antagonistic(L[(i,2,"South")],L[(i,1,"East")])
# 
# for i in [1,2,3]:
# 	N_whole.link2link(L[(4,i,"East")],L[(4,i+1,"East")],1,0.7)
# for j in [1,2,3,4]:
# 	N_whole.link2link(L[(4,j,"West")],L[(4,j+1,"West")],1,0.7)
# 
# # East Off ramps
# N_whole.link2link(L[(4,1,"East")],L[(4,2,"East Ramp")],1,0.1)
# N_whole.link2link(L[(4,2,"East")],L[(4,4,"East Ramp")],1,0.1)
# N_whole.link2link(L[(4,3,"East")],L[(4,6,"East Ramp")],1,0.1)
# # East On ramps
# N_whole.link2link(L[(4,1,"East Ramp")],L[(4,2,"East")],1,1)
# N_whole.link2link(L[(4,3,"East Ramp")],L[(4,3,"East")],1,1)
# N_whole.link2link(L[(4,5,"East Ramp")],L[(4,4,"East")],1,1)
# # West Off ramps
# N_whole.link2link(L[(4,1,"West")],L[(4,1,"West Ramp")],1,0.1)
# N_whole.link2link(L[(4,2,"West")],L[(4,3,"West Ramp")],1,0.1)
# N_whole.link2link(L[(4,3,"West")],L[(4,5,"West Ramp")],1,0.1)
# # West On ramps
# N_whole.link2link(L[(4,2,"West Ramp")],L[(4,3,"West")],1,1)
# N_whole.link2link(L[(4,4,"West Ramp")],L[(4,4,"West")],1,1)
# N_whole.link2link(L[(4,6,"West Ramp")],L[(4,5,"West")],1,1)
# 
# 
# N_whole.link2link(L[1,3,"East"],L[2,1,"East"],1,1)
# N_whole.link2link(L[2,3,"West"],L[1,1,"West"],1,1)
# N_whole.link2link(L[2,3,"East"],L[2,1,"East"],1,1)
# N_whole.link2link(L[1,3,"East"],L[2,1,"East"],1,1)
# N_whole.link2link(L[1,3,"East"],L[2,1,"East"],1,1)


			
			
# b=0.0
# for network_index in [1,2,3]: 
# 	for i in [1,2,3]:
# 		L[network_index,i,"North"].tail=((network_index-1)*2+2,i-2+b)
# 		L[network_index,i,"North"].head=((network_index-1)*2+2,i-1-b)
# 		L[network_index,i,"South"].tail=((network_index-1)*2+3,3-i-b)
# 		L[network_index,i,"South"].head=((network_index-1)*2+3,2-i+b) 
# 		L[network_index,i,"East"].tail=((network_index-1)*2+i+b,0)
# 		L[network_index,i,"East"].head=((network_index-1)*2+i+1-b,0)
# 		L[network_index,i,"West"].tail=((network_index-1)*2+i+1-b,1)
# 		L[network_index,i,"West"].head=((network_index-1)*2+i+b,1)

# N = dict([ (k-1, v) for (k,v) in N.iteritems()])




################################################################################################################################################

# for i in [1,2,3,4,5]:
#   L[4,i,"West"].tail=(9.5-(i-1)*2-b,-1.2)
#   L[4,i,"West"].head=(7.5-(i-1)*2+b,-1.2)
# for i in [1,2,3,4]:
#   L[4,i,"East"].tail=(1.5+(i-1)*2+b,-1.4)
#   L[4,i,"East"].head=(3.5+(i-1)*2-b,-1.4)        
# N[0]=network()
# N[0].links=N[1].links+N[2].links+N[3].links+N[4].links
# N[0].draw()
# D={}
# external_demand={}
# X={}
# Y={}
# 
# for l in N[network_index].links:
#   D[l]=0
#   external_demand[l]=0
# # Position of the subnetwork in the whole network is important!
# # Right now I have it located as NW
# 
# # Basis vector for initial and final states
# # (want to differentiate initial and final? do it!)
# X[L[1,"North"]]=1
# X[L[1,"South"]]=1
# X[L[1,"East"]]=1
# X[L[1,"West"]]=1
# X[L[2,"North"]]=1
# X[L[2,"South"]]=1
# X[L[2,"East"]]=1
# X[L[2,"West"]]=1
# 
# # Basis vector for inputs from other networks
# D[L[1,"North"]]=1
# D[L[1,"South"]]=0
# D[L[1,"East"]]=0
# D[L[1,"West"]]=1
# 
# # External demands (from outside of the entire system)
# external_demand[L[1,"North"]]=0
# external_demand[L[1,"South"]]=5
# external_demand[L[1,"East"]]=5
# external_demand[L[1,"West"]]=0
# 
# # Basis vector for  outputs (100 stands for directions that I don't care)
# Y[L[3,"North"]]=100
# Y[L[3,"South"]]=1
# Y[L[3,"East"]]=1
# Y[L[3,"West"]]=100
# 
# 
# 
# 
# # for l in N[network_index].links:
# # print l, "upstream:",l.up, "downstream:",l.down, "demand vector", D[l]
# T=10
# gamma=10
# beta_0=30
# beta_f=30
# state,control,output=N[network_index].mine(T,external_demand,X,Y,D,gamma,beta_0,beta_f)
# 
# # for l in N[network_index].links:
# #     print "\n",l
# #     for t in range(0,T+1):
# #         if l.type!="sink":
# #             print state[l,t],#control[l,t],
# #         if l.type=="sink":
# #             print "output:",output[l,t],"-",
#       
#       
# for l in N[network_index].links:
#   if l!="sink":
			
