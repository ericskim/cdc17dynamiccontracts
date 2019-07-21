import pickle
# import networkx as nx

feas=pickle.load( open( "feasible_contracts.txt", "rb" ) )
bad=pickle.load( open( "bad_contracts.txt", "rb" ) )

print "# of bad contacts",len(bad)

print feas[1]


def maximal_invariant(list):
	flag={}
	successor={}
	for l in list:
		flag[l[1]]=0 # initialize successors
	for l in list:
		successor[l[0]]=[] # initial successors = zero
		flag[l[0]]=1 # is it in maximal invariant set? initially yes
	for l in list:
		successor[l[0]].append(l[1]) # list of available transitions
	counter=1
	while counter>0:
		counter=0
		for l in list:
			keep=0
			if flag[l[0]]==1:
				for s in successor[l[0]]:
					if flag[s]==1:
						keep=1
						break
				if keep==0:
					flag[l[0]]=0 # if no s has flag[s]=1, make flag[l[0]]=0 well!
					counter+=1
					
	inv=[]
	for l in list:
		if flag[l[0]]==1 and not l[0] in inv:
			inv.append(l[0])
	u={}
	for s1 in inv:
	    u[s1]=[]
	    for s2 in inv:
	        if (s1,s2) in list:
	            u[s1].append(s2) # Least restrictive controls
	return (inv,u)

# print maximal_invariant(feas[1])
	
""" demo:
	has to find maximal invariant set according to the transitions
"""
list=[(0,1),(1,2),(2,0),(1,3),(3,4),(0,5),(5,1)]
"""
	it should return 0,1,2,5 (notice there is no cycle starting from 5, but there is a lasso
"""
# print maximal_invariant(list)

for i in [1,2,3,4]:
	print "# of nodes in maxmimal invariant of network ",i," is",len(maximal_invariant(feas[i])[0])
	
"""
	construct a graph-based representation of the automata
	don't include any contract vector which includes bad contract
	here is everything restricted to 4 networks, REMEMBER THIS!
"""
c_start=0
c_finish=25 # REMEMBER TO CHANGE THIS
list_of_good_contract_vectors=[]
for c_1 in range(c_start,c_finish):
	for c_2 in range(c_start,c_finish):
		if not (1,c_1,2,c_2) in bad and not (2,c_2,1,c_1) in bad:
			for c_3 in range(c_start,c_finish): 
				if (not (1,c_1,3,c_3) in bad) and (not (3,c_3,1,c_1) in bad) and (not (2,c_2,3,c_3) in bad) and (not (3,c_3,2,c_2) in bad):
					for c_4 in range(c_start,c_finish):
						if (not (4,c_4,1,c_1) in bad) and (not (1,c_1,4,c_4) in bad)\
						    and (not (4,c_4,2,c_2) in bad) and (not (2,c_2,4,c_4) in bad)\
						     and (not (4,c_4,3,c_3) in bad) and (not (3,c_3,4,c_4) in bad):
							list_of_good_contract_vectors.append((c_1,c_2,c_3,c_4))
print len(list_of_good_contract_vectors)

transitions={}
# counter=0
# for a in list_of_good_contract_vectors:
#	for b in list_of_good_contract_vectors:
#		if ((a[0],b[0]) in feas[1]) and ((a[1],b[1]) in feas[2]) and ((a[2],b[2]) in feas[3]) and ((a[3],b[3]) in feas[4]):
#			print "hoorah!"
#			counter+=1
#			print counter
#			transitions.append((a,b))
step_track=1
counter=0

contract_dict={} # contract_dict[i,contract]=list of contracts that are feasible from
for i in [1,2,3,4]:
	for t in feas[i]:
		contract_dict[i,t[0]]=[]
	for t in feas[i]:
		contract_dict[i,t[0]].append(t[1])	  

C={}
for i in [1,2,3,4]:
	C[i]=[]
for i in [1,2,3,4]:
	for v in list_of_good_contract_vectors:
		C[i].append(v[i-1]) # does contract v for subnetwork i exist in list_of_good_contract_vectors? 
	print len(C[i])	 
print "hasth table completed"


for a in list_of_good_contract_vectors:
	print step_track,"/",len(list_of_good_contract_vectors)
	step_track+=1
	for t1 in contract_dict[1,a[0]]:
		if t1 in C[1]:
			for t2 in contract_dict[2,a[1]]:
				if t2 in C[2]:
					for t3 in contract_dict[3,a[2]]:
						if t3 in C[3]:
							for t4 in contract_dict[4,a[3]]:
								if t4 in C[4]:
									if (t1,t2,t3,t4) in list_of_good_contract_vectors:
# 										print "hoorah!",
										counter+=1
# 										print counter
										transitions[counter]=(a,(t1,t2,t3,t4))
										
# for a in list_of_good_contract_vectors:
#	print step_track,"/",len(list_of_good_contract_vectors)
#	step_track+=1
#	for t1 in feas[1]:
#		if t1[0]==a[0]:
#			for t2 in feas[2]:
#				if t2[0]==a[1]:
#					for t3 in feas[3]:
#						if t3[0]==a[2]:
#							for t4 in feas[4]:
#								if t4[0]==a[3]:
#									if (t1[1],t2[1],t3[1],t4[1]) in list_of_good_contract_vectors:
#										print "hoorah!",
#										counter+=1
#										print counter
#										transitions[counter]=(a,(t1[1],t2[1],t3[1],t4[1]))

run = False
if run:
	step_track=1
	counter=0
	for a in list_of_good_contract_vectors:
		print step_track,"/",len(list_of_good_contract_vectors)
		step_track+=1
		for t1 in feas[1]:
			if t1[0]==a[0]:
				for t2 in feas[2]:
					if t2[0]==a[1]:
						for t3 in feas[3]:
							if t3[0]==a[2]:
								for t4 in feas[4]:
									if t4[0]==a[3]:
										if (t1[1],t2[1],t3[1],t4[1]) in list_of_good_contract_vectors:
											print "hoorah!", (t1[1],t2[1],t3[1],t4[1]),
											counter+=1
											print counter
											transitions[counter]=(a,(t1[1],t2[1],t3[1],t4[1]))
					  

print len(transitions.values()) 
print "Going for invariance!"	
(inv,u)=maximal_invariant(transitions.values())	
print len(inv)
pickle.dump( (inv,u), open( "invaraint_automata.txt", "wb" ) )

# for s in inv:
#     print "\n",s, u[s]

# G=[]
# for s in inv:
#     for sprime in u[s]:
#         graph.append((s,sprime))
# G=nx.DiGraph(G)
# cycle=find_cycle(G, orientation='original')
# print list(cycle)

							
						 
						  
