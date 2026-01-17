// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import {SoreToken} from "../src/SoreToken.sol";

/// @notice Deploy script for SoreToken (Foundry)
/// Env vars (recommended):
/// - PRIVATE_KEY                (required for broadcast)
/// - TOKEN_NAME                 (optional, default: "Sore Token")
/// - TOKEN_SYMBOL               (optional, default: "SORE")
/// - TOKEN_OWNER                (optional, default: deployer)
/// - TOKEN_INITIAL_SUPPLY       (optional, default: 0)  // in whole tokens
/// - TOKEN_MAX_SUPPLY           (optional, default: 1_000_000) // in whole tokens; 0 = uncapped
///
/// NOTE: initial/max supply are interpreted as "whole tokens" and multiplied by 1e18 (ERC20 decimals).
contract DeploySoreToken is Script {
    function run() external returns (SoreToken token) {
        uint256 deployerKey = vm.envUint("PRIVATE_KEY");
        address deployer = vm.addr(deployerKey);

        // Read config with sane defaults
        string memory name = _envStringOr("TOKEN_NAME", "Sore Token");
        string memory symbol = _envStringOr("TOKEN_SYMBOL", "SORE");

        address owner = _envAddressOr("TOKEN_OWNER", deployer);

        uint256 initialSupplyTokens = _envUintOr("TOKEN_INITIAL_SUPPLY", 0);
        uint256 maxSupplyTokens = _envUintOr("TOKEN_MAX_SUPPLY", 1_000_000);

        // Convert to 18 decimals
        uint256 initialSupply = initialSupplyTokens * 1e18;
        uint256 maxSupply = maxSupplyTokens == 0 ? 0 : (maxSupplyTokens * 1e18);

        vm.startBroadcast(deployerKey);
        token = new SoreToken(name, symbol, owner, initialSupply, maxSupply);
        vm.stopBroadcast();

        console2.log("SoreToken deployed at:", address(token));
        console2.log("Owner:", owner);
        console2.log("InitialSupply (wei):", initialSupply);
        console2.log("MaxSupply (wei):", maxSupply);

        return token;
    }

    // -------------------------
    // Env helpers (safe defaults)
    // -------------------------

    function _envStringOr(
        string memory key,
        string memory def
    ) internal returns (string memory) {
        try vm.envString(key) returns (string memory v) {
            return bytes(v).length == 0 ? def : v;
        } catch {
            return def;
        }
    }

    function _envUintOr(
        string memory key,
        uint256 def
    ) internal returns (uint256) {
        try vm.envUint(key) returns (uint256 v) {
            return v;
        } catch {
            return def;
        }
    }

    function _envAddressOr(
        string memory key,
        address def
    ) internal returns (address) {
        try vm.envAddress(key) returns (address v) {
            return v == address(0) ? def : v;
        } catch {
            return def;
        }
    }
}
