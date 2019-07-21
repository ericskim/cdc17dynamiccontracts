from topology import *
from network_everything import *
import pickle
from gurobipy import *

T=6 

for link_address, link_object in L.items():
    link_object.subnetwork=link_address[0]
    
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
# Changing it to a dic for easier use
upstream={} # dic: key: link, val: upstream links from other networks
for connection in connections:
    if not connection[1] in upstream.keys():
        upstream[connection[1]]=[connection[0]] # make a list
    else:
        upstream[connection[1]].append(connection[0])
AG=pickle.load( open( "contracts_hashtable.txt", "rb" ) )
(inv,u)=pickle.load( open( "invaraint_automata.txt", "rb" ) )
# associating costs to each contract vector    
cycle=[(17, 16, 13, 13), (23, 17, 12, 12)]
#initialization, even though done before
for link_address, link_object in L.items():
    link_object.x=0
    link_object.w=0
    link_object.u=0         
for c in cycle:
    print c in inv

                 
f=open("trajectory.txt","w")
g=open("traffic lights.txt","w")


U_history={}
def evolve_MPC(contract_vector,clock):
    print "**** clock is ",clock,"!"
    X_contract={}
    D_contract={}
    Output_contract={}
    for l in L.values():
        for t in range(0,T+1):
            D_contract[l,t]=0 # initialize demands
            if l.up==[] and (not l in upstream.keys()): # link has an external demand
                D_contract[l,t]=.25*l.qbar 
    # Now demand and others
    for link_address, link_object in L.items():
        network_index=link_address[0]
        if link_object.type!="sink":
            for t in range(0,T+1):
                X_contract[link_object,t]=AG[network_index,contract_vector[network_index-1]][5][link_address,t]
            for t in range(0,T):
                if link_object in upstream.keys():
                    D_contract[link_object,t]+=AG[network_index,contract_vector[network_index-1]][2][link_address,t]
        if link_object.type=="sink":
            for t in range(0,T):
                Output_contract[link_object,t]=AG[network_index,contract_vector[network_index-1]][3][link_address,t]
    # solve MPCs now!
    for i in [1,2,3,4]:
        print "solving MPC for network ", i
        N[i].MPC_Contract(T,clock,U_history,X_contract,D_contract,Output_contract)
    # Ready to evolve the network, without adding any demand
    for i in [1,2,3,4]:
        N[i].evolve_decentralized() # evolve without adding external (including intersections) demands
    # Compute demands (from time t)
    for l in L.values():
        l.w=0 # initialization, again!
    for l in upstream.keys():
        for k in upstream[l]:
            l.w+=k.output*(l.type!="sink")
    for l in L.values():
        if l.up==[] and (not l in upstream.keys()): # link has an external demand
            l.w=.25*l.qbar#*1*((l.subnetwork==4)+(l.subnetwork==5)+(l.subnetwork==5))
    for l in L.values():
        l.x+=l.w
        if l.type!="sink":
            U_history[l,clock]=l.u      

fixed_clock=0                 
def evolve_MPC_T():
    global fixed_clock 
    contract_vector=cycle[fixed_clock]
    print contract_vector
    fixed_clock+=1
    fixed_clock=fixed_clock%len(cycle)
    print "fixed_clock is",fixed_clock
    for t in range(0,T):
        evolve_MPC(contract_vector,t)
        for l in L.values():
            if l.type!="sink":
                f.write("%0.2f %0.2f "%(l.x,l.u))
        for i in [1,2,3]:
            g.write("%d %d "%(L[(i,1,"North")].u,L[(i,2,"East")].u))
            g.write("%d %d "%(L[(i,2,"North")].u,L[(i,1,"West")].u))
            g.write("%d %d "%(L[(i,1,"East")].u,L[(i,2,"South")].u))
            g.write("%d %d "%(L[(i,2,"East")].u,L[(i,1,"North")].u))
        f.write("\n")
        g.write("\n")


#initialization, even though done before
for link_address, link_object in L.items():
    link_object.x=0
    link_object.w=0
    link_object.u=0
    
for i in range(0,5):
    print "round is",i
    evolve_MPC_T()
# f.write("];\n")
f.close() 
g.close() 
Total_Delay=0
for i in [1,2,3,4]:
    Total_Delay+=N[i].delay
print "Total delay with fixed cycle", Total_Delay   



