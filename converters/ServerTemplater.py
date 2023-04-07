class ServerTemplater:

    def class_creation(self, class_name, args):
        return f"""\nclass {class_name}({args}):\n"""

    def method_creation(self, method_name, args):
        return f"""\n\tdef {method_name}({args}):\n"""
