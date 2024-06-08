import json
import io

class Dict:

    def set_attribute(self, data):

        for k, v in data.items():
            if isinstance(v, str)or isinstance(v, int) or isinstance(v, float) or isinstance(v,bool):
                setattr(self, f"{k}", v)
            elif isinstance(v, dict):
                my_dict = Dict()
                my_dict.set_attribute(v)
                setattr(self, f"{k}", my_dict)
            elif isinstance(v, list):
                my_list = List()
                my_list_data = my_list.set_attribute(data=v, parent=k)
                if my_list_data is None:
                    setattr(self, f"{k}", v)
                setattr(self, f"{k}", my_list_data)


class List:

    def __init__(self):
        self.temp_list = None

    def set_attribute(self, data, parent=None):
        self.temp_list = []
        for item in data:
            if isinstance(item, str)or isinstance(item, int) or isinstance(item, float) or isinstance(item,bool):
                self.temp_list.append(item)
            elif isinstance(item, dict):
                my_dict = Dict()
                my_dict.set_attribute(item)
                self.temp_list.append(my_dict)
            elif isinstance(item, list):
                my_list = List()
                self.temp_list.append(my_list.set_attribute(data=item, parent=f"{parent}+counter"))

        if len(self.temp_list) > 0:
            return self.temp_list


class JsonDecoder:

    def __init__(self):
        self.temp_list = None
        self.json_path = None

    def read_json_file(self, json_path):
        self.json_path = json_path
        self.get_data()

    def read_string(self, json_string):
        data = json.loads(json_string)
        if isinstance(data, dict):
            self.my_dict(data)
        if isinstance(data, str)or isinstance(data, int) or isinstance(data, float) or isinstance(data,bool):
            setattr(self, f"{data}", data)

    def get_data(self):
        f = open(self.json_path, 'r')
        data = json.load(f)
        if isinstance(data, dict):
            self.my_dict(data)
        if isinstance(data, list) or isinstance(data,tuple):
            self.my_list(data)
        if isinstance(data, str)or isinstance(data, int) or isinstance(data, float) or isinstance(data,bool):
            setattr(self, f"{data}", data)

    def my_dict(self, data):

        for k, v in data.items():
            if isinstance(v, str)or isinstance(v, int) or isinstance(v, float) or isinstance(v,bool):
                setattr(self, f"{k}", v)
            elif isinstance(v, dict):
                my_dict = Dict()
                my_dict.set_attribute(v)
                setattr(self, f"{k}", my_dict)
            elif isinstance(v, list):
                my_list = List()
                my_list_data = my_list.set_attribute(data=v, parent=k)
                setattr(self, f"{k}", my_list_data)

    def my_list(self, data,parent=None):
        self.temp_list = []
        for item in data:
            if isinstance(item, str) or isinstance(item, int) or isinstance(item, float) or isinstance(item, bool):
                self.temp_list.append(item)
            elif isinstance(item, dict):
                my_dict = Dict()
                my_dict.set_attribute(item)
                self.temp_list.append(my_dict)
            elif isinstance(item, list):
                my_list = List()
                self.temp_list.append(my_list.set_attribute(data=item, parent=f"{parent}+counter"))

        if len(self.temp_list) > 0:
            if parent is None:
                setattr(self, f"{0}", self.temp_list)
            else:
                setattr(self, f"{parent}", self.temp_list)

class JsonParser:

    @staticmethod
    def decode(json_object):
        json_decoder = JsonDecoder()
        try:
            if isinstance(json_object, io.IOBase):
                json_decoder.read_json_file(json_object)
            if isinstance(json_object, str):
                json_decoder.read_string(json_object)
            if isinstance(json_object, dict):
                json_decoder.read_string(str(json_object))
            return json_decoder
        except Exception:
            raise TypeError("Object type is not supported")
