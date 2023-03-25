import json


class Log:
    def __init__(self, title, number, state, author, comments):
        self.title = title
        self.number = number
        self.state = state
        self.author = author
        self.comments = comments


class LogEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Log):
           # JSON object would be a dictionary.
            return {
                "title": o.title,
                "number": o.number,
                "state": o.state,
                "author": o.author,
                "comments": o.comments
            }
        else:
            # Base class will raise the TypeError.
            return super().default(o)


class LogDecoder(json.JSONDecoder):
    def __init__(self, object_hook=None, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)
        
    def object_hook(self, o):
        decoded_log =  Log(
            o.get('title'), 
            o.get('number'), 
            o.get('state'),
            o.get('author'),
            o.get('comments'),
        )
        if (decoded_log.title != None) :
            logList.insert(0,decoded_log) 
        return logList
        
        
logList = []
with open('sample4.json','r') as f:
    log_List = json.load(f, cls=LogDecoder)

print(log_List[0].title)