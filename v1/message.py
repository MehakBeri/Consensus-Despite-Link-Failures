class Message():
    def __init__(self, sender_id, receiver_id, msg_type):
        self.senderID = sender_id
        self.receiverID = receiver_id
        self.msg_type = msg_type

    def __repr__(self):
        return "<Message sender index: %s receiver index: %s msg_type: %s>" % (self.senderID, self.receiverID, self.msg_type)




