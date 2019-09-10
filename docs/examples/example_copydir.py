import os
from shutil import copyfile

def create_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)

def copy_directory(src, dest):
    """Copy directory in src to dest directory.
    """
    create_dir(dest)
    
    for elem in os.listdir(src):

        src_path = os.path.join(src, elem)
        dest_path = os.path.join(dest, elem)

        if os.path.isdir(src_path):
            copy_directory(os.path.join(src, elem),
                           os.path.join(dest, elem), 
                           folder_only = folder_only)

        elif not folder_only:
            copyfile(os.path.join(src, elem),
                     os.path.join(dest, elem),)

copy_directory('docs', 'newdoc_folder')


