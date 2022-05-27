from pyteal import *

# Top level routing
program = Cond(
    [Txn.application_id() == Int(0), on_create],
    [Txn.on_completion() == OnComplete.NoOp, on_call],
    [
        Txn.on_completion() == OnComplete.DeleteApplication,
        on_delete
    ],
    [
        Or(
            Txn.on_completion() == OnComplete.OptIn,
            Txn.on_completion() == OnComplete.CloseOut,
            Txn.on_completion() == OnComplete.UpdateApplication,
        ),
        Reject()
    ],
)

