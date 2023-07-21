import sys
import base64
import json
import pickle

class StartBenchmarkUtils:
    @classmethod
    def encode_argument(cls, argument):
        return base64.b64encode(pickle.dumps(argument)).decode('ascii')

    @classmethod
    def decode_argument(cls, argument):
        return pickle.loads(base64.b64decode(argument.encode('ascii')))


