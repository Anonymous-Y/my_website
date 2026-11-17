---
title: "Decoding the Digital Tea Leaves: A Guide to Analyzing Polymarket's On-Chain Order Data"
date: 2025-11-12
permalink: /x01Crypto/decoding-polymarket
tags:
    - polymarket
    - blockchain
    - prediction market
excerpt: "A beginner's guide to understanding polymarket's on-chain order data."
read_time: true
---

What if you could tap directly into the collective wisdom of thousands of speculators on major world events? Welcome to the world of Polymarket, a leading decentralized prediction market on the Polygon network. It's more than just a betting platform; it's a real-time, transparent feed of user sentiment, with every prediction, trade, and transaction permanently etched onto the blockchain.

By learning to read this on-chain data, you can unlock unparalleled insights into market dynamics, user behavior, and the intricate mechanics of decentralized finance. Whether you're a data analyst, a crypto enthusiast, or a seasoned bettor, this guide will equip you with the skills to navigate Polymarket's on-chain world.

This article will break down how to access and interpret Polymarket's on-chain order data, transforming you from a casual observer into a savvy on-chain analyst.

## I. The On-Chain Foundation: Essential Background Knowledge

Before we dive into the data, it's crucial to understand the smart contracts that power Polymarket. Think of these as the digital bedrock upon which the entire platform is built.

### Key Smart Contracts

To navigate Polymarket's on-chain presence, familiarize yourself with these primary smart contract addresses on the Polygon network and their roles:

| **Contract Name/Role**                 | **Polygon Address**                          | **Notes**                                                    |
| -------------------------------------- | -------------------------------------------- | ------------------------------------------------------------ |
| **Conditional Tokens Framework (CTF)** | `0x4D97DCd97eC945f40cF65F87097ACe5EA0476045` | The core Gnosis contract for creating and managing ERC-1155 outcome tokens. This is the engine that generates the very tokens you'll be analyzing. |
| **CTF Exchange**                       | `0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E` | The main exchange for settling trades in standard binary (YES/NO) markets through atomic swaps of outcome tokens and USDC. |
| **NegRisk_CTFExchange**                | `0xC5d563A36AE78145C45a50134d48A1215220f80a` | A specialized exchange for the more complex multi-outcome markets that utilize the `NegRiskAdapter`. |
| **NegRiskAdapter**                     | `0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296` | A key innovation that adapts the Gnosis CTF for multi-outcome markets by structuring them from underlying binary components, cleverly managing "NO" to "YES" token conversions. |
| **USDC.e (Collateral)**                | `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174` | The bridged USDC stablecoin used as the universal collateral for betting and payouts on the platform. |
| **UMA Oracle (V2.0.0)**                | `0x6A9D222616C90FcA5754cd1333cFD9b7fb6a4F74` | The decentralized oracle responsible for the crucial task of resolving market outcomes. |
| **Gnosis Safe Proxy Factory**          | `0xaacfeea03eb1561c4e67d661e40682bd20e3541b` | Creates proxy wallets for users interacting with Polymarket via MetaMask. |
| **Polymarket Proxy Factory**           | `0xaB45c5A4B0c941a2F231C04C3f49182e1A254052` | Creates proxy wallets for users who sign up and interact using MagicLink. |
| **Polymarket: Neg Risk Fee Module**    | `0x78769D50Be1763ed1CA0D5E878D93f05aabff29e` | This contract works with the `NegRisk_CTFExchange` to apply the correct fee logic for trades in multi-outcome markets. |

**Note**：`0xaB45c54AB0c941a2F231C04C3f49182e1A254052` ('..54A..' instead of '..5A4..') is labelled as the `Polymarket proxy factory` in [Polymarket Official Documents](https://docs.polymarket.com/developers/proxy-wallet). This is most likely a typo, since this address is not a smart contract ([source](https://polygonscan.com/address/0xaB45c54aB0C941A2f231c04C3f49182E1A254052)). The correct address is listed on Polymarket Github page ([source](https://github.com/Polymarket/proxy-factories)).

**Who emits what?**

All trading activity on Polymarket is settled through two main contracts: the `CTF Exchange` for simple binary markets (i.e., YES/NO), and the `NegRisk_CTFExchange` for more complex, multi-outcome markets.  Traders' positions are managed through `CTF` and `NegRiskAdapter`. The events emitted by these contracts are we'll be focusing on.

`CTF Exchange` / `NegRisk_CTFExchange` $\rightarrow$ Order-related events (`OrderFilled`, `OrdersMatched`)
`CTF` and `NegRiskAdapter` $\rightarrow$ Position-related events (`PositionsSplit`, `PositionsMerge`)
`NegRiskAdapter` $\rightarrow$ Position Conversion events (`PositionsConverted`)

### The Lifecycle of an Outcome Token

Before we analyze trades, we need to understand what is being traded. Polymarket uses the Gnosis Conditional Tokens Framework to represent market outcomes. There are two different prediction markets. 

(1) Single-outcome prediction market, like "Will Candidate A win the election?".

Polymarket creates a pair of outcome tokens: a "YES" token and a "NO" token. Each pair is backed by **1 USDC** of collateral. These outcome tokens have a unique on-chain ID, the `positionId`, ensuring each token is tied to a specific outcome of a specific event. If Candidate A wins, the holders of the "YES" token can redeem it for the full 1 USDC of collateral. If Candidate A loses, the "NO" token holders get the 1 USDC.

(2) Multi-outcome prediction market, like "Who will win the election?".

In this market, bettors can purchases (YES, NO) outcome tokens for multiple candidates. Each outcome token is tied to a specific `positionId`. If Candidate A wins, the holders of Candidate A "YES" tokens, Candidate B "NO" tokens, Candidate C "NO" tokens...can redeem their tokens for 1 USDC/token. The holders of Candidate A "NO" tokens, Candidate B "YES" tokens, Candidate C "YES" tokens...get nothing. 

**Token Minting (Creation):**

Imagine two bettors with opposing views:

- Bettor X is willing to pay 0.70 USDC for a "YES" token.
- Bettor Y is willing to pay 0.30 USDC for a "NO" token.

Polymarket's matching engine brings them together. Their combined 1 USDC (0.70 + 0.30) is locked as collateral, and a new pair of "YES" and "NO" tokens is **minted**. Bettor X receives the "YES" token, and Bettor Y receives the "NO" token. 

For single-outcome markets (i.e. Will Candidate A win the election?), the activity is recorded in the log emitted by `CTF` smart contract under the event name `PositionSplit`.

For multi-outcome markets (i.e. Who will win the election?), smart contract `NegRiskAdapter` calls `CTF` to initiate the operation. Hence, this activity is recorded in the logs emitted by both `CTF` and `NegRiskAdapter` under the event name `PositionSplit`.

**Token Matching**

Bettors don't have to wait for the market to resolve. They can sell their outcome tokens at any time. A sell order can be matched with a buy order from another bettor.

For example:

- Bettor A wants to sell 1000 "YES" tokens for 0.60 USDC.
- Bettor B wants to buy 600 "YES" tokens for 0.60 USDC.
- Bettor C wants to buy 400 "YES" tokens for 0.60 USDC.

In a single-outcome market, the smart contract `CTF Exchange` will match these three orders togher. In a multi-outcome market, this job is conducted by the smart contract `NegRisk_CTFExchange`. These activities are recorded in two events: `OrderFilled` and `OrderMatched`.


**Token Burning (Merge):**

Besides being match with an opposite position, a sell order for a "YES" ("NO") token can also be matched with a sell order for the corresponding "NO" ("YES") token.

For example:

- Bettor A wants to sell a "YES" token for 0.60 USDC.
- Bettor B wants to sell a "NO" token for 0.40 USDC.

The exchange can match these two sell orders. The pair of outcome tokens is **burned** (Polymarket calls this operation **Merge**), and the 1 USDC of collateral is released: 0.60 USDC goes to Bettor A, and 0.40 USDC goes to Bettor B.

Similar to Token Minting, for single-outcome markets (i.e. Will Candidate A win the election?), the activity is recorded in the log emitted by `CTF` smart contract under the event name `PositionsMerge`.

For multi-outcome markets (i.e. Who will win the election?), smart contract `NegRiskAdapter` calls `CTF` to initiate the operation. Hence, this activity is recorded in the logs emitted by both `CTF` and `NegRiskAdapter` under the event name `PositionsMerge`.


**Token Conversion**

The activity, Token Conversion, is a useful operation in multi-outcome markets to enhance capital efficiency, and maintian the price consistency between different outcomes inside this prediction market. 

Consider a market for an election with three candidates: A, B, and C, where exactly one will win. A trader holds a portfolio consisting of `1 "NO A"` token and `1 "NO B"` token. The value of this portfolio can be analyzed under all three possible resolution scenarios:

- **Scenario 1: Candidate A wins.** The `1 "NO A"` token becomes worthless (0 USDC), while the `1 "NO B"` token redeems for 1 USDC. The total portfolio value is 1 USDC.
- **Scenario 2: Candidate B wins.** The `1 "NO A"` token redeems for 1 USDC, while the `1 "NO B"` token becomes worthless (0 USDC). The total portfolio value is 1 USDC.
- **Scenario 3: Candidate C wins.** Both the `1 "NO A"` token and the `1 "NO B"` token redeem for 1 USDC each. The total portfolio value is 2 USDC.

Now, consider an alternative portfolio: `1 "YES C"` token plus `1 USDC` held as collateral. Its value at resolution is:

- **Scenario 1: Candidate A wins.** The `1 "YES C"` token is worthless (0 USDC). The total portfolio value is 0 USDC + 1 USDC USDC = 1 USDC.
- **Scenario 2: Candidate B wins.** The `1 "YES C"` token is worthless (0 USDC). The total portfolio value is 0 USDC + 1 USDC USDC = 1 USDC.
- **Scenario 3: Candidate C wins.** The `1 "YES C"` token redeems for 1 USDC. The total portfolio value is 1 USDC + 1 USDC USDC = 2 USDC.

The payoff structures are identical. The two portfolios are economically equivalent. The `NegRiskAdapter` smart contract exists precisely to allow a user to atomically transform the first portfolio (`1 "NO A"` + `1 "NO B"`) into the second, more expressive and often more capital-efficient portfolio (`1 "YES C"` + `1 USDC`). 

Now, consider another case. For some reasons, the market suddenly has a high demand on Candidate A's `"YES A"` token. Arbitrageurs can convert their `"NO B"`, `"NO C"` tokens into `"YES A"` tokens to maintain the prices consistency between `"YES A"`, `"NO B"` and `"NO C"`.

**Where are the records?**

Token Matching activities are precisely recorded in events `OrderFilled` and `OrdersMatched`, which are emitted by smart contracts `NegRisk_CTFExchange` (multi-outcome markets) or `CTF Exchange` (binary markets).

Token Minting and Token Burning activities can be deduced from events `OrderFilled` and `OrdersMatched`, and are also precisely recorded in events `PositionSplit` and `PositionsMerge`, which are emitted by smart contracts `NegRiskAdapter` and `CTF`.

Token conversion activites can only be found through event `PositionsConverted`, which are emitted by smart contracts `NegRiskAdapter`.


## II. Accessing the Data: Your On-Chain Toolkit

There are two primary ways to access Polymarket's on-chain data:

1. **Directly from the Blockchain:** By querying a Polygon RPC endpoint. This method gives you raw, unfiltered access to the data.
2. **Using The Graph:** A decentralized indexing protocol that makes querying blockchain data much simpler and more efficient. For beginners, this is the recommended starting point.

In this article, we will focus on the direct RPC method to understand the fundamentals, be aware that tools like The Graph can significantly speed up your analysis.

To extract Polymarket order data for a specific prediction market, we need to examine transactions involving either the `CTF Exchange` or `NegRisk_CTFExchange` contracts when they execute the `matchOrders` function. You can find these activities in transactions' `logs` section on [PolygonScan](https://polygonscan.com/).

There are two primary methods to access settled Polymarket order data:

1. **Transaction Input Data:** Analyzing the `input data` section of transactions where either exchange contract executes the `matchOrders` function.
2. **Event Logs:** Examining the `OrderFilled` and `OrdersMatched` event logs emitted by these exchange contracts.

I recommend the second method for most use cases. While the first method shows the original order amounts, it doesn't reflect the actual settled amounts in each specific transaction. This is because a single order maker can serve as a liquidity provider across multiple separate transactions, making it harder to track individual trade executions.

The analysis procedures are nearly identical for both `CTF Exchange` and `NegRisk_CTFExchange`. For consistency, I'll use `NegRisk_CTFExchange` in the following examples. If you're analyzing data from binary outcome prediction markets, simply substitute the `NegRisk_CTFExchange` address with the `CTF Exchange` address and use the corresponding ABI file for data decoding.

### Tapping into the Blockchain with Python

First, you'll need to connect to a Polygon RPC (Remote Procedure Call) endpoint. Public RPCs, like [https://polygon-rpc.com](https://polygon-rpc.com), are a good starting point but may have rate limits. For more intensive analysis, consider private RPCs from providers like [Ankr](https://www.ankr.com/), [Alchemy](https://www.alchemy.com/), and [Infura](https://www.infura.io/).

Here's how you can fetch transaction logs using Python and the `web3` library:

```python
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

# Establish connection to a Polygon RPC endpoint
POLYGON_RPC_URL = "https://polygon-rpc.com/"
web3 = Web3(Web3.HTTPProvider(POLYGON_RPC_URL))

# Polygon uses a Proof-of-Authority consensus mechanism, so we need to inject this middleware
web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

# Define the block number and the target contract address we want to inspect
block_number = 51866068
# For this example, we'll look at the exchange for multi-outcome markets
TARGET_ADDRESS = "0xc5d563a36ae78145c45a50134d48A1215220f80a" # NegRisk_CTFExchange address

# Fetch all logs for the target address within the specified block range
logs = web3.eth.get_logs({
    'fromBlock': block_number,
    'toBlock': block_number,
    'address': Web3.to_checksum_address(TARGET_ADDRESS)
})

print(logs)
```

Running this script will return a list of logs, which at first glance might seem like gibberish:
```json
 [AttributeDict({'address': '0xC5d563A36AE78145C45a50134d48A1215220f80a',
  'topics': [HexBytes('0xd0a08e8c493f9c94f29311604c9de1b4e8c8d4c06bd0c789af57f2d65bfec0f6'),
   HexBytes('0x83b04dd4f7591c60e21694ce5808587fa5a331bb958994389ce95eddfdb148c6'),
   HexBytes('0x0000000000000000000000003cf3e8d5427aed066a7a5926980600f6c3cf87b3'),
   HexBytes('0x000000000000000000000000d42f6a1634a3707e27cbae14ca966068e5d1047d')],
  'data': HexBytes('0x6f3dc129ae1b3a62bd59c83235f421bb772d0bca3038a6f36df840e6577aab88000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000009896800000000000000000000000000000000000000000000000000000000000325aa00000000000000000000000000000000000000000000000000000000000000000'),
  'blockNumber': 51866068,
  'transactionHash': HexBytes('0x73ca58d58325b5cbb369588671844dd555dcb33723497e96097b196b8bdfdcd8'),
  'transactionIndex': 7,
  'blockHash': HexBytes('0xa2299601b0134f9e8c4107a401b5b9f899446f31cac59bb8ce1490f2271c59cc'),
  'logIndex': 25,
  'removed': False}),

 AttributeDict({'address': '0xC5d563A36AE78145C45a50134d48A1215220f80a',
  'topics': [HexBytes('0xd0a08e8c493f9c94f29311604c9de1b4e8c8d4c06bd0c789af57f2d65bfec0f6'),
   HexBytes('0x55a5da3494e8670f67e8952b61ea620bf0939a84065671ba2f4e2930653a7d3c'),
   HexBytes('0x000000000000000000000000d42f6a1634a3707e27cbae14ca966068e5d1047d'),
   HexBytes('0x000000000000000000000000c5d563a36ae78145c45a50134d48a1215220f80a')],
  'data': HexBytes('0x00000000000000000000000000000000000000000000000000000000000000006f3dc129ae1b3a62bd59c83235f421bb772d0bca3038a6f36df840e6577aab880000000000000000000000000000000000000000000000000000000000325aa000000000000000000000000000000000000000000000000000000000009896800000000000000000000000000000000000000000000000000000000000000000'),
  'blockNumber': 51866068,
  'transactionHash': HexBytes('0x73ca58d58325b5cbb369588671844dd555dcb33723497e96097b196b8bdfdcd8'),
  'transactionIndex': 7,
  'blockHash': HexBytes('0xa2299601b0134f9e8c4107a401b5b9f899446f31cac59bb8ce1490f2271c59cc'),
  'logIndex': 27,
  'removed': False}),

 AttributeDict({'address': '0xC5d563A36AE78145C45a50134d48A1215220f80a',
  'topics': [HexBytes('0x63bf4d16b7fa898ef4c4b2b6d90fd201e9c56313b65638af6088d149d2ce956c'),
   HexBytes('0x55a5da3494e8670f67e8952b61ea620bf0939a84065671ba2f4e2930653a7d3c'),
   HexBytes('0x000000000000000000000000d42f6a1634a3707e27cbae14ca966068e5d1047d')],
  'data': HexBytes('0x00000000000000000000000000000000000000000000000000000000000000006f3dc129ae1b3a62bd59c83235f421bb772d0bca3038a6f36df840e6577aab880000000000000000000000000000000000000000000000000000000000325aa00000000000000000000000000000000000000000000000000000000000989680'),
  'blockNumber': 51866068,
  'transactionHash': HexBytes('0x73ca58d58325b5cbb369588671844dd555dcb33723497e96097b196b8bdfdcd8'),
  'transactionIndex': 7,
  'blockHash': HexBytes('0xa2299601b0134f9e8c4107a401b5b9f899446f31cac59bb8ce1490f2271c59cc'),
  'logIndex': 28,
  'removed': False})]
```
These logs contain the `topics` and `data` fields, which hold the key to understanding each transaction. To decipher them, we need the contract's **ABI**.

### Decoding the Data with an ABI

An ABI (Application Binary Interface) is a JSON file that acts as a blueprint for a smart contract. It tells us how to interpret the contract's functions and events. You can find the ABI for any verified contract on PolygonScan. For the `NegRisk_CTFExchange`, you can find it on its contract page under the "Contract" tab.

Once you have the ABI file (e.g., `Polymarket_NegRisk_CTFExchange_abi.json`), you can use the following Python code to decode the logs into a human-readable format:

（1）First, we create an event signature mapping, so we can translate items like `HexBytes('0xd0a08e8c493f9c94f29311604c9de1b4e8c8d4c06bd0c789af57f2d65bfec0f6')` into the event name that we can read.

```python
from web3 import Web3
w3 = Web3()
# Load the ABI
with open('Polymarket_NegRisk_CTFExchange_abi.json', 'r') as abi_file:
    contract_abi = json.load(abi_file)

contract_address = '0xC5d563A36AE78145C45a50134d48A1215220f80a' # NegRisk_CTFExchange address
contract_address = Web3.to_checksum_address(contract_address) 
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Create Event Signature Mapping
event_signature_to_event = {}
for abi_item in contract_abi:
    if abi_item['type'] == 'event':
        event_obj = contract.events.__getattr__(abi_item['name'])()
        # Create event signature string and hash it
        event_signature = f"{abi_item['name']}({','.join([param['type'] for param in abi_item['inputs']])})"
        signature_hash = Web3.keccak(text=event_signature)
        signature_hash = '0x' + signature_hash.hex() # convert to hex
        event_signature_to_event[signature_hash] = event_obj
```
We get a mapping between the event IDs and the events inside this contract:
```json
{'0xacffcc86834d0f1a64b0d5a675798deed6ff0bcfc2231edd3480e7288dba7ff4': <Event FeeCharged(address,uint256,uint256)>,
 '0xf9ffabca9c8276e99321725bcb43fb076a6c66a54b7f21c4e8146d8519b417dc': <Event NewAdmin(address,address)>,
 '0xf1e04d73c4304b5ff164f9d10c7473e2a1593b740674a6107975e2a7001c1e5c': <Event NewOperator(address,address)>,
 '0x5152abf959f6564662358c2e52b702259b78bac5ee7842a0f01937e670efcc7d': <Event OrderCancelled(bytes32)>,
 '0xd0a08e8c493f9c94f29311604c9de1b4e8c8d4c06bd0c789af57f2d65bfec0f6': <Event OrderFilled(bytes32,address,address,uint256,uint256,uint256,uint256,uint256)>,
 '0x63bf4d16b7fa898ef4c4b2b6d90fd201e9c56313b65638af6088d149d2ce956c': <Event OrdersMatched(bytes32,address,uint256,uint256,uint256,uint256)>,
 '0x3053c6252a932554235c173caffc1913604dba3a41cee89516f631c4a1a50a37': <Event ProxyFactoryUpdated(address,address)>,
 '0x787a2e12f4a55b658b8f573c32432ee11a5e8b51677d1e1e937aaf6a0bb5776e': <Event RemovedAdmin(address,address)>,
 '0xf7262ed0443cc211121ceb1a80d69004f319245615a7488f951f1437fd91642c': <Event RemovedOperator(address,address)>,
 '0x9726d7faf7429d6b059560dc858ed769377ccdf8b7541eabe12b22548719831f': <Event SafeFactoryUpdated(address,address)>,
 '0xbc9a2432e8aeb48327246cddd6e872ef452812b4243c04e6bfb786a2cd8faf0d': <Event TokenRegistered(uint256,uint256,bytes32)>,
 '0x203c4bd3e526634f661575359ff30de3b0edaba6c2cb1eac60f730b6d2d9d536': <Event TradingPaused(address)>,
 '0xa1e8a54850dbd7f520bcc09f47bff152294b77b2081da545a7adf531b7ea283b': <Event TradingUnpaused(address)>}
```

Now we know in the above two event logs: 
`0xd0a08e8c493f9c94f29311604c9de1b4e8c8d4c06bd0c789af57f2d65bfec0f6` is a `OrderFilled` event, and `0x63bf4d16b7fa898ef4c4b2b6d90fd201e9c56313b65638af6088d149d2ce956c` is a `OrdersMatched` event.

（2）Second, we can now decode the whole `topic` and `data` sections:
```python
# Define the Decoding Function
def decode_log(raw_log, event_signature_to_event):
    event_signature = '0x' + raw_log['topics'][0].hex()
    event = event_signature_to_event.get(event_signature)

    log_dict = {
        'address': raw_log['address'], 
        'topics': raw_log['topics'],
        'data': raw_log['data'],
        'blockNumber': raw_log['blockNumber'],
        'blockHash': raw_log['blockHash'],
        'transactionHash': raw_log['transactionHash'],
        'transactionIndex': raw_log['transactionIndex'],
        'logIndex': raw_log['logIndex'],
    }
    
    decoded = event.process_log(log_dict)
    decoded_args = decoded['args']
    decoded_args['event'] = decoded['event']
    return decoded_args

# Apply the Decoding Function
# (1) raw_log 1 and 2 are OrderFilled event
raw_log_1 = logs[0]
decoded_log_1 = decode_log(raw_log_1, event_signature_to_event)
# convert orderHash from bytes to hex
decoded_log_1['orderHash'] = '0x' + decoded_log_1['orderHash'].hex()

raw_log_2 = logs[1]
decoded_log_2 = decode_log(raw_log_2, event_signature_to_event)
decoded_log_2['orderHash'] = '0x' + decoded_log_2['orderHash'].hex()

# (2) raw_log 3 is OrderMatched event
raw_log_3 = logs[2]
decoded_log_3 = decode_log(raw_log_3, event_signature_to_event)
# convert takerOrderHash from bytes to hex
decoded_log_3['takerOrderHash'] = '0x' + decoded_log_3['takerOrderHash'].hex()
```
Now the `topic` and `data` sections in the above three logs can be fully decoded into:
```json
{'orderHash': '0x83b04dd4f7591c60e21694ce5808587fa5a331bb958994389ce95eddfdb148c6',
 'maker': '0x3Cf3E8d5427aED066a7A5926980600f6C3Cf87B3',
 'taker': '0xd42F6a1634A3707e27cBae14ca966068E5D1047d',
 'makerAssetId': 50315837024432334213827041057729556211989649223066002327303150792784314280840,
 'takerAssetId': 0,
 'makerAmountFilled': 10000000,
 'takerAmountFilled': 3300000,
 'fee': 0,
 'event': 'OrderFilled'}

{'orderHash': '0x55a5da3494e8670f67e8952b61ea620bf0939a84065671ba2f4e2930653a7d3c',
 'maker': '0xd42F6a1634A3707e27cBae14ca966068E5D1047d',
 'taker': '0xC5d563A36AE78145C45a50134d48A1215220f80a',
 'makerAssetId': 0,
 'takerAssetId': 50315837024432334213827041057729556211989649223066002327303150792784314280840,
 'makerAmountFilled': 3300000,
 'takerAmountFilled': 10000000,
 'fee': 0,
 'event': 'OrderFilled'}

{'takerOrderHash': '0x55a5da3494e8670f67e8952b61ea620bf0939a84065671ba2f4e2930653a7d3c',
 'takerOrderMaker': '0xd42F6a1634A3707e27cBae14ca966068E5D1047d',
 'makerAssetId': 0,
 'takerAssetId': 50315837024432334213827041057729556211989649223066002327303150792784314280840,
 'makerAmountFilled': 3300000,
 'takerAmountFilled': 10000000,
 'event': 'OrdersMatched'}
```
We now have a much clearer, structured output of the event's data.

## III. Interpreting the Data: `OrderFilled` and `OrdersMatched` Events

When you decode the logs emitted by `NegRisk_CTFExchange`, you'll primarily be dealing with two types of events: `OrderFilled` and `OrdersMatched`.

### The `OrderFilled` Event

This event is emitted for each individual order that is filled or partially filled. Let's break down its key fields:

- **`orderHash`**: A unique identifier for the order.
- **`maker`**: The address of the user who placed the limit order (the liquidity provider).
- **`taker`**: The address that filled the order. This can be another user or the exchange contract itself if multiple orders are matched.
- **`makerAssetId`**: The ID of the asset the maker is providing. If it's `0`, the maker is offering USDC (a **Buy** order for an outcome token). If it's a long number (the `positionId`), the maker is offering an outcome token (a **Sell** order).
- **`takerAssetId`**: The ID of the asset the taker is providing. The logic is the inverse of `makerAssetId`.
- **`makerAmountFilled`**: The amount of the asset the maker has given out.
- **`takerAmountFilled`**: The amount of the asset the taker has given out.

**Example Interpretation:**

```json
{   
    'orderHash': '0x83b04dd4f7591c60e21694ce5808587fa5a331bb958994389ce95eddfdb148c6',
    'maker': '0x3Cf3E8d5427aED066a7A5926980600f6C3Cf87B3',
    'taker': '0xd42F6a1634A3707e27cBae14ca966068E5D1047d',
    'makerAssetId': 50315837024432334213827041057729556211989649223066002327303150792784314280840,
    'takerAssetId': 0,
    'makerAmountFilled': 10000000,   // 10 outcome tokens (10 * 10^6)
    'takerAmountFilled': 3300000,   // 3.3 USDC (3.3 * 10^6)
    'fee': 0,
    'event': 'OrderFilled'
}
```
- **The Maker (`0x3Cf3...`)** initiated a **SELL** order, providing **outcome tokens** (`makerAssetId` is not zero).
- **The Taker (`0xd42F...`)** filled this order, providing **USDC** (`takerAssetId` is zero).
- **The Trade:** The maker sold **10 outcome tokens** and received **3.3 USDC** in return.

### The `OrdersMatched` Event

```json
{
    'takerOrderHash': '0x55a5da3494e8670f67e8952b61ea620bf0939a84065671ba2f4e2930653a7d3c',
    'takerOrderMaker': '0xd42F6a1634A3707e27cBae14ca966068E5D1047d',
    'makerAssetId': 0,
    'takerAssetId': 50315837024432334213827041057729556211989649223066002327303150792784314280840,
    'makerAmountFilled': 3300000,
    'takerAmountFilled': 10000000,
    'event': 'OrdersMatched'
}
```

This event provides a summary when two or more orders are matched. It links the buy and sell orders together. This log shows that in the above matched order, the order taker is `0xd42F...`. The taker provids USDC (`makerAssetId: 0`) and buys token `5031...` in this transaction. 

When an `OrdersMatched` event occurs, you will always see at least two corresponding `OrderFilled` events—one for the buyer and one for the seller.


## IV. Interpreting the Data: `PositionsSplit`, `PositionsMerge` and `PositionsConverted` Events

Even though the token minting and burning activities can be deduced through the `OrderFilled` event records. We can directly access related information through `PositionsSplit`, `PositionsMerge` events emitted by `NegRiskAdapter` (or `CTF`). Meanwhile, we can access the  `PositionsConverted` events to know which outcome's NO tokens are converted to which outcome's YES tokens via `indexSet`. 

You can follow the same steps described in part II to download related information. The difference is now we need to look for the logs emitted by smart contract `NegRiskAdapter` instead of `NegRisk_CTFExchange`.

Let's break down its key fields:

- **`address`**: This is the address of smart contract `NegRiskAdapter`
- **`marketId`**: Indicate a signle outcome (i.e., Will candidate A win the election?) in the multi-outcome prediction market.
- **`amount`**: Number of token pairs or USDC
- **`event`**: `PositionsSplit`, `PositionsMerge` or `PositionsConverted`
- **`indexSet`**: indicates which NO tokens are converted to which YES tokens in `PositionsConverted` events.

### The `PositionSplit` Event

```json
{
  'log_index': 290,
  'transaction_hash': '0x165f9e720e0ad1b485d436f206603bbab2ec100f66317bf0cdaeffe8e543df2e',
  'transaction_index': 53,
  'address': '0xd91e80cf2e7be2e162c6513ced06f1dd0da35296',
  'data': '0x000000000000000000000000000000000000000000000000000000000bebc200',
  'topics': [
    '0xbbed930dbfb7907ae2d60ddf78345610214f26419a0128df39b6cc3d9e5df9b0',
    '0x000000000000000000000000c5d563a36ae78145c45a50134d48a1215220f80a',
    '0x40bbdd26dc08406eedcb913efee7f7faddf50e16fc21caedb4972d57fd71e0d1'
  ],
  'block_timestamp': '2024-01-05 02:06:46 UTC',
  'block_number': 51950841,
  'block_hash': '0x6adab81b6f582b1362a416a65759030d83d7e8141f0f1cc564fd58571ac30a3b',
  'decoded_args': {
    'stakeholder': '0xC5d563A36AE78145C45a50134d48A1215220f80a',
    'conditionId': '0x40bbdd26dc08406eedcb913efee7f7faddf50e16fc21caedb4972d57fd71e0d1',
    'amount': 200000000,
    'event': 'PositionSplit'
  }
}
```


### The `PositionsMerge` Event

```json
{
  'log_index': 193,
  'transaction_hash': '0x7af18fe1592c70f01f5e63e099447d0537fd59c7c3f16c9b7de2b8d00a109262',
  'transaction_index': 45,
  'address': '0xd91e80cf2e7be2e162c6513ced06f1dd0da35296',
  'data': '0x0000000000000000000000000000000000000000000000000000000000989680',
  'topics': [
    '0xba33ac50d8894676597e6e35dc09cff59854708b642cd069d21eb9c7ca072a04',
    '0x0000000000000000000000000d0107a300f01d1786a1c018fb5e75f476184c04',
    '0xbdc8ad55cb8fa7b3c84a971d6056f6a0f354f0f882c3fab598abae19d4e60a5e'
  ],
  'block_timestamp': '2024-01-04 01:20:15 UTC',
  'block_number': 51911521,
  'block_hash': '0x9f70299f9ae3398e519cf436534bdad2a0d1e09fbd29b2be9147cd4110b2c599',
  'decoded_args': {
    'stakeholder': '0x0d0107a300F01d1786A1C018FB5E75F476184c04',
    'conditionId': '0xbdc8ad55cb8fa7b3c84a971d6056f6a0f354f0f882c3fab598abae19d4e60a5e',
    'amount': 10000000,
    'event': 'PositionsMerge'
  }
}
```

### The `PositionsConverted` Event

```json
{
  'log_index': 160,
  'transaction_hash': '0x461219b6056b0d57d60a334fc9a1ffd92edfd957453dd692302478b67d98cb3d',
  'transaction_index': 27,
  'address': '0xd91e80cf2e7be2e162c6513ced06f1dd0da35296',
  'data': '0x0000000000000000000000000000000000000000000000000000000000989680',
  'topics': [
    '0xb03d19dddbc72a87e735ff0ea3b57bef133ebe44e1894284916a84044deb367e',
    '0x000000000000000000000000ff66a0ada4122c5d9292ffb7ec02922d167a7a07',
    '0xe3b1bc389210504ebcb9cffe4b0ed06ccac50561e0f24abb6379984cec030f00',
    '0x0000000000000000000000000000000000000000000000000000000000000001'
  ],
  'block_timestamp': '2024-01-05 08:29:52 UTC',
  'block_number': 51961107,
  'block_hash': '0xacfd425f86a0935f52ed8458b5ababb134e89337d25dde0fe31fd454cee6e06a',
  'decoded_args': {
    'stakeholder': '0xff66A0aDa4122C5d9292Ffb7eC02922d167a7A07',
    'marketId': '0xe3b1bc389210504ebcb9cffe4b0ed06ccac50561e0f24abb6379984cec030f00',
    'indexSet': 1,
    'amount': 10000000,
    'event': 'PositionsConverted'
  }
}
```


**How to interpret the indexSet data?**

the `indexSet` in this event is a bitmask representing the collection of "NO" tokens being supplied as input. Each bit position corresponds to a specific outcome within the market. If a bit is set to `1`, it signifies that the "NO" token for that corresponding outcome was part of the conversion input. This use of a bitmask is a highly gas-efficient method for encoding a variable-length array of inputs into a single `uint256` value.

The conversion output will consist of "YES" tokens for all outcome indices whose corresponding bits were 0 in the indexSet. The quantity will be equal to the input amount. Meanwhile, the released USDC collateral will be calculated using the formula (k - 1) * amount, where k is the number of input "NO" tokens.  Hence, if a holder converts M units of  k different "NO" tokens, the holder will get M units of (# of outcomes - k) "YES" tokens and aslo get the released collateral, which will be (k - 1) * M USDC.

**Example**:
If the indexSet is 6 (binary: 0110, i.e., outcome3, outcome2, outcome1, outcome0), it means the user is converting 2 "NO" tokens: one for outcome 1 and one for outcome 2. And suppose the conversion amount is 100 "NO" tokens for each of the two "NO" tokens.
The output will be 100 "YES" token for outcome 0 (since the bit for outcome 0 is 0 in the indexSet) and 100 "YES" token for outcome 3 (since the bit for outcome 3 is 0 in the indexSet).
The released collateral will be calculated as (2 - 1) * 100 = 100 USDC.
You can see the expected return for the holder will be the same before and after the conversion.

**Notice**: `PositionsConverted` event are designed for a one-way conversion only: from a collection of "NO" tokens into "YES" tokens. You cannot convert "YES" tokens into "NO" tokens using this function. If someone wants to convert "YES" tokens into "NO" tokens, they would not use the special `convertPositions` function. Instead, they would perform two separate, standard market transactions:
1. **Sell the "YES" tokens:** The user would place an order on Polymarket's central limit order book to sell their "YES" tokens for USDC.
2. **Buy the "NO" tokens:** They would then use the USDC from that sale to place a new order to buy the desired "NO" tokens on the same or a different market.
This process is simply standard trading, not the unique, capital-efficient portfolio rebalancing that the `PositionsConverted` event represents.




## V. Putting It All Together: Real-World Scenarios

Let's analyze a few examples to solidify your understanding.

**(1) A Simple Trade: Bettor vs. Bettor**

In a typical trade, a buyer and a seller are matched. You will see two `OrderFilled` events and one `OrdersMatched` event. One `OrderFilled` event will show a user selling an outcome token for USDC, and the other will show a user buying that same token with USDC.

The below `OrderFilled` and `OrdersMatched` logs record a slightly more complex case: a outcome token transactions between three bettors: bettors `0x8698...` and `0x5e9f...` sell outcome token `5031...` and bettor `0x6fd3...` buys the otucome token.

| log_index | transaction_index |             block_number | orderHash |                                             maker |                                      taker |                               makerAssetId |                                      takerAssetId |                                 makerAmountFilled | takerAmountFilled |       event | takerOrderHash |                                   takerOrderMaker | block_timestamp |
| --------: | ----------------: | --------------: | ----------------------: | --------: | ------------------------------------------------: | -----------------------------------------: | -----------------------------------------: | ------------------------------------------------: | ------------------------------------------------: | ----------------: | ----------: | -------------: | ------------------------------------------------: |
|               152 |              34 |   51865340 | 0x46b375b7a0f526ef3e6c122f38aaa5a3390430546454... | 0x8698EdBeFd013dB6D087E3d09EEFa08e40bC35c1 | 0x32e3742A6DD363c3DFDba700b77f845Ec99aD066 | 5031583702443233421382704105772955621198964922... |                                                 0 |       111820000.0 |  34664200.0 |    OrderFilled |                                              None | None                                       | 2024-01-02 20:27:28 UTC |
|               155 |              34 |   51865340 | 0x5e9f8e263b2b8bf538f91595472a0cb98d2bd3333b8d... | 0x3Cf3E8d5427aED066a7A5926980600f6C3Cf87B3 | 0x32e3742A6DD363c3DFDba700b77f845Ec99aD066 | 5031583702443233421382704105772955621198964922... |                                                 0 |        10000000.0 |   3100000.0 |    OrderFilled |                                              None | None                                       | 2024-01-02 20:27:28 UTC |
|               157 |              34 |   51865340 | 0x6fd37744eff1c1c11e413b2395445c06c0bd04dd6f85... | 0x32e3742A6DD363c3DFDba700b77f845Ec99aD066 | 0xC5d563A36AE78145C45a50134d48A1215220f80a |                                                 0 | 5031583702443233421382704105772955621198964922... |        37764200.0 | 121820000.0 |    OrderFilled |                                              None | None   |     2024-01-02 20:27:28 UTC |                               
|               158 |              34 |   51865340 |                                              None |                                       None      |                           None |                                                 0 | 5031583702443233421382704105772955621198964922... |        37764200.0 | 121820000.0 |  OrdersMatched | 0x6fd37744eff1c1c11e413b2395445c06c0bd04dd6f85... | 0x32e3742A6DD363c3DFDba700b77f845Ec99aD066 | 2024-01-02 20:27:28 UTC |

Usually, we only need to focus on the maker side:

(1) If the `makerAssetId` is `0`, then it means this bettor is buying a conditional token.

(2) If the `makerAssetId` is a string like `5031...` (the `positionID` in gnosis conditional token protocol), then it means this bettor is selling this conditional token.

(3) When polymarket is matching more than 2 orders, the taker ID can be the Polymarket `NegRisk_CTFExchange` address (`0xC5d563A36AE78145C45a50134d48A1215220f80a`), whose contract facilitated the match, not the real trading party.

**(2) Minting New Tokens**

If two users want to bet on opposite outcomes of a binary market, the exchange can mint new tokens for them. In this case, both `OrderFilled` events will show `makerAssetId` as `0`, as both parties are providing USDC. The `takerAssetId` in each event will correspond to the "YES" and "NO" outcome tokens, respectively.

| log_index | transaction_index | block_number |    maker |                                      taker |                               makerAssetId | takerAssetId |                                 makerAmountFilled | takerAmountFilled |        event | takerOrderHash |                                   takerOrderMaker |                            block_timestamp |                
| --------: | ----------------: | -----------: | -------: | -----------------------------------------: | -----------------------------------------: | -----------: | ------------------------------------------------: | ----------------: | -----------: | -------------: | ------------------------------------------------: | -----------------------------------------: | 
|               137 |           44 | 54432034 | 0x351A72160E477863D13666c62ef1e7631B3940bB | 0xE0DbDB7F005f233f4510e4Ef7e53A2f76a8Df44E |            0 | 3473165777088344114087500151809875113887709547... |      3.960000e+09 | 6.000000e+09 |    OrderFilled |                                              None |                                       None | 2024-03-09 00:24:25+00:00 | 
|               139 |           44 | 54432034 | 0xE0DbDB7F005f233f4510e4Ef7e53A2f76a8Df44E | 0xC5d563A36AE78145C45a50134d48A1215220f80a |            0 | 8802783960924362419341561417932867960261291649... |      2.040000e+09 | 6.000000e+09 |    OrderFilled |                                              None |                                       None | 2024-03-09 00:24:25+00:00 | 
|               140 |           44 | 54432034 |                                       None |                                       None |            0 | 8802783960924362419341561417932867960261291649... |      2.040000e+09 | 6.000000e+09 |  OrdersMatched | 0x02a26ec7f7fade1ca26db91b6b5d5f277f28f0fd5a40... | 0xE0DbDB7F005f233f4510e4Ef7e53A2f76a8Df44E | 2024-03-09 00:24:25+00:00 |  

In this case, bettor `0x351A7...` wants to buy 6000 `BidenLose` tokens (`3473...`) and bettor `0xE0Db...` wants to buy 6000 `BidenWin` tokens (`8802...`). Both are buy orders, but they want to bet on the opposite results, so Polymarket `NegRisk_CTFExchange` matched them together, took their USDC (3960 + 2040 = 6000 USDC) and minted new opposite tokens for these two users.

**(3) Burning Tokens**

If two users want to sell their opposing outcome tokens, the exchange can match them, burn the tokens, and release the collateral. Here, both `OrderFilled` events will show a non-zero `makerAssetId` (as they are both providing outcome tokens) and a `takerAssetId` of `0` (as they are both receiving USDC).

| log_index | transaction_index | block_number | orderHash |                                             maker |                                      taker |                               makerAssetId |                                      takerAssetId | makerAmountFilled | takerAmountFilled |       event | takerOrderHash |                                   takerOrderMaker |                            block_timestamp |   
| --------: | ----------------: | -----------: | --------: | ------------------------------------------------: | -----------------------------------------: | -----------------------------------------: | ------------------------------------------------: | ----------------: | ----------------: | ----------: | -------------: | ------------------------------------------------: | -----------------------------------------: | 
|               293 |           74 |  51958552 | 0xb06de8c9f6c2035e5464f1328a69e56e6c2eb28958a4... | 0x64C1FFb0283a322bdBE54298713c8013E5E2160F | 0xff66A0aDa4122C5d9292Ffb7eC02922d167a7A07 | 4833104333661288389093875950949315923475504897... |                 0 |       206190000.0 | 123714000.0 |    OrderFilled |                                              None |                                       None | 2024-01-05 06:54:00+00:00 | 
|               295 |           74 |  51958552 | 0x53085d51ac4ea1ddce4c3450bcdb5ff7402417f84883... | 0xff66A0aDa4122C5d9292Ffb7eC02922d167a7A07 | 0xC5d563A36AE78145C45a50134d48A1215220f80a | 2174263314346390629056905015582624153306727273... |                 0 |       206190000.0 |  82476000.0 |    OrderFilled |                                              None |                                       None | 2024-01-05 06:54:00+00:00 | 
|               296 |           74 |  51958552 |                                              None |                                       None |                                       None | 2174263314346390629056905015582624153306727273... |                 0 |       206190000.0 |  82476000.0 |  OrdersMatched | 0x53085d51ac4ea1ddce4c3450bcdb5ff7402417f84883... | 0xff66A0aDa4122C5d9292Ffb7eC02922d167a7A07 | 2024-01-05 06:54:00+00:00 | 

In this case, bettor `0x64C1...` wants to sell 206.19 `TrumpLose` tokens (`4833...`) and bettor `0xff66...` wants to sell 206.19 `TrumpWin` tokens (`2174...`). Their tokens represent the opposite results, so Polymarket `NegRisk_CTFExchange` matched them together, burned their token and sent the unlocked USDC (123.714 + 82.476 = 206.19 USDC) to these two users. (Remember: one locked USDC can mint out one pair of opposite tokens).

**(4) A Mixed Scenario**

This is where it gets interesting. Here is a scenario with three bettors:

| log_index | transaction_index | block_number | orderHash |                                             maker |                                      taker |                               makerAssetId |                                      takerAssetId | makerAmountFilled | takerAmountFilled |       event | takerOrderHash |                                   takerOrderMaker |                            block_timestamp |      
| --------: | ----------------: | -----------: | --------: | ------------------------------------------------: | -----------------------------------------: | -----------------------------------------: | ------------------------------------------------: | ----------------: | ----------------: | ----------: | -------------: | ------------------------------------------------: | -----------------------------------------: | 
|	300 |	70 |	51951654 |	0x0420e9f7b4867f52c63c2c7d5bbf8240a19ee77629fb...	| 0x8698EdBeFd013dB6D087E3d09EEFa08e40bC35c1 |	0xf0b049379BBD6399aD1C6704345a7CeC813968ec	| 2174263314346390629056905015582624153306727273...|	0	| 200000000.0 | 	84000000.0 |	OrderFilled |	None |	None |	2024-01-05 02:36:24 UTC |
|	314	| 70 |	51951654 |	0x87b9de8b3dc9bdcbf7e05cb4dd4e6c6f4d7a461a8866...	| 0xd42F6a1634A3707e27cBae14ca966068E5D1047d |	0xf0b049379BBD6399aD1C6704345a7CeC813968ec |	0	| 4833104333661288389093875950949315923475504897... |	22095238.0 |	38095237.0 |	OrderFilled	| None |	None |	2024-01-05 02:36:24 UTC	|
|	316 |	70	| 51951654 |	0x4cd69226a72cda1b9acc16b7cc4d350b8076f82635d1...	| 0xf0b049379BBD6399aD1C6704345a7CeC813968ec |	0xC5d563A36AE78145C45a50134d48A1215220f80a |	0	| 2174263314346390629056905015582624153306727273... |	99999999.0	| 238095237.0	| OrderFilled	| None |	None |	2024-01-05 02:36:24 UTC |
|	317	| 70	| 51951654	| None	| None	| None |	0	| 2174263314346390629056905015582624153306727273... | 	99999999.0 |	238095237.0 |	OrdersMatched	| 0x4cd69226a72cda1b9acc16b7cc4d350b8076f82635d1... |	0xf0b049379BBD6399aD1C6704345a7CeC813968ec	| 2024-01-05 02:36:24 UTC|

In this case, bettor `0x8698...` sells 200 `TrumpWin` tokens (`2174...`) for 84 USDC, bettor `0xd42F...` buys 38.095237 `TrumLose` tokens (`4833...`) for 22.095238 USDC, bettor `0xf0b0...` buys 238.095237 `TrumpWin` tokens (`2174...`) for 99.999999 USDC. 

The `NegRisk_CTFExchange` can facilitate this complex transaction:

1. **Direct Trade:** 200 of bettor `0xf0b0...`'s `TrumpWin` buy order are matched with bettor `0x8698...`'s sell order.
2. **Minting:** The remaining 38.095237 `TrumpWin` from `0xf0b0...`'s order are matched with bettor `0xd42F...`'s `TrumpLose` order. The combined USDC is used to mint new pairs of outcome tokens.

By carefully analyzing the `OrderFilled` events for each participant, you can piece together the intricate logic of the exchange.

**(5) Position Conversion Scenario**

Position conversion is only recorded in the `PositionsConverted` event. This operation does not change the trader's expected return, but only change the outstanding positions the trader is holding.

## Start Your On-Chain Journey

You now have the foundational knowledge and the practical tools to start your journey as an on-chain analyst. The world of Polymarket's data is vast and full of insights waiting to be discovered. So fire up your code editor, start exploring the blockchain, and begin decoding the digital tea leaves. The story of the markets is there for the taking—all you have to do is read it.