// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import "forge-std/StdInvariant.sol";

import {SoreToken} from "../../src/SoreToken.sol";
import {SoreTokenHandler} from "./SoreTokenHandler.sol";

contract SoreTokenInvariantTest is StdInvariant, Test {
    SoreToken internal token;
    SoreTokenHandler internal handler;

    address internal owner = address(0xA11CE);

    function setUp() public {
        token = new SoreToken("Sore Token", "SORE", owner, 0, 1_000_000);
        handler = new SoreTokenHandler(token, owner);

        targetContract(address(handler));
        targetSelector(FuzzSelector({addr: address(handler), selectors: _selectors()}));
    }

    // -------------------------
    // Invariants (core security properties)
    // -------------------------

    /// 1) Supply must never exceed cap (when capped)
    function invariant_totalSupplyNeverExceedsCap() public view {
        uint256 cap = token.maxSupply();
        if (cap != 0) {
            assertLe(token.totalSupply(), cap);
        }
    }

    /// 2) Zero address must never end up with a balance (mint(to=0) must always fail)
    function invariant_zeroAddressNeverReceivesTokens() public view {
        assertEq(token.balanceOf(address(0)), 0);
    }

    /// 3) DEFAULT_ADMIN_ROLE should never be assigned to zero address
    function invariant_zeroAddressIsNeverAdmin() public view {
        assertFalse(token.hasRole(bytes32(0), address(0)));
    }

    /// 4) If a handler action reports "reverted", it must not change totalSupply
    ///    (tests atomicity / no partial state updates)
    function invariant_revertsDoNotChangeTotalSupply() public view {
        assertEq(token.totalSupply(), handler.ghost_totalSupply());
    }

    /// 5) Sanity: the token owner should always have DEFAULT_ADMIN_ROLE (synced by design)
    function invariant_ownerAlwaysAdmin() public view {
        assertTrue(token.hasRole(bytes32(0), token.owner()));
    }

   function _selectors() internal pure returns (bytes4[] memory) {
        bytes4[] memory sels = new bytes4[](5);

        sels[0] = SoreTokenHandler.addMinter.selector;
        sels[1] = SoreTokenHandler.removeMinter.selector;
        sels[2] = SoreTokenHandler.mintAs.selector;
        sels[3] = SoreTokenHandler.attackAddMinter.selector;
        sels[4] = SoreTokenHandler.attackRemoveMinter.selector;
        return sels;
    }
}

    