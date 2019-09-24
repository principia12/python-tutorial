#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Download, unzip, and process raw data into usable format. 

Raw data is from https://ithub.korean.go.kr/user/total/database/electronicDicView.do
"""

import requests
import zipfile
import multiprocessing as mp 
import os 

from pathlib import Path

from time import time 

#-----------------------------------------------
# download raw data from google drive 
# code from https://stackoverflow.com/questions/38511444/python-download-files-from-google-drive-using-url 
#-----------------------------------------------

def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb+") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                
#--------------------------
# Unzip file 
#--------------------------


def create_dir(directory):    
    """Create directory if not exists. 
    
    This function can cause race conditions. 
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        
def explorer(root_dir):
    
    for elem in os.listdir(root_dir):
        p = os.path.join(root_dir, elem)
        if os.path.isdir(p):
            yield from explorer(p)
        yield p, elem
        
def unzip_file(path_to_zip, path_to_unzip):
    create_dir(path_to_unzip)
    
    with zipfile.ZipFile(path_to_zip, 'r') as f:
        f.extractall(path_to_unzip)
        
    print('%d finished unzipping %s'%(os.getpid(), path_to_zip.encode('cp437').decode('cp949')))
    for f_path, f_name in explorer(path_to_unzip):
        # continue
        try:
            os.rename(f_path, os.sep.join(f_path.split(os.sep)[:-1]) + os.sep + f_name.encode('cp437').decode('cp949'))
        except UnicodeEncodeError:
            print(f_name)
            # import traceback
            # traceback.print_exc()
            pass 
        except FileNotFoundError:
            print(f_name)
            print(12321)
            pass 
        # print('processed %s'%os.sep.join(f_path.split(os.sep)[:-1]) + os.sep + f_name.encode('cp437').decode('utf-8'))
    print('%d finished renaming %s'%(os.getpid(), path_to_zip.encode('cp437').decode('cp949')))
    
def install_kordic(d_path = '.', inspect = True):
    """Install 국립국어원 전자사전 in the specified directory accordingly.
    
    The raw data is downloaded from Google Drive of Seungwoo Schin (principia2718@gmail.com). It will download, unzip, and organize files accordingly. Tested on windows 10. 
    
    The expected directory structure is illustrated below;
    
    d_path 
        용언
            - subdirectories differ from pos to pos. 
        체언
        ... 
    """
    if inspect:
        begin = time()
        
    create_dir(d_path)
    
    
    file_id = '1Sz7wf3Zx_VS9h_gsxXwM9UNljbfMc5b-'
    
    dest = os.path.join(d_path, 'handic.zip')
    dict_path = dest.strip('.zip')
    
    if not os.path.exists(dest):
        download_file_from_google_drive(file_id, dest)
        zipfile.ZipFile(dest, 'r').extractall(dict_path)
    
    todos = []
    for elem in os.listdir(dict_path):
        for f in os.listdir(os.path.join(dict_path, elem)):
            if f.endswith('.zip'):
                print(f)
                # print(f.strip('.zip').encode('cp437').hex())
                # print(f.strip('.zip').encode('cp437'))
                # assert False 
                todos.append([os.path.join(dict_path, elem, f), 
                              # os.path.join(d_path, f.strip('.zip').encode('cp437').decode('utf-8'))])
                              os.path.join(d_path, f.strip('.zip').encode('cp437').decode('cp949'))])
                            
                              
    for todo in todos:
        if todo[-1].endswith('_기초') and todo[-1] != '고유명사_기초':
            todos.remove(todo)
    
    for todo in todos:
        lst = todo[-1].split(os.sep)
        todo[-1] = os.sep.join(lst[:-1] + [lst[-1][:-3]])
            
    todos = [tuple(e) for e in todos]
    from pprint import pprint 
    pprint(todos)
    p = mp.Pool(mp.cpu_count()-1)
    p.starmap_async(unzip_file, todos).get()
    if inspect:
        end = time()
        print('Takes %f time for unzipping.'%round(end-begin, 2))
    
    remove_dir(dict_path)
    os.remove(dest)
    if inspect:
        end = time()
        print('Takes %f time for installing dict.'%round(end-begin, 2))
    

if __name__ == "__main__":
    DATA_DIR = '.'
    print(DATA_DIR)
    install_kordic(os.path.join(DATA_DIR, 'kordic'))
    
