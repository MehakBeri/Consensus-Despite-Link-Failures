class Message():
    def __init__(self, sender_id, receiver_id, msg_type, level, value, key):
        self.senderID = sender_id
        self.receiverID = receiver_id
        self.msg_type = msg_type
        self.level = level
        self.value = value
        self.key = key

    def __repr__(self):
        return "<Message sender: %s | receiver: %s | msg_type: %s | level: %s | value: %s | key: %s >" % (self.senderID, self.receiverID, self.msg_type, self.level, self.value, self.key)




