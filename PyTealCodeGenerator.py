import ast
from converters.CodeConverter import CodeConverter
from converters.ServerTemplater import ServerTemplater
from converters.TemplateFiller import TemplateFiller
from macro.Mode import Mode

code_converter = CodeConverter()
template_filler = TemplateFiller()
server_filler = ServerTemplater()
tab = "\t"
algo_client = "algo_client"
default_handles = {"on_optin": 0, "on_closeout": 1}


class AnnotationTransformer(ast.NodeTransformer):
    def visit_ClassDef(self, node):
        # Check if the function has a scope annotation
        scope_annotation = next((a for a in node.decorator_list if a.id.startswith("X")), None)
        if scope_annotation:
            # Set the scope attribute of the node based on the annotation
            node.scope = scope_annotation.id
        else:
            # If no scope annotation is present, default to @XAll
            node.scope = "XAll"

        for stmt in node.body:
            self.visit(stmt)

        return node

    def visit_FunctionDef(self, node):
        # Check if the function has a scope annotation
        scope_annotation = next((a for a in node.decorator_list if a.id.startswith("X")), None)
        if scope_annotation:
            # Set the scope attribute of the node based on the annotation
            node.scope = scope_annotation.id
        else:
            # If no scope annotation is present, default to @XAll
            node.scope = "XAll"
        return node

    def visit_AnnAssign(self, node):
        # Check if the variable has a scope annotation
        scope_annotation = next((a for a in node.annotation.values if a.id.startswith("X")), None)
        if scope_annotation:
            # Set the scope attribute of the node based on the annotation
            node.scope = scope_annotation.id
        else:
            # If no scope annotation is present, default to @XAll
            node.scope = "XAll"
        return node


class PyTealCodeGenerator(ast.NodeVisitor):
    def __init__(self):

        self.code = ""
        self.blockchain_vars = ""
        self.blockchain_methods = ""
        self.blockchain_methods_inner = ""
        self.blockchain_class_name = ""
        self.method_arg_buffer = ""
        self.if_elif_else = "if"

        self.current_scope = "XAll"
        self.bc_vars_mode = {}
        self.bc_vars_type = {}

        self.is_class = False
        self.is_method = False
        self.is_args = False
        self.to_else = False
        self.is_if = False
        self.is_for = False
        self.is_while = False
        self.is_assert = False
        self.inner_if = False
        self.is_output = False
        self.is_output_type = ""

        self.is_init_bc = False
        self.to_buffer = False
        self.og_visit_counter = 0
        self.tab_counter = 0

    def bc_methods(self):
        return self.blockchain_methods

    def contract_name(self):
        return self.blockchain_class_name

    def visit_Import(self, node):
        names = ""
        for name in node.names:
            names += name.name + ", "
        names = names[:-2]
        self.code += f"import {names}\n"

    def visit_ImportFrom(self, node):
        names = ""
        for name in node.names:
            names += name.name + ", "
        names = names[:-2]
        self.code += f"from {node.module} import {names}\n"

    def visit_ClassDef(self, node):
        self.is_class = True
        self.current_scope = node.scope
        args = ""
        if hasattr(node, "bases"):
            for arg in node.bases:
                args += self.visit(arg) + ", "
            args = args[:-2]

        if self.current_scope == "XAll" or self.current_scope == "XOnBlockchain":
            self.blockchain_class_name = node.name
        if self.current_scope == "XAll" or self.current_scope == "XOnServer":
            self.code += server_filler.class_creation(node.name, args)

        self.tab_counter += 1
        for stmt in node.body:
            self.visit(stmt)

        self.tab_counter -= 1
        self.is_class = False

    def visit_FunctionDef(self, node):
        self.current_scope = node.scope
        self.is_method = True
        match self.current_scope:
            # case "XAll":
            #     args = ""
            #     if node.name == "__init__":
            #         self.is_init_bc = True
            #     else:
            #         self.blockchain_methods += template_filler.create_function(node.name)
            #
            #     self.tab_counter += 1
            #     for arg in node.args.args:
            #         args += str(arg.arg) + ", "
            #     args = args[:-2]
            #     self.code += server_filler.method_creation(node.name, args)
            #
            #     for stmt in node.body:
            #         self.method_arg_buffer = ""
            #         self.visit(stmt)
            #
            #     if self.is_init_bc:
            #         self.code += "\t\tpass\n"
            #     self.is_init_bc = False
            #
            #     if self.blockchain_methods_inner != "":
            #         self.blockchain_methods += template_filler.fill_function(self.blockchain_methods_inner)
            #     self.blockchain_methods_inner = ""
            #     self.tab_counter -= 1

            case "XAll":
                self.current_scope = "XOnBlockchain"
                if node.name == "__init__":
                    self.is_init_bc = True
                else:
                    if node.name not in default_handles:
                        args = ""
                        for arg in node.args.args:
                            if str(arg.arg) == "self":
                                continue
                            if str(arg.arg) == "output":
                                self.is_output = True
                                self.is_output_type = self.visit(arg.annotation)
                            args += str(arg.arg) + " : " + self.visit(arg.annotation) + ", "
                        args = args[:-2]
                        self.blockchain_methods += template_filler.create_function(node.name, args)

                for stmt in node.body:
                    self.method_arg_buffer = ""
                    self.visit(stmt)

                if node.name not in default_handles and not self.is_init_bc:
                    self.blockchain_methods += template_filler.fill_function(self.blockchain_methods_inner)
                else:
                    match node.name:
                        case "on_optin":
                            self.blockchain_methods += template_filler.handle_opt_in \
                                (self.blockchain_methods_inner)
                        case "on_closeout":
                            self.blockchain_methods += template_filler.handle_close_out \
                                (self.blockchain_methods_inner)
                self.blockchain_methods_inner = ""
                self.is_output = False
                self.is_output_type = ""

                self.current_scope = "XOnServer"
                args = ""
                for arg in node.args.args:
                    args += str(arg.arg) + ", "
                args = args[:-2]
                self.code += server_filler.method_creation(node.name, args)

                self.tab_counter += 1
                for stmt in node.body:
                    self.method_arg_buffer = ""
                    self.visit(stmt)
                self.tab_counter -= 1
                self.is_init_bc = False
            case "XOnBlockchain":
                if node.name == "__init__":
                    self.is_init_bc = True
                else:
                    if node.name not in default_handles:
                        args = ""
                        for arg in node.args.args:
                            if str(arg.arg) == "self":
                                continue
                            if str(arg.arg) == "output":
                                self.is_output = True
                                self.is_output_type = self.visit(arg.annotation)
                            args += str(arg.arg) + " : " + self.visit(arg.annotation) + ", "
                        args = args[:-2]
                        self.blockchain_methods += template_filler.create_function(node.name, args)

                for stmt in node.body:
                    self.method_arg_buffer = ""
                    self.visit(stmt)
                self.is_init_bc = False
                if node.name not in default_handles:
                    self.blockchain_methods += template_filler.fill_function(self.blockchain_methods_inner)
                else:
                    match node.name:
                        case "on_optin":
                            self.blockchain_methods += template_filler.handle_opt_in \
                                (self.blockchain_methods_inner)
                        case "on_closeout":
                            self.blockchain_methods += template_filler.handle_close_out \
                                (self.blockchain_methods_inner)
                self.blockchain_methods_inner = ""
                self.is_output = False
                self.is_output_type = ""

            case "XOnServer":
                args = ""
                for arg in node.args.args:
                    args += str(arg.arg) + ", "
                args = args[:-2]
                self.code += server_filler.method_creation(node.name, args)

                self.tab_counter += 1
                for stmt in node.body:
                    self.method_arg_buffer = ""
                    self.visit(stmt)
                self.tab_counter -= 1

        self.is_method = False

    def visit_Expr(self, node):
        return self.visit(node.value)

    def visit_Name(self, node):
        return node.id

    def visit_Return(self, node):
        tabs = tab * self.tab_counter
        if self.current_scope == "XOnServer":
            self.code += tabs + "return " + self.visit(node.value) + "\n"
        elif self.current_scope == "XOnBlockchain":
            self.blockchain_methods_inner += tabs + f"Return({self.visit(node.value)}),\n"

    def visit_List(self, node):
        string = ""
        if self.current_scope == "XOnServer" or self.current_scope == "XAll":
            for elt in node.elts:
                string += self.visit(elt) + ", "
            string = string[:-2]
        return f"[{string}]"

    def visit_Match(self, node):
        match self.current_scope:
            case "XAll":
                self.current_scope = "XOnBlockchain"
                conds = ""
                self.to_buffer = True
                self.is_args = True
                subject = self.visit(node.subject)
                self.to_buffer = False
                self.is_args = False
                for case in node.cases:
                    conds += "[" + subject + "==" + self.visit(case) + "], "
                self.blockchain_methods_inner += f"Cond({conds})\n"

                self.method_arg_buffer = ""
                self.if_elif_else = "if"

                self.current_scope = "XOnServer"
                self.to_buffer = True
                subject = self.visit(node.subject)
                self.to_buffer = False
                tabs = tab * self.tab_counter
                self.code += tabs + f"match {subject}:\n"
                self.tab_counter += 1
                for case in node.cases:
                    self.visit(case)
                self.tab_counter -= 1
            case "XOnBlockchain":
                conds = ""
                self.to_buffer = True
                self.is_args = True
                subject = self.visit(node.subject)
                self.to_buffer = False
                self.is_args = False
                for case in node.cases:
                    conds += "[" + subject + "==" + self.visit(case) + "], "
                self.blockchain_methods_inner += f"Cond({conds})\n"
            case "XOnServer":
                self.to_buffer = True
                subject = self.visit(node.subject)
                self.to_buffer = False
                tabs = tab * self.tab_counter
                self.code += tabs + f"match {subject}:\n"
                self.tab_counter += 1
                for case in node.cases:
                    self.visit(case)
                self.tab_counter -= 1

    def visit_match_case(self, node):
        if self.current_scope == "XOnBlockchain":
            body = ""
            eq = self.visit(node.pattern.value)
            self.to_buffer = True
            for bod in node.body:
                body += self.visit(bod)
            self.to_buffer = False
            if len(node.body) > 1:
                body = f"Seq([{body}])"
            return eq + ", " + body
        if self.current_scope == "XOnServer":
            eq = self.visit(node.pattern.value)
            tabs = tab * self.tab_counter
            self.code += tabs + f"case {eq}:\n"
            self.tab_counter += 1
            self.to_buffer = True
            body = ""
            for bod in node.body:
                body += self.visit(bod) + "\n"
            self.code += body
            self.to_buffer = False
            self.tab_counter -= 1

    def visit_If(self, node):
        self.to_buffer = True
        self.is_if = True
        self.to_else = False
        self.og_visit_counter += 1
        ret = ""
        test = ""
        body = ""
        if self.current_scope == "XAll":
            self.current_scope = "XOnServer"
            self.method_arg_buffer = ""
            if hasattr(node, "test"):
                test += self.visit(node.test)

            self.tab_counter += 1
            for line in node.body:
                self.to_buffer = True
                body += self.visit(line)
            self.to_buffer = False
            self.tab_counter -= 1

            tabs = tab * self.tab_counter
            ret = tabs + f"{self.if_elif_else} {test}:\n"
            self.code += ret + body

            for stmt in node.orelse:
                if type(node.orelse) == ast.If:
                    self.if_elif_else = "elif"
                else:
                    self.if_elif_else = "else"
                self.visit(stmt)

            self.to_else = False
            self.if_elif_else = "if"

            self.current_scope = "XOnBlockchain"
            ret = ""
            test = ""
            for else_stmt in node.orelse:
                self.to_else = True
                ret = self.visit(else_stmt)
                if type(else_stmt) != ast.If:
                    ret = f".Else({ret}),\n"

            self.to_else = False
            self.method_arg_buffer = ""
            if hasattr(node, "test"):
                test += self.visit(node.test)

            for line in node.body:
                self.to_buffer = True
                if type(line) == ast.If:
                    self.inner_if = True
                body += self.visit(line)
                if type(line) == ast.If:
                    self.inner_if = False
            self.to_buffer = False

            if hasattr(node, "test"):
                ret = f".ElseIf({test}).Then({body})" + ret
                if self.inner_if:
                    ret = ret[5:]
                if self.og_visit_counter == 1:
                    ret = ret[5:]
                    self.blockchain_methods_inner += ret

            self.current_scope = "XAll"

        if self.current_scope == "XOnServer":
            self.method_arg_buffer = ""
            if hasattr(node, "test"):
                test += self.visit(node.test)

            self.tab_counter += 1
            for line in node.body:
                self.to_buffer = True
                body += self.visit(line)
            self.to_buffer = False
            self.tab_counter -= 1

            tabs = tab * self.tab_counter
            ret = tabs + f"{self.if_elif_else} {test}:\n"
            self.code += ret + body

            for stmt in node.orelse:
                if type(node.orelse) == ast.If:
                    self.if_elif_else = "elif"
                    self.visit(stmt)
                else:
                    else_body = ""
                    self.to_buffer = True
                    self.if_elif_else = "else"
                    self.tab_counter += 1
                    for else_stmt in node.orelse:
                        else_body += self.visit(else_stmt)
                    self.tab_counter -= 1

                    tabs = tab * self.tab_counter
                    ret = tabs + f"{self.if_elif_else}:\n"
                    self.code += ret + else_body
                    break

            self.to_else = False
            self.if_elif_else = "if"

        if self.current_scope == "XOnBlockchain":
            ret = ""
            test = ""
            for else_stmt in node.orelse:
                self.to_else = True
                ret = self.visit(else_stmt)
                if type(else_stmt) != ast.If:
                    ret = f".Else({ret}),\n"

            self.to_else = False
            self.method_arg_buffer = ""
            if hasattr(node, "test"):
                test += self.visit(node.test)

            for line in node.body:
                self.to_buffer = True
                if type(line) == ast.If:
                    self.inner_if = True
                body += self.visit(line)
                if type(line) == ast.If:
                    self.inner_if = False
            self.to_buffer = False

            if hasattr(node, "test"):
                ret = f".ElseIf({test}).Then({body})" + ret
                if self.inner_if:
                    ret = ret[5:]
                if self.og_visit_counter == 1:
                    ret = ret[5:]
                    self.blockchain_methods_inner += ret

        self.og_visit_counter -= 1
        self.is_if = False
        return ret

    def visit_Compare(self, node):
        self.to_buffer = True
        ops = ""
        right = ""
        left = self.visit(node.left)
        for op in node.ops:
            ops += self.visit(op)
        for comparator in node.comparators:
            right += self.visit(comparator)

        self.to_buffer = False
        if self.current_scope == "XOnBlockchain":
            return left + ops + right + ", "
        if self.current_scope == "XOnServer":
            return left + ops + right

    def visit_UnaryOp(self, node):
        s = self.visit(node.op)
        return s + self.visit(node.operand)

    def visit_USub(self, node):
        return "-"

    def visit_UAdd(self, node):
        return "+"

    def visit_Lt(self, node):
        return "<"

    def visit_LtE(self, node):
        return "<="

    def visit_Gt(self, node):
        return ">"

    def visit_GtE(self, node):
        return ">="

    def visit_NotEq(self, node):
        return "!="

    def visit_Eq(self, node):
        return "=="

    def visit_Pass(self, node):
        tabs = tab * self.tab_counter
        if self.to_buffer:
            if self.current_scope == "XOnBlockchain":
                return "Return(Int(1)),\n"
            elif self.current_scope == "XOnServer":
                return tabs + "pass\n"
        else:
            if self.current_scope == "XOnBlockchain":
                self.blockchain_methods_inner += "Return(Int(1)),\n"
            elif self.current_scope == "XOnServer":
                self.code += tabs + "pass\n"

    def visit_Subscript(self, node):
        tabs = tab * self.tab_counter
        self.current_scope = "XOnServer"
        index = self.visit(node.slice)
        self.current_scope = "XOnBlockchain"
        value = self.visit(node.value)
        if self.to_buffer or self.is_args:
            return f"{value}[{index}]"
        else:
            if self.current_scope == "XOnBlockchain":
                self.blockchain_methods_inner += f"{value}[{index}],\n"
            elif self.current_scope == "XOnServer":
                self.code += tabs + f"{value}[{index}]\n"

    def visit_Call(self, node):
        buffer = ""
        for stmt in node.args:
            self.is_args = True
            self.method_arg_buffer += self.visit(stmt) + ", "

        if self.method_arg_buffer != "":
            self.is_args = False
            self.method_arg_buffer = self.method_arg_buffer[:-2]

        if self.current_scope == "XAll" or self.current_scope == "XOnBlockchain":
            func_name = self.visit(node.func)
            # hard coding
            var_name = func_name.split(".")[0]
            if var_name == "self":
                var_name = func_name.split(".")[1]

            if func_name.find('get_x') != -1:
                if self.is_args or self.to_buffer:
                    if self.bc_vars_mode[var_name] == Mode.GLOBAL:
                        buffer += code_converter.global_get(var_name, self.is_args, True)
                    else:
                        buffer += code_converter.local_get(var_name, self.is_args, True)
                else:
                    if self.bc_vars_mode[var_name] == Mode.GLOBAL:
                        self.blockchain_methods_inner += code_converter.global_get(var_name, self.is_args,
                                                                                   False)
                    else:
                        self.blockchain_methods_inner += code_converter.local_get(var_name, self.is_args,
                                                                                  False)
            elif func_name.find('set_x') != -1:
                if self.is_args or self.to_buffer:
                    if self.bc_vars_type[var_name] == int:
                        if self.bc_vars_mode[var_name] == Mode.GLOBAL:
                            buffer += code_converter.global_put_int(var_name, self.method_arg_buffer, self.is_args, self.is_init_bc)
                        else:
                            buffer += code_converter.local_put_int(var_name, self.method_arg_buffer, self.is_init_bc)
                    elif self.bc_vars_type[var_name] == str:
                        if self.bc_vars_mode[var_name] == Mode.GLOBAL:
                            buffer += code_converter.global_put_bytes(var_name, self.method_arg_buffer, self.is_args, self.is_init_bc)
                        else:
                            buffer += code_converter.local_put_bytes(var_name, self.method_arg_buffer, self.is_init_bc)
                else:
                    if self.bc_vars_type[var_name] == int:
                        if self.bc_vars_mode[var_name] == Mode.GLOBAL:
                            self.blockchain_methods_inner += code_converter.global_put_int(var_name,
                                                                                           self.method_arg_buffer,
                                                                                           self.is_args, self.is_init_bc)
                        else:
                            self.blockchain_methods_inner += code_converter.local_put_int(var_name,
                                                                                          self.method_arg_buffer, self.is_init_bc)
                    elif self.bc_vars_type[var_name] == str:
                        if self.bc_vars_mode[var_name] == Mode.GLOBAL:
                            self.blockchain_methods_inner += code_converter.global_put_bytes(var_name,
                                                                                             self.method_arg_buffer,
                                                                                             self.is_args, self.is_init_bc)
                        else:
                            self.blockchain_methods_inner += code_converter.local_put_bytes(var_name,
                                                                                            self.method_arg_buffer,
                                                                                            self.is_init_bc)
            elif func_name.find('time') != -1:
                if self.is_args or self.to_buffer:
                    buffer += code_converter.unix_time(self.is_args, True)
                else:
                    self.blockchain_methods_inner += code_converter.unix_time(self.is_args, False)
            elif func_name.find('Txn') != -1 or func_name.find('Global') != -1 or func_name.find('Gtxn') != -1\
                    or func_name.find('get') != -1 or func_name.find('set') != -1:
                if self.is_args:
                    buffer += f"{func_name}({self.method_arg_buffer})"
                elif self.to_buffer:
                    buffer += f"{func_name}({self.method_arg_buffer}),\n"
                else:
                    self.blockchain_methods_inner += f"{func_name}({self.method_arg_buffer}),\n"
            else:
                if self.is_args:
                    buffer += f"{var_name}({self.method_arg_buffer})"
                elif self.to_buffer:
                    buffer += f"{var_name}({self.method_arg_buffer}),\n"
                else:
                    self.blockchain_methods_inner += f"{func_name}({self.method_arg_buffer}),\n"

        if (self.current_scope == "XAll" or self.current_scope == "XOnServer") and buffer == "":
            tabs = tab * self.tab_counter
            call = self.visit(node.func)
            # hard coding
            if len(call.split(".")) > 1:
                func_name = call.split(".")[1]
            else:
                func_name = call

            if hasattr(node.func, "value"):
                var_name = self.visit(node.func.value)
            else:
                var_name = ""

            # rework to have a method call to retrieve value if get_x
            # algo_client.read_variable_state("counter", Mode.Global)
            if var_name in self.bc_vars_mode:
                if func_name.find('get_x') != -1:
                    return f"algo_client.read_variable_state(\"{var_name}\", Mode.{self.bc_vars_mode[var_name]})"
            else:
                if var_name == "":
                    if self.to_buffer:
                        buffer += tabs + f"{func_name}({self.method_arg_buffer})\n"
                    else:
                        self.code += tabs + f"{func_name}({self.method_arg_buffer})\n"
                else:
                    if self.is_args:
                        buffer += f"{var_name}.{func_name}({self.method_arg_buffer}), "
                    elif self.to_buffer:
                        buffer += tabs + f"{var_name}.{func_name}({self.method_arg_buffer})"
                    else:
                        self.code += tabs + f"{var_name}.{func_name}({self.method_arg_buffer})\n"

        return buffer

    def visit_BinOp(self, node):
        buffer = ""
        if self.visit(node.op) == "Concat(":
            buffer += f"Concat({self.visit(node.left)}, {self.visit(node.right)})"
        else:
            buffer += self.visit(node.left)
            buffer += self.visit(node.op)
            buffer += self.visit(node.right)
        return buffer

    def visit_BoolOp(self, node):
        values = ""
        op = self.visit(node.op)
        if self.current_scope == "XOnServer":
            for value in node.values:
                values += self.visit(value) + f" {op} "
            values = values[:-5]
        elif self.current_scope == "XOnBlockchain":
            for value in node.values:
                values += self.visit(value)
            values = op + "(" + f"{values}" + "),"

        return values

    def visit_Add(self, node):
        if not self.is_output:
            return "+"
        else:
            if self.is_output_type == "abi.String":
                return "Concat("
            else:
                return "+"

    def visit_Sub(self, node):
        return "-"

    def visit_Mult(self, node):
        return "*"

    def visit_Div(self, node):
        return "//"

    def visit_Mod(self, node):
        return "%"

    def visit_In(self, node):
        return " in "

    def visit_NotIn(self, node):
        return " not in "

    def visit_Is(self, node):
        return " is "

    def visit_IsNot(self, node):
        return " is not "

    def visit_Delete(self, node):
        return "delete"

    def visit_And(self, node):
        if self.current_scope == "XOnBlockchain":
            return "And"
        elif self.current_scope == "XOnServer":
            return " and "

    def visit_Or(self, node):
        if self.current_scope == "XOnBlockchain":
            return "Or"
        elif self.current_scope == "XOnServer":
            return " or "

    def visit_Constant(self, node):
        if self.current_scope == "XOnBlockchain":
            if type(node.n) == int:
                return f"Int({node.n})"
            if type(node.n) == str:
                return f"Bytes(\"{node.n}\")"
        else:
            if type(node.n) == int or type(node.n) == float:
                return str(node.n)
            if type(node.n) == str:
                return f"\"{node.n}\""

    def visit_Module(self, node):
        for stmt in node.body:
            self.visit(stmt)

    def visit_Attribute(self, node):
        string = ""
        if node.attr in self.bc_vars_mode:
            return node.attr
        string += self.visit(node.value)
        return string + "." + node.attr

    def visit_Tuple(self, node):
        string = ""
        for elt in node.elts:
            string += self.visit(elt) + ", "
        string = string[:-2]
        return string

    # For(loop-start, loop-condition, loop-step).Do(loop-body)
    def visit_For(self, node):
        if self.current_scope == "XOnServer" or self.current_scope == "XAll":
            iter = self.visit(node.iter)
            target = self.visit(node.target)
            tabs = tab * self.tab_counter
            for_stmt = tabs + f"for {target} in {iter}:\n"
            self.code += for_stmt

            self.tab_counter += 1
            for body in node.body:
                self.visit(body)

            self.tab_counter -= 1

        if self.current_scope == "XOnBlockchain" or self.current_scope == "XAll":
            stmt = "Use While Loop"
            return stmt

    def visit_While(self, node):
        self.is_while = True
        match self.current_scope:
            case "XAll":
                self.current_scope = "XOnServer"
                test = self.visit(node.test)
                tabs = tab * self.tab_counter
                while_stmt = tabs + f"while {test}:\n"
                self.code += while_stmt

                self.tab_counter += 1
                for body in node.body:
                    self.visit(body)
                self.tab_counter -= 1

                self.current_scope = "XOnBlockchain"
                self.method_arg_buffer = ""
                test = self.visit(node.test)
                body_stmt = ""
                self.to_buffer = True
                for body in node.body:
                    body_stmt += self.visit(body)

                self.blockchain_methods_inner += f"While({test}).Do({body_stmt}),\n"
                self.is_while = False
            case "XOnServer":
                test = self.visit(node.test)
                tabs = tab * self.tab_counter
                while_stmt = tabs + f"while {test}:\n"
                self.code += while_stmt

                self.tab_counter += 1
                for body in node.body:
                    self.visit(body)

                self.tab_counter -= 1
                self.is_while = False
            case "XOnBlockchain":
                # While(loop-condition).Do(loop-body)
                test = self.visit(node.test)
                body_stmt = ""
                for body in node.body:
                    body_stmt += self.visit(body)
                self.blockchain_methods_inner += f"While({test}).Do({body_stmt}),\n"
                self.is_while = False

    def visit_Assert(self, node):
        self.is_assert = True
        match self.current_scope:
            case "XAll":
                self.current_scope = "XOnBlockchain"
                test = self.visit(node.test)
                self.blockchain_methods_inner += f"Assert({test}),\n"

                self.current_scope = "XOnServer"
                test = self.visit(node.test)
                tabs = tab * self.tab_counter
                ast_stmt = f"assert {test}\n"
                self.code += tabs + ast_stmt

                self.current_scope = "XAll"

            case "XOnBlockchain":
                test = self.visit(node.test)
                self.blockchain_methods_inner += f"Assert({test}),\n"

            case "XOnServer":
                test = self.visit(node.test)
                tabs = tab * self.tab_counter
                ast_stmt = f"assert {test}\n"
                self.code += tabs + ast_stmt

        self.is_assert = False

    def visit_Continue(self, node):
        buffer = ""
        match self.current_scope:
            case "XAll":
                self.blockchain_methods_inner += "Continue(),\n"
                tabs = tab * self.tab_counter
                self.code += tabs + "continue\n"

            case "XOnBlockchain":
                if self.to_buffer:
                    buffer += "Continue(),\n"
                else:
                    self.blockchain_methods_inner += "Continue(),\n"

            case "XOnServer":
                tabs = tab * self.tab_counter
                if self.to_buffer:
                    buffer += tabs + "continue\n"
                else:
                    self.code += tabs + "continue\n"
        return buffer

    def visit_Break(self, node):
        buffer = ""
        match self.current_scope:
            case "XAll":
                self.blockchain_methods_inner += "Break(),\n"
                tabs = tab * self.tab_counter
                self.code += tabs + "break\n"

            case "XOnBlockchain":
                if self.to_buffer:
                    buffer += "Break(),\n"
                else:
                    self.blockchain_methods_inner += "Break(),\n"

            case "XOnServer":
                tabs = tab * self.tab_counter
                if self.to_buffer:
                    buffer += tabs + "break\n"
                else:
                    self.code += tabs + "break\n"

        return buffer

    def visit_Dict(self, node):
        string = ""
        for i in range(len(node.values)):
            key = self.visit(node.keys[i])
            value = self.visit(node.values[i])
            string += f"{key}: {value}, "
        string = string[:-2]
        return "{" + string + "}"

    def visit_AugAssign(self, node):
        self.to_buffer = True
        tabs = tab * self.tab_counter
        var_name = self.visit(node.target)
        value = self.visit(node.value)
        op = self.visit(node.op)
        self.code += tabs + f"{var_name} {op}= {value}\n"
        self.to_buffer = False

    def visit_Assign(self, node):
        self.to_buffer = True
        if isinstance(node.value, ast.Call):
            if self.is_init_bc:
                if node.value.func.id == 'XWrapper':
                    var_name = node.targets[0].attr
                    value = node.value.args[0].n
                    mode = node.value.args[1].attr
                    self.bc_vars_mode[var_name] = mode
                    self.bc_vars_type[var_name] = type(value)

                    if isinstance(node.value.args[0], ast.Str):
                        if mode == Mode.GLOBAL.name:
                            self.blockchain_vars += code_converter.global_put_bytes(var_name, f"Bytes({value})",
                                                                                    self.is_args, self.is_init_bc)
                        elif mode == Mode.LOCAL.name:
                            code_converter.local_put_bytes(var_name, f"Bytes({value})", self.is_init_bc)
                    elif isinstance(node.value.args[0], ast.Num):
                        if mode == Mode.GLOBAL.name:
                            self.blockchain_vars += code_converter.global_put_int(var_name, f"Int({value})",
                                                                                  self.is_args, self.is_init_bc)
                        elif mode == Mode.LOCAL.name:
                            code_converter.local_put_int(var_name, f"Int({value})", self.is_init_bc)
                else:
                    tabs = tab * self.tab_counter
                    assignments = ""

                    for target in node.targets:
                        assignments += self.visit(target) + ", "
                    assignments = assignments[:-2]
                    call = self.visit(node.value)
                    self.code += tabs + f"{assignments} = {call}"
            else:
                if not hasattr(node.value.func, "id"):
                    args = ""
                    for stmt in node.value.args:
                        args += self.visit(stmt)

                    tabs = tab * self.tab_counter

                    var_name = ""
                    for target in node.targets:
                        var_name += self.visit(target)
                    func_call = self.visit(node.value.func)
                    val = ""
                    if len(func_call.split(".")) > 1:
                        val = func_call.split(".")[0]

                    if val in self.bc_vars_mode:
                        value = f"{algo_client}.read_variable_state(\"{val}\", Mode.{self.bc_vars_mode[val]})"
                    else:
                        value = func_call + f"({args})"

                    self.code += tabs + f"{var_name} = {value}\n"
                else:
                    tabs = tab * self.tab_counter
                    assignments = ""

                    for target in node.targets:
                        assignments += self.visit(target) + ", "
                    assignments = assignments[:-2]
                    call = self.visit(node.value)

                    self.code += tabs + f"{assignments} = {call}"
        elif not isinstance(node.value, ast.Call):
            if self.current_scope == "XOnServer" or self.current_scope == "XAll":
                tabs = tab * self.tab_counter
                var_name = ""
                for target in node.targets:
                    var_name += self.visit(target)
                value = self.visit(node.value)
                self.code += tabs + f"{var_name} = {value}\n"
        self.to_buffer = False

    def generate_code(self, node):
        self.visit(node)
        return self.code, self.blockchain_vars


def parse_and_generate_code(input_code):
    bc = ""
    tree = ast.parse(input_code)
    annotated_tree = AnnotationTransformer().visit(tree)
    code_generator = PyTealCodeGenerator()
    server_code, blch_vars = code_generator.generate_code(annotated_tree)

    # handle blockchain code creation
    bc += template_filler.handle_imports()
    bc += template_filler.handle_creation(blch_vars)
    bc += template_filler.handle_update()
    bc += template_filler.handle_delete()
    template_filler.configure_handles()
    bc += template_filler.get_optin()
    bc += template_filler.get_closeout()
    bc += template_filler.router_creation(code_generator.contract_name())
    bc += code_generator.bc_methods()
    bc += template_filler.compile_program()
    with open("generated_code/blockchain_code.py", "w") as f:
        f.write(bc)
    with open("generated_code/server_code.py", "w") as f:
        f.write(server_code)


def get_schema_metrics():
    return code_converter.global_ints, code_converter.global_bytes, \
           code_converter.local_ints, code_converter.local_bytes
