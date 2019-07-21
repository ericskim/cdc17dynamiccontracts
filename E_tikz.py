from topology import *
from network_all import *


# HERE WE PARTITION

# print len(N.links)
# N.partition(4,20)

# for l in N.links:
#     print l,":",l.subnetwork

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



for i in [1,2]:
    for dir in ["East","West"]:
        L[(i,dir,8)]=link("sink",40,15,"road %d %s %d" %(i,dir,8))
        L[(i,dir,8)].lane="double"
        N.links.append(L[(i,dir,8)])
        
for i in [1,2,3]:
    for dir in ["North","South"]:
        L[(i,dir,6)]=link("sink",40,15,"road %d %s %d" %(i,dir,6))
        L[(i,dir,6)].lane="double"
        N.links.append(L[(i,dir,6)])
            
for dir in ["NW","SW","NE","SE"]:
    L[(dir,4)]=link("sink",40,15,"side road %s %d" %(dir,4))
    L[(dir,4)].lane="double"
    N.links.append(L[(dir,4)])
    
    

for j in [1,2,3,4,5,6,7,8]:
    L[(1,"East",j)].tail=(j-1,1)
    L[(1,"East",j)].head=(j,1)
    L[(2,"East",j)].tail=(j-1,4)
    L[(2,"East",j)].head=(j,4)  
    L[(1,"West",j)].tail=(9-j,2)
    L[(1,"West",j)].head=(8-j,2)
    L[(2,"West",j)].tail=(9-j,5)
    L[(2,"West",j)].head=(8-j,5)

b=0.05
for i in [1,2,3]:
        for j in [1,2,3,4,5,6]:
            L[(i,"North",j)].tail=(3*i-2+b,j-1)
            L[(i,"North",j)].head=(3*i-2+b,j)
            L[(i,"South",j)].tail=(3*i-2-b,7-j)
            L[(i,"South",j)].head=(3*i-2-b,6-j)

L[("SW",1)].tail=(3,0)
L[("SW",2)].tail=(3,1)
L[("SW",3)].tail=(2,2)
L[("SW",4)].tail=(2,1)
L[("SW",1)].head=(3,1)
L[("SW",2)].head=(3,2)
L[("SW",3)].head=(2,1)
L[("SW",4)].head=(2,0)

L[("SE",1)].tail=(6,0)
L[("SE",2)].tail=(6,1)
L[("SE",3)].tail=(5,2)
L[("SE",4)].tail=(5,1)
L[("SE",1)].head=(6,1)
L[("SE",2)].head=(6,2)
L[("SE",3)].head=(5,1)
L[("SE",4)].head=(5,0)

L[("NW",1)].tail=(2,6)
L[("NW",2)].tail=(2,5)
L[("NW",3)].tail=(3,4)
L[("NW",4)].tail=(3,5)
L[("NW",1)].head=(2,5)
L[("NW",2)].head=(2,4)
L[("NW",3)].head=(3,5)
L[("NW",4)].head=(3,6)

L[("NE",1)].tail=(5,6)
L[("NE",2)].tail=(5,5)
L[("NE",3)].tail=(6,4)
L[("NE",4)].tail=(6,5)
L[("NE",1)].head=(5,5)
L[("NE",2)].head=(5,4)
L[("NE",3)].head=(6,5)
L[("NE",4)].head=(6,6)
   
N.draw_subnetworks()