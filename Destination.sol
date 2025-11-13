// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "./BridgeToken.sol";

contract Destination is AccessControl {
    bytes32 public constant WARDEN_ROLE = keccak256("BRIDGE_WARDEN_ROLE");
    bytes32 public constant CREATOR_ROLE = keccak256("CREATOR_ROLE");
    mapping(address => address) public underlying_tokens;
    mapping(address => address) public wrapped_tokens;
    address[] public tokens;

    event Creation(address indexed underlying_token, address indexed wrapped_token);
    event Wrap(address indexed underlying_token, address indexed wrapped_token, address indexed to, uint256 amount);
    event Unwrap(address indexed underlying_token, address indexed wrapped_token, address frm, address indexed to, uint256 amount);

    constructor(address admin) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(CREATOR_ROLE, admin);
        _grantRole(WARDEN_ROLE, admin);
    }

    function wrap(address _u, address _to, uint256 _amt) public onlyRole(WARDEN_ROLE) {
        address w = wrapped_tokens[_u];
        require(w != address(0), "token not registered");
        BridgeToken(w).mint(_to, _amt);
        emit Wrap(_u, w, _to, _amt);
    }

    function unwrap(address _w, address _to, uint256 _amt) public {
        address u = underlying_tokens[_w];
        require(u != address(0), "token not registered");
        BridgeToken(_w).burnFrom(msg.sender, _amt);
        emit Unwrap(u, _w, msg.sender, _to, _amt);
    }

    function createToken(address _u, string memory n, string memory s) public onlyRole(CREATOR_ROLE) returns (address) {
        BridgeToken t = new BridgeToken(_u, n, s, address(this));
        address w = address(t);
        wrapped_tokens[_u] = w;
        underlying_tokens[w] = _u;
        tokens.push(w);
        emit Creation(_u, w);
        return w;
    }
}