# Copyright 2013 by Kamil Koziara. All rights reserved.               
# This code is part of the Biopython distribution and governed by its    
# license.  Please see the LICENSE file that should have been included   
# as part of this package.


from functools import total_ordering

class DiGraph(object):
    """
    Base class for directed graph representation.

    Nodes' labels can be any hashable objects.

    Examples
    --------

    >>> g = DiGraph()

    """
    
    _REACHABLE = "reachable"
    _IS_VISITED = "is_visited"
    
    def __init__(self, edges=None):
        """
        Initialize graph with edges.
    
        Parameters
        ----------
        data - list of edges in a graph.
        """
        
        self.has_cycle = False
        
        self.cycles = []
        
        self.nodes = {}
        if edges != None:
            for (u, v) in edges:
                self.add_edge(u, v)

    def add_edge(self, u, v, data = None):
        """
        Adds an edge u->v to the graph

        Parameters
        ----------
        u,v - nodes connected by the edge
        """
        if u not in self.nodes:
            self.add_node(u)
        if v not in self.nodes:
            self.add_node(v)
        
        u_node = self.nodes[u]
        v_node = self.nodes[v]
        v_node.pred.add(DiEdge(u_node, data))
        u_node.succ.add(DiEdge(v_node, data))
        
    def add_node(self, u, data = None):
        """
        Adds node to the graph

        Parameters
        ----------
        u - node to add
        data - node data
        """
        
        self.nodes[u] = DiNode(u, data)
        
    def node_exists(self, u):
        return u in self.nodes

    def update_node(self, u, data):
        """
        Updates node data

        Parameters
        ----------
        u - node to update
        data - node data
        """
        self.nodes[u].data = data


    def get_node(self, u):
        """
        Gets node from the graph

        Parameters
        ----------
        u - node id
        """
        return self.nodes[u]

    
    def _get_reachable(self, node):
        """
        Gets all nodes reachable from given node. Finds cycles along the way.

        Parameters
        ----------
        node - node which descendants we want to obtain.
        
        >>> g = DiGraph([(1,2), (2,3), (3,4), (3,5), (5,2), (5,6), (6,8), (6,7), (2,9), (9,2)])
        
        Get all nodes reachable from 2.
        
        >>> n1 = g.get_node(2)
        >>> g._get_reachable(n1)
        ([], set([2, 3, 4, 5, 6, 7, 8, 9]))
        >>> n2 = g.get_node(6)
        >>> g._get_reachable(n2)
        ([], set([8, 7]))
        
        Let's see cycles that we found:
        
        >>> g.cycles
        [[2, 9], [2, 5, 3]]
        
        """
        if DiGraph._REACHABLE in node.attr:
            return ([], node.attr[DiGraph._REACHABLE]) # generalnie trzeba wlozyc tutaj label od node'a ktory zaczyna cykl
        else:
            my_set = set()
            
            if DiGraph._IS_VISITED in node.attr:
                in_cycle = [node.label]
            else:
                node.attr[DiGraph._IS_VISITED] = None
                
                in_cycle = []
                for edge in node.succ:
                    up_cycle, up_set = self._get_reachable(edge.to_node)
                    if len(up_cycle) > 0:
                        if up_cycle[0] == node.label:
                            # we closed the cycle
                            self.cycles.append(up_cycle)
                        else:
                            up_cycle.append(node.label)
                            in_cycle = up_cycle
                        up_set |= my_set
                        my_set = up_set # we are binding sets of reachable nodes of every node in cycle
                    else:
                        my_set |= up_set
                    my_set.add(edge.to_node.label)
                node.attr[DiGraph._REACHABLE] = my_set
                node.attr.pop(DiGraph._IS_VISITED)
            return (in_cycle, my_set)

class DiEdge(object):
    """
    Class representing an edge in the graph.
    """
    
    def __init__(self, to_node, data):
        self.to_node = to_node
        self.data = data

    def __eq__(self, other):
        return self.to_node == other.to_node and self.data == other.data

    def __hash__(self):
        return hash((self.to_node, self.data))

    def __str__(self):
        return str(self.to_node) + "(" + str(self.data) + ")"

    def __repr__(self):
        return str(self.to_node) + "(" + str(self.data) + ")"
    
@total_ordering
class DiNode(object):
    """
    Class containing information about graph structure. Only used
    internally in DiGraph.

    Nodes with the same label are not distinguishable.
    
    >>> a = DiNode(1)
    >>> b = DiNode(1)
    >>> a >= b
    True
    >>> a
    DiNode(1)
    """

    def __init__(self, label, data = None):
        """
        Initialize node with data.

        Parameters
        ----------
        label - node label
        data - internal node data
        """
        self.label = label
        self.data = data
        self.pred = set()
        self.succ = set()
        self.attr = {}

    def __lt__(self, other):
        return self.label< other.label

    def __eq__(self, other):
        return self.label == other.label

    def __hash__(self):
        return hash(self.label)

    def __str__(self):
        return "Node: " + str(self.label)

    def __repr__(self):
        return "DiNode(" + repr(self.label)+ ")"

if __name__ == "__main__":
    from Bio._utils import run_doctest
    run_doctest()
