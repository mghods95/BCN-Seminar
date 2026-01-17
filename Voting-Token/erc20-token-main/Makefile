# ----------------------------------------
# Professional Makefile for Foundry
# Supports:
# - Build / Test
# - Deploy + Verify (Sepolia & Mainnet)
# ----------------------------------------

SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c

# ----------------------------------------
# Load .env if exists
# ----------------------------------------
ifneq (,$(wildcard .env))
include .env
export
endif

# ----------------------------------------
# Help
# ----------------------------------------
.PHONY: help
help:
	@echo ""
	@echo "Available targets:"
	@echo ""
	@echo "  make clean            - clean build artifacts"
	@echo "  make build            - compile contracts"
	@echo "  make fmt              - format Solidity code"
	@echo "  make test             - run all tests"
	@echo ""
	@echo "  make deploy-sepolia   - deploy + verify on Sepolia testnet"
	@echo "  make deploy-mainnet   - deploy + verify on Ethereum mainnet"
	@echo ""
	@echo "Required .env variables:"
	@echo "  PRIVATE_KEY"
	@echo "  SEPOLIA_RPC_URL / MAINNET_RPC_URL"
	@echo "  ETHERSCAN_API_KEY"
	@echo ""
	@echo "Optional token params:"
	@echo "  TOKEN_NAME"
	@echo "  TOKEN_SYMBOL"
	@echo "  TOKEN_OWNER"
	@echo "  TOKEN_INITIAL_SUPPLY"
	@echo "  TOKEN_MAX_SUPPLY"
	@echo ""

# ----------------------------------------
# Core
# ----------------------------------------
.PHONY: clean
clean:
	forge clean

.PHONY: build
build:
	forge build

.PHONY: fmt
fmt:
	forge fmt

# ----------------------------------------
# Tests
# ----------------------------------------
.PHONY: test
test:
	forge test -vv

# ----------------------------------------
# Deploy: Sepolia
# ----------------------------------------
.PHONY: deploy-sepolia
deploy-sepolia: build
	@if [[ -z "$${SEPOLIA_RPC_URL:-}" ]]; then echo "❌ Missing SEPOLIA_RPC_URL"; exit 1; fi
	@if [[ -z "$${PRIVATE_KEY:-}" ]]; then echo "❌ Missing PRIVATE_KEY"; exit 1; fi
	@if [[ -z "$${ETHERSCAN_API_KEY:-}" ]]; then echo "❌ Missing ETHERSCAN_API_KEY"; exit 1; fi

	@echo "🚀 Deploying SoreToken to Sepolia..."
	forge script script/DeploySoreToken.s.sol:DeploySoreToken \
		--sig "run()" \
		--rpc-url "$$SEPOLIA_RPC_URL" \
		--broadcast \
		--verify \
		--chain sepolia \
		--etherscan-api-key "$$ETHERSCAN_API_KEY" \
		-vvvv

# ----------------------------------------
# Deploy: Ethereum Mainnet
# ----------------------------------------
.PHONY: deploy-mainnet
deploy-mainnet: build
	@if [[ -z "$${MAINNET_RPC_URL:-}" ]]; then echo "❌ Missing MAINNET_RPC_URL"; exit 1; fi
	@if [[ -z "$${PRIVATE_KEY:-}" ]]; then echo "❌ Missing PRIVATE_KEY"; exit 1; fi
	@if [[ -z "$${ETHERSCAN_API_KEY:-}" ]]; then echo "❌ Missing ETHERSCAN_API_KEY"; exit 1; fi

	@echo "🚀 Deploying SoreToken to Ethereum Mainnet..."
	forge script script/DeploySoreToken.s.sol:DeploySoreToken \
		--sig "run()" \
		--rpc-url "$$MAINNET_RPC_URL" \
		--broadcast \
		--verify \
		--chain mainnet \
		--etherscan-api-key "$$ETHERSCAN_API_KEY" \
		-vvvv
