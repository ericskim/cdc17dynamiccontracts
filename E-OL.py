from topology import *
from network_all import *

# HERE I WANT EVERYTHING OPEN-LOOP


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



T=6
x_terminal={}
u_terminal={} 
y={}    

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
                x_terminal[(l,t)]=float(f.readline())
                u_terminal[(l,t)]=float(g.readline())
    for i in [1,2,3]:
        for dir in ["North","South"]:
            for j in [1,2,3,4,5]:
                l=L[(i,dir,j)]
                y[(l,t)]=float(h.readline())
                x_terminal[(l,t)]=float(f.readline())
                u_terminal[(l,t)]=float(g.readline())
    for dir in ["NW","SW","NE","SE"]:
        for j in [1,2,3]:
                l=L[(dir,j)]
                y[(l,t)]=float(h.readline())
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




H=9
h=6

x_history={}
u_history={}
for t in range(-h+1,1):
    for l in N.links:
        x_history[(l,t)]=0
for t in range(-h+1,0):
    for l in N.links:
        u_history[(l,t)]=1
        



f=open("open-loop.txt","w")
def one_step_evolution(clock,k):
    for l in N.links:
        l.u=u_terminal[(l,clock)]
        l.w=demand[(l,clock)]*r[(l,k)]**(1-(l.subnetwork==1))
    N.evolve()
    for l in N.links:
        f.write(str(l.x)+" ")
    f.write("\n")

            
k=0
clock=0
for t in range(0,45):
    one_step_evolution(clock,k)
    clock=(clock+1)%T
    k=k+1        


f.close()


print "total delay was:",N.delay
    
             
# print s
# print c
    
    
