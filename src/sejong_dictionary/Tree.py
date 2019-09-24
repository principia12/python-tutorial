from Node import Node

class Tree:
    def __init__(self, root_node = None, children = [], debug = False):
        """Tree Implementation in python. (ver 07852ff7)
            
        is_TAGTree need to be implemented to use TAG class 
            
        Versions:
            ver 07852ff7 (2019/08/30)
                Organize comments, basic test conducted. Also unecessary commented codes are removed
        """
        self.children = []
        
        if isinstance(root_node, Node):
            self.root_node = root_node.datum
            self.root = root_node
        else:
            self.root_node = root_node
            self.root = Node(root_node)
        
        self.parent = None 
        
        for child in children:
            if isinstance(child, Tree):
                self.children.append(child)
                child.parent = self 
            else:
                t = Tree(child, [])
                t.parent = None 
                self.children.append(Tree(child, []))
                
            
        self.meta_data = {}
        addr_dict = {}
        
        for addr, sub in Tree.iter_subtree_with_addr(self):
            addr_dict[tuple(addr)] = sub 
            
        self.addr_dict = addr_dict
        
    def iter_subtree_with_addr(self, bottom_up = True):
        if bottom_up:
            for idx, child in enumerate(self.children):
                yield from [([idx] + addr, sub) for addr, sub in child.iter_subtree_with_addr()]
            yield [], self
        else:
            yield [], self
            for idx, child in enumerate(self.children):
                yield from [([idx] + addr, sub) for addr, sub in child.iter_subtree_with_addr()]
        
    def copy(self):
        from copy import deepcopy
        
        return Tree(root_node = deepcopy(self.root_node), 
            children = [e.copy() for e in self.children], )
        
    def depth(self):
        
        if self.children == []:
            d = 1
        else:
            d = max([c.depth() for c in self.children]) + 1
        return d
        
    def code(self, delim = ';', mark = False):
        """Prefix notation with ; on the leaf. Only used for find_common_subtrees on util.py. 
        
        roots of trees are assumed to be lists of tags. 
        """
        if mark:
            res = [(self.root_node, mark)]
        else:
            res = [self.root_node]
        
        for child in self.children:
            res += child.code(delim = delim, mark = mark)
        res += [delim]
        
        return res 
        
    def __repr__(self):
        return str(hex(id(self)))[-4:]
    
    def mark(self, marking):
        """Enables arbitary markings on the tree. 
        """
        self.meta_data.update(marking)
        
    def __str__(self):
        res = str(self.root_node)
        
        for idx, elem in enumerate(self.children):
            res += '\n\t'
            res += str(elem).replace('\n', '\n\t')
            
        return res
        
    def __eq__(self, other):
        if isinstance(self, Tree) and isinstance(other, Tree):
            if self.root_node == other.root_node and \
                    len(self.children) == len(other.children):
                return all([Tree.__eq__(c,d) for c,d in zip(self.children, other.children)])
            else:
                return False
                
        else:   
            assert False, 'compared %s with %s'%(type(self), type(other))
            NotImplemented
            
    def __hash__(self):
        from util import recursive_hash
        res = [self.root_node]
        for child in self.children:
            res.append(child)
        return recursive_hash(res)
    
    def __ne__(self, other):
        return not Tree.__eq__(self, other)

    def __lt__(self, other): 
        """Return True if self is a subtree of other
        """
        from util import find_common_subsequence
        if isinstance(self, Tree) and isinstance(other, Tree):
            if Tree.__eq__(self, other):
                return False
            return Tree.__le__(self, other)
        else:
            NotImplemented

    def __le__(self, other, debug = False): 
        from util import find_common_subsequence
        
        if isinstance(self, Tree) and isinstance(other, Tree):
            if any([Tree.__le__(self, c) for c in other.children]):
                return True
            elif Tree.__eq__(self, other):
                return True
            elif self.root_node == other.root_node:
                for seq in find_common_subsequence(self.children, other.children, \
                        cmp_func = lambda x, y:x.root_node == y.root_node):
                    if all([Tree.__le__(self.children[i], other.children[j]) \
                                for i,j in seq]) and len(seq) == len(self.children):
                        return True
                return self.children == []
            
        else:
            NotImplemented

    def __gt__(self, other):
        if isinstance(self, Tree) and isinstance(other, Tree):
            return Tree.__lt__(other, self)
        else:
            NotImplemented

    def __ge__(self, other):
        if isinstance(self, Tree) and isinstance(other, Tree):
            return Tree.__le__(other, self)
        else:
            NotImplemented
            
    def __getitem__(self, indices):
        if isinstance(indices, tuple):
            return Tree.get_subtree_by_addr(self, indices)
        else:
            return self.children[indices]
        
    def get_children(self):
        return self.children
        
    def get_root_node(self):
        return self.root_node
        
    def apply_func(self, func = lambda x:x):
        self.root_node = func(self.root_node)
        for child in self.children:
            Tree.apply_func(child, func = func)
        
    def print_func(self, func=lambda x:str(x), delim = '- '):
        """Tree printing function with arbitary print function. 
        """
        res = func(self.root_node)
        
        for child in self.children:
            res += '\n' + delim
            res += Tree.print_func(child, func=func, delim = delim).replace('\n', '\n' + delim)
            
        return res

    def iter_subtree(self, bottom_up = False, internal = False, 
                            leaves = False, children_selection = lambda x:x):
        if leaves:
            if children_selection(self.children) == []:
                yield self
            else:
                for child in children_selection(self.children):
                    if isinstance(child, Tree):
                        yield from child.iter_subtree(leaves = True)
                    else:
                        print('Child is not a node')
                        assert False
        if bottom_up:
            if internal: # bottom-up, internal
                if children_selection(self.children) != []:
                    for child in children_selection(self.children):
                        if isinstance(child, Tree):
                            yield from child.iter_subtree(bottom_up = bottom_up, 
                                            internal = internal)
                        else:
                            print('Child is not a node')
                            assert False
                    yield self
            else: # bottom-up, all nodes
                for child in children_selection(self.children):
                    if isinstance(child, Tree):
                        yield from child.iter_subtree(bottom_up = bottom_up, 
                                        internal = internal)
                    else:
                        print('Child is not a node')
                        assert False
                yield self
        else:
            if internal: # top-down, internal
                if children_selection(self.children) != []:
                    yield self
                    for child in children_selection(self.children):
                        if isinstance(child, Tree):
                            yield from child.iter_subtree(bottom_up = bottom_up, 
                                            internal = internal)
                        else:
                            print('Child is not a node')
                            assert False
                    
            else: # top-down, all nodes
                yield self
                for child in children_selection(self.children):
                    if isinstance(child, Tree):
                        yield from child.iter_subtree(bottom_up = bottom_up, 
                                        internal = internal)
                    else:
                        print('Child is not a node')
                        assert False
                
    def leftmost(self, subtree = False, crit = lambda x : True):
        tmp = self
        
        while tmp.children != [] and crit(tmp):
            tmp = tmp.children[0]
        if subtree:
            return tmp 
        return tmp.root_node 
        
    def rightmost(self, subtree = False, crit = lambda x : True):
        tmp = self
        
        while tmp.children != [] and crit(tmp.children[-1]):
            tmp = tmp.children[-1]
        if subtree: 
            return tmp 
        return tmp.root_node
            
    def internal_nodes(self, bottom_up = False):
        if bottom_up:
            if self.children != []:
                for child in self.children:
                    if isinstance(child, Tree):
                        yield from child.internal_nodes()
                    else:
                        print('Child is not a node')
                        assert False
                yield self.root_node
        else:
            if self.children != []:
                yield self.root_node
                for child in self.children:
                    if isinstance(child, Tree):
                        yield from child.internal_nodes()
                    else:
                        print('Child is not a node')
                        assert False
        
    def leaves(self):
        if self.children == []:
            yield self.root_node
        else:
            # yield self.root_node
            for child in self.children:
                if isinstance(child, Tree):
                    yield from child.leaves()
                else:
                    print('Child is not a Tree')
                    assert False
    
    def nodes(self):
        yield from self.internal_nodes()
        yield from self.leaves()
    
    def get_subtree_by_addr(self, addr):
        return self.addr_dict[tuple(addr)]
        cur = self
        for add in addr:
            if add is None:
                return cur
            try:
                cur = cur.children[add]
            except IndexError:
                assert False, "Not a valid address."
            
        return cur
    
    def get_subtree_by_name(self, new_root):
        return Tree.get_subtree(self, new_root)
    
    def get_subtree(self, new_root):
        """Get subtree with given new_root as root. 
        
        Might need optimization, by saving all nodes, leaves, internal nodes 
        as class attributes. 
        """
        
        assert new_root in self.nodes(), \
            '%s not in tree'%(str(new_root))
        
        if self.root_node == new_root:
            return self
        else:
            for child in self.children:
                if new_root in child.nodes():
                    return child.get_subtree(new_root)
        print('sth wrong!')
        assert False # should not reach here
    
                
    def add_child(self, child):
        if isinstance(child, Tree):
            self.children.append(child)
            # self.nodes.extend(child.nodes())
            # self.leaves.extend(child.leaves())
            # self.internal_nodes.extend(child.internal_nodes)
        else:
            Tree.add_child(self, Tree(child))
    def to_dict(self):
        children = [ch.to_dict() for ch in self.children]
        root = str(self.root_node)
        return {root : children}
        
        
    def to_json(self):
        import json
        return json.dumps(self.to_dict())
        
    @staticmethod
    def distance(a, b, option='edit distance', **args):
        metric_dict = {\
            'edit distance' : Tree.edit_distance, 
            }
        
        return metric_dict[option](a,b,**args)
        
    @staticmethod
    def edit_distance(a, b, node_dist_func = lambda a,b : 0 if a==b else 1):
        try:
           import zss
           assert isinstance(a, Tree), a
           assert isinstance(b, Tree), b  
        
           return zss.simple_distance(a, b, \
               Tree.get_children, Tree.get_root_node, node_dist_func)
        except ModuleNotFoundError:
            return None
