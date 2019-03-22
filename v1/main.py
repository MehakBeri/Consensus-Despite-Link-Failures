from queue import Queue
from message import Message
from process import Process
import threading
import time
import sys
import json

def launch_master_thread(n, ids, root, conn_matrix):
    global id_process, id_label
    i=0
    for p_id in ids:
        id_label[p_id] = i
        i += 1
    i=0
    index_to_id = {}
    for p_id in ids:
        index_to_id[i] = p_id
        i += 1
    print(f'In master thread. Launching {n} threads..')
    initial_config = {}
    q = [] #list of communication channels
    for i in range(n):
        q.append(Queue()) #append comm channel for each process
    q.append(Queue()) # last comm channel to communicate with master
    for pid in ids:
        initial_config[int(pid)] = {'parent': None,
                                    'children':[],
                                    'marked':False,
                                    'sent':[],
                                    'r':0,
                                    'my_index':id_label[int(pid)], #to know which queue belongs to me from the array q
                                    }
    initial_config['comm']=q
    threadLock = threading.Lock()
    r=1
    cleanup = False
    while True:
        print(f'********** master broadcast {r} ***********')
        if r==1:
            config = initial_config
            latest_q = q[-1]
            print(f'|| BFS LEVEL: {root}')
        r = r+1
        id_process = launch_threads(ids, conn_matrix, root, config)
        config={}
        done_threads=[]
        while True: #wait for all threads to complete one round after the first broadcast
            if len(done_threads) == len(id_process):
                break
            tmp=None
            threadLock.acquire()
            if latest_q.qsize()!=0:
                tmp = latest_q.get()
            threadLock.release()
            if tmp==None:
                continue
            else:    #if tmp.receiverID == 'Master':
                config[tmp.senderID] = tmp.msg_type['done_msg'] 
                config['comm'] = tmp.msg_type['comm']
                latest_q = tmp.msg_type['comm'][-1]
                done_threads.append(tmp.senderID)
        for v in id_process.values():
            v.join()
        # check termination
        visited = []
        for key in config.keys():
            if key!="comm":
                if config[key]['marked']==True:
                    visited.append(key)
        if len(visited)==n:
            if not cleanup:
                cleanup=True
            else:
                break
    print('**********************************************')
    for c in config:
        if c!="comm":
            print(f'{c} : Parent: {index_to_id[config[c]["parent"]]} Children: {config[c]["children"]} Marked: {config[c]["marked"]}')
    print('exiting master thread. bye!')

def launch_threads(ids, conn_matrix, root, config):
    for p_id, conn in zip(ids, conn_matrix):
        process = Process(int(p_id), root, conn, config)
        id_process[p_id] = process  
    for v in id_process.values():
            v.start()
    return id_process

if __name__=="__main__":
    with open("input.dat","r") as dat_file:
        data = dat_file.readlines()
    n = int(data[0])
    root = int(data[2])
    ids = data[1].strip()[1:-1].split(",")
    for i in range(len(ids)): ids[i] = int(ids[i])
    matrix_rows = data[3][2:-3].split("],[")
    connectivity_matrix = []
    for row in matrix_rows:
        connectivity_matrix.append(row.split(","))
    for row in range(len(connectivity_matrix)):
        for j in range(len(connectivity_matrix)):
            connectivity_matrix[row][j] = int(connectivity_matrix[row][j])
    id_process = {}
    id_label = {} 
    master_thread = threading.Thread(name='master',target=launch_master_thread, args=(n, ids, root, connectivity_matrix))
    master_thread.start()    



