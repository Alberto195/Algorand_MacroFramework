from pyteal import *

# locals
local_opponent = Bytes("opponent")  # byteslice
local_wager = Bytes("wager")  # uint64
local_commitment = Bytes("commitment")  # byteslice
local_reveal = Bytes("reveal")  # byteslice

op_challenge = Bytes("challenge")
op_accept = Bytes("accept")
op_reveal = Bytes("reveal")


@Subroutine(TealType.none)
def reset(account: Expr):
    return Seq(
        App.localPut(account, local_opponent, Bytes("")),
        App.localPut(account, local_wager, Int(0)),
        App.localPut(account, local_commitment, Bytes("")),
        App.localPut(account, local_reveal, Bytes("")),
    )


@Subroutine(TealType.uint64)
def is_empty(account: Expr):
    return Return(
        And(
            App.localGet(account, local_opponent) == Bytes(""),
            App.localGet(account, local_wager) == Int(0),
            App.localGet(account, local_commitment) == Bytes(""),
            App.localGet(account, local_reveal) == Bytes(""),
        )
    )


@Subroutine(TealType.uint64)
def is_valid_play(p: Expr):
    return Seq(
        Return(
            Or(
                p == Bytes("r"),
                p == Bytes("p"),
                p == Bytes("s"),
            )
        ),
    )



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
        Return(Int(1)),
    ]
)

close_out = Seq(
    [
        Return(Int(0)),
    ]
)

router = Router(
    # Name of the contract
    "RockPaperScissors",
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
def create_challenge(commitment: abi.String):
    return Seq(
        App.localPut(Txn.sender(), local_opponent, Txn.accounts[1]),
        App.localPut(Txn.sender(), local_wager, Gtxn[1].amount()),
        App.localPut(
            Txn.sender(),
            local_commitment,
            commitment.get(),
        ),
        Approve(),
    )


@router.method
def accept_challenge():
    return Seq(
        App.localPut(Int(0), local_opponent, Txn.accounts[1]),
        App.localPut(Int(0), local_wager, Gtxn[1].amount()),
        App.localPut(Int(0), local_reveal, Txn.application_args[1]),
        Approve(),
    )


@Subroutine(TealType.uint64)
def play_value(p: Expr):
    return Seq(
        Return(
            Cond(
                [p == Bytes("r"), Int(0)],
                [p == Bytes("p"), Int(1)],
                [p == Bytes("s"), Int(2)],
            )
        ),
    )


@Subroutine(TealType.uint64)
def winner_account_index(play: Expr, opponent_play: Expr):
    return Return(
        Cond(
            [play == opponent_play, Int(2)],  # tie
            [(play + Int(1)) % Int(3) == opponent_play, Int(1)],  # opponent wins
            [
                (opponent_play + Int(1)) % Int(3) == play,
                Int(0),
            ],  # current account win
        )
    )


@Subroutine(TealType.none)
def send_reward(account_index: Expr, amount: Expr):
    return Seq(
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum: TxnType.Payment,
                TxnField.receiver: Txn.accounts[account_index],
                TxnField.amount: amount,
            }
        ),
        InnerTxnBuilder.Submit(),
    )


@router.method
def reveal():
    return Seq(
        If(winner_account_index(
                play_value(Txn.application_args[1]),
                play_value(App.localGet(Int(1), local_reveal)),
                                                                ) == Int(2))
        .Then(
            Seq(
                # tie: refund wager to each party
                send_reward(Int(0), App.localGet(Int(0), local_wager)),
                send_reward(Int(1), App.localGet(Int(0), local_wager)),
            )
        )
        .Else(
            # send double wager to winner
            send_reward(winner_account_index(
                play_value(Txn.application_args[1]),
                play_value(App.localGet(Int(1), local_reveal)),
            ), App.localGet(Int(0), local_wager) * Int(2))
        ),
        reset(Int(0)),
        reset(Int(1)),
        Approve(),
    )


if __name__ == '__main__':
    # Compile the program
    approval_program, clear_program, contract = router.compile_program(
        version=6)

    with open("../teal/approval.teal", "w") as f:
        f.write(approval_program)

    with open("../teal/clear.teal", "w") as f:
        f.write(clear_program)

    with open("../teal/contract.json", "w") as f:
        import json

        f.write(json.dumps(contract.dictify()))
