import struct
from copy import deepcopy

Byte2StructType = {
    1: "B",
    2: "H",
    4: "I",
    8: "Q"
}

#======================Exception class==============================

class FlagErrorException(Exception):
    def __init__(self, message):
        super(FlagErrorException, self).__init__(message)
        self.message = message + " error flag checked!!"

    def __str__(self):
        return self.message

#===================================================================


class BaseStructParser(object):
    STRUCT = []
    def __init__(self, stream_data):
        # print stream_data.encode("hex"), self.STRUCT
        self.show_struct_info = deepcopy(self.STRUCT)
        self.struct_length = 0
        self._field_name = "BaseStruct"
        for struct_key, key_len in self.STRUCT:
            # print struct_key
            if type(struct_key) == str:
                if type(key_len) == int:
                    if key_len == 0:
                        self.__dict__[struct_key] = None
                    else:
                        if key_len <= 8:
                            self.__dict__[struct_key] = struct.unpack("<{0}".format(Byte2StructType.get(key_len)),
                                                                                      stream_data[self.struct_length:
                                                                                                  self.struct_length + key_len])[0]
                        else:
                            self.__dict__[struct_key] = stream_data[self.struct_length: self.struct_length+key_len].encode("hex")
                        self.struct_length += key_len
                elif type(key_len) == list:
                    #if the key is list, the meas the property is the variable array
                    #so we should set the project which in the list to full into the array
                    class_n = key_len[0]
                    T = class_n(stream_data)
                    T.get_array(stream_data[self.struct_length:])
                    self.__dict__[struct_key] = T
                    self.struct_length += T.Struct_len
                elif type(key_len) == tuple:
                    #if the key_len is tuple, it means this field get from other information
                    #key_len[0] is source and the key_len[1] is the data field
                    t_class = key_len[0].get(self.__dict__[key_len[1]])
                    self.__dict__[struct_key] = t_class(stream_data[self.Struct_len:])
                    self.struct_length += self.__dict__[struct_key].Struct_len
                elif type(key_len) == unicode:
                    #if the data is base of unicode, pls set the key_len as u'key_len'
                    self.__dict__[struct_key] = stream_data[self.struct_length:
                                                            self.struct_length + self.__dict__[str(key_len)] * 2]
                    self.struct_length += self.__dict__[key_len] * 2
                else:
                    #if the key_len is str, it means use a variable length from the property
                    #the key_len become the property name in the self directory
                    self.__dict__[struct_key] = stream_data[self.struct_length:
                                                            self.struct_length + self.__dict__[key_len]]
                    self.struct_length += self.__dict__[key_len]
            else:
                # if the key is not str, it must be the object, and the following object must come from BaseStructParser
                temporoly_class = struct_key(stream_data[self.struct_length:])
                self.__dict__[temporoly_class.__class__.__name__] = temporoly_class
                self.struct_length += temporoly_class.Struct_len
        self.field_parser(stream_data)
        self.check_flag()

    @property
    def Struct_len(self):
        return self.struct_length

    def field_parser(self, stream):
        pass

    def check_flag(self):
        pass

    def show_struct(self, p=0):
        for _ in self.show_struct_info:
            if type(_[0]) == str:
                try:
                    if type(self.__dict__[_[0]]) == int:
                        print "\t"*p, _[0], ":", hex(self.__dict__[_[0]])
                    elif type(self.__dict__[_[0]]) == str:
                        print "\t" * p, _[0], ":", self.__dict__[_[0]]
                    elif type(self.__dict__[_[0]]) == long:
                        print "\t" * p, _[0], ":", hex(self.__dict__[_[0]])
                    else:
                        self.__dict__[_[0]].show_struct(p=p + 1)
                except:
                    print "\t"*p, _[0], ":", "None"
            else:
                try:
                    print "\t"*p, _[0].__class__.__name__, ":"
                    self.__dict__[_[0].__class__.__name__].show_struct(p+1)
                except:
                    print "\t" * p, _[0].__name__, ":"
                    self.__dict__[_[0].__name__].show_struct(p + 1)

    def get_str(self, stream, offset, t=int):
        if t == int:
            A = ""
            for _ in stream[offset:]:
                if ord(_) == 0:
                    break
                else:
                    A += _
            return A
        elif t == unicode:
            A = ""
            for _ in range(0, len(stream), 2):
                if ord(stream[_]) == 0:
                    break
                else:
                    A += stream[_]
            return A

