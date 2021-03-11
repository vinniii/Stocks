'''
Script to automate cloud syncs
    1. takes source(on-prem) and target(cloud), and also gateway procman path
        i.      find leaf directory
        ii.     generated dry run sync commands(threaded)
        iii.    run and get file list
        iv.     stop gateway
        v.      run sync commands to the same files
        vi.     run dry run again, check if not files
        vii.    if no files start gateway 
    2. level of sync (may be in phase - 2)(default to leaf directory)
    3. level of soft link creation (may be in phase - 2)
'''
import logging
import argparse
import socket
import subprocess
import os
import sys
import getpass
import threading
import time
import queue

logging.basicConfig(level=logging.DEBUG)

def get_args():
    parser = argparse.ArgumentParser(description='cloud sync script')
    parser.add_argument('-source', '-s', dest='source', required=True, help='on prem data directory')
    parser.add_argument('-target', '-t', dest='target', required=True,  help='target cloud directory')
    parser.add_argument('-level', '-l', dest='level', type=int, default=1, help='source directory depth to generate sync commands')
    parser.add_argument('-user', '-u', dest='user', type=str, default=getpass.getuser(), help='user for rsync, default command runner')
    parser.add_argument('-thread_count', '-tc', dest='t_count', type=int, default=9, help='No of syncs per box')
    parser.add_argument('-hosts', '-ho', dest='m_list', nargs='+',  default=[socket.gethostname()], help='machines to run syncs')
    parser.add_argument('-gateway_proc_path', dest='gateway_path', help='procman path to stop before syncs')
    return parser.parse_args()

valid_boxes = ['unixdeva16', 'newsfhdeva02', 'newsfhstaga03', 'newsfhstagea04', 'newsfha06', 'newsfha05', 'newsfhb06', 'newsfhb05']

def check_dir(path):
    if os.path.isdir(path):
        return True
    return False

def check_box(args):
    for each_box in args.m_list:
        if each_box in valid_boxes:
            logging.info(each_box)
        else:
            logging.info(f"invalid {each_box}")
            args.m_list.remove(each_box)

def check_inputs(args):
    if check_dir(args.source) and check_dir(args.target):
        logging.info(f'valid {args.source}\nvalid {args.target}')
        if args.t_count > 8:
            logging.warning(f'thread_count should not be more than 8, setting to 8')
            args.t_count = 8
        check_box(args)
        if args.m_list:
            logging.info(f'list of boxes to use: {args.m_list}') 
            return True
        else:
            logging.error(f'No valid boxes to run')
    return False

def gen_commands(source, target, level):
    rsync_cmd = 'rsync -av --bwlimit=15000 --modify-window=1 {}/ {}'
    cmds = []
    #logging.info(level)
    if level:
        if isinstance(level, list):
            logging.info(f' level is list ')
            for e_level in level:
                cmds.append(rsync_cmd.format(
                    os.path.join(source, e_level),
                    os.path.join(target, e_level)
                ))
        elif isinstance(level, dict):
            for e_key in level.keys():
                for e_sub_level in level[e_key]:
                    cmds.append(rsync_cmd.format(
                        os.path.join(source, e_key, e_sub_level),
                        os.path.join(target, e_key, e_sub_level)
                    ))
        else:
            logging.warning(f'I do not know what you sent')
    return cmds

def generate_commands(source, target, level):
    logging.info(f'generates sync commands from leaf directory') 
    logging.info(f'directories along with files in same directory are not leaf dirs')
    level_1 = os.listdir(source)
    commands = []
    if level == 1:
        commands = gen_commands(source, target, level_1)
    elif level == 2:
        level_2 = {}
        if level_1:
            for e_l1 in level_1:
                sub_path = os.path.join(source, e_l1)
                l2 = os.listdir(sub_path)
                if l2:
                   level_2[e_l1] = l2
        commands = gen_commands(source, target, level_2)
    #logging.info(f'comamnds = {commands}')
    return commands

def run_dry_runs(commands, box, user, cmd_queue):
    logging.info(f'box = {box}, user = {user}')
    run_cmd = 'ssh {} sudo -u {} {}'
    count = 1
    box_count = len(box)
    fd = open('commands.txt', 'a')
    for e_cmd in commands:
        box_index = count%box_count
        ex_cmd = run_cmd.format(box[box_index], user, e_cmd)
        cmd_queue.put(ex_cmd)
        fd.write(f'{ex_cmd}\n')
        count += 1
    logging.info(f'commands generated {len(commands)}')
    fd.close()
        #data = subprocess.Popen(ex_cmd.split(), stdout = subprocess.PIPE)
        #logging.info(f'output : {data.communicate()}')

def exec_commands(thread_id):
    logging.info('starting executing')
    count = 0
    while not cmds_list.empty():
        cmd = cmds_list.get()
        logging.info(f'{thread_id}: exectuing {cmd}')
        data = subprocess.Popen(cmd.split(), stdout = subprocess.PIPE)
        logging.info(f'{thread_id}: output : {data.communicate()}\n')
        count += 1
        logging.info(f'{thread_id}: {count} commands executed')
        #with open('/home/user/pkudithi/share/cloud_migration/sync/exec_output.txt', 'wa') as fd:
        #    fd.write(f'output : {data.communicate()}\n')

class myThread (threading.Thread):
    def _init_(self, name):
        threading.Thread._init_(self)
        self.name = name

    def run(self):
        print ("Starting " + self.name)
        exec_commands(self.name)
        print ("Exiting " + self.name)

def main():
    '''
    generate dry run commands
        1. source path leaf directories
        2. sync command for all leaf dirs
    '''
    args = get_args()
    check_inputs(args)
    dry_commands = generate_commands(args.source, args.target, args.level)
    run_dry_runs(dry_commands, args.m_list, args.user, cmds_list)
    ''' threads creation'''
    threads= []
    for i in range(args.t_count * len(args.m_list)):
        threads.append(myThread(f'thread-{i}'))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    cmds_list.join()
    

if _name_ == "_main_":
    cmds_list = queue.Queue()
    main()