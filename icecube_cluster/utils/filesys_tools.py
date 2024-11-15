'''
Tools for file system operations

Tom Stuttard
'''

import os, glob, datetime, stat, shutil

# py2 vs 3 compatibility
try:
    input = raw_input
except NameError:
    pass

    
#
# Tools for handling files and directories
#

#Create a directory with robust error handling, including race conditions
def make_dir(dir_path, raise_exception=False) :
    if not os.path.exists(dir_path) :
        try :
            os.makedirs(dir_path)
            return True
        except OSError : 
            assert os.path.isdir(dir_path), "Could not create directory \"%s\"" % (dir_path)
    return False


#Make a symbolic link, with error handling
def make_symlink(file_path, link_path) :
    if not os.path.exists(file_path) :
        raise Exception( "Could not create sym link : Source file \"%s\" does not exist" % file_path )
    else :
        if os.path.exists(link_path) :
            raise Exception( "Could not create sym link : File \"%s\" already exists" % link_path )
        else :
            os.symlink(file_path,link_path)


#Make a directory with the data/time as the name
TMP_FILE_STRFTIME = '%Y-%m-%d_%H-%M-%S'
def make_tmp_dir(parent_dir):
        dir_path = os.path.join( parent_dir , datetime.datetime.now().strftime(TMP_FILE_STRFTIME) )
        make_dir(dir_path)
        return dir_path


#Get parent directory of a file (or potential file)
def get_parent_dir(file_path) :
    #file_path = os.path.realpath(file_path)
    return os.path.abspath( os.path.dirname(file_path) )


#Get file stem
def get_file_stem(file_path, include_path=False) :
    tokens = os.path.splitext( file_path if include_path else os.path.basename(file_path) )
    if len(tokens) > 0 : 
        return tokens[0]
    else :
        raise Exception( "Could not extract stem from \"%s\"" % file_path )


def replace_file_ext(file_path, ext, include_path=False) :
    '''
    Replace the extension in the file path with the one provided
    '''
    new_file_path = get_file_stem(file_path, include_path=include_path)
    if not ext.startswith(".") :
        new_file_path += "."
    new_file_path += ext
    return new_file_path


#Check that the containing directory exists for a given file path
#Useful for checking before creating a new file that the directory actually exists
def check_parent_dir_exists(file_path) :
    dir_path = get_parent_dir(file_path)
    if os.path.isdir(dir_path) :
        return True
    else :
        return False

#Make file executable
def set_exectuable(file_path) :
    if os.path.exists(file_path) :
        os.chmod( file_path, os.stat(file_path).st_mode | stat.S_IEXEC )


#Check file is executable
def is_executable(file_path) :
    if os.path.exists(file_path) :
        return os.stat(file_path).st_mode & stat.S_IEXEC > 0


#Check file/dir is writable
#From https://stackoverflow.com/questions/2113427/determining-whether-a-directory-is-writeable
def is_writable(file_path) :
    if os.path.exists(file_path) :
        return os.access(file_path,os.W_OK)


#Get file size (bytes)
def get_file_size(file_path) :
    if os.path.exists(file_path) :
        return os.path.getsize(file_path)
    else :
        raise Exception( "File \"%s\" does not exist, cannot check file size" )


#Get nicely formatted units for file size (from http://stackoverflow.com/questions/2104080/how-to-check-file-size-in-python)
def format_num_bytes(numBytes) :
    for unit in ['[bytes]', '[kB]', '[MB]', '[GB]', '[TB]', '[PB]', '[EB]', '[ZB]', '[YB]', '[XB]' ] :
        if numBytes < 1024.0:
            return "%0.3g %s" % (numBytes, unit)
        numBytes /= 1024.0


#Get file last modified time as datetime
def get_file_mod_time(file_path) :
    if os.path.exists(file_path) :
        return datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
    else :
        raise Exception( "File \"%s\" does not exist, cannot get last modified time" )


#Get all subdirectories from a directory
def get_subdirs(dir_path) :
    if not os.path.isdir(dir_path) : 
        raise Exception( "Could not find directory \"%s\", cannot get subdirectories" % (dir_path) )
    return [ d for d in glob.glob( dir_path + "/*" ) if os.path.isdir(d) ]


#Get all files in a directory (NOT recursive)
def get_files_in_dir(dir_path) :
    if not os.path.isdir(dir_path) : 
        raise Exception( "Could not find directory \"%s\", cannot get files in directory" % (dir_path) )
    return [ d for d in glob.glob( dir_path + "/*" ) if not os.path.isdir(d) ]


#Test if file locking is supported by the file system / mounting options for a directory
def is_file_lock_possible(dir_path) :

    import fcntl, tempfile

    #Check directory to test exists
    if os.path.isdir(dir_path) :

        #Create a temporary file (auto-deleted)
        with tempfile.NamedTemporaryFile(mode='w+',dir=dir_path) as fd :

            #Try to lock the file
            #If successful, unlock and return True
            #Otherwise returns False
            try :
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(fd, fcntl.LOCK_UN)
                return True
            except e :
                return False

    else :
        raise Exception( "Cannot test locking in '%s', does not exist" % dir_path )

