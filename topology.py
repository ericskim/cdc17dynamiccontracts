global M
M=1000
import pdb

from gurobipy import *

class link:
	def __init__(self,type,capacity,maxflow,name):
		self.x=0  # State of the link
		self.type=type # Available types: "freeway", "road", "on-ramp"
		self.cap=capacity # Capacity of the link
		self.qbar=maxflow # Maximum amount of vehicles allowed to flow in one sample time
		self.up=[] # List of the upstream links
		self.down=[] # List of the downstream links
		self.adj=[] # List of the adjacent links (not used in this project)
		self.u=1 # The control actuation 
		self.w=0 # Adversarial Input
		self.name=name # in case if you want to name a link!
		self.lane="single" # Single lane, or double lane
		self.head=(0,0) #head intersection coordinates
		self.tail=(0,0) #tail intersection coordinates
		self.subnetwork=0 #Which subnetwork am I assigned to?
		self.output=0 #output
		
	def __str__(self):
		return str(self.name)
	
	def __repr__(self):
		return str(self.name)
		
	def update_link_up(self):
		for L in self.down:
			if not(self in L.up):
					(L.up).append(self)

	def update_link_adj(self):
		for L in self.up:
			for J in L.down:
				if not(J in self.adj) and J!=self:
					(self.adj).append(J)	
	def get_up(self):
		return self.up

	def get_down(self):
		return self.down
				
	def get_adj(self):
		return self.adj
		
	def get_x(self):
		return self.x
		
class network:
	def __init__(self):
		self.links=[]
		self.link_address={}
		self.alphas={}
		self.betas={}
		self.delay=0
		self.antagonistics=[]

	def __repr__(self):
		return str(self.links)
	
	def update(self): # Call at the very end of everything
		for L in self.links:
			L.update_link_adj()
	
	def evolve(self):
		f={}
		for L in self.links:
			if L.type!="sink":
				f[L]=min(L.x,L.qbar*L.u)
				for k in L.down:
					f[L]=min(f[L],self.alphas[(L,k)]/self.betas[(L,k)]*(k.cap-k.x))
				self.delay+=L.x-f[L]
		for L in self.links:
			in_flow=0
			for k in L.up:
				in_flow+=self.betas[(k,L)]*f[k]
			L.output=in_flow
			if L.type!="sink":
				L.x=min(L.x-f[L]+in_flow+L.w,L.cap)

	def evolve_decentralized(self):
		f={}
		for L in self.links:
			if L.type!="sink":
				f[L]=min(L.x,L.qbar*L.u)
				for k in L.down:
					f[L]=min(f[L],self.alphas[(L,k)]/self.betas[(L,k)]*(k.cap-k.x))
				self.delay+=L.x-f[L]
		for L in self.links:
			in_flow=0
			for k in L.up:
				in_flow+=self.betas[(k,L)]*f[k]
			if L.type=="sink":
				L.output=in_flow
			else:
				L.output=0
			if L.type!="sink":
				L.x=min(L.x-f[L]+in_flow,L.cap)
				
					
	def antagonistic(self,link1,link2):
		self.antagonistics.append((link1,link2))
		
			

	def link2link(self,l1,l2,alpha,beta): # Flow from l1 to l2
		(l1.down).append(l2)
		(l2.up).append(l1)
		self.alphas[(l1,l2)]=alpha
		self.betas[(l1,l2)]=beta
	
	def MILP_constraints(self,T,external_demand):
		model=Model("traffic_sequence")
		x={}
		u={}
		d={}
		q={}
		f={}
		for t in range(0,T+1):
			for l in self.links:
				x[(l,t)]=model.addVar(lb=0, ub=l.cap)
		for t in range(0,T+1):
			for l in self.links:
				d[(l,t)]=model.addVar(vtype=GRB.BINARY,lb=0, ub=1)
				if l.type=="road":
					u[(l,t)]=model.addVar(vtype=GRB.BINARY,lb=0, ub=1)
				if l.type=="freeway" or l.type=="sink":
					u[(l,t)]=1
				if l.type=="on-ramp":
					u[(l,t)]=model.addVar(lb=0, ub=1)
				f[(l,t)]=model.addVar(lb=0, ub=l.qbar)
		model.update()
		for t in range(0,T+1):
			for l in self.links:
				model.addConstr(f[(l,t)] <= x[(l,t)])
				model.addConstr(f[(l,t)] <= l.qbar * u[(l,t)])
				model.addConstr(f[(l,t)] >= x[(l,t)] - M * d[(l,t)])
				model.addConstr(f[(l,t)] >= l.qbar * u[(l,t)] - M + M * d[(l,t)])
				for k in self.links:
					if (l,k) in self.antagonistics:
						model.addConstr(u[(l,t)] + u[(k,t)] <= 1)
		for t in range(0,T):
			for l in self.links:
				upflow=LinExpr()
				for k in l.up:
					upflow.add(self.betas[(k,l)]*f[(k,t)])
				if l.up==[]:
					upflow=0
				model.addConstr(x[(l,t+1)] == x[(l,t)] - f[(l,t)] + upflow + external_demand[l])
		for t in range(0,T+1):
			for l in self.links:
				for k in l.down:
					model.addConstr(self.betas[(l,k)]*f[(l,t)] <= self.alphas[(l,k)]*k.cap -self.alphas[(l,k)]*x[(k,t)] )
		for l in self.links:
				model.addConstr(x[(l,T)] <= x[(l,0)])
		
		model.optimize()
		state={}
		control={}
		for t in range(0,T+1):
			for l in self.links: 
				state[(l,t)]=x[(l,t)].X
				if t<T:
					control[(l,t)]=(u[(l,t)].X)
		return (state,control)
	
	
	
	
	
	
	
	
	
	
	def MILP_MTL_constraints(self,T,external_demand):
		# specification has h=4
		# The red light is eventually between [0,4)
		# The bridge is h=0
		# The sequentiality has h=3
		# The liveness has h=4, i.e. between [0,4)		  
		model=Model("MTL_traffic_sequence")
		x={}
		u={}
		d={}
		q={}
		f={}
		z={}
		y={}
		h=1
		for t in range(0,T+h):
			for l in self.links:
				x[(l,t)]=model.addVar(lb=0, ub=l.cap)
		for t in range(0,T+h):
			for l in self.links:
				d[(l,t)]=model.addVar(vtype=GRB.BINARY,lb=0, ub=1)
				if l.type=="road":
					u[(l,t)]=model.addVar(vtype=GRB.BINARY,lb=0, ub=1)
				if l.type=="freeway" or l.type=="sink":
					u[(l,t)]=1
				if l.type=="on-ramp":
					u[(l,t)]=model.addVar(lb=0, ub=1)
				f[(l,t)]=model.addVar(lb=0, ub=l.qbar)
				y[(l,t)]=model.addVar(lb=0, ub=100)
		# Red light spec variables:	  
		model.update()
		for t in range(0,T+h):
			for l in self.links:
				model.addConstr(f[(l,t)] <= x[(l,t)])
				model.addConstr(f[(l,t)] <= l.qbar * u[(l,t)])
				model.addConstr(f[(l,t)] >= x[(l,t)] - M * d[(l,t)])
				model.addConstr(f[(l,t)] >= l.qbar * u[(l,t)] - M + M * d[(l,t)])
				for k in self.links:
					if (l,k) in self.antagonistics:
						model.addConstr(u[(l,t)] + u[(k,t)] <= 1)
		for t in range(0,T+h):
			for l in self.links:
				upflow=LinExpr()
				for k in l.up:
					upflow.add(self.betas[(k,l)]*f[(k,t)])
				if l.up==[]:
					upflow=0
				model.addConstr(upflow==y[(l,t)])
		for t in range(0,T+h-1):
			for l in self.links:
				model.addConstr(x[(l,t+1)] == x[(l,t)] - f[(l,t)] + y[l,t] + external_demand[(l,t%T)])
		for t in range(0,T+h):
			for l in self.links:
				for k in l.down:
					model.addConstr(self.betas[(l,k)]*f[(l,t)] <= self.alphas[(l,k)]*k.cap -self.alphas[(l,k)]*x[(k,t)] )
		
		for l in self.links:
			for tau in range(0,h):
				model.addConstr(x[(l,T+tau)] <= x[(l,tau)])
				if not l.type=="freeway":
					model.addConstr(u[(l,T+tau)] == u[(l,tau)])
		
		model.optimize()
		state={}
		control={}
		output={}
		for t in range(0,T+h):
			for l in self.links: 
				state[(l,t)]=x[(l,t)].X
				if l.type=="road":
					control[(l,t)]=(u[(l,t)].X)
				elif l.type=="freeway":
					control[(l,t)]=1
				output[(l,t)]=(y[(l,t)].X)
		return (state,control,output)
	
# ==============================================
# ==============================================
# ==============================================
# ==============================================
# ================== TIKZ ================
# ==============================================
# ==============================================
# ==============================================	
	
	def draw(self):
		f=open("tikz.txt",'w')
		a=0.1
		b=0.05
		nodes=[]
		i=1
		for l in self.links:
			ax=a*(l.head[0]-l.tail[0])
			ay=a*(l.head[1]-l.tail[1])
			f.write("\draw [line width=0.4mm,->] ("+str(l.tail[0]+ax)+" , "+str(l.tail[1]+ay)+"	 ) -- ( "+str(l.head[0]-ax)+" , "+str(l.head[1]-ay)+" );\n")
			f.write("\draw ("+str(l.tail[0]+5*ax+1.6*ay)+","+str(l.tail[1]+5*ay+1.6*ax)+") node[black!50] {$"+str(i)+"$};\n")
			i+=1
			if not (l.head in nodes) and l.lane=="single":
				f.write("\draw [] ("+str(l.head[0]-a)+" , "+str(l.head[1]-a)+"	) rectangle ( "+str(l.head[0]+0.1)+" , "+str(l.head[1]+0.1)+" );\n")
		f.close()
		
# ==============================================
# ==============================================
# ==============================================
# ==============================================
# ================== PARTIONING ================
# ==============================================
# ==============================================
# ==============================================

	def partition(self,N,S):
		p=Model("Partitioning")
		z={}
		q={}
		for n in range(1,N+1):
			for l in self.links:
				z[(l,n)]=p.addVar(vtype=GRB.BINARY,lb=0, ub=1)
				for k in l.down:
					q[(l,k,n)]=p.addVar(lb=0, ub=1,obj=1)
					 
		p.update()
		cost=LinExpr()
		for l in self.links:
			index=LinExpr()
			for n in range(1,N+1):
				index.add(z[l,n]) 
				for k in l.down:
					p.addConstr(q[(l,k,n)]>=z[(l,n)]-z[(k,n)])
					p.addConstr(q[(l,k,n)]>=-z[(l,n)]+z[(k,n)])
			p.addConstr(index==1)
		for n in range(1,N+1):
			all_links=LinExpr()
			for l in self.links:
				all_links.add(z[(l,n)])
			p.addConstr(all_links<=S)
		for l in self.links:
			for k in self.links:
				 if (l,k) in self.antagonistics:
					for n in range(1,N+1):
						p.addConstr(z[(l,n)] == z[(k,n)])
		l1=self.link_address[(2,"North",2)]
		l2=self.link_address[(2,"South",4)]
		l3=self.link_address[(1,"West",4)]
		for n in range(1,N+1):
			p.addConstr(z[(l1,n)]==z[(l2,n)])
			p.addConstr(z[(l3,n)]==z[(l2,n)])
		l1=self.link_address[(3,"North",3)]
		l2=self.link_address[(3,"North",4)]
		l3=self.link_address[(3,"South",3)]
		l4=self.link_address[(3,"South",4)]
		for n in range(1,N+1):
			p.addConstr(z[(l1,n)]==z[(l2,n)])
			p.addConstr(z[(l2,n)]==z[(l3,n)])		
			p.addConstr(z[(l3,n)]==z[(l4,n)])
		p.optimize()
		for n in range(1,N+1):
#			  print "\n \n \n The subnetwork #",n,":"
			for l in self.links:
				if z[(l,n)].X==1:
#					  print l
					l.subnetwork=n 
	
	
	
	
	
	
	
	def draw_subnetworks(self):
		f=open("tikz_subnetworks.txt",'w')
		a=0.1
		b=0.05
		nodes=[]
		i=1
		for l in self.links:
			ax=a*(l.head[0]-l.tail[0])
			ay=a*(l.head[1]-l.tail[1])
			if l.subnetwork==0:
				color="black"
			if l.subnetwork==1:
				color="red!50!black"
			if l.subnetwork==2:
				color="cyan!50!black"
			if l.subnetwork==3:
				color="green!50!black"
			if l.subnetwork==4:
				color="blue!50!black"
			f.write("\draw ["+color+",line width=0.4mm,->] ("+str(l.tail[0]+ax)+" , "+str(l.tail[1]+ay)+"  ) -- ( "+str(l.head[0]-ax)+" , "+str(l.head[1]-ay)+" );\n")
			i+=1
			if not (l.head in nodes) and l.lane=="single":
				f.write("\draw [] ("+str(l.head[0]-a)+" , "+str(l.head[1]-a)+"	) rectangle ( "+str(l.head[0]+0.1)+" , "+str(l.head[1]+0.1)+" );\n")
				nodes.append(l.head)
		f.close()
		
		
	def MPC_MTL(self,H,T,clock,external_demand,x_terminal,u_terminal,x_history,u_history):
		# specification has h=4
		# The red light is eventually between [0,4)
		# The bridge is h=0
		# The sequentiality has h=3
		# The liveness has h=4, i.e. between [0,4)		  
		model=Model("MTL_traffic_sequence")
		x={}
		u={}
		d={}
		q={}
		f={}
		z={}
		y={}
		h=6
		hred=6
		for t in range(1,H+1):
			for l in self.links:
				x[(l,t)]=model.addVar(lb=0, ub=l.cap,obj=0.5**t)
		for t in range(0,H+1):
			for l in self.links:
				d[(l,t)]=model.addVar(vtype=GRB.BINARY,lb=0, ub=1)
				if l.type=="road":
					u[(l,t)]=model.addVar(vtype=GRB.BINARY,lb=0, ub=1)
				if l.type=="freeway" or l.type=="sink":
					u[(l,t)]=1
				if l.type=="on-ramp":
					u[(l,t)]=model.addVar(lb=0, ub=1)
				f[(l,t)]=model.addVar(lb=0, ub=l.qbar,obj=-(0.5**t))
		for t in range(-h+1,1):
			for l in self.links:
				x[(l,t)]=x_history[(l,t)]
		for t in range(-h+1,0):
			for l in self.links:
				u[(l,t)]=u_history[(l,t)]		 
		# Red light spec variables:
		for t in range(-h+1,H+1):
			z[("red",t)]=model.addVar(lb=0, ub=1) #Everything determined using this!
			z[("reactive",t)]=model.addVar(vtype=GRB.BINARY,lb=0, ub=1) #Everything determined using this!	  
		model.update()
		for t in range(0,H+1):
			for l in self.links:
				model.addConstr(f[(l,t)] <= x[(l,t)])
				model.addConstr(f[(l,t)] <= l.qbar * u[(l,t)])
				model.addConstr(f[(l,t)] >= x[(l,t)] - M * d[(l,t)])
				model.addConstr(f[(l,t)] >= l.qbar * u[(l,t)] - M + M * d[(l,t)])
				for k in self.links:
					if (l,k) in self.antagonistics:
						model.addConstr(u[(l,t)] + u[(k,t)] <= 1)
		for t in range(0,H+1):
			for l in self.links:
				upflow=LinExpr()
				for k in l.up:
					upflow.add(self.betas[(k,l)]*f[(k,t)])
				if l.up==[]:
					upflow=0
				y[(l,t)]=upflow
		for t in range(0,H):
			for l in self.links:
				model.addConstr(x[(l,t+1)] == x[(l,t)] - f[(l,t)] + y[(l,t)] + external_demand[(l,(t+clock)%T)])
		for t in range(0,H+1):
			for l in self.links:
				for k in l.down:
					model.addConstr(self.betas[(l,k)]*f[(l,t)] <= self.alphas[(l,k)]*k.cap -self.alphas[(l,k)]*x[(k,t)] )
		# now MTL constraints:
		# The red light spec:
		if (2,"North",2) in self.link_address.keys():
			l1=self.link_address[(2,"North",2)]
			l2=self.link_address[(2,"South",4)]
			l3=self.link_address[(1,"West",4)]
			for t in range(-h+1,H+1):
				model.addConstr(z[("red",t)]<=1-u[(l1,t)])
				model.addConstr(z[("red",t)]<=1-u[(l2,t)])
				model.addConstr(z[("red",t)]<=1-u[(l3,t)])
				model.addConstr(z[("red",t)]>=1-u[(l1,t)]-u[(l2,t)]-u[(l3,t)])
			for t in range(-h+1,H-5):
				sum=LinExpr()
				for tau in range(0,hred):
					sum.add(z[("red",t+tau)])
				model.addConstr(sum>=1)
		# Lets go to second spec: not red green red
		if (2,"West",4) in self.link_address.keys():
			l_green=self.link_address[(2,"West",4)]
			for t in range(-3+1,H-1):
				model.addConstr(1<=u[(l_green,t)]+u[(l_green,t+2)]-u[(l_green,t+1)]+1)
		# Lets go to third spec: reactiveness to traffic
		if ("SW",1) in self.link_address.keys():
			l_r=self.link_address[("SW",1)]
			for t in range(-h+1,H-3):
				model.addConstr(x[(l,t)]<=5 + M - M * z[("reactive",t)] )
				model.addConstr(x[(l,t)]>=5 - M * z[("reactive",t)] )
				model.addConstr(z[("reactive",t)] + u[(l_r,t)] + u[(l_r,t+1)] + u[(l_r,t+2)] + u[(l_r,t+3)] >= 1 )
		# Lets go to fourth spec: bridge thing
		if (3,"North",3) in self.link_address.keys():
			l1=self.link_address[(3,"North",3)]
			l2=self.link_address[(3,"North",4)]
			l3=self.link_address[(3,"South",3)]
			l4=self.link_address[(3,"South",4)]
			for t in range(1,H+1):
				model.addConstr(x[(l1,t)]+x[(l2,t)]+x[(l3,t)]+x[(l4,t)]<=100)		 
			
		# TERMINAL CONSTRAINT	
		for l in self.links:
			for tau in range(H-h+1,H+1):
				model.addConstr(x[(l,tau)] <= x_terminal[l,(tau+clock)%T])
				if not l.type=="freeway":
					model.addConstr(u[(l,tau)] == u_terminal[l,(tau+clock)%T])
		model.optimize()
		running=model.Runtime
		state={}
		control={}
		output={}
		for t in range(1,H+1):
			for l in self.links: 
				state[(l,t)]=x[(l,t)].X
		for t in range(0,H+1):
			for l in self.links:
				if not l.type=="freeway": 
					control[(l,t)]=(u[(l,t)].X)
				else:
					control[(l,t)]=1
		return (running,state,control)				


	def MPC_MTL_Subnetwork(self,H,T,clock,external_demand,x_terminal,u_terminal,y_output,output_subnetwork,output_turn,upstream,x_history,u_history):
		# specification has h=4
		# The red light is eventually between [0,4)
		# The bridge is h=0
		# The sequentiality has h=3
		# The liveness has h=4, i.e. between [0,4)		  
		model=Model("MTL_traffic_sequence")
		x={}
		u={}
		d={}
		q={}
		f={}
		z={}
		y={}
		h=6
		hred=6
		for t in range(1,H+1):
			for l in self.links:
				x[(l,t)]=model.addVar(lb=0, ub=l.cap,obj=0.5**t)
		for t in range(0,H+1):
			for l in self.links:
				d[(l,t)]=model.addVar(vtype=GRB.BINARY,lb=0, ub=1)
				if l.type=="road":
					u[(l,t)]=model.addVar(vtype=GRB.BINARY,lb=0, ub=1)
				if l.type=="freeway" or l.type=="sink":
					u[(l,t)]=1
				if l.type=="on-ramp":
					u[(l,t)]=model.addVar(lb=0, ub=1)
				f[(l,t)]=model.addVar(lb=0, ub=l.qbar,obj=-(0.5**t))
		for t in range(-h+1,1):
			for l in self.links:
				x[(l,t)]=x_history[(l,t)]
		for t in range(-h+1,0):
			for l in self.links:
				u[(l,t)]=u_history[(l,t)]		 
		# Red light spec variables:
		for t in range(-h+1,H+1):
			z[("red",t)]=model.addVar(lb=0, ub=1) #Everything determined using this!
			z[("reactive",t)]=model.addVar(vtype=GRB.BINARY,lb=0, ub=1) #Everything determined using this!	  
		model.update()
		for t in range(0,H+1):
			for l in self.links:
				model.addConstr(f[(l,t)] <= x[(l,t)])
				model.addConstr(f[(l,t)] <= l.qbar * u[(l,t)])
				model.addConstr(f[(l,t)] >= x[(l,t)] - M * d[(l,t)])
				model.addConstr(f[(l,t)] >= l.qbar * u[(l,t)] - M + M * d[(l,t)])
				for k in self.links:
					if (l,k) in self.antagonistics:
						model.addConstr(u[(l,t)] + u[(k,t)] <= 1)
		for t in range(0,H+1):
			for l in self.links:
				upflow=LinExpr()
				for k in l.up:
					upflow.add(self.betas[(k,l)]*f[(k,t)])
				if l.up==[]:
					upflow=0
				y[(l,t)]=upflow
		for t in range(0,H):
			for l in self.links:
				model.addConstr(x[(l,t+1)] == x[(l,t)] - f[(l,t)] + y[(l,t)] + external_demand[(l,(t+clock)%T)])
		for t in range(0,H+1):
			for l in self.links:
				for k in l.down:
					model.addConstr(self.betas[(l,k)]*f[(l,t)] <= self.alphas[(l,k)]*k.cap -self.alphas[(l,k)]*x[(k,t)] )
		# now MTL constraints:
		# The red light spec:
		if (2,"North",2) in self.link_address.keys():
			l1=self.link_address[(2,"North",2)]
			l2=self.link_address[(2,"South",4)]
			l3=self.link_address[(1,"West",4)]
			for t in range(-h+1,H+1):
				model.addConstr(z[("red",t)]<=1-u[(l1,t)])
				model.addConstr(z[("red",t)]<=1-u[(l2,t)])
				model.addConstr(z[("red",t)]<=1-u[(l3,t)])
				model.addConstr(z[("red",t)]>=1-u[(l1,t)]-u[(l2,t)]-u[(l3,t)])
			for t in range(-h+1,H-5):
				sum=LinExpr()
				for tau in range(0,hred):
					sum.add(z[("red",t+tau)])
				model.addConstr(sum>=1)
		# Lets go to second spec: not red green red
		if (2,"West",4) in self.link_address.keys():
			l_green=self.link_address[(2,"West",4)]
			for t in range(-3+1,H-1):
				model.addConstr(1<=u[(l_green,t)]+u[(l_green,t+2)]-u[(l_green,t+1)]+1)
		# Lets go to third spec: reactiveness to traffic
		if ("SW",1) in self.link_address.keys():
			l_r=self.link_address[("SW",1)]
			for t in range(-h+1,H-3):
				model.addConstr(x[(l,t)]<=5 + M - M * z[("reactive",t)] )
				model.addConstr(x[(l,t)]>=5 - M * z[("reactive",t)] )
				model.addConstr(z[("reactive",t)] + u[(l_r,t)] + u[(l_r,t+1)] + u[(l_r,t+2)] + u[(l_r,t+3)] >= 1 )
		# Lets go to fourth spec: bridge thing
		if (3,"North",3) in self.link_address.keys():
			l1=self.link_address[(3,"North",3)]
			l2=self.link_address[(3,"North",4)]
			l3=self.link_address[(3,"South",3)]
			l4=self.link_address[(3,"South",4)]
			for t in range(1,H+1):
				model.addConstr(x[(l1,t)]+x[(l2,t)]+x[(l3,t)]+x[(l4,t)]<=100)		 
		# CONTRACT CONSTRAINTS
		for t in range(0,H+1):
			for k in output_subnetwork:
				contractflow=LinExpr()
				for l in upstream[k]:
					if not (l in self.links):
						print ("ERROR, upstream not here!")
					contractflow.add(f[l,t]*output_turn[(l,k)])
				model.addConstr(contractflow <= y_output[(k,(t+clock)%T)])
				
		# TERMINAL CONSTRAINT	
		for l in self.links:
			for tau in range(H-h+1,H+1):
				model.addConstr(x[(l,tau)] <= x_terminal[l,(tau+clock)%T])
				if not l.type=="freeway":
					model.addConstr(u[(l,tau)] == u_terminal[l,(tau+clock)%T])
		model.optimize()
		running=model.Runtime
		state={}
		control={}
		output={}
		for t in range(1,H+1):
			for l in self.links: 
				state[(l,t)]=x[(l,t)].X
		for t in range(0,H+1):
			for l in self.links:
				if not l.type=="freeway":
					control[(l,t)]=(u[(l,t)].X)
				else:
					control[(l,t)]=1
		return (running,state,control)

	def MPC_MTL_Subnetwork_infeasible(self,H,T,clock,external_demand,x_terminal,u_terminal,y_output,output_subnetwork,output_turn,upstream,x_history,u_history):
		# specification has h=4
		# The red light is eventually between [0,4)
		# The bridge is h=0
		# The sequentiality has h=3
		# The liveness has h=4, i.e. between [0,4)		  
		model=Model("MTL_traffic_sequence")
		x={}
		u={}
		d={}
		q={}
		f={}
		z={}
		y={}
		h=6
		hred=6
		for t in range(1,H+1):
			for l in self.links:
				x[(l,t)]=model.addVar(lb=0, ub=l.cap,obj=0.5**t)
		for t in range(0,H+1):
			for l in self.links:
				d[(l,t)]=model.addVar(vtype=GRB.BINARY,lb=0, ub=1)
				if l.type=="road":
					u[(l,t)]=model.addVar(vtype=GRB.BINARY,lb=0, ub=1)
				if l.type=="freeway" or l.type=="sink":
					u[(l,t)]=1
				if l.type=="on-ramp":
					u[(l,t)]=model.addVar(lb=0, ub=1)
				f[(l,t)]=model.addVar(lb=0, ub=l.qbar,obj=-(0.5**t))
		for t in range(-h+1,1):
			for l in self.links:
				x[(l,t)]=x_history[(l,t)]
		for t in range(-h+1,0):
			for l in self.links:
				u[(l,t)]=u_history[(l,t)]		 
		# Red light spec variables:
		for t in range(-h+1,H+1):
			z[("red",t)]=model.addVar(lb=0, ub=1) #Everything determined using this!
			z[("reactive",t)]=model.addVar(vtype=GRB.BINARY,lb=0, ub=1) #Everything determined using this!	  
		model.update()
		for t in range(0,H+1):
			for l in self.links:
				model.addConstr(f[(l,t)] <= x[(l,t)])
				model.addConstr(f[(l,t)] <= l.qbar * u[(l,t)])
				model.addConstr(f[(l,t)] >= x[(l,t)] - M * d[(l,t)])
				model.addConstr(f[(l,t)] >= l.qbar * u[(l,t)] - M + M * d[(l,t)])
				for k in self.links:
					if (l,k) in self.antagonistics:
						model.addConstr(u[(l,t)] + u[(k,t)] <= 1)
		for t in range(0,H+1):
			for l in self.links:
				upflow=LinExpr()
				for k in l.up:
					upflow.add(self.betas[(k,l)]*f[(k,t)])
				if l.up==[]:
					upflow=0
				y[(l,t)]=upflow
		for t in range(0,H):
			for l in self.links:
				model.addConstr(x[(l,t+1)] == x[(l,t)] - f[(l,t)] + y[(l,t)] + external_demand[(l,(t+clock)%T)])
		for t in range(0,H+1):
			for l in self.links:
				for k in l.down:
					model.addConstr(self.betas[(l,k)]*f[(l,t)] <= self.alphas[(l,k)]*k.cap -self.alphas[(l,k)]*x[(k,t)] )
		# now MTL constraints:
		# The red light spec:
		if (2,"North",2) in self.link_address.keys():
			l1=self.link_address[(2,"North",2)]
			l2=self.link_address[(2,"South",4)]
			l3=self.link_address[(1,"West",4)]
			for t in range(-h+1,H+1):
				model.addConstr(z[("red",t)]<=1-u[(l1,t)])
				model.addConstr(z[("red",t)]<=1-u[(l2,t)])
				model.addConstr(z[("red",t)]<=1-u[(l3,t)])
				model.addConstr(z[("red",t)]>=1-u[(l1,t)]-u[(l2,t)]-u[(l3,t)])
			for t in range(-h+1,H-5):
				sum=LinExpr()
				for tau in range(0,hred):
					sum.add(z[("red",t+tau)])
				model.addConstr(sum>=1)
		# Lets go to second spec: not red green red
		if (2,"West",4) in self.link_address.keys():
			l_green=self.link_address[(2,"West",4)]
			for t in range(-3+1,H-1):
				model.addConstr(1<=u[(l_green,t)]+u[(l_green,t+2)]-u[(l_green,t+1)]+1)
		# Lets go to third spec: reactiveness to traffic
		if ("SW",1) in self.link_address.keys():
			l_r=self.link_address[("SW",1)]
			for t in range(-h+1,H-3):
				model.addConstr(x[(l,t)]<=5 + M - M * z[("reactive",t)] )
				model.addConstr(x[(l,t)]>=5 - M * z[("reactive",t)] )
				model.addConstr(z[("reactive",t)] + u[(l_r,t)] + u[(l_r,t+1)] + u[(l_r,t+2)] + u[(l_r,t+3)] >= 1 )
		# Lets go to fourth spec: bridge thing
		if (3,"North",3) in self.link_address.keys():
			l1=self.link_address[(3,"North",3)]
			l2=self.link_address[(3,"North",4)]
			l3=self.link_address[(3,"South",3)]
			l4=self.link_address[(3,"South",4)]
			for t in range(1,H+1):
				model.addConstr(x[(l1,t)]+x[(l2,t)]+x[(l3,t)]+x[(l4,t)]<=100)		 
		# CONTRACT CONSTRAINTS
		for t in range(0,H+1):
			for k in output_subnetwork:
				contractflow=LinExpr()
				for l in upstream[k]:
					if not (l in self.links):
						print ("ERROR, upstream not here!")
					contractflow.add(f[l,t]*output_turn[(l,k)])
				model.addConstr(contractflow <= y_output[(k,(t+clock)%T)])
				
		# TERMINAL CONSTRAINT	
		for l in self.links:
			for tau in range(H-h+1,H+1):
				model.addConstr(x[(l,tau)] <= x_terminal[l,(tau+clock)%T])
				if not l.type=="freeway":
					model.addConstr(u[(l,tau)] == u_terminal[l,(tau+clock)%T])
		model.optimize()
		print ("THE STATUS AFTER SOLVE IS:"), model.Status
		if model.Status==3:
			return (0,"2","3",1000000)
		running=model.Runtime
		state={}
		control={}
		output={}
		for t in range(1,H+1):
			for l in self.links: 
				state[(l,t)]=x[(l,t)].X
		for t in range(0,H+1):
			for l in self.links:
				if l.type=="road":
					control[(l,t)]=(u[(l,t)].X)
				elif l.type=="freeway":
					control[(l,t)]=1
		return (running,state,control,model.ObjVal)
		
		
	def mine(self,T,external_demand,X,Y,D,gamma,beta_0,beta_f):
		# specification is only congestion avoidance
		# Exogenous demands are fixed (not time varying)
		"""
		T : time horizon
		external_demand: dict. key = link address, val = scalar disturbance
		X: dict. link address, scalar initial state 
		D: dict. link, scalar but not over time yet <--- should be over time	
		beta_0: scales X only for initial condition

		Maybe unnecessary:
			beta_f: scales X only for terminal condition <-- is this necessary for guar mining?
			gamma: scales Y <--- is this necessary for guar mining?
			Y: dict. link, scalar	<--- might be unnecessary
	
		Maybe necessary but not here:
			beta_d: scales D (perhaps depends on time)

		Problem:
			Given: initial state, disturbance = (external_demand + demand from other networks) trajectory
			Find: a state trajectory that is minimal wrt some norm (perhaps weighted)

			Use that generated state trajectory as a guarantee

			This state trajectory is used as another network's disturbance assumption, with an appropriate conversion to a disturbance.
			Also used as a future network's assumption on their initial state.

		"""

		model=Model("mine")
		x={}
		u={}
		d={}
		q={}
		f={}
		z={}
		y={}
		h=1
		alpha=model.addVar(lb=0, ub=10, obj=-1)
		for t in range(0,T+h):
			for l in self.links:
				x[(l,t)]=model.addVar(lb=0, ub=l.cap)
		for t in range(0,T+h):
			for l in self.links:
				d[(l,t)]=model.addVar(vtype=GRB.BINARY,lb=0, ub=1)
				if l.type=="road":
					u[(l,t)]=model.addVar(vtype=GRB.BINARY,lb=0, ub=1)
				if l.type=="freeway" or l.type=="sink":
					u[(l,t)]=1
				if l.type=="on-ramp":
					u[(l,t)]=model.addVar(lb=0, ub=1)
				f[(l,t)]=model.addVar(lb=0, ub=l.qbar)
				y[(l,t)]=model.addVar(lb=0, ub=100, obj=0*l.type=="sink")
		model.update()
		for t in range(0,T+h):
			for l in self.links:
				if not l.type=="sink":
					model.addConstr(f[(l,t)] <= x[(l,t)])
					model.addConstr(f[(l,t)] <= l.qbar * u[(l,t)])
					model.addConstr(f[(l,t)] >= x[(l,t)] - M * d[(l,t)])
					model.addConstr(f[(l,t)] >= l.qbar * u[(l,t)] - M + M * d[(l,t)])
				for k in self.links:
					if (l,k) in self.antagonistics:
						model.addConstr(u[(l,t)] + u[(k,t)] <= 1)
		for t in range(0,T+h):
			for l in self.links:
				upflow=LinExpr()
				for k in l.up:
					upflow.add(self.betas[(k,l)]*f[(k,t)])
				if l.up==[]:
					upflow=0
				model.addConstr(upflow==y[(l,t)])
		for t in range(0,T+h-1):
			for l in self.links:
				if l.type!="sink":
					model.addConstr(x[(l,t+1)] == x[(l,t)] - f[(l,t)] + y[l,t] + D[l]*alpha + external_demand[l,t])
		for t in range(0,T+h):
			for l in self.links:
				for k in l.down:
					model.addConstr(self.betas[(l,k)]*f[(l,t)] <= self.alphas[(l,k)]*k.cap -self.alphas[(l,k)]*x[(k,t)] )
#		for l in self.links:
#			for tau in range(0,h):
#				model.addConstr(x[(l,T+tau)] <= x[(l,tau)])
#				if not l.type=="freeway":
#					model.addConstr(u[(l,T+tau)] == u[(l,tau)])
		for t in range(0,T+h):
			for l in self.links:
				if l.type=="sink":
					model.addConstr(y[(l,t)] <= gamma*Y[l])
		for l in self.links:
			if l.type!="sink":
				model.addConstr(x[(l,0)] >= beta_0*X[l])
		for l in self.links:
			if l.type!="sink":
				model.addConstr(x[(l,T+h-1)] <= beta_f*X[l])
		
		model.optimize()
		print ("alpha was"), alpha.X
		state={}
		control={}
		output={}
		for t in range(0,T+h):
			for l in self.links: 
				state[(l,t)]=x[(l,t)].X
				if l.type=="road":
					control[(l,t)]=(u[(l,t)].X)
				elif l.type=="freeway":
					control[(l,t)]=1
				if l.type=="sink":
					output[(l,t)]=(y[(l,t)].X)
		return (state,control,output)
				
	
	
	
	
	
	
	
	def guarantee_miner(self,T,D,X_initial):
		# specification is only congestion avoidance
		# Exogenous demands are fixed (not time varying)
		"""
		Inputs:
		T : time horizon
		external_demand: dict. key = (link address, time), val = scalar disturbance
		Note: D = external demand from outside of the entire network + 
					demand from other networks 
		X_initial: dict. link address, scalar initial state 
		Note: do not need an initial state for sink links
		
		Output: 
		State: dict. key: (link,time), val: scalar: State of the system
		Output: dict. key: (link,time), val: scalar: Cars leaving the network 
			

		Problem:
			Given: initial state, demand D = (external_demand + demand from other networks) trajectory
			Find: a state trajectory that is minimal wrt some norm (perhaps weighted)
			
			Note:  T-trajectory satisfies the following properties:
			1) satisfies always in monotone region
			2) satisfies the following temporal logic formula: 
				eventually 0_T all red, for each of the intersections

			Use that generated state trajectory as a guarantee

			This state trajectory is used as another network's disturbance assumption, with an appropriate conversion to a disturbance.
			Also used as a future network's assumption on their initial state.

		"""

		model=Model("guarantee_miner")
		x={}
		u={}
		d={}
		q={}
		f={}
		z={}
		y={}
		h=1
		weight_Linfity=10000
		Linfinity_norm=model.addVar(lb=0,obj=weight_Linfity)		   
		for t in range(0,T+h):
			for l in self.links:
				x[(l,t)]=model.addVar(lb=0, ub=l.cap,obj=1) # minimize L_1 norm for now
		for t in range(0,T+h):
			for l in self.links:
				d[(l,t)]=model.addVar(vtype=GRB.BINARY,lb=0, ub=1)
				if l.type=="road":
					u[(l,t)]=model.addVar(vtype=GRB.BINARY,lb=0, ub=1)
				if l.type=="freeway" or l.type=="sink":
					u[(l,t)]=1
				if l.type=="on-ramp":
					u[(l,t)]=model.addVar(lb=0, ub=1)
				f[(l,t)]=model.addVar(lb=0, ub=l.qbar)
				y[(l,t)]=model.addVar(lb=0, ub=100, obj=0*l.type=="sink")
		model.update()
		for l in self.links:
				if not l.type=="sink":
					model.addConstr(x[(l,0)]==X_initial[l]) # initial condition assignment
		for t in range(0,T+h):
			for l in self.links:
				if not l.type=="sink":
					model.addConstr(f[(l,t)] <= x[(l,t)])
					model.addConstr(f[(l,t)] <= l.qbar * u[(l,t)])
					model.addConstr(f[(l,t)] >= x[(l,t)] - M * d[(l,t)])
					model.addConstr(f[(l,t)] >= l.qbar * u[(l,t)] - M + M * d[(l,t)])
				for k in self.links:
					if (l,k) in self.antagonistics:
						model.addConstr(u[(l,t)] + u[(k,t)] <= 1)
		for t in range(0,T+h):
			for l in self.links:
				upflow=LinExpr()
				for k in l.up:
					upflow.add(self.betas[(k,l)]*f[(k,t)])
				if l.up==[]:
					upflow=0
				model.addConstr(upflow==y[(l,t)])
		for t in range(0,T+h-1):
			for l in self.links:
				if l.type!="sink":
					model.addConstr(x[(l,t+1)] == x[(l,t)] - f[(l,t)] + y[l,t] + D[l,t])
		for t in range(0,T+h):
			for l in self.links:
				for k in l.down:
					model.addConstr(self.betas[(l,k)]*f[(l,t)] <= self.alphas[(l,k)]*k.cap -self.alphas[(l,k)]*x[(k,t)] )
#		for l in self.links:
#			for tau in range(0,h):
#				model.addConstr(x[(l,T+tau)] <= x[(l,tau)])
#				if not l.type=="freeway":
#					model.addConstr(u[(l,T+tau)] == u[(l,tau)])
#		  for t in range(0,T+h):
#			  for l in self.links:
#				  if l.type=="sink":
#					  model.addConstr(y[(l,t)] <= gamma*Y[l])
#		  for l in self.links:
#			  if l.type!="sink":
#				  model.addConstr(x[(l,0)] >= beta_0*X[l])
#		  for l in self.links:
#			  if l.type!="sink":
#				  model.addConstr(x[(l,T+h-1)] <= beta_f*X[l])
		"""
			Temporal logic specification goes here
			If there exists a red/red combination in [0,T-1]
			assign red=0, green=1
			assign first link:l , second link: k
			two links are antagonistic : u[l]+u[k] <=1
			that means sum_0:T-1(u[l])+sum(u[k]) <= T-1
			at least there
		"""
		for k in self.links:
			for l in self.links:
				if (l,k) in self.antagonistics:
					sum=LinExpr()
					for t in range(0,T+h):
						sum.add(u[l,t],1)
						sum.add(u[k,t],1)
					model.addConstr(sum <= T-1)
		for t in range(1,T):
			for l in self.links:
				if l.type!="sink":
					model.addConstr(x[l,t]<=Linfinity_norm)		   
		model.optimize()
		print Linfinity_norm.X
		state={}
		control={}
		output={}
		cost=model.ObjVal
		for t in range(0,T+h):
			for l in self.links:
				state[(l,t)]=x[(l,t)].X
				if l.type=="road":
					control[(l,t)]=(u[(l,t)].X)
				elif l.type=="freeway":
					control[(l,t)]=1
				elif l.type=="on-ramp":
					control[(l,t)]=u[(l,t)].X
				if l.type=="sink":
					output[(l,t)]=(y[(l,t)].X)
		"""
			we do not need control
			included only for debugging, observing controls to verify spec
			and plot the histogram for the paper
		"""
		cost_contract=0
		for t in range(1,T):
			for l in self.links:
				if l.type!="sink":
					cost_contract+=state[l,t]#-f[l,t].X
		print "cost contract is",cost_contract
		return (state,control,output,cost_contract) 
			  
#		  model=Model("guarantee_miner")
#		  x={}
#		  u={}
#		  d={}
#		  q={}
#		  f={}
#		  z={}
#		  y={}
#		  h=1
#		  weight_Linfity=1
#		  Linfinity_norm=model.addVar(obj=weight_Linfity)		 
#		  for t in range(0,T+h):
#			  for l in self.links:
#				  x[(l,t)]=model.addVar(lb=0, ub=l.cap,obj=1*0) # minimize L_1 norm for now
#		  for t in range(0,T+h):
#			  for l in self.links:
#				  d[(l,t)]=model.addVar(vtype=GRB.BINARY,lb=0, ub=1)
#				  if l.type=="road":
#					  u[(l,t)]=model.addVar(vtype=GRB.BINARY,lb=0, ub=1)
#				  if l.type=="freeway" or l.type=="sink":
#					  u[(l,t)]=1
#				  if l.type=="on-ramp":
#					  u[(l,t)]=model.addVar(lb=0, ub=1)
#				  f[(l,t)]=model.addVar(lb=0, ub=l.qbar)
#				  y[(l,t)]=model.addVar(lb=0, ub=100, obj=0*l.type=="sink")
#		  model.update()
#		  for l in self.links:
#				  if not l.type=="sink":
#					  model.addConstr(x[(l,0)]==X_initial[l]) # initial condition assignment
#		  for t in range(0,T+h):
#			  for l in self.links:
#				  if not l.type=="sink":
#					  model.addConstr(f[(l,t)] <= x[(l,t)])
#					  model.addConstr(f[(l,t)] <= l.qbar * u[(l,t)])
#					  model.addConstr(f[(l,t)] >= x[(l,t)] - M * d[(l,t)])
#					  model.addConstr(f[(l,t)] >= l.qbar * u[(l,t)] - M + M * d[(l,t)])
#				  for k in self.links:
#					  if (l,k) in self.antagonistics:
#						  model.addConstr(u[(l,t)] + u[(k,t)] <= 1)
#		  for t in range(0,T+h):
#			  for l in self.links:
#				  upflow=LinExpr()
#				  for k in l.up:
#					  upflow.add(self.betas[(k,l)]*f[(k,t)])
#				  if l.up==[]:
#					  upflow=0
#				  model.addConstr(upflow==y[(l,t)])
#		  for t in range(0,T+h-1):
#			  for l in self.links:
#				  if l.type!="sink":
#					  model.addConstr(x[(l,t+1)] == x[(l,t)] - f[(l,t)] + y[l,t] + D[l,t])
#		  for t in range(0,T+h):
#			  for l in self.links:
#				  for k in l.down:
#					  model.addConstr(self.betas[(l,k)]*f[(l,t)] <= self.alphas[(l,k)]*k.cap -self.alphas[(l,k)]*x[(k,t)] )
# #		  for l in self.links:
# #			  for tau in range(0,h):
# #				  model.addConstr(x[(l,T+tau)] <= x[(l,tau)])
# #				  if not l.type=="freeway":
# #					  model.addConstr(u[(l,T+tau)] == u[(l,tau)])
# #			for t in range(0,T+h):
# #				for l in self.links:
# #					if l.type=="sink":
# #						model.addConstr(y[(l,t)] <= gamma*Y[l])
# #			for l in self.links:
# #				if l.type!="sink":
# #					model.addConstr(x[(l,0)] >= beta_0*X[l])
# #			for l in self.links:
# #				if l.type!="sink":
# #					model.addConstr(x[(l,T+h-1)] <= beta_f*X[l])
#		  """
#			  Temporal logic specification goes here
#			  If there exists a red/red combination in [0,T-1]
#			  assign red=0, green=1
#			  assign first link:l , second link: k
#			  two links are antagonistic : u[l]+u[k] <=1
#			  that means sum_0:T-1(u[l])+sum(u[k]) <= T-1
#			  at least there
#		  """
#		  for k in self.links:
#			  for l in self.links:
#				  if (l,k) in self.antagonistics:
#					  sum=LinExpr()
#					  for t in range(0,T+h):
#						  sum.add(u[l,t],1)
#						  sum.add(u[k,t],1)
#					  model.addConstr(sum <= T-1)
#		  for t in range(1,T):
#			  for l in self.links:
#				  if l.type!="sink":
#					  model.addConstr(x[l,t] <= Linfity_norm)
#		  model.optimize()
#		  print Linfinity_norm.X
#		  state={}
#		  control={}
#		  output={}
#		  cost=model.ObjVal
#		  for t in range(0,T+h):
#			  for l in self.links:
#				  state[(l,t)]=x[(l,t)].X
#				  if l.type=="road":
#					  control[(l,t)]=(u[(l,t)].X)
#				  elif l.type=="freeway":
#					  control[(l,t)]=1
#				  if l.type=="sink":
#					  output[(l,t)]=(y[(l,t)].X)
#		  """
#			  we do not need control
#			  included only for debugging, observing controls to verify spec
#			  and plot the histogram for the paper
#		  """
#		  return (state,control,output) 
	def MPC_Contract(self,T,clock,U_history,X_contract,D,Output_Contract):
		"""
		Inputs:
		T : time horizon
		X_now
		"""
		model=Model("MPC")
		x={}
		u={}
		d={}
		q={}
		f={}
		z={}
		y={}
		h=1
		for t in range(0,T+h):
			for l in self.links:
				x[(l,t)]=model.addVar(lb=0, ub=l.cap,obj=1) # minimize L_1 norm for now
		for t in range(0,T+h):
			for l in self.links:
				d[(l,t)]=model.addVar(vtype=GRB.BINARY,lb=0, ub=1)
				if l.type=="road":
					u[(l,t)]=model.addVar(vtype=GRB.BINARY,lb=0, ub=1)
				if l.type=="freeway" or l.type=="sink":
					u[(l,t)]=1
				if l.type=="on-ramp":
					u[(l,t)]=model.addVar(lb=0, ub=1)
				f[(l,t)]=model.addVar(lb=0, ub=l.qbar,obj=-1)
				y[(l,t)]=model.addVar(lb=0, ub=100, obj=0*l.type=="sink")
		model.update()
		for t in range(0,T+h):
			for l in self.links:
				if not l.type=="sink":
					model.addConstr(f[(l,t)] <= x[(l,t)])
					model.addConstr(f[(l,t)] <= l.qbar * u[(l,t)])
					model.addConstr(f[(l,t)] >= x[(l,t)] - M * d[(l,t)])
					model.addConstr(f[(l,t)] >= l.qbar * u[(l,t)] - M + M * d[(l,t)])
				for k in self.links:
					if (l,k) in self.antagonistics:
						model.addConstr(u[(l,t)] + u[(k,t)] <= 1)
		for t in range(clock,T+h):
			for l in self.links:
				upflow=LinExpr()
				for k in l.up:
					upflow.add(self.betas[(k,l)]*f[(k,t)])
				if l.up==[]:
					upflow=0
				model.addConstr(upflow==y[(l,t)])
		for t in range(clock,T+h-1):
			for l in self.links:
				if l.type!="sink":
					model.addConstr(x[(l,t+1)] == x[(l,t)] - f[(l,t)] + y[l,t] + D[l,t])
		for t in range(clock,T+h-1):
			for l in self.links:
				for k in l.down:
					model.addConstr(self.betas[(l,k)]*f[(l,t)] <= self.alphas[(l,k)]*k.cap -self.alphas[(l,k)]*x[(k,t)] )
		"""
			Temporal logic specification goes here
			If there exists a red/red combination in [0,T-1]
			assign red=0, green=1
			assign first link:l , second link: k
			two links are antagonistic : u[l]+u[k] <=1
			that means sum_0:T-1(u[l])+sum(u[k]) <= T-1
			at least there
		"""
		for k in self.links:
			for l in self.links:
				if (l,k) in self.antagonistics:
					sum=LinExpr()
					for t in range(0,T+h):
						sum.add(u[l,t],1)
						sum.add(u[k,t],1)
					model.addConstr(sum <= T-1)	   
		# obligations:"
		for l in self.links:
			if not l.type=="sink":
				model.addConstr(l.x==x[(l,clock)]) # current condition assignment
				model.addConstr(x[(l,T)]<=X_contract[l,T]) # terminal assignment
				for t in range(0,clock):
					if l.type=="road":
						model.addConstr(u[(l,t)]==U_history[l,t]) # history of controls
			if l.type=="sink":
				for t in range(clock,T):
					model.addConstr(y[(l,t)]<=Output_Contract[l,t]) # outputs less than contract
		# End of obligations
		model.optimize()
		state={}
		control={}
		output={}
		for t in range(clock,T+h):
			for l in self.links:
				state[(l,t)]=x[(l,t)].X
				if l.type=="road":
					control[(l,t)]=(u[(l,t)].X)
				elif l.type=="freeway":
					control[(l,t)]=1
				elif l.type=="on-ramp":
					control[(l,t)]=u[(l,t)].X
				if l.type=="sink":
					output[(l,t)]=(y[(l,t)].X)
		for l in self.links:
			if l.type!="sink":
				l.u=control[l,clock]
			  