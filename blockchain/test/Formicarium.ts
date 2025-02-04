import { expect } from "chai";
import hre from "hardhat";
import {
  time,
  loadFixture,
} from "@nomicfoundation/hardhat-toolbox-viem/network-helpers";
import { getAddress, parseEther } from "viem";

describe("Formicarium Smart Contract", function () {
  async function deployFormicariumFixture() {
    const [owner, printer, customer, otherAccount] =
      await hre.viem.getWalletClients();

    // Deploy a mock ERC20 token
    const paymentToken = await hre.viem.deployContract("MockERC20", []);

    // Deploy the Formicarium contract
    const formicarium = await hre.viem.deployContract(
      "Formicarium",
      [paymentToken.address]
    );

    return {
      formicarium,
      paymentToken,
      owner,
      printer,
      customer,
      otherAccount,
    };
  }

  describe("Deployment", function () {
    it("Should set the correct owner", async function () {
      const { formicarium, owner } = await loadFixture(deployFormicariumFixture);
      expect(await formicarium.read.owner()).to.equal(getAddress(owner.account.address));
    });

    it("Should set the correct payment token", async function () {
      const { formicarium, paymentToken } = await loadFixture(deployFormicariumFixture);
      expect(await formicarium.read.paymentToken()).to.equal(paymentToken.address);
    });
  });

  describe("Printer Registration", function () {
    it("Should allow a user to register as a printer", async function () {
      const { formicarium, printer } = await loadFixture(deployFormicariumFixture);

      await formicarium.write.registerPrinter(["High-Precision Printer"], {
        account: printer.account,
      });

      const registeredPrinter = await formicarium.read.printers([
        printer.account.address,
      ]);

      expect(registeredPrinter.ID).to.equal(getAddress(printer.account.address));
      expect(registeredPrinter.printerDetails).to.equal("High-Precision Printer");
    });

    it("Should prevent duplicate printer registration", async function () {
      const { formicarium, printer } = await loadFixture(deployFormicariumFixture);

      await formicarium.write.registerPrinter(["High-Precision Printer"], {
        account: printer.account,
      });

      await expect(
        formicarium.write.registerPrinter(["Another Printer"], {
          account: printer.account,
        })
      ).to.be.rejectedWith("Printer already registered");
    });
  });

  describe("Order Creation", function () {
    it("Should allow customers to create an order", async function () {
      const { formicarium, paymentToken, customer, printer } =
        await loadFixture(deployFormicariumFixture);

      // Register printer
      await formicarium.write.registerPrinter(["Test Printer"], {
        account: printer.account,
      });

      // Mint and approve payment tokens
      await paymentToken.write.mint([customer.account.address, parseEther("10")]);
      await paymentToken.write.approve([formicarium.address, parseEther("5")], {
        account: customer.account,
      });

      // Create order
      const orderId = customer.account.address; // Use customer address as order ID for simplicity
      await formicarium.write.createOrder(
        [orderId, printer.account.address, parseEther("5"), 600],
        { account: customer.account }
      );

      const order = await formicarium.read.orders([orderId]);
      expect(order.ID).to.equal(orderId);
      expect(order.customerId).to.equal(customer.account.address);
      expect(order.initialPrice).to.equal(parseEther("5"));
      expect(order.duration).to.equal(600);
    });

    it("Should reject orders if insufficient balance", async function () {
      const { formicarium, paymentToken, customer, printer } =
        await loadFixture(deployFormicariumFixture);

      await formicarium.write.registerPrinter(["Test Printer"], {
        account: printer.account,
      });

      // Create order without funding the customer
      const orderId = customer.account.address;
      await expect(
        formicarium.write.createOrder(
          [orderId, printer.account.address, parseEther("5"), 600],
          { account: customer.account }
        )
      ).to.be.rejectedWith("Insufficient balance");
    });
  });

  describe("Order Execution", function () {
    it("Should allow a printer to sign an order", async function () {
      const { formicarium, paymentToken, printer, customer } =
        await loadFixture(deployFormicariumFixture);

      await formicarium.write.registerPrinter(["Test Printer"], {
        account: printer.account,
      });

      // Mint tokens and approve contract
      await paymentToken.write.mint([customer.account.address, parseEther("10")]);
      await paymentToken.write.approve([formicarium.address, parseEther("5")], {
        account: customer.account,
      });

      const orderId = customer.account.address;
      await formicarium.write.createOrder(
        [orderId, printer.account.address, parseEther("5"), 600],
        { account: customer.account }
      );

      // Sign the order
      await formicarium.write.signOrder([orderId], { account: printer.account });

      const order = await formicarium.read.orders([orderId]);
      expect(order.isSigned).to.be.true;
    });

    it("Should allow a printer to execute an order", async function () {
      const { formicarium, paymentToken, printer, customer } =
        await loadFixture(deployFormicariumFixture);

      await formicarium.write.registerPrinter(["Test Printer"], {
        account: printer.account,
      });

      await paymentToken.write.mint([customer.account.address, parseEther("10")]);
      await paymentToken.write.approve([formicarium.address, parseEther("5")], {
        account: customer.account,
      });

      const orderId = customer.account.address;
      await formicarium.write.createOrder(
        [orderId, printer.account.address, parseEther("5"), 600],
        { account: customer.account }
      );

      await formicarium.write.signOrder([orderId], { account: printer.account });

      // Execute the order
      await formicarium.write.executeNewOrder([], { account: printer.account });

      const order = await formicarium.read.orders([orderId]);
      expect(order.startTime).to.be.greaterThan(0);
    });
  });

  describe("Order Completion and Payments", function () {
    it("Should allow a printer to complete an order", async function () {
      const { formicarium, paymentToken, printer, customer } =
        await loadFixture(deployFormicariumFixture);

      await formicarium.write.registerPrinter(["Test Printer"], {
        account: printer.account,
      });

      await paymentToken.write.mint([customer.account.address, parseEther("10")]);
      await paymentToken.write.approve([formicarium.address, parseEther("5")], {
        account: customer.account,
      });

      const orderId = customer.account.address;
      await formicarium.write.createOrder(
        [orderId, printer.account.address, parseEther("5"), 600],
        { account: customer.account }
      );

      await formicarium.write.signOrder([orderId], { account: printer.account });
      await formicarium.write.executeNewOrder([], { account: printer.account });

      await time.increase(610);

      await formicarium.write.completeOrderProvider([orderId], { account: printer.account });

      const order = await formicarium.read.orders([orderId]);
      expect(order.isCompletedProvider).to.be.true;
    });
  });
});
