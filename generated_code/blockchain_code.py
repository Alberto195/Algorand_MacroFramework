from pyteal import *

handle_creation = Seq(
    [

        Approve()
    ]
)

handle_update = Seq(
    [
        If(Global.creator_address() == Txn.sender())
        .Then(Approve())
        .Else(Reject()),
    ]
)

handle_delete = Seq(
    [
        If(Global.creator_address() == Txn.sender())
        .Then(Approve())
        .Else(Reject()),
    ]
)

opt_in = Seq(
    [
        If(App.localGet(Int(0), Bytes("counter")) == Int(0), ).Then(Return(Int(1)),
                                                                    )
    ]
)

close_out = Seq(
    [
        Return(Int(1)),

    ]
)

router = Router(
    # Name of the contract
    "Counter",
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


@router.method
def increment():

    return Seq(
        App.localPut(Int(0), Bytes("counter"), App.localGet(
            Int(0), Bytes("counter"))+Int(1)),

    )


@router.method
def decrement():

    return Seq(
        App.localPut(Int(0), Bytes("counter"), App.localGet(
            Int(0), Bytes("counter"))-Int(1)),

    )


close_out = Seq(
    [
        Return(Int(1)),

    ]
)

opt_in = Seq(
    [
        If(App.localGet(Int(0), Bytes("counter")) == Int(0), ).Then(Return(Int(1)),
                                                                    )
    ]
)

if __name__ == '__main__':
    # Compile the program
    approval_program, clear_program, contract = router.compile_program(
        version=6)

    with open("./teal/approval.teal", "w") as f:
        f.write(approval_program)

    with open("./teal/clear.teal", "w") as f:
        f.write(clear_program)

    with open("./teal/contract.json", "w") as f:
        import json

        f.write(json.dumps(contract.dictify()))
