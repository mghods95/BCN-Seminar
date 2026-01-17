// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import {IAccessControl} from "@openzeppelin/contracts/access/IAccessControl.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {SoreToken} from "../src/SoreToken.sol";

contract SoreTokenUnitTest is Test {
    SoreToken internal token;

    address internal owner  = address(0xA11CE);
    address internal alice  = address(0xB0B);
    address internal bob    = address(0xBEEF);
    address internal minter = address(0xC0FFEE);

    function setUp() public {
        token = new SoreToken("Sore Token", "SORE", owner, 0, 1_000_000);
    }

    // -------------------------
    // Constructor / setup
    // -------------------------

    function test_constructor_setsOwnerAndInitialRoles() public {
        assertEq(token.owner(), owner);
        assertTrue(token.hasRole(bytes32(0), owner));
        assertTrue(token.hasRole(token.MINTER_ROLE(), owner));
        assertEq(token.maxSupply(), 1_000_000);
        assertEq(token.totalSupply(), 0);
    }

    function test_constructor_revertsOnZeroOwner() public {
        vm.expectRevert(
            abi.encodeWithSelector(
                Ownable.OwnableInvalidOwner.selector,
                address(0)
            )
        );
        new SoreToken("Sore Token", "SORE", address(0), 0, 1_000_000);
    }

    function test_constructor_mintsInitialSupplyToOwner() public {
        SoreToken t = new SoreToken("Sore Token", "SORE", owner, 123, 1_000_000);
        assertEq(t.totalSupply(), 123);
        assertEq(t.balanceOf(owner), 123);
    }

    function test_constructor_revertsIfInitialSupplyExceedsCap() public {
        vm.expectRevert(
            abi.encodeWithSelector(
                SoreToken.InitialSupplyExceedsCap.selector,
                101,
                100
            )
        );
        new SoreToken("Sore Token", "SORE", owner, 101, 100);
    }

    // -------------------------
    // Owner-only minter management
    // -------------------------

    function test_onlyOwner_canAddMinter() public {
        vm.prank(alice);
        vm.expectRevert();
        token.addMinter(minter);

        vm.prank(owner);
        token.addMinter(minter);
        assertTrue(token.hasRole(token.MINTER_ROLE(), minter));
    }

    function test_addMinter_revertsOnZeroAddress() public {
        vm.prank(owner);
        vm.expectRevert(SoreToken.ZeroAddress.selector);
        token.addMinter(address(0));
    }

    function test_onlyOwner_canRemoveMinter() public {
        vm.prank(owner);
        token.addMinter(minter);

        vm.prank(alice);
        vm.expectRevert();
        token.removeMinter(minter);

        vm.prank(owner);
        token.removeMinter(minter);
        assertFalse(token.hasRole(token.MINTER_ROLE(), minter));
    }

    function test_removeMinter_revertsOnZeroAddress() public {
        vm.prank(owner);
        vm.expectRevert(SoreToken.ZeroAddress.selector);
        token.removeMinter(address(0));
    }

    function test_removeMinter_onNonMinter_keepsRoleFalse() public {
        vm.prank(owner);
        token.removeMinter(minter);
        assertFalse(token.hasRole(token.MINTER_ROLE(), minter));
    }

    // -------------------------
    // Minting rules
    // -------------------------

    function test_onlyMinter_canMint() public {
        bytes32 MINTER = token.MINTER_ROLE();

        vm.prank(alice);
        vm.expectRevert(
            abi.encodeWithSelector(
                IAccessControl.AccessControlUnauthorizedAccount.selector,
                alice,
                MINTER
            )
        );
        token.mint(alice, 1);

        vm.prank(owner);
        token.mint(alice, 10);
        assertEq(token.balanceOf(alice), 10);
    }

    function test_mint_revertsToZeroAddress() public {
        vm.prank(owner);
        vm.expectRevert(SoreToken.ZeroAddress.selector);
        token.mint(address(0), 1);
    }

    function test_addedMinter_canMint_andRemovedMinter_cannotMint() public {
        bytes32 MINTER = token.MINTER_ROLE();

        vm.prank(owner);
        token.addMinter(minter);

        vm.prank(minter);
        token.mint(alice, 100);
        assertEq(token.balanceOf(alice), 100);

        vm.prank(owner);
        token.removeMinter(minter);

        vm.prank(minter);
        vm.expectRevert(
            abi.encodeWithSelector(
                IAccessControl.AccessControlUnauthorizedAccount.selector,
                minter,
                MINTER
            )
        );
        token.mint(alice, 1);
    }

    function test_mint_respectsCap() public {
        vm.prank(owner);
        token.mint(alice, 1_000_000);

        vm.prank(owner);
        vm.expectRevert(
            abi.encodeWithSelector(
                SoreToken.MaxSupplyExceeded.selector,
                1_000_001,
                1_000_000
            )
        );
        token.mint(alice, 1);
    }

    // -------------------------
    // Ownership 2-step + role sync
    // -------------------------

    function test_transferOwnership_isTwoStep() public {
        vm.prank(owner);
        token.transferOwnership(bob);

        assertEq(token.owner(), owner);
        assertEq(token.pendingOwner(), bob);
    }

    function test_onlyPendingOwner_canAccept() public {
        vm.prank(owner);
        token.transferOwnership(bob);

        vm.prank(alice);
        vm.expectRevert();
        token.acceptOwnership();
    }

    function test_onlyOwner_canTransferOwnership() public {
        vm.prank(alice);
        vm.expectRevert();
        token.transferOwnership(bob);
    }

    /// @dev Ownable2Step allows setting pendingOwner to zero to cancel the transfer.
    function test_transferOwnership_toZero_cancelsPendingOwner() public {
        vm.prank(owner);
        token.transferOwnership(bob);
        assertEq(token.pendingOwner(), bob);

        vm.prank(owner);
        token.transferOwnership(address(0));

        assertEq(token.owner(), owner);
        assertEq(token.pendingOwner(), address(0));

        vm.prank(bob);
        vm.expectRevert();
        token.acceptOwnership();
    }

    function test_transferOwnership_overwritesPendingOwner() public {
        vm.prank(owner);
        token.transferOwnership(alice);
        assertEq(token.pendingOwner(), alice);

        vm.prank(owner);
        token.transferOwnership(bob);
        assertEq(token.pendingOwner(), bob);

        vm.prank(alice);
        vm.expectRevert();
        token.acceptOwnership();

        vm.prank(bob);
        token.acceptOwnership();
        assertEq(token.owner(), bob);
    }

    function test_acceptOwnership_movesAdminAndMinterRoles() public {
        assertTrue(token.hasRole(bytes32(0), owner));
        assertTrue(token.hasRole(token.MINTER_ROLE(), owner));

        vm.prank(owner);
        token.transferOwnership(bob);

        vm.prank(bob);
        token.acceptOwnership();

        assertEq(token.owner(), bob);
        assertEq(token.pendingOwner(), address(0));

        assertFalse(token.hasRole(bytes32(0), owner));
        assertFalse(token.hasRole(token.MINTER_ROLE(), owner));

        assertTrue(token.hasRole(bytes32(0), bob));
        assertTrue(token.hasRole(token.MINTER_ROLE(), bob));
    }

    function test_oldOwner_cannotGrantRoleAfterOwnershipTransfer() public {
        bytes32 ADMIN  = bytes32(0);
        bytes32 MINTER = token.MINTER_ROLE();

        vm.prank(owner);
        token.transferOwnership(bob);
        vm.prank(bob);
        token.acceptOwnership();

        vm.prank(owner);
        vm.expectRevert(
            abi.encodeWithSelector(
                IAccessControl.AccessControlUnauthorizedAccount.selector,
                owner,
                ADMIN
            )
        );
        token.grantRole(MINTER, alice);
    }

    function test_oldOwner_cannotMint_afterOwnershipTransfer() public {
        bytes32 MINTER = token.MINTER_ROLE();

        vm.prank(owner);
        token.transferOwnership(bob);
        vm.prank(bob);
        token.acceptOwnership();

        vm.prank(owner);
        vm.expectRevert(
            abi.encodeWithSelector(
                IAccessControl.AccessControlUnauthorizedAccount.selector,
                owner,
                MINTER
            )
        );
        token.mint(alice, 1);
    }

    function test_newOwner_canAddMinter_afterOwnershipTransfer() public {
        vm.prank(owner);
        token.transferOwnership(bob);
        vm.prank(bob);
        token.acceptOwnership();

        vm.prank(bob);
        token.addMinter(minter);
        assertTrue(token.hasRole(token.MINTER_ROLE(), minter));
    }

    function test_otherMinters_remainAfterOwnershipTransfer() public {
        vm.prank(owner);
        token.addMinter(minter);

        vm.prank(owner);
        token.transferOwnership(bob);
        vm.prank(bob);
        token.acceptOwnership();

        vm.prank(minter);
        token.mint(alice, 50);
        assertEq(token.balanceOf(alice), 50);
    }

    // -------------------------
    // Interface support (sanity)
    // -------------------------

    function test_supportsInterface_includesIAccessControl() public view {
        assertTrue(token.supportsInterface(type(IAccessControl).interfaceId));
    }
}
