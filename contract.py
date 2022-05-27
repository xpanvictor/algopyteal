from pyteal import *

# Create the constants
seller_key = Bytes("seller_key")
nft_id_key = Bytes("nft_id_key")
start_time_key = Bytes("start_time_key")
end_time_key = Bytes("end_time_key")
reserve_amount_key = Bytes("reserve_amount_key")
min_bid_increment_key = Bytes("min_bid_increment_key")
lead_bid_account_key = Bytes("lead_bid_amount_key")
lead_bid_amount_key = Bytes("lead_bid_amount_key")

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

# On bid code logic
on_bid_txn_index = Txn.group_index() - Int(1)
on_bid_nft_holding = AssetHolding.balance(
    Global.current_application_address(), App.globalGet(nft_id_key)
)
on_bid = Seq(
    on_bid_nft_holding,
    Assert(
        And(
            # we've set the auction
            on_bid_nft_holding.hasValue(),
            on_bid_nft_holding.value() > Int(0),
            # the auction has started
            Global.latest_timestamp() >= App.globalGet(start_time_key),
            # the auction has not ended
            Global.latest_timestamp() < App.globalGet(end_time_key),
            # the actual bid payment is before the app call
            Gtxn[on_bid_txn_index].type_enum() == TxnType.Payment,
            Gtxn[on_bid_txn_index].sender() == Txn.sender(),
            Gtxn[on_bid_txn_index].receiver() ==
            Global.current_application_address(),
            Gtxn[on_bid_txn_index].amount() >= Global.min_txn_fee(),
        )
    ),
    If(
        Gtxn[on_bid_txn_index].amount() >
        App.globalGet(lead_bid_amount_key)
    ).Then(
        Seq(
            If(App.globalGet(lead_bid_account_key))
        )
    )
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
