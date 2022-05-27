from pyteal import *


# On create code logic
on_create_start_time = Btoi(Txn.application_args[2])
on_create_end_time = Btoi(Txn.application_args[3])
on_create = Seq(
    App.globalPut(Bytes("seller_key"), Txn.application_args[0]),
    App.globalPut(Bytes("nft_id_key"), Txn.application_args[1]),
    App.globalPut(Bytes("start_time_key"), on_create_start_time),
    App.globalPut(Bytes("end_time_key"), on_create_end_time),
    App.globalPut(Bytes("reserve_amount_key"), Btoi(Txn.application_args[4])),
    App.globalPut(Bytes("min_bid_increment_key"), Btoi(Txn.application_args[5])),
    App.globalPut(Bytes("lead_bid_account_key"), Global.zero_address()),
    Assert(
        And(
            Global.latest_timestamp() < on_create_start_time,
            on_create_start_time < on_create_end_time
        )
    ),
    Approve(),
)

# On call routing logic
on_call_method = Txn.application_args[0]
on_call = Cond(
    [on_call_method == Bytes('setup'), on_setup],
    [on_call_method == Bytes('bid'), on_bid]
)

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

