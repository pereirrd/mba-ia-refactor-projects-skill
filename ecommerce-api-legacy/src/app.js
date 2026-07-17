const express = require("express");
const { settings } = require("./config/settings");
const { createDatabase } = require("./models/database");
const {
  createUserModel,
  createCourseModel,
  createEnrollmentModel,
  createPaymentModel,
  createAuditModel,
  createReportModel,
} = require("./models");
const { registerRoutes } = require("./views/routes");
const { notFoundHandler, errorHandler } = require("./middlewares/errorHandler");

async function bootstrap() {
  const app = express();
  app.use(express.json());

  const db = createDatabase();
  await db.init();

  const models = {
    user: createUserModel(db),
    course: createCourseModel(db),
    enrollment: createEnrollmentModel(db),
    payment: createPaymentModel(db),
    audit: createAuditModel(db),
    report: createReportModel(db),
  };

  registerRoutes(app, models);
  app.use(notFoundHandler);
  app.use(errorHandler);

  app.listen(settings.port, () => {
    console.log(`LMS API (MVC) rodando na porta ${settings.port}...`);
  });
}

bootstrap().catch((err) => {
  console.error("Falha ao iniciar aplicação:", err);
  process.exit(1);
});
