from message import Message
from queue import Queue
import threading
import time
import random

threadLock = threading.Lock()
msg_counter = 0
class Process(threading.Thread):
    def __init__(self, pid, n, leader, x, config):
        threading.Thread.__init__(self)
        self.pid = pid
        self.n = n
        self.x = x
        self.leader = leader
        self.comm_channel = config['comm']
        self.decision = config[pid]['decision']
        self.key = config[pid]['key']
        self.value_v = config[pid]['value']
        self.level_v = config[pid]['level']
        self.master_q = config['comm'][0] # first comm channel is comm channel with the master
        self.q = config['comm'][int(self.pid)]
        self.roundNumber = config[pid]['r']
        self.totalRounds = config[self.pid]["total_rounds"]
        if int(self.pid) == int(self.leader) and self.key==None:
            self.key = random.randint(1, self.totalRounds)
            print(f"Leader {self.pid} chose key {self.key}")

    def run(self):
        for i in range(self.n):
            if (i+1)!= self.pid:
                self.send_message(i+1)
        pending_msgs = 0
        snapshot = list(self.q.queue)
        for msg in snapshot:
            if (int(msg.msg_type.split(':')[1])<self.roundNumber):
                pending_msgs += 1
        print(f'{self.pid} pending msgs: {pending_msgs}')
        while(pending_msgs!=0):
            threadLock.acquire()
            tmp = self.q.get()
            threadLock.release()
            if (int(tmp.msg_type.split(':')[1])<self.roundNumber):
                if 'x' not in tmp.msg_type:
                    print(f'{self.pid}: Receiving msg {tmp}')
                    self.receive_message(tmp.senderID, tmp)
                pending_msgs -= 1
        self.comm_channel[int(self.pid)] = self.q
        done_msg = {'decision': self.decision,
                    'key' : self.key,
                    'value': self.value_v,
                    'level': self.level_v,
                    'r': self.roundNumber + 1,
                    'total_rounds': self.totalRounds
                    }
        done_config={}
        done_config['done_msg'] = done_msg
        done_config['comm'] = self.comm_channel
        threadLock.acquire()
        self.master_q.put(Message(self.pid, 'Master', done_config, self.level_v, self.value_v, self.key))
        threadLock.release()


    def send_message(self, receiver):
        global msg_counter 
        threadLock.acquire()
        msg_counter += 1
        print("---------------------> msg_count: ", msg_counter)
        if msg_counter%self.x == 0:
            msg = Message(self.pid, int(receiver), f'x-inter-thread:{self.roundNumber}', self.level_v, self.value_v, self.key)
            print(f"-- dropping msg {msg_counter} x x x ----")
        else:
            msg = Message(self.pid, int(receiver), f'inter-thread:{self.roundNumber}', self.level_v, self.value_v, self.key)
            self.comm_channel[int(receiver)].put(msg)
            print(f'{self.pid}: sent {msg} to queue')
        threadLock.release()
        
    def receive_message(self, sender_pid, msg):
        if msg.key != None:
            self.key = msg.key
        my_index = self.pid-1
        for j in range(self.n):
            if j!= my_index:
                if msg.value[j] != None:
                    self.value_v[j] = msg.value[j]
                if msg.level[j] > self.level_v[j]:
                    self.level_v[j] = msg.level[j]
        level_without_my_index = []
        i=0
        for l in self.level_v:
            if i!=my_index:
                level_without_my_index.append(l)
            i += 1
        self.level_v[my_index] = 1 + min(level_without_my_index)
        if self.roundNumber == self.totalRounds:
            all_j_1 = True
            for v in self.value_v:
                if int(v)!=1:
                    all_j_1 = False
                    break
            if self.key!=None and self.level_v[my_index]>=self.key and all_j_1:
                self.decision = 1
            else:
                self.decision = 0

