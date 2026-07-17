const {
  createCheckoutController,
  createReportController,
  createUserController,
} = require("../controllers");

function registerRoutes(app, models) {
  const checkoutController = createCheckoutController(models);
  const reportController = createReportController(models);
  const userController = createUserController(models);

  app.post("/api/checkout", (req, res, next) =>
    checkoutController.checkout(req, res, next)
  );
  app.get("/api/admin/financial-report", (req, res, next) =>
    reportController.financialReport(req, res, next)
  );
  app.delete("/api/users/:id", (req, res, next) =>
    userController.deleteUser(req, res, next)
  );
}

module.exports = { registerRoutes };
