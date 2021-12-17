[course TOC, code, and resources](https://github.com/smartcontractkit/full-blockchain-solidity-course-py/blob/main/README.md#lesson-10-defi--aave)

[Github](https://github.com/PatrickAlphaC/aave_brownie_py_freecode)

[AAVE web3 version](https://github.com/PatrickAlphaC/aave_web3_py)

# AAVE testnet

## connecting to MetaMask

- connecting MetaMask to [AAVE](https://staging.aave.com/#/deposit) on **Kovan Test Network**
  - -> click Connect -> MetaMask (browser wallet)
  - connect/authorize on MetaMask
  - will see my MetaMask ETH balance at AAVE Deposit tab

## deposit

- Deposit tab -> Ethereum (which show my balance) -> enter ETH amount -> continue -> deposit
- authorize/confirm at MetaMask (from MetaMask account to `0xA61ca04DF33B72b235a8A28CfB535bb7A5271B70`)
- button to add **aETH** (interest bearing ETH we just deposited) to our MetaMask wallet
- now my [dashboard](https://staging.aave.com/#/dashboard) show the deposited balance

## WETHGateway

- if we search the above address `0xA61ca04DF33B72b235a8A28CfB535bb7A5271B70` on [Kovan etherscan](https://kovan.etherscan.io/), we'll see this address is a contract called WETHGateway
- what AAVE is doing here is swapping our ETH for WETH, which is ERC20 version of ethereum, which allows for working with all other ERC20s on the AAVE protocol

## borrowing

- Frictionless **short selling**
- Obtaining **liquidity** w/o selling assets
- Gain yield on deposited collateral
- Things impossible in the traditional fintech world, like **flash loans**.

# Programmatic Interactions with Aave

- [AAVE documentation](https://docs.aave.com/developers/)
- setup, `$brownie init`
- no need to deploy any contract. All the necessary contracts are already deployed on the chain.

- Objectives
  1. Swap our ETH for WETH
  2. Deposit some ETH into AAVE
  3. Borrow some asset with the ETH collateral
     1. Sell that borrowed asset (short selling)
  4. Repay everything back

## Testing

- for integration test, we need to use Kovan testnet
- for unit test, default testing network is development with mocking; but if you have no oracle (e.g. chainlink pricefeed), you can just use mainnet-fork (basically just mock the netire mainnet)
  - first, delete the brownie's built-in mainnet-fork, `$brownie networks delete mainnet-fork`
  - then add our custom mainnet-fork `$brownie networks add development mainnet-fork cmd=ganache-cli host=http://127.0.0.1 fork=my_Alchemy_mainnet_HTTP_address accounts=10 mnemonic=brownie port=8545`
- WETH token contract on etherscan is `0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2`, which we'll use in brownie-config for **mainnet-fork** (it will be the same for mainnet if we go for production)
- It's a better practice to use `get_contract()` as we did in brownie Lottery, but here we'll just use brownie-config for simplicity.

## Swap our ETH for WETH, on Kovan

- [WETH token contract](https://kovan.etherscan.io/address/0xd0a1e359811322d97991e03f863a0c30c2cf029c#code), different from above WETHGateway. We'll use this address in our `brownie-config` file.

- `scripts/get_weth.py`
- to save gas we could interact with above **WETHGateway** directly for AAVE, but we want to learn how to get WETH in general
- `interfaces/IWeth.sol` (copied from course material)

- `$ brownie run scripts/get_weth.py --network kovan`
  - Transaction sent: 0x7144c240a5695f7578deda28011a8df7078817d1d95e2dd4667876183b5fa10f
  - check MetaMask, our ETH balance is reduced by 0.1
  - using above transaction hash to locate the WETH contract address (0xd0a1e359811322d97991e03f863a0c30c2cf029c), use it to import the 0.1WETH to MetaMask wallet.

**Commit 1**

## Swap our ETH for WETH, on mainnet-fork

- `$scripts/aave_borrow.py`
- test `get_weth()` on mainnet-fork
  - `$brownie run scripts/aave_borrow.py --network mainnet-fork`
  - testing everything on mainnet-fork is going to give us an accurate view of what we will get when doing this on the mainnet.

**Commit 2**

## Deposit

- [AAVE LendingPool](https://docs.aave.com/developers/the-core-protocol/lendingpool)

  - deposit()
  - withdraw()
  - borrow()
  - repay()
  - ...

- `interfaces/ILendingPoolAddressesProvider.sol`, copied from [AAVE](https://docs.aave.com/developers/the-core-protocol/addresses-provider/ilendingpooladdressesprovider)

  - we can make a custom interface if we're only going to use one or two functions:
  - `interface ILendingPoolAddressesProvider {function getLendingPool() external view returns (address);}`
  - specify the address of LendingPoolAddressesProvider contract (mainnet `0xb53c1a33016b2dc2ff3653530bff1848a515c8c5`, Kovan `0x88757f2f99175387ab4c6a4b3067c77a695b0349`), from [AAVE](https://docs.aave.com/developers/deployed-contracts/deployed-contracts), in brownie-config

- `interfaces/ILendingPool.sol`, copied from [AAVE](https://docs.aave.com/developers/the-core-protocol/lendingpool/ilendingpool), but to change from

  - importing locally:
    - `import {ILendingPoolAddressesProvider} from './ILendingPoolAddressesProvider.sol';`
    - `import {DataTypes} from './DataTypes.sol';`
  - to importing from Github:
    - `from "@aave/contracts/interfaces/....`
  - and add corresponding dependencies and remapping in brownie-config.

  - interfaces/IERC20.sol, copied from course github. See [EIP-20](https://eips.ethereum.org/EIPS/eip-20) for more info.
    - need its `approve()` function to approve the token before we can deposit it.

- `$brownie run scripts/aave_borrow.py --network mainnet-fork`

**Commit 3**

## Borrow

- `getUserAccountData()` see [AAVE doc](https://docs.aave.com/developers/the-core-protocol/lendingpool#getuseraccountdata)
- brownie-config

  - `dai_eth_price_feed` (DAI/ETH), from [Chainlink Data Feed](https://docs.chain.link/docs/ethereum-addresses/)
  - `interfaces/AggregatorV3Interface.sol`, [Chainlink](https://github.com/smartcontractkit/chainlink/blob/develop/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol). We can name is as `IAggregatorV3.sol` if we want
  - `dai_token`, from [etherscan](https://etherscan.io/token/0x6b175474e89094c44da98b954eedeac495271d0f)
    - Kovan's address changes often, make sure the check the lastest at [AAVE doc](https://aave.github.io/aave-addresses/kovan.json)

- [borrow()](https://docs.aave.com/developers/the-core-protocol/lendingpool#borrow)

- `$brownie run scripts/aave_borrow.py`, din't specify `--network mainnet-fork` because that's the default in brownie-config.

**Commit 4**

## Repay

- [repay()]()https://docs.aave.com/developers/the-core-protocol/lendingpool#borrow

- `$brownie run scripts/aave_borrow.py`, din't specify `--network mainnet-fork` because that's the default in brownie-config.

**Commit 5**

## Deploy to Kovan testnet

- comment out `repay_all()` so to see the balance
- make sure MetaMast is open, on Kovan testnet, with ETH balance

- `$brownie run scripts/get_weth.py --network kovan` to get 0.1WETH

  - if MetaMask doesn't have WETH yet, you can use weth_token address `0xd0a1e359811322d97991e03f863a0c30c2cf029c` to import the token
  - there is an error message `TransactionError: Tx dropped without known replacement: 0x6e25847611aaddca40f727791c135f9179e331ad548b8c3c0b9ac755bbc1ca9b`, but transaction seems went throught (MetaMask ETH reducted by 0.1 and WETH added by 0.1)

- `$brownie run scripts/aave_borrow.py --network kovan`
  - use Dai Token address `0xFf795577d9AC8bD7D90Ee22b6C1703490b6512FD` to import the borrowed Dai token into MetaMast, there are 301.866 Dai in it.
  - also see WETH reduced by 0.1 (deposited to AAVE)
  - but see 0.1 aWETH (money in AAVE)
  - we can also check our [AAVE dashboard](https://staging.aave.com/#/dashboard) for the whole picture
  - keep in mind, when we repay, it will be more than what we just borrowed because of the interest accrued interest.

## Test

- `tests/test_aave_borrow.py`
- `$brownie test`

**Commit 6**
