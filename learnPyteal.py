from pyteal import *

x = Bytes("Content")
y = Concat(Bytes("example "), x)

# print(y)

z = Substring(y, Int(2), Len(y))

# Logging to the chain
Log(x)

# Conditionals with cond
program = Cond(
    [Txn.application_id() == Int(0), on_create],
    [Txn.on_completion() == OnComplete.UpdateApplication, on_update],
    [Txn.on_completion() == OnComplete.DeleteApplication, on_delete],
    [Txn.on_completion() == OnComplete.OptIn, on_opt_in],
    [Txn.on_completion() == OnComplete.CloseOut, on_close_out],
    [Txn.on_completion() == OnComplete.NoOp, on_no_op],
    # If none of the conditions are satisfied, code terminates with error
)

#Conditionals with if else

code = Seq(
    If(App.globalGet(Bytes("count")) == Int(100))
    .Then(
        App.globalPut(Bytes("100th caller"), Txn.sender())
    ).Else(
        App.globalPut(Bytes("Not 100th caller"), Txn.sender())
    ),
    App.globalPut(Bytes("count"), App.globalGet(Bytes("count")) + Int(1)),
    Approve()
)
