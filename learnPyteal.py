from pyteal import *

x = Bytes("Content")
y = Concat(Bytes("example "), x)

# print(y)

z = Substring(y, Int(2), Len(y))

# Logging to the chain
Log(x)

# For loops

i = ScratchVar(TealType.uint64)

on_create = Seq(
    For(i.store(Int(0)), i < Int(16), i.store(i.load() + Int(1)))
    .Do(
        App.globalPut(Concat(Bytes("Index"), Itob(i.load())), Int(1))
    ),
    Approve()
)

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

# Conditionals with if else

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


# Subroutines (functions)
@Subroutine(TealType.uint64)
def isEven(i):
    return i % Int(2) == Int(0)


App.globalPut(Bytes("value_is_even"), isEven(Int(10)))


@Subroutine(TealType.uint64)
def recursiveIsEven(i):
    return (
        If(i == Int(0))
        .Then(Int(1))
        .ElseIf(i == Int(1))
        .Then(Int(0))
        .Else(recursiveIsEven(i - Int(2)))
    )


# Escrow account transaction
Seq(
    InnerTxnBuilder.Begin(),
    InnerTxnBuilder.SetFields(
        {
            TxnField.type_enum: TxnType.Payment,
            TxnField.receiver: Txn.sender(),
            TxnField.amount: Int(1_000_000),
        }
    ),
    InnerTxnBuilder.Submit()
    # Sends 1Algo from the app escrow account to the sender account
)