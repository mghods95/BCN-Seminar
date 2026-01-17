# SoreToken (Foundry)

An ERC‑20 token built with OpenZeppelin and Foundry, featuring controlled minting via roles, optional max‑supply cap, and safer 2‑step ownership transfers.

---

## Contents

- [SoreToken (Foundry)](#soretoken-foundry)
  - [Contents](#contents)
  - [Features](#features)
  - [Project Structure](#project-structure)
  - [Prerequisites](#prerequisites)
    - [Install Foundry](#install-foundry)
  - [Install \& Setup](#install--setup)
  - [Environment Variables](#environment-variables)
    - [1) Create `.env`](#1-create-env)
    - [2) Add variables](#2-add-variables)
    - [How the deploy script interprets supply](#how-the-deploy-script-interprets-supply)
  - [Build](#build)
  - [Test](#test)
  - [Deploy \& Verify](#deploy--verify)
    - [Sepolia](#sepolia)
    - [Ethereum Mainnet](#ethereum-mainnet)
    - [Local (Anvil)](#local-anvil)
  - [Contract Overview](#contract-overview)
    - [Roles](#roles)
    - [Supply Rules](#supply-rules)
    - [Ownership Transfer (2‑step)](#ownership-transfer-2step)
  - [Troubleshooting](#troubleshooting)
    - [1) Verify failed on Etherscan](#1-verify-failed-on-etherscan)
    - [2) "insufficient funds" / gas issues](#2-insufficient-funds--gas-issues)
    - [3) Token not visible in MetaMask](#3-token-not-visible-in-metamask)
  - [Security Notes](#security-notes)
  - [License](#license)

---

## Features

* **ERC‑20** token (OpenZeppelin)
* **Role‑based minting** using `AccessControl`
* **Owner-managed minter list** (`addMinter` / `removeMinter`)
* **Optional max supply cap** (`maxSupply = 0` means uncapped)
* **2‑step ownership transfer** (`Ownable2Step`) to prevent accidental ownership loss
* **Foundry scripts + Makefile** for reproducible build/test/deploy/verify

---

## Project Structure

```text
.
├── broadcast/                     # Foundry broadcast artifacts (tx receipts, args)
├── foundry.toml                   # Foundry configuration
├── foundry.lock                   # Dependency lock
├── Makefile                       # Build/Test/Deploy commands
├── README.md                      # You are here
├── script/
│   └── DeploySoreToken.s.sol      # Deploy script (reads env vars)
├── src/
│   └── SoreToken.sol              # Main token contract
└── test/
    ├── Base.t.sol
    ├── SoreToken.unit.t.sol
    ├── SoreToken.fuzz.t.sol
    └── invariant/
        ├── SoreTokenHandler.sol
        └── SoreToken.invariant.t.sol
```

---

## Prerequisites

* **Git**
* **Foundry** (forge/cast/anvil)
* (Recommended) An RPC provider account:

  * Infura / Alchemy / QuickNode
* (For verification) **Etherscan API key**

### Install Foundry

```bash
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

Verify installation:

```bash
forge --version
cast --version
anvil --version
```

---

## Install & Setup

Clone the repository and install dependencies:

```bash
git clone <YOUR_REPO_URL>
cd tokenProject1
forge install
```

> If this repository already contains installed dependencies, `forge install` may be a no-op.

---

## Environment Variables

This project reads configuration from a local `.env` file (loaded automatically by the `Makefile`).

### 1) Create `.env`

```bash
cp .env.example .env 2>/dev/null || touch .env
```

### 2) Add variables

> ⚠️ Never commit `.env` or your private key.

```env
# Wallet used for deployment
PRIVATE_KEY=0xYOUR_PRIVATE_KEY

# RPC URLs
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
MAINNET_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID

# Etherscan (used for source verification)
ETHERSCAN_API_KEY=YOUR_ETHERSCAN_API_KEY

# Optional token parameters (defaults shown)
TOKEN_NAME=Sore Token
TOKEN_SYMBOL=SORE
# If omitted, owner defaults to deployer address
# TOKEN_OWNER=0xYourOwnerAddress

# These are interpreted as **whole tokens** (not wei) and multiplied by 1e18 in the deploy script
TOKEN_INITIAL_SUPPLY=0
TOKEN_MAX_SUPPLY=1000000
# Set TOKEN_MAX_SUPPLY=0 for uncapped supply
```

### How the deploy script interprets supply

* `TOKEN_INITIAL_SUPPLY` and `TOKEN_MAX_SUPPLY` are **whole tokens**.
* The deploy script multiplies them by `1e18` to match ERC‑20 decimals.

---

## Build

Using Make:

```bash
make build
```

Or directly:

```bash
forge build
```

---

## Test

Run all tests:

```bash
make test
```

Or directly with more/less verbosity:

```bash
forge test -vv
forge test -vvvv
```

Common selective runs:

```bash
# Unit tests only
forge test --match-path "test/*unit*.t.sol" -vv

# Fuzz tests only
forge test --match-path "test/*fuzz*.t.sol" -vv

# Invariant tests only
forge test --match-path "test/invariant/*.t.sol" -vv
```

---

## Deploy & Verify

Deployments use `script/DeploySoreToken.s.sol:DeploySoreToken`.

The Makefile targets will:

1. Build the project
2. Broadcast the deploy transaction
3. Verify the contract source on Etherscan

> Ensure your deployer account has enough ETH on the target network for gas.

### Sepolia

```bash
make deploy-sepolia
```

Required in `.env`:

* `PRIVATE_KEY`
* `SEPOLIA_RPC_URL`
* `ETHERSCAN_API_KEY`

### Ethereum Mainnet

```bash
make deploy-mainnet
```

Required in `.env`:

* `PRIVATE_KEY`
* `MAINNET_RPC_URL`
* `ETHERSCAN_API_KEY`

### Local (Anvil)

Start a local chain:

```bash
anvil
```

In a new terminal, deploy locally (no verification):

```bash
forge script script/DeploySoreToken.s.sol:DeploySoreToken \
  --sig "run()" \
  --rpc-url http://127.0.0.1:8545 \
  --broadcast \
  -vvvv
```

---

## Contract Overview

### Roles

* `DEFAULT_ADMIN_ROLE`

  * Granted to the initial owner.
  * Admin over role management.
* `MINTER_ROLE`

  * Accounts with this role can call `mint(to, amount)`.
  * The owner is granted `MINTER_ROLE` at deployment.

Owner-only functions:

* `addMinter(address)`
* `removeMinter(address)`

### Supply Rules

* `maxSupply` is **immutable**.
* If `maxSupply == 0` → supply is **uncapped**.
* If capped:

  * Deployment reverts if `initialSupply > maxSupply`.
  * Minting reverts if `totalSupply + amount > maxSupply`.

### Ownership Transfer (2‑step)

Ownership transfers are safer with a two-step process:

1. Current owner calls `transferOwnership(newOwner)` (sets pending owner)
2. New owner calls `acceptOwnership()` to finalize

The contract keeps roles in sync with the owner during `_transferOwnership`:

* Revokes `DEFAULT_ADMIN_ROLE` and `MINTER_ROLE` from old owner
* Grants both roles to the new owner

---

## Troubleshooting

### 1) Verify failed on Etherscan

Common causes:

* Wrong `ETHERSCAN_API_KEY`
* RPC URL points to a different chain than `--chain`
* Etherscan hasn’t indexed the deployment yet (try again after ~1–2 minutes)
* Build settings mismatch (solc/optimizer/remappings)

Tip: re-run deployment with `-vvvv` to see detailed verify logs.

### 2) "insufficient funds" / gas issues

* Ensure the deployer address has enough ETH on the target network.
* On Sepolia, use a faucet to get test ETH.

### 3) Token not visible in MetaMask

* Make sure you selected the correct network (Sepolia vs Mainnet).
* Import the token manually:

  * MetaMask → Import tokens → paste the deployed token contract address

---

## Security Notes

* **Do not commit your private key**. Add `.env` to `.gitignore`.
* Prefer a dedicated deployer wallet.
* For mainnet deployments:

  * Consider using a hardware wallet or a multisig as the token owner.
  * Double-check constructor parameters (`TOKEN_OWNER`, supply/cap).
  * Run a dry-run on Sepolia first.

---

## License

MIT
