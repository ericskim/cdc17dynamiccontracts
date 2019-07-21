from topology import *

L={}
N=network()

for i in [1,2]:
    for dir in ["East","West"]:
        for j in [1,2,3,4,5,6,7]:
            L[(i,dir,j)]=link("road",40,15,"road %d %s %d" %(i,dir,j))
            N.links.append(L[(i,dir,j)])
        L[(i,dir,8)]=link("sink",40,15,"road %d %s %d" %(i,dir,8))
        L[(i,dir,8)].lane="double"
        N.links.append(L[(i,dir,8)])
        
for i in [1,2,3]:
    for dir in ["North","South"]:
        for j in [1,2,3,4,5]:
            L[(i,dir,j)]=link("road",40,15,"boulevard %d %s %d" %(i,dir,j))
            L[(i,dir,j)].lane="double"
            N.links.append(L[(i,dir,j)])
        L[(i,dir,6)]=link("sink",40,15,"road %d %s %d" %(i,dir,6))
        L[(i,dir,6)].lane="double"
        N.links.append(L[(i,dir,6)])
            
for dir in ["NW","SW","NE","SE"]:
    for j in [1,2,3]:
        L[(dir,j)]=link("road",40,15,"side road %s %d" %(dir,j))
        N.links.append(L[(dir,j)])
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
N.draw()