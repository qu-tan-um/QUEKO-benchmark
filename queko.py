import networkx as nx
from networkx.algorithms.matching import maximal_matching
import random
import math
import csv


class queko_cycle:
    def __init__(self):
        self.list_1qbg = list()
        self.list_2qbg = list()
        self.taken_nodes = list()
        self.critical_nodes = list()

    def add_1qbg(self, tmp_1qbg, critical=False):
        self.list_1qbg.append(tmp_1qbg)
        self.taken_nodes.append(tmp_1qbg)
        if critical:
            self.critical_nodes.append(tmp_1qbg)

    def add_2qbg(self, tmp_2qbg, critical=False):
        self.list_2qbg.append(tmp_2qbg)
        self.taken_nodes.append(tmp_2qbg[0])
        self.taken_nodes.append(tmp_2qbg[1])
        if critical:
            self.critical_nodes.append(tmp_2qbg[0])
            self.critical_nodes.append(tmp_2qbg[1])

    def can_put_1qbg(self, tmp_1qbg):
        if tmp_1qbg in self.taken_nodes:
            return False
        return True

    def can_put_2qbg(self, tmp_2qbg):
        if (tmp_2qbg[0] in self.taken_nodes) or (tmp_2qbg[1] in self.taken_nodes):
            return False
        return True


class queko:
    def __init__(self,
                 connection_list: list,
                 depth: int,
                 gate_dist_vec: tuple,
                 name: str = None,
                 partial_nodes: list = None):

        # internalizing initial parameters
        self.connection_list = connection_list
        self.device_layout = nx.Graph()
        self.device_layout.add_edges_from(self.connection_list)
        self.depth = depth
        self.gate_dist_vec = gate_dist_vec
        self.name = "queko_depth{}_gate{}".format(depth, gate_dist_vec)
        if name:
            self.name = name

        # if we only want a subgraph, say we want to test a circuit which
        # absolutely has fewer qubits than the device
        if partial_nodes:
            self.device_layout = self.device_layout.subgraph(partial_nodes)
        """
        nx.draw(self.device_layout)
        plt.suptitle("input device layout")
        plt.show()
        """
        self.nodes = list(self.device_layout.nodes())
        self.edges = list(self.device_layout.edges())
        self.count_node = len(self.nodes)
        self.count_edge = len(self.edges)

        # compute how many 1qbg and 2qbg required
        self.count_1qbg = math.ceil(gate_dist_vec[0] * self.count_node * self.depth)
        self.count_2qbg = math.ceil(gate_dist_vec[1] * self.count_node * self.depth / 2)

        # sanity check for initial parameters
        if self.depth <= 0:
            raise ValueError("Depth must be positive integer.")
        if self.count_1qbg + self.count_2qbg < self.depth:
            raise ValueError("Quantum gates are too few. At least one for each cycle.")
        if self.count_1qbg + 2 * self.count_2qbg > self.depth * self.count_node:
            raise ValueError("Gate density is too high.")

        # generate the critical path
        self.cycles = list()
        self.count_1qbg_now = 0
        self.count_2qbg_now = 0
        self.generate_critical_path()

        self.sprinkle_2qbg()
        self.sprinkle_1qbg()

        self.nodes_test = list()
        self.nodes_to_test = dict()
        self.cycles_test = list()
        self.nodes_to_original = dict()
        self.shuffle_nodes()


    def generate_critical_path(self):
        # how many 1qbgs and 2qbgs we have inserted when generating the critical path
        count_1qbg = 0
        count_2qbg = 0

        for n_cycle in range(self.depth):
            cycle = queko_cycle()

            # randomly pick 1qbg or 2qbg to extend the critical path
            gate_type = random.randrange(2)
            gate_type += 1

            # if used up one kind of gate, switch to the other kind
            # at least one of them has leftovers because of previous checks
            if count_1qbg == self.count_1qbg:
                gate_type = 2
            if count_2qbg == self.count_2qbg:
                gate_type = 1
            

            # get the critical path from last cycle
            if n_cycle == 0:
                last_critical_nodes = self.nodes
            else:
                last_critical_nodes = self.cycles[n_cycle - 1].critical_nodes

            # randomly pick a node on the critical path to extend the critical path
            critical_node = random.choice(last_critical_nodes)
            if gate_type == 1:
                cycle.add_1qbg(critical_node, critical=True)
                count_1qbg += 1
            else:
                candidate_edges = [edge for edge in self.edges
                                   if (edge[0] == critical_node) or (edge[1] == critical_node)]
                edge = random.choice(candidate_edges)
                cycle.add_2qbg(edge, critical=True)
                count_2qbg += 1

            self.cycles.append(cycle)

        self.count_1qbg_now = count_1qbg
        self.count_2qbg_now = count_2qbg

    def sprinkle_1qbg(self):
        # check if there are enough nodes left 
        num_avail_nodes = 0
        for cycle in self.cycles:
            for node in self.nodes:
                if node in cycle.taken_nodes:
                    continue
                num_avail_nodes += 1
        
        if num_avail_nodes < self.count_1qbg - self.count_1qbg_now:
            raise ValueError("Failed to sprinkle 1-qubit gates, might have asked for too many.")

        # sprinkle the rest of 1qbg on the ciruit
        while self.count_1qbg_now < self.count_1qbg:
            # randomly choose a cycle and a 1qbg, check if it is available
            cycle = random.choice(self.cycles)
            tmp_1qbg = random.choice(self.nodes)
            if cycle.can_put_1qbg(tmp_1qbg):
                cycle.add_1qbg(tmp_1qbg)
                self.count_1qbg_now += 1

    def sprinkle_2qbg(self):
        # check if there are enough edges left 
        num_avail_edges = 0
        for cycle in self.cycles:
            temp_graph = nx.Graph(self.device_layout)
            temp_graph.remove_nodes_from(cycle.taken_nodes)
            max_match = maximal_matching(temp_graph)
            num_avail_edges += len(max_match)

        if num_avail_edges < self.count_2qbg - self.count_2qbg_now:
            raise ValueError("Failed to sprinkle 2-qubit gates, might have asked for too many.")

        # random pick edges and cycle to put 2qbg
        while self.count_2qbg_now < self.count_2qbg:
            cycle = random.choice(self.cycles)
            tmp_2qbg = random.choice(self.edges)
            if cycle.can_put_2qbg(tmp_2qbg):
                cycle.add_2qbg(tmp_2qbg)
                self.count_2qbg_now += 1

    def shuffle_nodes(self):
        shuffled_index = list(range(self.count_node))
        random.shuffle(shuffled_index)
        self.nodes_to_test = dict()
        for i in range(self.count_node):
            # nodes_to_test(original index) = shuffled
            self.nodes_to_test[i] = shuffled_index[i]
            # nodes_to_original(shuffled_index) = original_index
            self.nodes_to_original[shuffled_index[i]] = i
        # print(self.nodes_to_test)
        # print(self.nodes_to_original)

        for cycle in self.cycles:
            cycle_test = queko_cycle()
            for tmp_1qbg in cycle.list_1qbg:
                cycle_test.add_1qbg(self.nodes_to_test[tmp_1qbg])
            for tmp_2qbg in cycle.list_2qbg:
                cycle_test.add_2qbg((self.nodes_to_test[tmp_2qbg[0]], self.nodes_to_test[tmp_2qbg[1]]))
            self.cycles_test.append(cycle_test)

    def output_cycles_file(self):
        with open(self.name + ".csv", 'w') as csvFile:
            writer = csv.writer(csvFile)
            for cycle in self.cycles_test:
                # print(cycle.list_1qbg)
                # print(cycle.list_2qbg)
                writer.writerow(cycle.list_1qbg + cycle.list_2qbg)
        csvFile.close()

        with open(self.name + "_solution.csv", 'w') as csvFile:
            writer = csv.writer(csvFile)
            for node_test in range(self.count_node):
                writer.writerow([self.nodes_to_original[node_test]])
        csvFile.close()

    def output_queko(self):
        optimal_mapping = [self.nodes_to_original[i] for i in range(self.count_node)]
        queko_cycles = list()
        for cycle in self.cycles_test:
            this_cycle = list()
            for i in cycle.list_1qbg:
                this_cycle.append((i,))
            this_cycle += cycle.list_2qbg
            queko_cycles.append(this_cycle)
        return [optimal_mapping, queko_cycles]


