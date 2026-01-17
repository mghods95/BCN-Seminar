// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import "forge-std/Test.sol";
import {SoreToken} from "../src/SoreToken.sol";

abstract contract BaseTest is Test {
    SoreToken internal token;

    address internal owner = address(0xA11CE);
    address internal alice = address(0xB0B);
    address internal bob   = address(0xBEEF);
    address internal minter = address(0xC0FFEE);

    function deployToken(uint256 initialSupply, uint256 cap) internal returns (SoreToken) {
        return new SoreToken("Sore Token", "SORE", owner, initialSupply, cap);
    }
}
