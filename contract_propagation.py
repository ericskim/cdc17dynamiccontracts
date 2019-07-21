from topology import *

import pdb


def get_net_from_link(l):
	if 'off-ramp' in l.name.split():
		return 4
	if 'on-ramp' in l.name.split():
		return 4		
	else:
		return int(l.name.split()[1])


class network_guarantee_miner(object):
	"""
	Given:
		A set of networks
		An interconnection function relating states of some networks to demand inputs of adjacent networks

	Compute:
		A set of assume-guarantee pairs for each network

	How:

	"""


	def __init__(self, networks, prop_dem, connections, grouped_connections, iter_depth = 30, start_net = 1, T = 6): 
		self.networks = networks
		self.prop_dem = prop_dem
		self.iter_depth = iter_depth
		self.start_net = start_net
		self.connections = connections
		self.grouped_connections = grouped_connections
		self.T = T
		self.num_nets = len(self.networks)
		# Dict of lists with key = network index. Values vary
		self.AGpairs = dict([(n, []) for n in range(1,1+self.num_nets)]) # list of AG tuples
		self.unmined_demand_assums = dict([(n, {}) for n in range(1,1+self.num_nets)]) # dict key input (link,t) value link demand at time t
		self.unmined_init_states = dict([(n, {}) for n in range(1,1+self.num_nets)]) # dict key link value initial states
		self.unmined_exog_demand = dict([(n, {}) for n in range(1,1+self.num_nets)]) # dict key (link,t) value link exog demand at time t

		# Keeps track of which things were reduced
		self.reduced_demand_assums = dict([(n, {}) for n in range(1,1+self.num_nets)]) # dict of assumptions along each input link
		self.reduced_init_states   = dict([(n, {}) for n in range(1,1+self.num_nets)]) # dict of initial states along each internal link
		self.reduced_exog_demand   = dict([(n, {}) for n in range(1,1+self.num_nets)]) # dict of assumptions along each exog input link

		self.failures = dict([(n, []) for n in range(1,1+self.num_nets)])


	def mine(self):

		"""
		Mines and puts AG contract parameters into self.AGpairs

		Initializes each input and state to be unreasonable high and induce an error
		Hash table used to mark that an initial state or demand has been lessened until a guarantee is feasible
		Once a initial state or demand has been shrinked, it's been marked as altered and cannot be altered again

		"""

		# Initialize inter-network demands to 1.5 times the flow
		for c in self.connections:
			connection_link = c[1]
			i_n = get_net_from_link(connection_link)
			self.reduced_demand_assums[i_n][connection_link] = False
			for t in range(0,0+self.T):
				self.unmined_demand_assums[i_n][connection_link,t] = 1.5 * connection_link.qbar

		# Initialize initial states and exogenous demands to be benign
		for i_n in range(1, 1+ len(self.networks)):

			connection_input_links = [l[1] for l in self.connections if get_net_from_link(l[1]) == i_n]
			for l in self.networks[i_n].links:

				self.unmined_init_states[i_n][l] = l.cap 
				self.reduced_init_states[i_n][l] = False
				# If input link and there is no upstream link from a diff network, then assign an exogenous demand
				if len(l.up) == 0 and l not in connection_input_links: 
					self.reduced_exog_demand[i_n][l] = False
					for t in range(0,0+self.T):
						self.unmined_exog_demand[i_n][l,t] = .25 * l.qbar

		# Mining procedure, finally!
		for i in range(self.iter_depth):

			# Mine for each network
			for j in range(1, 1+ len(self.networks)):

				# Pick network to be mined, with appropriate offset self.start_net
				net_index = ((j + self.start_net -2) % self.num_nets) + 1 # self.network is 1 indexed 
				n = self.networks[net_index]
				connection_input_links = [l[1] for l in self.connections if get_net_from_link(l[1]) == net_index]

				# Mine 
				failures = 0 
				while(True):
					X = {}
					D = {}
					external_demand = {}
					D_combined = {}

					# Set up inter-network demands coming into net_index-th net
					for c in self.connections:
						connection_link = c[1]
						i_n = get_net_from_link(connection_link)
						if i_n == net_index:
							for t in range(0,self.T):
								D[connection_link,t] = self.unmined_demand_assums[i_n][connection_link,t]

					# Set initial state and external demand
					for l in n.links:
						X[l] = self.unmined_init_states[net_index][l]
						if len(l.up) == 0 and l not in connection_input_links:
							for t in range(0,self.T):
								external_demand[l,t] = self.unmined_exog_demand[net_index][l,t]

					# Combine external and intra-network demands
					for l in n.links:
						for t in range(0,self.T):
							if (l,t) not in D_combined.keys():
								D_combined[(l,t)] = 0
							if (l,t) in external_demand:
								D_combined[(l,t)] += external_demand[(l,t)]
							if (l,t) in D:
								D_combined[(l,t)] += D[(l,t)]

					try:
						#gamma = 1000 # really loose internal guarantee 
						#state,control,output=n.mine(T,external_demand,X,Y,D,gamma,beta_0 = 1,beta_f = 1)
						print "mining", net_index
						# pdb.set_trace()
						state, control, output, cost = n.guarantee_miner(self.T, D_combined, X)

						break 

					except:
						failures += 1
						# Error handling code which decreases the assumption severity
						reduction_occured = False
						for c in self.connections:
							connection_link = c[1]
							i_n = get_net_from_link(connection_link)
							if (self.reduced_demand_assums[i_n][connection_link] == False) or True:
								reduction_occured = True
								for t in range(0,self.T):
									self.unmined_demand_assums[i_n][connection_link,t] *= .9

						for l in n.links:
							if (self.reduced_init_states[net_index][l] == False)  or True:
								self.unmined_init_states[net_index][l] *= .9
								reduction_occured = True
							if len(l.up) == 0 and l not in connection_input_links:
								if (self.reduced_exog_demand[net_index][l] == False) or True:
									reduction_occured = True
									for t in range(0,self.T):
										self.unmined_exog_demand[net_index][l,t] *= 1.0

						# Cannot reduce assumptions further. Exit mining procedure
						if reduction_occured == False:
							print "Termined on Iteration Cycle %i On Network %i" % (i, net_index)
							return

				self.failures[net_index].append(failures)
				# Append to mined AG pair to list
# 				self.AGpairs[net_index].append((X, D, state, output, cost))
				self.AGpairs[net_index].append((X, D, state, output, cost, control))
				print "cost is:",cost
				print "the length of AG.pairs of subnetwork",net_index,"is", len(self.AGpairs[net_index])

				# Successful. 
				# Copy state and output to assumptions for a different iteration
				# Record that assumptions can't be reduced further via the loop iteration.
				# Assumptions can only be changed via the mining procedure now

				# Compute demand for other networks.
				# output list of demands for each network. The "net_index"th element should be None
				for olink,t in output.keys():
					downstream_links = [l[1] for l in self.connections if str(l[0]) == str(olink)]
					for d in downstream_links:
						i_n = get_net_from_link(d)
						if t < self.T:
							self.unmined_demand_assums[i_n][d,t] = 0 # First need to initialize to zero
				for olink,t in output.keys():
					downstream_links = [l[1] for l in self.connections if str(l[0]) == str(olink)]
					for d in downstream_links:
						#pdb.set_trace()
						# This assumes that outputs only are to a single other link 
						i_n = get_net_from_link(d)
						if t < self.T:
							try:
								self.unmined_demand_assums[i_n][d,t] += output[olink,t] * 1.1 + .5
								self.reduced_demand_assums[i_n][d] = True
							except:
								pdb.set_trace()

				# Set initial state assumptions
				for l in n.links:
					self.unmined_init_states[net_index][l] = state[l,self.T] * 1.1 + .5
					self.reduced_init_states[net_index][l] = True

				# Exogenous demand cannot be reduced further 
				for l in n.links:
					if len(l.up) == 0 and l not in self.unmined_demand_assums[net_index].keys():
						self.reduced_exog_demand[net_index][l] = True

				# for c in self.connections:
				#	connection_link = c[0]
				#	i_n = get_net_from_link(connection_link)
				#	self.reduced_demand_assums[i_n][connection_link] = True

				# # Record that initial state and demand can't be reduced further
				# for i_n in range(1, 1+ len(self.networks)):
				#	for l in self.networks[i_n].links:
				#		self.reduced_init_states[i_n][l] = True
				#		if len(l.up) == 0 and l not in self.unmined_demand_assums[i_n].keys():
				#			self.reduced_exog_demand[i_n][l] = True

		
	def recurrent_feasibility(self):
		"""
		Takes a dict of AGpairs and determines if AG contracts are consistent

		Returns two items
		1) Recurrent feasibility constraint from a network to itself. 
			
		2) Guarantee => Adjacent network's assumptions			  
		Takes a dict of AGpairs and determines if AG contracts are recursively feasible
		"""

		f = lambda n: dict([(l, 0) for l in self.networks[n].links])
		self.recfeas_failures = dict([ (n, f(n)) for n in range(1,1+len(self.networks))])
		recfeas = dict([ (n, []) for n in range(1,1+len(self.networks))])

		# Recurrent feasibility
		for net_index in range(1,1+len(self.networks)):
			# Pick network to be mined, with appropriate offset self.start_net
			n = self.networks[net_index]
			n_contracts = len(self.AGpairs[net_index])
			for before_index in range(n_contracts):
				for after_index in range(n_contracts):
					X_0 = self.AGpairs[net_index][after_index][0]
					state_traj = self.AGpairs[net_index][before_index][2]

					# Detect violations to recurssive feasibility
					flag = True
					for l in n.links:
						if state_traj[l, self.T] > X_0[l]:
							flag = False
							self.recfeas_failures[net_index][l] += 1
							#print "RF violation", l, state_traj[l, self.T], X_0[l]
							break
					if flag:
						recfeas[net_index].append((before_index, after_index))

		return recfeas

	def contract_consistency(self):
		"""
		Takes a dict of AGpairs and determines if AG contracts are consistent
		Guarantee => Adjacent network's assumptions
		returns a set of bad contract pairs
		"""

		# Record on which input consistency failures most often occur
		self.consistency_failures = dict([(i[1],0.0) for i in self.connections])

		badcontracts = set([])
		# Inter-network Consistency 
		for a_index in self.networks.keys():
			in_links = {k[0] for k in self.AGpairs[a_index][0][1]} # set of input links
			for in_l in in_links:
				up_links = [i[0] for i in self.connections if i[1] == in_l]

				up_nets = [get_net_from_link(up_l) for up_l in up_links]
				if len(set(up_nets)) > 1:
					raise ValueError("Code assumes only one upstream network exists for each connection link")

				g_index = up_nets[0]
				# Iterate over contract pairs for this pair of networks
				for gc_index in range(len(self.AGpairs[g_index])):
					for ac_index in range(len(self.AGpairs[a_index])):

						# Check if symmetric scenario with AG pair reversed has been violated
						if (g_index, gc_index, a_index, ac_index) in badcontracts:
							continue

						# Check for input demand violation
						violation = False
						for t in range(self.T):
							# Add up demands across upstream links
							incoming = 0.0
							for up_l in up_links:
								incoming += self.AGpairs[g_index][gc_index][3][up_l,t]

							if incoming > self.AGpairs[a_index][ac_index][1][in_l,t]:
								violation = True
								self.consistency_failures[in_l] += 1
								break

						# A violation
						if violation:
							badcontracts.add((a_index, ac_index, g_index, gc_index))

		return badcontracts



