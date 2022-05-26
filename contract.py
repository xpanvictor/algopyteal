from pyteal import *

program = Cond(
    [Txn.application_id() == Int(0), on_create],
    [Txn.on_completion() == OnComplete.NoOp, on_call],
    [
        Txn.on_completion() == OnComplete.DeleteApplication,
        on_delete,
    ],
    [
        Or(
            Txn.on_completion() == OnComplete.OptIn,
            Txn.on_completion() == OnComplete.CloseOut,
            Txn.on_completion() == OnComplete.UpdateApplication,
        ),
        Reject(),
    ],
)

on_create_start_time = Btoi(Txn.application_args[2])
on_create_end_time = Btoi(Txn.application_args[3])
on_create = Seq(
    App.globalPut(seller_key, Txn.application_args[0]),
    App.globalPut(nft_id_key, Btoi(Txn.application_args[1])),
    App.globalPut(start_time_key, on_create_start_time),
    App.globalPut(end_time_key, on_create_end_time),
    App.globalPut(reserve_amount_key, Btoi(Txn.application_args[4])),
    App.globalPut(min_bid_increment_key, Btoi(Txn.application_args[5])),
    App.globalPut(lead_bid_account_key, Global.zero_address()),
    Assert(
        And(
            Global.latest_timestamp() < on_create_start_time,
            on_create_start_time < on_create_end_time
        )
    ),
    Approve(),
)
