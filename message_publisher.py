import queue


class Subscription:
    def __init__(self, q_len=5):
        self.q = queue.Queue(maxsize=q_len)

    def listen(self):
        while True:
            yield self.q.get()


class MessageService:
    def __init__(self, q_len=5):
        self.q_len = q_len
        self.subscriptions = []

    def get_subscription(self):
        self.subscriptions.append(Subscription(self.q_len))
        return self.subscriptions[-1]

    def publish(self, msg):
        for i in list(reversed(range(len(self.subscriptions)))):
            try:
                self.subscriptions[i].q.put_nowait(msg)
            except queue.Full:
                del self.subscriptions[i]