from network_all import *
import random


f=open("random_demand.txt","w")

r={}
T_end=100
for t in range(0,T_end):
	for i in [1,2]:
		for dir in ["East","West"]:
			for j in [1,2,3,4,5,6,7]:
				l=L[(i,dir,j)]
				r[(l,t)]=random.random()
				f.write(str(r[(l,t)])+"\n")
	for i in [1,2,3]:
		for dir in ["North","South"]:
			for j in [1,2,3,4,5]:
				l=L[(i,dir,j)]
				r[(l,t)]=random.random()
				f.write(str(r[(l,t)])+"\n")
	for dir in ["NW","SW","NE","SE"]:
		for j in [1,2,3]:
				l=L[(dir,j)]
				r[(l,t)]=random.random()
				f.write(str(r[(l,t)])+"\n")
f.close()  