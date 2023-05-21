class TemplateFiller:

    def __init__(self):
        self.no_op = ""
        self.update_application = ""
        self.delete_application = ""
        self.close_out = ""
        self.opt_in = ""

    def handle_imports(self):
        return "from pyteal import *\n"

    # add assert for number of vars
    def handle_creation(self, init):
        return f"""
handle_creation = Seq(
    [
        {init}
        Approve()
    ]
)
"""

    def handle_update(self):
        return f"""
handle_update = Seq(
    [
        If(Global.creator_address() == Txn.sender())
        .Then(Approve())
        .Else(Reject()),
    ]
)
"""

    def handle_delete(self):
        return f"""
handle_delete = Seq(
    [
        If(Global.creator_address() == Txn.sender())
        .Then(Approve())
        .Else(Reject()),
    ]
)
"""

    def handle_close_out(self, inner):
        self.close_out = f"""
close_out = Seq(
    [
        {inner}
    ]
)
"""
        return self.close_out

    def handle_opt_in(self, inner):
        self.opt_in = f"""
opt_in = Seq(
    [
        {inner}
    ]
)        
"""
        return self.opt_in

    def configure_handles(self):
        if self.close_out == "":
            self.close_out = """
close_out = Seq(
    [
        Return(Int(1)),
    ]
)        
"""
        if self.opt_in == "":
            self.opt_in = """
opt_in = Seq(
    [
        Return(Int(1)),
    ]
)        
"""

    def get_optin(self):
        return self.opt_in

    def get_closeout(self):
        return self.close_out

    def router_creation(self, contract_name):
        return f"""
router = Router(
    # Name of the contract
    "{contract_name}",
    # What to do for each on-complete type when no arguments are passed (bare call)
    BareCallActions(
        # On create only, just approve
        no_op=OnCompleteAction.create_only(handle_creation),
        # Always let creator update/delete but only by the creator of this contract
        update_application=OnCompleteAction.always(handle_update),
        delete_application=OnCompleteAction.always(handle_delete),
        close_out=OnCompleteAction.always(close_out),
        opt_in=OnCompleteAction.always(opt_in),
    ),
)
"""

    def create_function(self, method_name, args=""):
        return f"""
@router.method
def {method_name}({args}):

"""

    def fill_function(self, actions):
        return f"""
    return Seq(
        {actions}
    )
"""

    def compile_program(self):
        return """
if __name__ == '__main__':
    # Compile the program
    approval_program, clear_program, contract = router.compile_program(version=6)

    with open("./teal/approval.teal", "w") as f:
        f.write(approval_program)

    with open("./teal/clear.teal", "w") as f:
        f.write(clear_program)

    with open("./teal/contract.json", "w") as f:
        import json

        f.write(json.dumps(contract.dictify()))
"""
