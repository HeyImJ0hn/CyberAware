class Logger:
    def __init__(self, game_manager):
        self.logs = []
        self.full_logs = []
        self.subscribers = []
        self.game_manager = game_manager

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)
        print("subscribers: ", self.subscribers)
        
    def log(self, message):
        self.full_logs.append(message.split("<br>")[0] if "BUILD FAILED in" in message or "BUILD SUCCESSFUL in"else message)
        self.logs.append(message)
        if "BUILD FAILED in" in message or "BUILD SUCCESSFUL in" in message:
                self.game_manager.finished_compiling = True
                self.game_manager.compilation_logs = self.full_logs
                self.logs = []
                self.full_logs = []