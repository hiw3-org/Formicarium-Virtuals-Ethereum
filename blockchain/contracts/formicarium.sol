// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

// Uncomment this line to use console.log
// import "hardhat/console.sol";

interface IERC20 {
    function transfer(address recipient, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
}

contract Formicarium {
    address public owner;
    IERC20 public paymentToken;

    struct Printer {
        address ID;
        string printerDetails;
        address currentOrderId;
    }

    struct Order {
        address ID;
        address printerId;
        address customerId;
        uint256 price;
        uint256 duration;
        uint256 startTime;
        bool isSigned;
    }

    mapping(address => Printer) public printers;
    mapping(address => Order) public orders;


    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }

    modifier onlyPrinter() {
        require(printers[msg.sender].ID == msg.sender, "Only printer can call this function");
        _;
    }

    constructor(address _paymentToken) {
        owner = msg.sender;
        paymentToken = IERC20(_paymentToken);
    }


    // Functions
    function registerPrinter(string memory _printerDetails) public {
        require(printers[msg.sender].ID == address(0), "Printer already registered");
        printers[msg.sender] = Printer(msg.sender, _printerDetails, address(0));
    }

    function createOrder(address _orderId, address _printerId, uint256 _price, uint256 _duration) public {
        require(orders[_orderId].ID == address(0), "Order already exists");
        orders[_orderId] = Order(_orderId, _printerId, msg.sender, _price, _duration, 0, false);
    }

    function signOrder(address _orderId) public onlyPrinter {
        require(orders[_orderId].ID == _orderId, "Order does not exist");
        require(orders[_orderId].printerId == msg.sender, "Only service provider can sign order");
        require(orders[_orderId].isSigned == false, "Order already signed");
        orders[_orderId].isSigned = true;
    }

    function executeNewOrder(address _orderId) public onlyPrinter {
        require(orders[_orderId].ID == _orderId, "Order does not exist");
        require(orders[_orderId].printerId == msg.sender, "Only service provider can execute order");
        require(orders[_orderId].isSigned == true, "Order not signed");
        require(orders[_orderId].startTime == 0, "Order already started");
        orders[_orderId].startTime = block.timestamp;
    }

}
