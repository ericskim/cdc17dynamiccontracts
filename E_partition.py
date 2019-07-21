from topology import *
from network_all import *

print len(N.links)
N.partition(4,20)

# Here We partition and save

# for l in N.links:
#     print l,":",l.subnetwork


f=open("subnetwork_indices.txt","w")
for i in [1,2]:
    for dir in ["East","West"]:
        for j in [1,2,3,4,5,6,7]:
            l=L[(i,dir,j)]
            f.write(str(l.subnetwork)+"\n")
for i in [1,2,3]:
    for dir in ["North","South"]:
        for j in [1,2,3,4,5]:
            l=L[(i,dir,j)]
            f.write(str(l.subnetwork)+"\n")
for dir in ["NW","SW","NE","SE"]:
    for j in [1,2,3]:
        l=L[(dir,j)]
        f.write(str(l.subnetwork)+"\n")
f.close()


# SubNetworks={}
# for n in [1,2,3,4]:
#     SubNetworks[n]=network()
#     
# for key in L.keys():
#     l=L[key]
#     L[("sub",l.subnetwork,key)]=l
#     SubNetworks[l.subnetwork].links.append(l)
# 
# print SubNetworks[3].links

    