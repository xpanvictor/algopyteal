from pyteal import *


#Create the constants
seller_key = Bytes("seller_key")
nft_id_key = Bytes("nft_id_key")
start_time_key = Bytes("start_time_key")
end_time_key = Bytes("end_time_key")
reserve_amount_key = Bytes("reserve_amount_key")
min_bid_increment_key = Bytes("min_bid_increment_key")
lead_bid_account_key = Bytes("lead_bid_account_key")

# On create code logic
on_create_start_time = Btoi(Txn.application_args[2])
on_create_end_time = Btoi(Txn.application_args[3])
on_create = Seq(
    App.globalPut(seller_key, Txn.application_args[0]),
    App.globalPut(nft_id_key, Txn.application_args[1]),
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

# On setup code logic
on_setup = Seq(
    Assert(Global.latest_timestamp() < App.globalGet(start_time_key)),
    # Build the transaction to hold the nft
    InnerTxnBuilder.Begin(),
    InnerTxnBuilder.SetFields(
        {
            TxnField.type_enum: TxnType.AssetTransfer,
            TxnField.xfer_asset: App.globalGet(nft_id_key),
            TxnField.receiver: Global.current_application_address(),
        }
    ),
    InnerTxnBuilder.Submit(),
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

