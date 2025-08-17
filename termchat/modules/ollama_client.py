import ollama
from rich import print # debug use only



class ollama_client:
    def __init__(self, host):
        # spawns an ollama client
        self.host = host
        self.client = ollama.Client(host) # create a client object
        models_raw = self.client.list()
        self.models = [] # wait ollama instance to return model list
        self.chat_history=[] # use to handle interactive chat
        for model in models_raw["models"]:
            self.models.append(model["model"])
    

    def chat(self, model, prompt, stream=True):
        """send chat request to ollama(context aware).
        """
        response = self.client.chat(model, messages=[{"role":"user", "content": prompt}], stream=stream)
        for chunk in response:
            yield chunk["message"]["content"]


    def generate(self, model, prompt, stream=True): 
        """send chat request to ollama(context free).
        """
        response = self.client.generate(model, prompt, stream)
        for chunk in response:
            yield chunk["response"]


    def show(self):
        """inspect a model and make it into a dictionary. Omit modelfile, license and template since it's quite uselsss.
        """
        self.info = self.client.show(self.models[0])
        # self.info.pop("modelfile")
        self.info_new = {}
        for item in self.info:
            self.info_new[item[0]] = item[1]
        self.info_new.pop("modelfile")
        self.info_new.pop("license")
        self.info_new.pop("template")
        return self.info_new
