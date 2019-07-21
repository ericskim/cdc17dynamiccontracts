from topology import *
import contract_propagation as cp
from network_everything import *
import pickle

def get_net_from_link(l):
	if 'off-ramp' in l.name.split():
		return 4
	if 'on-ramp' in l.name.split():
		return 4
	else:
		return int(l.name.split()[1])

# (sending from network link, receiving to network link)
connections = [ 
(L[2,1,"East"], L[1,3,"East"]), 
(L[1,1,"West"], L[2,3,"West"]),
(L[3,1,"East"], L[2,3,"East"]),
(L[2,1,"West"], L[3,3,"West"]),
(L[1,1,"North"], L[4,2,"East Ramp"]),
(L[1,1,"North"], L[4,5,"West Ramp"]),
(L[4,6,"West Ramp"], L[1,3,"South"]),
(L[4,1,"East Ramp"], L[1,3,"South"]),
(L[2,1,"North"], L[4,4,"East Ramp"]),
(L[2,1,"North"], L[4,3,"West Ramp"]),
(L[4,4,"West Ramp"], L[2,3,"South"]),
(L[4,3,"East Ramp"], L[2,3,"South"]),
(L[3,1,"North"], L[4,6,"East Ramp"]),
(L[3,1,"North"], L[4,1,"West Ramp"]),
(L[4,2,"West Ramp"], L[3,3,"South"]),
(L[4,5,"East Ramp"], L[3,3,"South"]),
]
connections = [(k[1], k[0]) for k in connections] # swapping left and right elements b/c declaration above switched

# Dict of network pairs
# key: (from net, to net)
# value: set or list of link pairs (from link, to link)
grouped_connections = dict([ ((i,j), []) for i in range(1,5) for j in range(1,5)])
for c in connections:
	pair = (get_net_from_link(c[0]), get_net_from_link(c[1]))
	grouped_connections[pair].append(c)


miner_ready = True
if miner_ready: 
	miner = cp.network_guarantee_miner(N, propogate_demand, connections, grouped_connections, iter_depth = 25, start_net = 1, T = 6)
	# miner = cp.network_guarantee_miner(N, propogate_demand, connections, grouped_connections, iter_depth = 40, start_net = 1)
	miner.mine()
#	miner.start_net = 2
#	miner.mine()
#	miner.start_net = 3
#	miner.mine()
#	miner.start_net = 4
#	miner.mine()

	feas = miner.recurrent_feasibility()
	badcontracts = miner.contract_consistency()
	for i in [1,2,3,4]:
		print "network",i," had ",len(feas[i]), "recursively feasible switches"
	pickle.dump( feas, open( "feasible_contracts.txt", "wb" ) )
	print len(badcontracts)
	pickle.dump( badcontracts, open( "bad_contracts.txt", "wb" ) )
	
		
print miner.consistency_failures
print miner.recfeas_failures


AG_index_cost={} # dict: key: (network_index, contract_index), val: cost		
for i in [1,2,3,4]:
	index=0
	for c in miner.AGpairs[i]:
		AG_index_cost[i,index]=c[4]
		index+=1
			  
# print AG_index_cost
pickle.dump( AG_index_cost, open( "contracts_costs.txt", "wb" ) )


AG={} 
"""
	dict: key(network_index, contract_index)
	val: tuple of Dictionaries: X: initial state, D: demands (inputs), Y: outputs, c: cost
	In order to dump, the key in each dictionary is NOT the link object ...
	... but the link key address (which is a tuple of numbers and strings)
	We will recover them in a separate file
"""
# print miner.T

for i in [1,2,3,4]:
	index=0
	#c=(X, D, state, output, cost, control)
	#   0  1    2      3       4      5
	for c in miner.AGpairs[i]:
		X_initial={}
		for key, val in c[0].items():
			for link_address,link_object in L.items():
				if key==link_object:
					X_initial[link_address]=val
		Demands={}
		for key, val in c[1].items(): #key[0]=link, key[1]=t
			for link_address,link_object in L.items():
				if key[0]==link_object:
					Demands[link_address,key[1]]=val
		state={}
		for key, val in c[2].items(): #key[0]=link, key[1]=t
			for link_address,link_object in L.items():
				if key[0]==link_object:
					state[link_address,key[1]]=val
		Controls={}
		for key, val in c[5].items(): #key[0]=link, key[1]=t
			for link_address,link_object in L.items():
				if key[0]==link_object:
					Controls[link_address,key[1]]=val		
		Outputs={}
		for key, val in c[3].items(): #key[0]=link, key[1]=t
			for link_address,link_object in L.items():
				if key[0]==link_object:
					Outputs[link_address,key[1]]=val
		cost=c[4]
		AG[i,index]=(X_initial,Controls,Demands,Outputs,cost,state)
		index+=1

# for key,val in AG.items():
#	  print key,val
pickle.dump( AG, open( "contracts_hashtable.txt", "wb" ) )

