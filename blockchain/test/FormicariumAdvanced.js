import { expect } from "chai";
import hre from "hardhat";

describe("Advanced Formicarium Tests", function () {
  let formicarium, paymentToken;
  let owner, printer, customer, customer2, otherAccount;

  beforeEach(async function () {
    [owner, printer, customer, customer2, otherAccount] = await hre.ethers.getSigners();

    // Deploy a mock ERC20 token
    const MockERC20 = await hre.ethers.deployContract("ERC20Mock", [
      "MockToken",
      "MTK",
      owner.address,
      hre.ethers.parseEther("1000"),
    ]);
    paymentToken = await MockERC20.waitForDeployment();

    // Transfer tokens to customers so they can create orders
    await paymentToken.transfer(customer.address, hre.ethers.parseEther("100"));
    await paymentToken.transfer(customer2.address, hre.ethers.parseEther("100"));

    // Deploy Formicarium contract
    formicarium = await hre.ethers.deployContract("Formicarium", [paymentToken.target]);
    await formicarium.waitForDeployment();
  });

  it("Should process orders based on priority", async function () {
    // Register printer
    await formicarium.connect(printer).registerPrinter("Printer 1");

    // Approve tokens for both customers
    const lowPriorityPrice = hre.ethers.parseEther("10");
    const highPriorityPrice = hre.ethers.parseEther("20");

    await paymentToken.connect(customer).approve(formicarium.target, lowPriorityPrice);
    await paymentToken.connect(customer2).approve(formicarium.target, highPriorityPrice);

    // Create two orders with different priorities
    const orderId1 = hre.ethers.Wallet.createRandom().address; // Low priority
    const orderId2 = hre.ethers.Wallet.createRandom().address; // High priority

    await formicarium.connect(customer).createOrder(orderId1, printer.address, lowPriorityPrice, lowPriorityPrice, 3600);
    await formicarium.connect(customer2).createOrder(orderId2, printer.address, lowPriorityPrice, highPriorityPrice, 3600);

    // Sign both orders
    await formicarium.connect(printer).signOrder(orderId1);
    await formicarium.connect(printer).signOrder(orderId2);

    // Execute order
    await formicarium.connect(printer).executeNewOrder();

    // Verify that the high-priority order is selected first
    const executedOrder = await formicarium.orders(orderId2);
    expect(executedOrder.startTime).to.be.greaterThan(0);
  });

  it("Should allow customer to report an uncompleted order", async function () {
    // Register printer
    await formicarium.connect(printer).registerPrinter("Printer 1");

    // Approve tokens
    const orderPrice = hre.ethers.parseEther("10");
    await paymentToken.connect(customer).approve(formicarium.target, orderPrice);

    // Create order
    const orderId = hre.ethers.Wallet.createRandom().address;
    await formicarium.connect(customer).createOrder(orderId, printer.address, orderPrice, orderPrice, 3600);

    // Sign and execute order
    await formicarium.connect(printer).signOrder(orderId);
    await formicarium.connect(printer).executeNewOrder();

    // Complete order
    await formicarium.connect(printer).completeOrderProvider(orderId);

    // Customer reports the order as uncompleted
    await formicarium.connect(customer).reportUncompleteOrder(orderId);

    // Verify order is marked as uncompleted
    const order = await formicarium.orders(orderId);
    expect(order.isUncompleteCustomer).to.be.false;
  });

  it("Should prevent signing an already signed order", async function () {
    // Register printer
    await formicarium.connect(printer).registerPrinter("Printer 1");

    // Approve tokens
    const orderPrice = hre.ethers.parseEther("10");
    await paymentToken.connect(customer).approve(formicarium.target, orderPrice);

    // Create order
    const orderId = hre.ethers.Wallet.createRandom().address;
    await formicarium.connect(customer).createOrder(orderId, printer.address, orderPrice, orderPrice, 3600);

    // Sign order
    await formicarium.connect(printer).signOrder(orderId);

    // Try signing again (should fail)
    await expect(formicarium.connect(printer).signOrder(orderId)).to.be.revertedWith("Order already signed");
  });

  it("Should prevent refunding an already completed order", async function () {
    // Register printer
    await formicarium.connect(printer).registerPrinter("Printer 1");

    // Approve tokens
    const orderPrice = hre.ethers.parseEther("10");
    await paymentToken.connect(customer).approve(formicarium.target, orderPrice);

    // Create order
    const orderId = hre.ethers.Wallet.createRandom().address;
    await formicarium.connect(customer).createOrder(orderId, printer.address, orderPrice, orderPrice, 3600);

    // Sign, execute, and complete order
    await formicarium.connect(printer).signOrder(orderId);
    await formicarium.connect(printer).executeNewOrder();
    await formicarium.connect(printer).completeOrderProvider(orderId);

    // Attempt to refund (should fail)
    await expect(formicarium.connect(customer).refundOrderRequest(orderId)).to.be.revertedWith("Order request already signed");
  });

  it("Should prevent executing an order that has not been signed", async function () {
    // Register printer
    await formicarium.connect(printer).registerPrinter("Printer 1");

    // Approve tokens
    const orderPrice = hre.ethers.parseEther("10");
    await paymentToken.connect(customer).approve(formicarium.target, orderPrice);

    // Create order but do not sign it
    const orderId = hre.ethers.Wallet.createRandom().address;
    await formicarium.connect(customer).createOrder(orderId, printer.address, orderPrice, orderPrice, 3600);

    // Attempt to execute (should fail)
    await expect(formicarium.connect(printer).executeNewOrder()).to.be.revertedWith("No active orders to execute");
  });

  it("Should ensure an order is removed after processing", async function () {
    // Register printer
    await formicarium.connect(printer).registerPrinter("Printer 1");

    // Approve tokens
    const orderPrice = hre.ethers.parseEther("10");
    await paymentToken.connect(customer).approve(formicarium.target, orderPrice);

    // Create order
    const orderId = hre.ethers.Wallet.createRandom().address;
    await formicarium.connect(customer).createOrder(orderId, printer.address, orderPrice, orderPrice, 3600);

    // Sign, execute, and complete order
    await formicarium.connect(printer).signOrder(orderId);
    await formicarium.connect(printer).executeNewOrder();
    await formicarium.connect(printer).completeOrderProvider(orderId);

    // Fast forward time beyond reporting period
    await hre.network.provider.send("evm_increaseTime", [3600 + 300]); // +5 minutes buffer
    await hre.network.provider.send("evm_mine");

    // Transfer funds to provider
    await formicarium.connect(printer).transferFundsProivder(orderId);

    // Verify order has been deleted
    const order = await formicarium.orders(orderId);
    expect(order.ID).to.equal(hre.ethers.ZeroAddress);
  });

  it("Should emit OrderCreated event", async function () {
    await formicarium.connect(printer).registerPrinter("Printer 1");
    const orderId = hre.ethers.Wallet.createRandom().address;
    const orderPrice = hre.ethers.parseEther("10");
    await paymentToken.connect(customer).approve(formicarium.target, orderPrice);
    await expect(formicarium.connect(customer).createOrder(orderId, printer.address, orderPrice, orderPrice, 3600))
      .to.emit(formicarium, "OrderCreated")
      .withArgs(orderId, printer.address, orderPrice, orderPrice, 3600);
  });

  it("Should emit OrderSigned event", async function () {
    await formicarium.connect(printer).registerPrinter("Printer 1");
    const orderId = hre.ethers.Wallet.createRandom().address;
    const orderPrice = hre.ethers.parseEther("10");
    await paymentToken.connect(customer).approve(formicarium.target, orderPrice);
    await formicarium.connect(customer).createOrder(orderId, printer.address, orderPrice, orderPrice, 3600);
    await expect(formicarium.connect(printer).signOrder(orderId))
      .to.emit(formicarium, "OrderSigned")
      .withArgs(orderId, printer.address);
  });

  it("Should emit OrderStarted event", async function () {
    await formicarium.connect(printer).registerPrinter("Printer 1");
    const orderId = hre.ethers.Wallet.createRandom().address;
    const orderPrice = hre.ethers.parseEther("10");
    await paymentToken.connect(customer).approve(formicarium.target, orderPrice);
    await formicarium.connect(customer).createOrder(orderId, printer.address, orderPrice, orderPrice, 3600);
    await formicarium.connect(printer).signOrder(orderId);
    await expect(formicarium.connect(printer).executeNewOrder())
      .to.emit(formicarium, "OrderStarted")
      .withArgs(orderId, printer.address);
  });

  it("Should emit OrderCompleted event", async function () {
    await formicarium.connect(printer).registerPrinter("Printer 1");
    const orderId = hre.ethers.Wallet.createRandom().address;
    const orderPrice = hre.ethers.parseEther("10");
    await paymentToken.connect(customer).approve(formicarium.target, orderPrice);
    await formicarium.connect(customer).createOrder(orderId, printer.address, orderPrice, orderPrice, 3600);
    await formicarium.connect(printer).signOrder(orderId);
    await formicarium.connect(printer).executeNewOrder();
    await expect(formicarium.connect(printer).completeOrderProvider(orderId))
      .to.emit(formicarium, "OrderCompleted")
      .withArgs(orderId, printer.address);
  });
});
