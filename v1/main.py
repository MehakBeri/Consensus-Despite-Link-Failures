from queue import Queue
from message import Message
from process import Process
import threading
import time
import sys
import json

def launch_master_thread(n, r, x, input_val):
    process_ids = [i for i in range(n+1)] #0th process id for master
    print(f'In master thread. Launching {n} threads..')
    initial_config = {}
    q = [] #list of communication channels
    for i in range(n+1):
        q.append(Queue()) #append comm channel for each process
    for pid in process_ids:
        val_vector=[]
        level_vector = []
        for i in range(n):
            if i!=pid-1:
                val_vector.append(None)
                level_vector.append(-1)
            else:
                val_vector.append(input_val[pid-1])
                level_vector.append(0)
        initial_config[int(pid)] = {'decision': None,
                                    'key' : None,
                                    'value': val_vector,
                                    'level': level_vector,
                                    'r': 1,
                                    'total_rounds': r
                                    }
    initial_config['comm'] = q
    threadLock = threading.Lock()
    roundno = 1
    leader = 1 #each process knows that the leader is 1
    while roundno < r+1:
        print(f'********** Round {roundno} ***********')
        if roundno==1:
            config = initial_config
            latest_q = q[0]
        roundno = roundno + 1
        id_process = launch_threads(n, leader, x, config)
        config={}
        done_threads=[]
        while True: 
            if len(done_threads) == len(id_process):
                break
            tmp=None
            threadLock.acquire()
            if latest_q.qsize()!=0:
                tmp = latest_q.get()
            threadLock.release()
            if tmp==None:
                continue
            else:   
                config[tmp.senderID] = tmp.msg_type['done_msg'] 
                config['comm'] = tmp.msg_type['comm']
                latest_q = tmp.msg_type['comm'][0]
                done_threads.append(tmp.senderID)
        for v in id_process.values():
            v.join()
    print("********* SUMMARY ***********")
    for c in config:
        if c!="comm":
            print(f'ID: {c} | Decision: {config[c]["decision"]} | Level Vector: {config[c]["level"]} | Value Vector: {config[c]["value"]} | Key: {config[c]["key"]}')
    print('exiting master thread. bye!')

def launch_threads(n, leader, x, config):
    id_process = {}
    for p_id in range(n):
        process = Process(int(p_id+1), n, leader, x, config)
        id_process[p_id+1] = process  
    for v in id_process.values():
            v.start()
    return id_process

if __name__=="__main__":
    with open("input_basic.dat","r") as dat_file:
        data = dat_file.readlines()
    n = int(data[0]) #number of processes
    r = int(data[1]) #number of rounds
    x = int(data[2]) #xth msg lost
    input_val = data[3].strip()[1:-1].split(",")
    master_thread = threading.Thread(name='master',target=launch_master_thread, args=(n, r, x, input_val))
    master_thread.start()    



