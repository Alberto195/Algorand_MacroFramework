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
        Assert(App.localGet(Int(0), Bytes("counter")) > Int(0), ),
        If(Global.round() > Int(10000), ).Then(Return(Int(1)),
                                               )
    ]
)

close_out = Seq(
    [
        If(App.localGet(Int(0), Bytes("counter")) < Int(10), ).Then(App.localPut(Int(0), Bytes("counter"), Int(0)),
                                                                    If(App.localPut(Int(0), Bytes("counter"), Int(0)),
                                                                       ).Then(Return(Int(1)),
                                                                              )).ElseIf(Or(And(App.localGet(Int(0), Bytes("counter")) == Int(11), Global.round() > Int(10000), ),	App.localGet(Int(0), Bytes("counter")) == Int(11), ),).Then(App.localPut(Int(0), Bytes("counter"), Int(5)),
                                                                                                                                                                                                                                              ).Else(App.localPut(Int(0), Bytes("counter"), Int(2)),
                                                                                                                                                                                                                                                     ),

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
        If(App.localGet(Int(0), Bytes("counter")) < Int(10), ).Then(App.localPut(Int(0), Bytes("counter"), Int(0)),
                                                                    If(App.localPut(Int(0), Bytes("counter"), Int(0)),
                                                                       ).Then(Return(Int(1)),
                                                                              )).ElseIf(Or(And(App.localGet(Int(0), Bytes("counter")) == Int(11), Global.round() > Int(10000), ),	App.localGet(Int(0), Bytes("counter")) == Int(11), ),).Then(App.localPut(Int(0), Bytes("counter"), Int(5)),
                                                                                                                                                                                                                                              ).Else(App.localPut(Int(0), Bytes("counter"), Int(2)),
                                                                                                                                                                                                                                                     ),

    ]
)

opt_in = Seq(
    [
        Assert(App.localGet(Int(0), Bytes("counter")) > Int(0), ),
        If(Global.round() > Int(10000), ).Then(Return(Int(1)),
                                               )
    ]
)


@router.method
def match_test():

    return Seq(
        Cond(
            [Global.group_size() == Int(0), Seq([Txn.sender(), Return(Int(1))])],
            [Global.group_size() == Int(1), Return(Int(1))]
        )
    )


@router.method
def nullify():

    return Seq(
        Assert(App.localGet(Int(0), Bytes("counter")) > Int(0), ),
        If(App.localGet(Int(0), Bytes("counter")) == Int(1), ).Then(Break(),
                                                                    ).Else(Continue(),
                                                                           ),
        While(App.localGet(Int(0), Bytes("counter")) > Int(0), ).Do(If(App.localGet(Int(0), Bytes("counter")) == Int(1), ).Then(Break(),
                                                                                                                                ).Else(Continue(),
                                                                                                                                       ),
                                                                    ),

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
