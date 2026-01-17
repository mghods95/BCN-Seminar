// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import {SoreToken} from "../../src/SoreToken.sol";

/**
 * @notice Handler for invariant tests.
 * Foundry calls these functions in random order with random inputs.
 *
 * Key idea:
 * - We track expected totalSupply (ghost_totalSupply) to ensure failed calls
 *   never partially update state.
 */
contract SoreTokenHandler is Test {
    SoreToken internal immutable token;
    address internal immutable owner;

    address internal constant A = address(0x111);
    address internal constant B = address(0x222);
    address internal constant C = address(0x333);
    address internal constant D = address(0x444);

    // Ghost variable: what totalSupply "should be" if all successful mints are accounted for.
    uint256 internal _ghostTotalSupply;

    constructor(SoreToken _token, address _owner) {
        token = _token;
        owner = _owner;
        _ghostTotalSupply = _token.totalSupply();
    }

    // Expose ghost var for invariant assertions
    function ghost_totalSupply() external view returns (uint256) {
        return _ghostTotalSupply;
    }

    // -------------------------
    // Owner actions (expected to succeed)
    // -------------------------

    function addMinter(address who) external {
        who = _actor(who);

        // snapshot
        uint256 beforeSupply = token.totalSupply();

        vm.prank(owner);
        token.addMinter(who);

        // should not change supply
        _assertSupplyUnchanged(beforeSupply);
    }

    function removeMinter(address who) external {
        who = _actor(who);

        uint256 beforeSupply = token.totalSupply();

        vm.prank(owner);
        token.removeMinter(who);

        _assertSupplyUnchanged(beforeSupply);
    }

    // -------------------------
    // Mint action (may succeed or revert)
    // -------------------------

    function mintAs(address caller, address to, uint256 amount) external {
        caller = _actor(caller);
        to = _actor(to);

        uint256 cap = token.maxSupply();
        uint256 upper = cap == 0 ? 1_000_000 : cap;
        amount = bound(amount, 0, upper);

        uint256 beforeSupply = token.totalSupply();
        uint256 beforeToBal = token.balanceOf(to);

        vm.prank(caller);
        (bool ok, ) = address(token).call(
            abi.encodeWithSelector(SoreToken.mint.selector, to, amount)
        );

        if (ok) {
            // If mint succeeded, state must reflect it
            uint256 afterSupply = token.totalSupply();
            assertEq(afterSupply, beforeSupply + amount);
            assertEq(token.balanceOf(to), beforeToBal + amount);

            _ghostTotalSupply = afterSupply;
        } else {
            // If mint failed, supply must not change
            _assertSupplyUnchanged(beforeSupply);
            assertEq(token.balanceOf(to), beforeToBal);
            // ghost stays the same
        }
    }

    // -------------------------
    // Attack actions (must always fail)
    // -------------------------

    function attackAddMinter(address attacker, address who) external {
        attacker = _actor(attacker);
        who = _actor(who);

        // attacker must not be owner
        if (attacker == owner) attacker = A;

        uint256 beforeSupply = token.totalSupply();

        vm.prank(attacker);
        (bool ok, ) = address(token).call(
            abi.encodeWithSelector(SoreToken.addMinter.selector, who)
        );

        // must fail (onlyOwner)
        assertTrue(!ok);
        _assertSupplyUnchanged(beforeSupply);
    }

    function attackRemoveMinter(address attacker, address who) external {
        attacker = _actor(attacker);
        who = _actor(who);

        if (attacker == owner) attacker = B;

        uint256 beforeSupply = token.totalSupply();

        vm.prank(attacker);
        (bool ok, ) = address(token).call(
            abi.encodeWithSelector(SoreToken.removeMinter.selector, who)
        );

        // must fail (onlyOwner)
        assertTrue(!ok);
        _assertSupplyUnchanged(beforeSupply);
    }

    // -------------------------
    // Helpers
    // -------------------------

    function _assertSupplyUnchanged(uint256 beforeSupply) internal view {
        assertEq(token.totalSupply(), beforeSupply);
        assertEq(_ghostTotalSupply, beforeSupply); // ghost and real must match
    }

    function _actor(address x) internal pure returns (address) {
        // note: we intentionally avoid returning address(0) to prevent trivial reverts
        uint160 v = uint160(x);
        if (v % 4 == 0) return A;
        if (v % 4 == 1) return B;
        if (v % 4 == 2) return C;
        return D;
    }
}
