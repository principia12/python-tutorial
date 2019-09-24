import os 
import re 
import pickle 
import bs4 
from pprint import pprint 
from time import time 
from Tree import Tree 
from Node import Node 

kordic_path = r'C:\Users\principia12\Desktop\Work\sent2dl\data\kordic'

def file_explorer(root_dir, crit = lambda x:True):
    for f in os.listdir(root_dir):
        f_path = os.path.join(root_dir, f)
        if os.path.isdir(f_path):
            yield from file_explorer(f_path, crit = crit)
        else:
            if crit(f_path):
                yield f_path 
                
def find_word(word):
    for f in file_explorer(kordic_path, crit = lambda x:x.endswith('%s.xml'%word)):
        return f 
        
def create_dict():
    res = {}
    for f in file_explorer(kordic_path, crit = lambda x:x.endswith('.xml')):
        word = f.split(os.sep)[-1].strip('.xml')
        res[word] = f
    pickle.dump(res, open('kordic.pickle', 'wb+'))
    
def parse_lexicon(f):
    # soup = bs4.BeautifulSoup(open(f, 'r').read(), 'lxml')
    # for entry in soup.find_all('entry'):
        # for sense in entry.find_all('sense'):
            # for trans in sense.find_all('trans'):
                # print(trans.text)
            # for frame_grp in sense.find_all('frame_grp'):
                # print(frame_grp['type'])
                # for frame in frame_grp.find_all('frame'):
                    # print(frame.text)
            # for subsense in sense.find_all('subsense'):
                # for ex in subsense.find_all('eg'):
                    # print(ex.text)
    t = parse_xml_file(f)
    print(t)
    return t 
                    
def parse_xml_file(f):
    xml_content = open(f, 'r').read()
    # xml_content = re.sub(r'\s', '', xml_content)
    
    return Tree('document root', children = parse_xml(xml_content))
    
def parse_xml_tag(text):
    text = text.split()
    datum = None
    meta_info = {}
    for idx, elem in enumerate(text):
        
        if idx == 0:
            datum = elem 
        else:
            elem = elem.split('=')
            if len(elem) == 1:
                datum += ' %s'%elem[0]
            else:
                meta_info[elem[0]] = elem[1].strip('"')
    return Node(datum, meta_info = meta_info)
            
    
def parse_xml(xml_content):
    xml_content = xml_content.strip()
    if xml_content == '':
        return []
    elif not ('<' in xml_content and '>' in xml_content):
        return [Tree(xml_content)]
    # print('--------------')
    # print(xml_content[:100])
    assert xml_content[0] == '<', xml_content[:100]
    res = []
    idx = 0
    # for idx, char in xml_content:
    # while idx < len(xml_content):
    para = re.search('>', xml_content)
    if para is None:
        return Node(xml_content)
    else:
        idx = para.start()
        # print(idx, char)
    
        # print(xml_content[1:idx])
        node = parse_xml_tag(xml_content[1:idx].strip())
        # print(node)
        # print(node.datum)
        if node.datum[0] in ['?', '!'] or xml_content[idx-1] == '/':
            res.append(Tree(node))
            res.extend(parse_xml(xml_content[idx+1:]))
        else:
            m = re.search('</%s>'%node.datum, xml_content[idx:])
            # print(xml_content[idx:100])
            # print('</%s>'%node.datum)
            # print(m)
            end, new_start = m.start(), m.end()
            # print(end, new_start)
            # print(xml_content[idx+end:idx+new_start+1])
            # if xml_content[idx+1:end-1] != '':
            children = parse_xml(xml_content[idx+1:idx+end])
            res.append(Tree(node, children))
            # else:
                # res.append(Tree(node))
            res.extend(parse_xml(xml_content[idx+new_start+1:]))
    
    return res 
    
    
        
                
            
    
    
                    
                
                
if __name__ == '__main__':
    # print(list(os.listdir()))
    print(list(os.listdir(kordic_path)))
    # print(len(list(file_explorer(kordic_path, crit = lambda x:x.endswith('.xml')))))
    
    # begin = time()
    # print(find_word('가감하다'))
    # end = time()
    
    # print(end-begin) # takes 30s 
    
    # begin = time()
    # create_dict()
    # end = time()
    
    # print(end-begin) # takes 30s 
    
    begin = time()
    d = pickle.load(open('kordic.pickle', 'rb'))
    t = parse_lexicon(d['가다'])
    end = time()
    
    print(end-begin) # takes 30s 
    
    from code import interact 
    interact(local = locals())