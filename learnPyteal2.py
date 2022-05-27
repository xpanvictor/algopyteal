# The inner transactions
from pyteal import  *

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

# Creating an asset from inner account
appAddr = Global.current_application_address()

Seq(
    InnerTxnBuilder.Begin(),
    InnerTxnBuilder.SetFields(
        {
            TxnField.type_enum: TxnType.AssetConfig,
            TxnField.config_asset_name: Bytes("Bad Coin"),
            TxnField.config_asset_unit_name: Bytes("BC"),
            TxnField.config_asset_url: Bytes("https://badcoin.ng"),
            TxnField.config_asset_decimals: Int(6),
            TxnField.config_asset_total: Int(800_000_000),
            TxnField.config_asset_manager: appAddr
        }
    ),
    InnerTxnBuilder.Submit(), # Creates a bad coin asset
    App.globalPut(Bytes("Bad Coin Id"),
                  InnerTxn.created_asset_id())
    # Remembers the asset's id
)
