class CodeConverter:

    def __init__(self):
        self.local_ints = 0
        self.local_bytes = 0
        self.global_ints = 0
        self.global_bytes = 0

    def global_put_int(self, key, value, is_args, is_init):
        if is_init:
            self.global_ints += 1
        string = f"App.globalPut(Bytes(\"{key}\"), {value}),\n"
        if not is_args:
            string = "\t" + string
        return string

    def global_put_bytes(self, key, value, is_args, is_init):
        if is_init:
            self.global_bytes += 1
        string = f"App.globalPut(Bytes(\"{key}\"), {value}),\n"
        if not is_args:
            string = "\t" + string
        return string

    def local_put_int(self, key, value, is_init):
        if is_init:
            self.local_ints += 1
            return
        return f"App.localPut(Int(0), Bytes(\"{key}\"), {value}),\n"

    def local_put_bytes(self, key, value, is_init):
        if is_init:
            self.local_bytes += 1
            return
        return f"App.localPut(Int(0), Bytes(\"{key}\"), {value}),\n"

    def global_get(self, key, is_args, to_buffer):
        string = f"App.globalGet(Bytes(\"{key}\"))"
        if not is_args:
            string = "\t" + string
        if not to_buffer:
            string = string + ",\n"
        return string

    def local_get(self, key, is_args, to_buffer):
        string = f"App.localGet(Int(0), Bytes(\"{key}\"))"
        if not is_args:
            string = "\t" + string
        if not to_buffer:
            string = string + ",\n"
        return string

    def unix_time(self, is_args, to_buffer):
        string = f"Global.round()"
        # if to_buffer:
        #     return string
        # if not is_args:
        #     string = "\t" + string + ",\n"
        return string
