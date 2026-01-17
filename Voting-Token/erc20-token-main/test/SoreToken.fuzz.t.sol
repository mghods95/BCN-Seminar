// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import {SoreToken} from "../src/SoreToken.sol";
import {BaseTest} from "./Base.t.sol";

contract SoreTokenFuzzTest is BaseTest {
    function setUp() public {
        token = deployToken(0, 1_000_000); // capped
    }

    function testFuzz_mintNeverExceedsCap(uint256 a, uint256 b) public {
        uint256 cap = token.maxSupply();

        // bound fuzz values
        a = bound(a, 0, cap);
        b = bound(b, 0, cap);

        // owner is a minter in our deployment
        vm.startPrank(owner);

        // Mint a (always allowed now because a <= cap)
        token.mint(alice, a);

        uint256 supplyAfterA = token.totalSupply();
        assertLe(supplyAfterA, cap);

        // Compute remaining safely
        uint256 remaining = cap - supplyAfterA;

        if (b <= remaining) {
            token.mint(bob, b);
            assertLe(token.totalSupply(), cap);
        } else {
            // b would exceed cap -> must revert with our custom error
            vm.expectRevert();
            token.mint(bob, b);
        }

        vm.stopPrank();
    }
}
