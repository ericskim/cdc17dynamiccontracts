from topology import *
from network_all import *

# Here we should consider output links

f=open("subnetwork_indices.txt","r")
for i in [1,2]:
	for dir in ["East","West"]:
		for j in [1,2,3,4,5,6,7]:
			l=L[(i,dir,j)]
			l.subnetwork=int(f.readline())
for i in [1,2,3]:
	for dir in ["North","South"]:
		for j in [1,2,3,4,5]:
			l=L[(i,dir,j)]
			l.subnetwork=int(f.readline())
for dir in ["NW","SW","NE","SE"]:
	for j in [1,2,3]:
		l=L[(dir,j)]
		l.subnetwork=int(f.readline())
f.close()

SubNetwork={}
for n in [1,2,3,4]:
	SubNetwork[n]=network()
 
Lsub={}	   
for key in L.keys():
	l=L[key]
	Lsub[(l.subnetwork,key)]=link(l.type,l.cap,l.qbar,"Sub"+str(l.subnetwork)+"-"+l.name)
	SubNetwork[l.subnetwork].links.append(Lsub[(l.subnetwork,key)])


for key in Lsub.keys():
	n=key[0]
	address=key[1]
	SubNetwork[n].link_address[address]=Lsub[(n,address)]

for key1,value1 in Lsub.items():
	key_l=key1[1]
	n_l=key1[0]
	l=value1
	for key2,value2 in Lsub.items():
		key_k=key2[1]
		n_k=key2[0]
		k=value2
		if n_l==n_k:
			if L[key_k] in L[key_l].down:
				SubNetwork[n_l].link2link(l,k,N.alphas[(L[key_l],L[key_k])],N.betas[(L[key_l],L[key_k])])
			if (L[key_l],L[key_k]) in N.antagonistics:
				SubNetwork[n_l].antagonistic(l,k)


output_subnetwork={}
for n in [1,2,3,4]:
	output_subnetwork[n]=[]

output_turn={}
upstream={}
for l in N.links:
	upstream[l]=[]

for key1,value1 in Lsub.items():
	key_l=key1[1]
	n_l=key1[0]
	l=value1
	if l.down==[]:
		for k in L[key_l].down:
			output_subnetwork[n_l].append(k)
			upstream[k].append(l)
			output_turn[(l,k)]=N.betas[(L[key_l],k)]   


	   
		
# for l in SubNetwork[4].links:
#	  print l,"down:",l.down,"up:",l.up



T=6
x_terminal={}
u_terminal={} 
y={}		  
f=open("contracts_state.txt","r")
g=open("contracts_control.txt","r")
h=open("contracts_output.txt","r")
for t in range(0,T):
	for i in [1,2]:
		for dir in ["East","West"]:
			for j in [1,2,3,4,5,6,7]:
				l=L[(i,dir,j)]
				y[(l,t)]=float(h.readline())
				n=l.subnetwork
				l=Lsub[(n,(i,dir,j))]
				x_terminal[(l,t)]=float(f.readline())
				u_terminal[(l,t)]=float(g.readline())
	for i in [1,2,3]:
		for dir in ["North","South"]:
			for j in [1,2,3,4,5]:
				l=L[(i,dir,j)]
				y[(l,t)]=float(h.readline())
				n=l.subnetwork
				l=Lsub[(n,(i,dir,j))]
				x_terminal[(l,t)]=float(f.readline())
				u_terminal[(l,t)]=float(g.readline())
	for dir in ["NW","SW","NE","SE"]:
		for j in [1,2,3]:
				l=L[(dir,j)]
				y[(l,t)]=float(h.readline())
				n=l.subnetwork
				l=Lsub[(n,(dir,j))]
				x_terminal[(l,t)]=float(f.readline())
				u_terminal[(l,t)]=float(g.readline())
f.close() 
g.close()
h.close() 

demand={}
demand_subs={}
for n in [1,2,3,4]:
	demand_subs[n]={}
	
	
demand={}
for t in range(0,T):
	for l in N.links:
		demand[(l,t)]=0
	for i in [1,2]:
		for dir in ["East","West"]:
			demand[(L[(i,dir,1)],t)]=6

	for i in [1,2,3]:
		for dir in ["North","South"]:
			demand[(L[(i,dir,1)],t)]=7
	for dir in ["NW","SW","NE","SE"]:
		demand[(L[(dir,1)],t)]=1			 


for t in range(0,T):
	for i in [1,2]:
		for dir in ["East","West"]:
			for j in [1,2,3,4,5,6,7]:
				l=L[(i,dir,j)]
				n=l.subnetwork
				l_sub=Lsub[(n,(i,dir,j))]
				demand_subs[n][l_sub,t]=demand[(l,t)]
				if l_sub.up==[]:
					demand_subs[n][l_sub,t]+=y[(l,t)]			
	for i in [1,2,3]:
		for dir in ["North","South"]:
			for j in [1,2,3,4,5]:
				l=L[(i,dir,j)]
				n=l.subnetwork
				l_sub=Lsub[(n,(i,dir,j))]
				demand_subs[n][l_sub,t]=demand[(l,t)]
				if l_sub.up==[]:
					demand_subs[n][l_sub,t]+=y[(l,t)] 
	for dir in ["NW","SW","NE","SE"]:
		for j in [1,2,3]:
			l=L[(dir,j)]
			n=l.subnetwork
			l_sub=Lsub[(n,(dir,j))]
			demand_subs[n][(l_sub,t)]=demand[(l,t)]
			if l_sub.up==[]:
				demand_subs[n][l_sub,t]+=y[(l,t)]								  
 
# for key,value in demand_subs[2].items():
#	  print key,value

r={}
rand=open("random_demand.txt","r")
T_end=100
for t in range(0,T_end):
	for i in [1,2]:
		for dir in ["East","West"]:
			for j in [1,2,3,4,5,6,7]:
				l=L[(i,dir,j)]
				r[(l,t)]=float(rand.readline())
	for i in [1,2,3]:
		for dir in ["North","South"]:
			for j in [1,2,3,4,5]:
				l=L[(i,dir,j)]
				r[(l,t)]=float(rand.readline())
	for dir in ["NW","SW","NE","SE"]:
		for j in [1,2,3]:
				l=L[(dir,j)]
				r[(l,t)]=float(rand.readline())
rand.close()  





H=11
h=6


x_history={}
u_history={}
for n in [1,2,3,4]:
	for t in range(-h+1,1):
		for l in SubNetwork[n].links:
			x_history[(l,t)]=0
	for t in range(-h+1,0):
		for l in SubNetwork[n].links:
			u_history[(l,t)]=1		  



total_run=0
max_run=0
natural_clock=0
clock_change=0

what_happened=[]

f=open("MPC_cooperative.txt","w")
def one_step_evolution(k):
	global total_run
	global max_run
	global natural_clock
	global clock_change
# 	global u_history
# 	global x_history
	c={}
	J={}
	run_all=0
	for clock in [1,2,5,3,4,0]:
		for n in [1,2,3,4]:
			(runtime,states,controls,JJ)=SubNetwork[n].MPC_MTL_Subnetwork_infeasible(H,T,clock,demand_subs[n],x_terminal,u_terminal,y,output_subnetwork[n],output_turn,upstream,x_history,u_history)		
			J[(clock,n)]=JJ
			c[clock,n]=controls
			total_run+=runtime
			run_all+=runtime
	max_run=max(max_run,run_all)
	cost=1000000
	for clock in range(0,T):
		J["all",clock]=J[clock,1]+J[clock,2]+J[clock,3]+J[clock,4]
		if J["all",clock]<cost:
			consensus=clock
			cost=J["all",consensus]
	if k==0:
		natural_clock=consensus
	if not(consensus==natural_clock):
		clock_change+=1
		natural_clock=consensus
	natural_clock=(natural_clock+1)%T
	what_happened.append(consensus)
	for key_sub,value_sub in Lsub.items():
		n_sub=key_sub[0]
		address_sub=key_sub[1]
		appropriate_c=c[consensus,n_sub]
		L[address_sub].u=appropriate_c[(Lsub[key_sub],0)]
#		  print L[address_sub],L[address_sub].u
		L[address_sub].w=demand[(L[address_sub],clock)]*r[(L[address_sub],k)]**(1-(L[address_sub].subnetwork==1))
	N.evolve()
	for l in N.links:
		f.write(str(l.x)+" ")
	for key_sub,value_sub in Lsub.items():
		n_sub=key_sub[0]
		address_sub=key_sub[1]
		for t in range(-h+1,0):
			x_history[(Lsub[key_sub],t)]=x_history[(Lsub[key_sub],t+1)]
		for t in range(-h+1,-1):
			u_history[(Lsub[key_sub],t)]=u_history[(Lsub[key_sub],t+1)]
		u_history[(Lsub[key_sub],-1)]=L[address_sub].u
		x_history[(Lsub[key_sub],0)]=L[address_sub].x
	f.write("\n")
	

k=0

for i in range(0,45):
	one_step_evolution(k) 
	print "\n \n \n step is:",k,"\n \n \n"
	k=k+1
f.close()		


for  t in what_happened:
    print "clock was", t
print "Maximum Runtime is ", max_run
print "Average Runtime is",total_run/180
print "Total delay is", N.delay
print "total shifts in clock is", clock_change
	
