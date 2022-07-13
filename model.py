import json

class Model:
    def __init__(self):
        self.VERSION = "v-1-0-1"
        with open(f"model-parameters/{self.VERSION}.json") as f:
            self.parameters = json.load(f)