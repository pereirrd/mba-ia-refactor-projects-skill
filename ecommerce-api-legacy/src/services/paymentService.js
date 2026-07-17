const { settings } = require("../config/settings");

class PaymentService {
  processCard(cardNumber) {
    const sanitized = String(cardNumber || "").replace(/\s+/g, "");
    const last4 = sanitized.slice(-4);
    const status = sanitized.startsWith("4") ? "PAID" : "DENIED";
    return {
      status,
      last4,
      gateway: settings.paymentGatewayKey.startsWith("pk_live")
        ? "live-misconfigured"
        : "test",
    };
  }
}

module.exports = { PaymentService };
