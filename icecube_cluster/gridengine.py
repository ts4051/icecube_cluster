'''
Tools for supporting DESY Zeuthen's Gridengine cluster system.
'''

import os, collections
from math import floor
from shutil import copy2


#
# Globals
#

GRIDENGINE_SUBMIT_EXE = "qsub"
GRIDENGINE_SCRIPT_DIRECTIVE = "#$"

#
# Submission
#

#Create a Gridengine submit file
def create_gridengine_submit_file(
    job_dir,
    job_name,
    exe_commands,
    memory,
    wall_time_hours=None, # total runtime in hours (use 0.49 to get in 30 min queue)
    tmpdir_size=500, # size of node scratch directory in MB
    working_dir=None,
    partition=None,
    use_gpu=False,
    use_array=True,
    num_cpus=None,
    out_dir=None,
    export_env=False,
) :
    assert isinstance(exe_commands,collections.abc.Sequence), "`exe_commands` must be a list or similar"
    num_exe_commands = len(exe_commands)
    if num_exe_commands == 0 :
        raise Exception( "No executable commands provided, cannot created SLURM submit file" )
    
    if wall_time_hours is None:
        wall_time_hours = 23.99
    #Check output dir exists
    job_dir = os.path.expandvars(os.path.expanduser(job_dir))
    job_dir = os.path.abspath(job_dir)
    if not os.path.isdir(job_dir) :
        raise Exception( "Cannot create GRIDENGINE file, output directory \"%s\" does not exist" % job_dir )
    if out_dir is None:
        output_dir_stem = job_dir
    else:
        output_dir_stem = out_dir
    script_directive = GRIDENGINE_SCRIPT_DIRECTIVE

    # Write the submit file

    #Define a name for the submit file we are about to generate
    submit_file_path = os.path.join(job_dir, job_name + ".sh")
    print(submit_file_path)
    #Make file
    with open(submit_file_path, "w") as submit_file :
        #Use zsh
        submit_file.write("#!/bin/zsh\n")
        #Write a header
        submit_file.write("# Autogenerated using fridge/utils/cluster/gridengine.create_gridengine_submit_file\n")
        submit_file.write("\n")
        minutes = wall_time_hours*60. % 60
        seconds = minutes*60. % 60
        hours = floor(wall_time_hours)
        minutes = floor(minutes)
        seconds = floor(seconds)
        submit_file.write(script_directive+" -l h_cpu=%d:%d:%d\n" % (hours, minutes, seconds))
        submit_file.write(script_directive+" -l h_rss=%dM\n" % memory)
        submit_file.write(script_directive+" -l tmpdir_size=%dM\n" % tmpdir_size)
        submit_file.write(script_directive+" -m a\n") # send an email on abort
        if num_cpus is not None and num_cpus > 1:
            submit_file.write(script_directive+" -pe multicore %d\n" % num_cpus)
        if job_name is not None:
            submit_file.write(script_directive+" -N %s\n" % job_name) # by default this would be the script name
        if partition is not None:
            submit_file.write(script_directive+" -P %s\n" % partition)
        # Define paths for log files
        # Format depends on whether this with be run as a single job or as part of a job array
        output_file_stem = "job_" + ("$TASK_ID" if use_array else "$JOB_ID")
        log_file_stem = os.path.join(output_dir_stem, output_file_stem)
        out_file = os.path.join(log_file_stem, output_file_stem+".out")
        submit_file.write("%s -o %s\n" % (script_directive, out_file))
        err_file = os.path.join(log_file_stem, output_file_stem+".err")
        submit_file.write("%s -e %s\n" % (script_directive, err_file))
        if use_gpu:
            submit_file.write("%s -l gpu\n" % script_directive)
        if export_env:
            submit_file.write("%s -V\n" % script_directive)
        submit_file.write("\n")

        #
        # Launch processes
        #

        #Report a few basic details
        submit_file.write("echo 'Running on host' $HOSTNAME 'at' `date`\n")
        if use_array :
            submit_file.write("echo 'SGE array index :' $SGE_TASK_ID\n")
        submit_file.write("echo ""\n")
        submit_file.write("\n")

        # Change to the working dir
        if working_dir is not None :
            submit_file.write("mkdir -p  %s\n" % working_dir)
            submit_file.write("cd  %s\n" % working_dir )
            submit_file.write("echo 'Changed working directory :' $PWD\n")
            submit_file.write("echo ""\n")
            submit_file.write("\n")

        # Loop over jobs provided and add a line to run it
        submit_file.write("echo 'Running %i commands'\n" % len(exe_commands))
        for i_cmd, exe_cmd in enumerate(exe_commands):
            submit_file.write( "%s\n" % (exe_cmd))
        submit_file.write("echo ""\n")
        submit_file.write("\n")
    print(("GRIDENGINE submit file written : %s" % (submit_file_path)))
    return submit_file_path

# TEST
if __name__ == "__main__" :

    from utils.filesys_tools import make_dir

    test_dir = "./tmp/gridengine"
    make_dir(test_dir)

    exe_commands = [
        "echo 'bar'",
        "echo 'bar'",
    ]

    submit_file_path = create_gridengine_submit_file(
        job_dir=test_dir,
        job_name="test",
        exe_commands=exe_commands,
        memory=1000,
        wall_time_hours=1.0,
        use_array=True,
    )