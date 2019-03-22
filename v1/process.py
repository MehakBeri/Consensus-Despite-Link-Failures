from message import Message
from queue import Queue
import threading
import time

threadLock = threading.Lock()


class Process(threading.Thread):
    def __init__(self, pid, root_id, connectivity_matrix_row, config):
        threading.Thread.__init__(self)
        self.pid = pid
        self.neighbor_ids = []
        self.index = config[pid]['my_index']
        for j in range(len(connectivity_matrix_row)):
            if (connectivity_matrix_row[j]==1) and j!=self.index:
                self.neighbor_ids.append(j) # neighbor ids has indexes of neighbors derived from conn_matrix row
        self.root_id = root_id
        self.comm_channel = config['comm']
        self.parent = config[pid]['parent']
        self.children = config[pid]['children']
        self.marked = config[pid]['marked']
        self.master_q = config['comm'][-1] # last comm channel is comm channel with the master
        self.q = config['comm'][int(self.index)]
        self.sent = config[pid]['sent']
        self.roundNumber = config[pid]['r']
        if int(self.pid) == int(self.root_id):
            self.marked=True
            self.parent = 0

    def run(self):
        if self.marked and len(self.neighbor_ids) > len(self.sent):
            for i in range(len(self.neighbor_ids)):
                if self.parent != self.neighbor_ids[i]:
                    self.sent.append(self.neighbor_ids[i])
                    self.send_message(self.neighbor_ids[i])
        pending_msgs = 0
        snapshot = list(self.q.queue)
        for msg in snapshot:
            if msg.receiverID==self.index and (int(msg.msg_type.split(':')[1])<self.roundNumber):
                pending_msgs += 1
        print(f'{self.pid} pending msgs: {pending_msgs}')
        while(pending_msgs!=0):
            threadLock.acquire()
            tmp = self.q.get()
            threadLock.release()
            if tmp.receiverID==self.index and (int(tmp.msg_type.split(':')[1])<self.roundNumber):
                if ('inter-thread' in tmp.msg_type) :
                    print(f'{self.pid}: Receiving msg {tmp}, {self.q.qsize()}')
                    self.receive_message(tmp.senderID)
                elif ('inform-parent' in tmp.msg_type) :
                    print(f'{self.pid} -- Added {tmp.senderID} to my children')
                    if tmp.senderID not in self.children:
                        self.children.append(tmp.senderID)
                pending_msgs -= 1
        self.comm_channel[int(self.index)] = self.q
        done_msg = {'parent': self.parent,
                    'children':self.children,
                    'marked':self.marked,
                    'sent':self.sent,
                    'r':self.roundNumber+1,
                    'my_index':self.index
                    }
        done_config={}
        done_config['done_msg'] = done_msg
        done_config['comm']=self.comm_channel
        threadLock.acquire()
        self.master_q.put(Message(self.pid, 'Master', done_config))
        threadLock.release()


    def set_parent(self, parent):
        self.parent = parent

    def send_message(self, receiver):
        msg = Message(self.index, int(receiver), f'inter-thread:{self.roundNumber}')
        threadLock.acquire()
        self.comm_channel[int(receiver)].put(msg)
        threadLock.release()
        print(f'{self.pid}: sent {msg} to queue')
        
    def receive_message(self, sender):
        if not self.marked:
            self.mark_me()
            self.set_parent(sender)
            self.inform_parent(sender)

    def mark_me(self, r=None):
        self.marked = True
        print(f'|| BFS LEVEL: {self.pid}')

    def inform_parent(self, sender):
        threadLock.acquire()
        self.comm_channel[int(sender)].put(Message(self.pid, int(sender), f'inform-parent:{self.roundNumber}'))
        threadLock.release()
        print(f'{self.pid} -- informing parent {sender}')

