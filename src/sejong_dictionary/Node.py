from copy import deepcopy

class Node:
    def __init__(self, datum = None, node_name = '', 
                    meta_info = {}, **kargs):
        """Wrapper class for arbitary datum. (ver 07852ff7)
        
        Class Node serves as basic building block for all classes as a wrapper class for arbitary data. meta_info and kargs are for arbitary metadata, and meta_info attribute is for backward compatibility. 
        
        Args:
            datum: containing data
            node_name: for debugging. 
            meta_info, **kargs: Additional metadata. 
            
        Attributes: Identical to Args
            
        Versions:
            ver 07852ff7 (2019/08/30)
                Organize comments, basic test conducted. Also unecessary commented codes are removed
        """        
        self.datum = datum 
        self.node_name = node_name
        self.meta_info = meta_info
        
        
    def __str__(self):
        end = ''
        if self.check('foot'):
            end = '*'
        elif self.check('downarrow'):
            end = '↓'
        
        if self.node_name == '':
            return 'Node ' + str(self.datum) + end
        else:
            return 'Node ' + self.node_name + ' containing ' + str(self.datum) + end
        
    def modify(self, new):
        self.datum = new
        
    def __eq__(self, other):
        #print(self, other)
        if isinstance(other, self.__class__):
            try:
                if self.datum[:4] == 'root' and other.datum[:4] == 'root':
                    #print('root')
                    return True
                else:   
                    return self.datum == other.datum \
                    and self.node_name == other.node_name \
                    and self.meta_info == other.meta_info
            except:
                
                
                #print(self, other)
                #print(self.datum == other.datum \
                #    and self.node_name == other.node_name \
                #    and self.meta_info == other.meta_info)
                return self.datum == other.datum \
                    and self.node_name == other.node_name \
                    and self.meta_info == other.meta_info
        return NotImplemented
            
        
    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented     
    
    def __hash__(self):
        return hash(self.datum)
    
        
    def label_node(self, info_category, info_datum):
        '''
        For labeling node with specific information. 
        info_category should contain hash method.  
        '''
        self.meta_info[info_category] = info_datum
    
    def clone(self):
        return Node(deepcopy(self.datum), 
                    node_name = deepcopy(self.node_name), 
                    meta_info = deepcopy(self.meta_info))
        
    def check(self, category, datum=True, weak=False, chk_func=None):
        if chk_func:
            try:
                return category in self.meta_info.keys() and chk_func(self.meta_info[category])
            except TypeError:
                assert False
        elif weak:
            assert datum is True
            return category in self.meta_info.keys() and self.meta_info[category] is not None
        else:
            return category in self.meta_info.keys() and self.meta_info[category]==datum
    
    def get_info(self, category):
        assert self.check(category, weak = True)
        
        return self.meta_info[category]
        
    def contain_symbol(self):
        return self.check('fb_t', chk_func = lambda x:x.is_symbol) or\
               self.check('fb_b', chk_func = lambda x:x.is_symbol)
               
if __name__ == '__main__':
    n = Node('1212')
    m = Node(123)
    print(dir(n))
    print(n.startswith('1'))
