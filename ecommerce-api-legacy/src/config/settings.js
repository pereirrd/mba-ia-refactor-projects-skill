const settings = {
  port: Number(process.env.PORT || 3000),
  databasePath: process.env.DATABASE_PATH || ":memory:",
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || "pk_test_dev_only",
  smtpUser: process.env.SMTP_USER || "no-reply@example.com",
  bcryptRounds: Number(process.env.BCRYPT_ROUNDS || 10),
  environment: process.env.NODE_ENV || "development",
};

module.exports = { settings };
