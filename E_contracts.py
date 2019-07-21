from topology import *
from network_all import *

# Here we have the contracts

for l in N.links:
    print l,"up:", l.up, "down:", l.down

T=6
h=6

#N.partition(3,12)

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
    
    
    
for l in N.links:
    l.w=demand[(l,0)]


(state,control,output)=N.MILP_MTL_constraints(T,demand)


s=open("contracts_state.txt",'w')
c=open("contracts_control.txt",'w')
o=open("contracts_output.txt",'w')
for t in range(0,T):
    for i in [1,2]:
        for dir in ["East","West"]:
            for j in [1,2,3,4,5,6,7]:
                s.write(str(state[(L[i,dir,j],t)])+"\n")
                c.write(str(control[(L[i,dir,j],t)])+"\n")
                o.write(str(output[(L[i,dir,j],t)])+"\n")
    for i in [1,2,3]:
        for dir in ["North","South"]:
            for j in [1,2,3,4,5]:
                s.write(str(state[(L[(i,dir,j)],t)])+"\n")
                c.write(str(control[(L[(i,dir,j)],t)])+"\n")
                o.write(str(output[(L[(i,dir,j)],t)])+"\n")
    for dir in ["NW","SW","NE","SE"]:
        for j in [1,2,3]:
            s.write(str(state[(L[(dir,j)],t)])+"\n")
            c.write(str(control[(L[(dir,j)],t)])+"\n")
            o.write(str(output[(L[(dir,j)],t)])+"\n")

s.close()
c.close()
o.close()
                
                
    

# for i in [1,2]:
#     for dir in ["East","West"]:
#         for j in [1,2,3,4,5,6,7]:
#             for t in range(0,T+h):
#                 print "t: ",t, 
#                 print L[i,dir,j],state[(L[i,dir,j],t)],"control:",control[(L[i,dir,j],t)],
#             print "\n"
# for i in [1,2,3]:
#     for dir in ["North","South"]:
#         for j in [1,2,3,4,5]:
#             for t in range(0,T+h):
#                 print "t: ",t, 
#                 print L[i,dir,j],state[(L[i,dir,j],t)],"control:",control[(L[i,dir,j],t)],
#             print "\n"
# 
# 
for i in [1,2]:
    for dir in ["East","West"]:
        for j in [1,2,3,4,5,6,7]:
            l=L[i,dir,j]
            l.x=state[(L[i,dir,j],0)]
            l.u=control[(L[i,dir,j],0)]
for i in [1,2,3]:
    for dir in ["North","South"]:
        for j in [1,2,3,4,5]:
            l=L[i,dir,j]
            l.x=state[(L[i,dir,j],0)]
            l.u=control[(L[i,dir,j],0)]
for dir in ["NW","SW","NE","SE"]:
    for j in [1,2,3]:
        l=L[dir,j]
        l.x=state[(L[dir,j],0)]
        l.u=control[(L[dir,j],0)]
 
print "The problem is here"

f=open("states.txt",'w')
f.write("X=[")
for tau in range(0,100):
    t=tau%T
    for i in [1,2]:
        for dir in ["East","West"]:
            for j in [1,2,3,4,5,6,7]:
                l=L[i,dir,j]
                l.u=control[(L[i,dir,j],t)]
    for i in [1,2,3]:
        for dir in ["North","South"]:
            for j in [1,2,3,4,5]:
                l=L[i,dir,j]
                l.u=control[(L[i,dir,j],t)]
    for dir in ["NW","SW","NE","SE"]:
        for j in [1,2,3]:
            l=L[dir,j]
            l.u=control[(L[dir,j],t)]
    for i in [1,2]:
        for dir in ["East","West"]:
            for j in [1,2,3,4,5,6,7]:
                f.write(str(L[i,dir,j].x)+" ")
    for i in [1,2,3]:
        for dir in ["North","South"]:
            for j in [1,2,3,4,5]:
                f.write(str(L[i,dir,j].x)+" ")
    for dir in ["NW","SW","NE","SE"]:
        for j in [1,2,3]:
            f.write(str(L[dir,j].x)+" ")
    f.write("\n")
    N.evolve()
f.write("];")
f.close()


f=open("open_loop_controls.txt",'w')
for t in range(0,T):
    for i in [1,2]:
        for dir in ["East","West"]:
            for j in [1,2,3,4,5,6,7]:
                f.write(str(control[(L[i,dir,j],t)])+" ")
            f.write("1 ")
    for i in [1,2,3]:
        for dir in ["North","South"]:
            for j in [1,2,3,4,5]:
                f.write(str(control[(L[i,dir,j],t)])+" ")
            f.write("1 ")
    for dir in ["NW","SW","NE","SE"]:
        for j in [1,2,3]:
            f.write(str(control[(L[dir,j],t)])+" ")
        f.write("1 ")
    f.write("\n")
f.close()





# print "checking things"
# print L[(2,"South",4)].x, L[(2,"South",4)].u, L[(2,"South",4)].down, L[(2,"South",4)].up
# print L[(1,"North",4)].x, L[(1,"North",4)].u, L[(1,"North",4)].down, L[(1,"North",4)].up
# print state[(L[(2,"East",1)],0)],control[(L[(2,"East",1)],0)]
# print state[(L[(2,"South",3)],0)],control[(L[(2,"South",3)],0)]

# for i in [1,2]:
#     for dir in ["East","West","North","South"]:
#       print state[(L[(i,dir,5)],0)],state[(L[(i,dir,5)],1)]

