from topology import *

L={}

for i in [1,2]:
    for dir in ["East","West"]:
        for j in [1,2,3,4,5,6,7]:
            L[(i,dir,j)]=link("road",40,15,"road %d %s %d" %(i,dir,j))
#         L[(i,dir,8)]=link("sink",40,15,"road %d %s %d" %(i,dir,8))
#         L[(i,dir,8)].lane="double"
        
for i in [1,2,3]:
    for dir in ["North","South"]:
        for j in [1,2,3,4,5]:
            L[(i,dir,j)]=link("road",40,15,"boulevard %d %s %d" %(i,dir,j))
            L[(i,dir,j)].lane="double"
#         L[(i,dir,6)]=link("sink",40,15,"road %d %s %d" %(i,dir,6))
#         L[(i,dir,6)].lane="double"
            
for dir in ["NW","SW","NE","SE"]:
    for j in [1,2,3]:
        L[(dir,j)]=link("road",40,15,"side road %s %d" %(dir,j))
#     L[(dir,4)]=link("sink",40,15,"side road %s %d" %(dir,4))
#     L[(dir,4)].lane="double"

for dir in ["North","South"]:
    for i in [1,2,3]:
        L[(i,dir,3)].type="freeway"
    
N=network()
N.links=L.values()
for key in L.keys():
    N.link_address[key]=L[key]

for i in [1,2]:
    for dir in ["East","West"]:
        for j in [1,2,3,4,5,6]:
            if j in [2,3,5,6]:
                N.link2link(L[(i,dir,j)],L[(i,dir,j+1)],1,0.8)
            if j in [1,4]:
                N.link2link(L[(i,dir,j)],L[(i,dir,j+1)],1,0.4)

for i in [1,2,3]:
    for dir in ["North","South"]:
        for j in [1,2,3,4]:
            N.link2link(L[(i,dir,j)],L[(i,dir,j+1)],1,0.8) 


for i in [1,2]:
    for j in [1,2,3]:
        N.link2link(L[(i,"East",3*j-2)],L[(j,"North",3*i-1)],1,0.3)
        N.antagonistic(L[(i,"East",3*j-2)],L[(j,"North",3*i-2)])
        if 3*j-1<8:
            N.link2link(L[(j,"North",3*i-2)],L[(i,"East",3*j-1)],0.5,0.2)

for i in [1,2]:
    for j in [1,2,3]:
        if 9-3*i<6:
            N.link2link(L[(i,"East",3*j-2)],L[(j,"South",9-3*i)],1,0.3)
        N.antagonistic(L[(i,"East",3*j-2)],L[(j,"South",8-3*i)])
        if 3*j-1<8:
            N.link2link(L[(j,"South",8-3*i)],L[(i,"East",3*j-1)],0.5,0.2)

for i in [1,2]:
    for j in [1,2,3]:
        N.link2link(L[(i,"West",10-3*j)],L[(j,"South",8-3*i)],1,0.3)
        N.antagonistic(L[(i,"West",10-3*j)],L[(j,"South",7-3*i)])
        if 11-3*j<8:
            N.link2link(L[(j,"South",7-3*i)],L[(i,"West",11-3*j)],0.5,0.2)

for i in [1,2]:
    for j in [1,2,3]:
        if 3*i<6:
            N.link2link(L[(i,"West",10-3*j)],L[(j,"North",3*i)],1,0.3)
        N.antagonistic(L[(i,"West",10-3*j)],L[(j,"North",3*i-1)])
        if 11-3*j<8:
            N.link2link(L[(j,"North",3*i-1)],L[(i,"West",11-3*j)],0.5,0.2)      

for dir in ["NW","SW","NE","SE"]:
    N.link2link(L[(dir,1)],L[(dir,2)],1,0.5)


N.link2link(L[("SW",1)],L[(1,"East",4)],1,0.5)  
N.link2link(L[(1,"East",3)],L[("SW",2)],1,0.2)
N.link2link(L[("SW",2)],L[(1,"West",6)],1,1)
N.link2link(L[(1,"West",6)],L[("SW",3)],1,0.2)
N.link2link(L[("SW",3)],L[(1,"East",3)],1,0.5)
N.antagonistic(L[(1,"East",2)],L[("SW",3)])
N.antagonistic(L[(1,"East",3)],L[("SW",1)])
N.antagonistic(L[(1,"West",5)],L[("SW",2)])

N.link2link(L[("SE",1)],L[(1,"East",7)],1,0.5)  
N.link2link(L[(1,"East",6)],L[("SE",2)],1,0.2)
N.link2link(L[("SE",2)],L[(1,"West",3)],1,1)
N.link2link(L[(1,"West",3)],L[("SE",3)],1,0.2)
N.link2link(L[("SE",3)],L[(1,"East",6)],1,0.5)
N.antagonistic(L[(1,"East",5)],L[("SE",3)])
N.antagonistic(L[(1,"East",6)],L[("SE",1)])
N.antagonistic(L[(1,"West",2)],L[("SE",2)])

N.link2link(L[("NE",1)],L[(2,"West",4)],1,0.5)
N.link2link(L[(2,"West",3)],L[("NE",2)],1,0.2)
N.link2link(L[("NE",2)],L[(2,"East",6)],1,1)
N.link2link(L[(2,"East",6)],L[("NE",3)],1,0.2)
N.link2link(L[("NE",3)],L[(2,"West",3)],1,0.5)
N.antagonistic(L[(2,"West",2)],L[("NE",3)])
N.antagonistic(L[(2,"West",3)],L[("NE",1)])
N.antagonistic(L[(2,"East",5)],L[("NE",2)])

N.link2link(L[("NW",1)],L[(2,"West",7)],1,0.5)
N.link2link(L[(2,"West",6)],L[("NW",2)],1,0.2)
N.link2link(L[("NW",2)],L[(2,"East",3)],1,1)
N.link2link(L[(2,"East",3)],L[("NW",3)],1,0.2)
N.link2link(L[("NW",3)],L[(2,"West",6)],1,0.5)
N.antagonistic(L[(2,"West",5)],L[("NW",3)])
N.antagonistic(L[(2,"West",6)],L[("NW",1)])
N.antagonistic(L[(2,"East",2)],L[("NW",2)])

N.update()
