// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {Ownable2Step} from "@openzeppelin/contracts/access/Ownable2Step.sol";

/**
 * @title SoreToken
 * @notice ERC20 with:
 *  - Controlled minting (MINTER_ROLE)
 *  - Owner-managed minter list
 *  - Optional max supply cap (0 = uncapped)
 *  - 2-step ownership transfer (safer)
 *
 * @dev Roles:
 *  - DEFAULT_ADMIN_ROLE: role admin root (synced with owner)
 *  - MINTER_ROLE: accounts allowed to mint
 */
contract SoreToken is ERC20, AccessControl, Ownable2Step {
    // -------------------------
    // Roles
    // -------------------------
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");

    // -------------------------
    // Supply controls
    // -------------------------
    /// @notice Max supply of the token. If 0 => uncapped.
    uint256 public immutable maxSupply;

    // -------------------------
    // Events
    // -------------------------
    event MinterAdded(address indexed account);
    event MinterRemoved(address indexed account);

    // -------------------------
    // Errors
    // -------------------------
    error MaxSupplyExceeded(uint256 attemptedTotalSupply, uint256 maxSupplyLimit);
    error InitialSupplyExceedsCap(uint256 initialSupply, uint256 maxSupplyLimit);
    error ZeroAddress();

    // -------------------------
    // Constructor
    // -------------------------

    /**
     * @param name_ Token name
     * @param symbol_ Token symbol
     * @param owner_ Initial owner (and admin)
     * @param initialSupply Initial supply minted to owner_
     * @param maxSupply_ Max supply cap (0 = uncapped)
     */
    constructor(
        string memory name_,
        string memory symbol_,
        address owner_,
        uint256 initialSupply,
        uint256 maxSupply_
    )
        ERC20(name_, symbol_)
        Ownable(owner_) // OZ v5 validates non-zero owner
    {
        if (maxSupply_ != 0 && initialSupply > maxSupply_) {
            revert InitialSupplyExceedsCap(initialSupply, maxSupply_);
        }

        maxSupply = maxSupply_;

        // Owner is admin of roles and initial minter
        _grantRole(DEFAULT_ADMIN_ROLE, owner_);
        _grantRole(MINTER_ROLE, owner_);

        // Optional initial mint
        if (initialSupply > 0) {
            _mint(owner_, initialSupply);
        }
    }

    // -------------------------
    // Owner-managed minters
    // -------------------------

    /// @notice Grant MINTER_ROLE to an account (owner-only).
    function addMinter(address account) external onlyOwner {
        if (account == address(0)) revert ZeroAddress();
        _grantRole(MINTER_ROLE, account);
        emit MinterAdded(account);
    }

    /// @notice Revoke MINTER_ROLE from an account (owner-only).
    function removeMinter(address account) external onlyOwner {
        if (account == address(0)) revert ZeroAddress();
        _revokeRole(MINTER_ROLE, account);
        emit MinterRemoved(account);
    }

    // -------------------------
    // Minting (controlled)
    // -------------------------

    /// @notice Mint tokens to `to`. Requires MINTER_ROLE.
    function mint(address to, uint256 amount) external onlyRole(MINTER_ROLE) {
        if (to == address(0)) revert ZeroAddress();

        if (maxSupply != 0) {
            uint256 newTotalSupply = totalSupply() + amount;
            if (newTotalSupply > maxSupply) {
                revert MaxSupplyExceeded(newTotalSupply, maxSupply);
            }
        }

        _mint(to, amount);
    }

    // -------------------------
    // Ownership ↔ Role sync
    // -------------------------

    /**
     * @dev Keep DEFAULT_ADMIN_ROLE and MINTER_ROLE synced with the owner.
     * Ownable2Step finalizes transfers via acceptOwnership(), which calls _transferOwnership().
     */
    function _transferOwnership(address newOwner) internal override(Ownable2Step) {
        address oldOwner = owner();
        super._transferOwnership(newOwner);

        // Move roles from old owner to new owner
        if (oldOwner != address(0)) {
            _revokeRole(DEFAULT_ADMIN_ROLE, oldOwner);
            _revokeRole(MINTER_ROLE, oldOwner);
        }
        _grantRole(DEFAULT_ADMIN_ROLE, newOwner);
        _grantRole(MINTER_ROLE, newOwner);
    }

    // -------------------------
    // ERC165 support
    // -------------------------

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(AccessControl)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
