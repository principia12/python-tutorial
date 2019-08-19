import os 

# understanding os path 
print(os.getcwd()) # get current working directory 
print(os.sep)
print(os.chdir()) # change working directory 
print(os.getcwd()) # get current working directory 

print(os.path.isdir()) # check if the path is directory 
print(os.path.isfile()) # check if it is a file 


# list the files and path inside 

for file in os.listdir():
    print()
    
# create dir

def create_dir(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)
        
        

