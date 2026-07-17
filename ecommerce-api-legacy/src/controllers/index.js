const { hashPassword, verifyPassword } = require("../models/database");
const { PaymentService } = require("../services/paymentService");

function createCheckoutController(models) {
  const paymentService = new PaymentService();

  return {
    async checkout(req, res, next) {
      try {
        const name = req.body.usr || req.body.name;
        const email = req.body.eml || req.body.email;
        const password = req.body.pwd || req.body.password;
        const courseId = req.body.c_id || req.body.course_id;
        const card = req.body.card;

        if (!name || !email || !courseId || !card) {
          return res.status(400).json({ error: "Bad Request" });
        }

        const course = await models.course.findActiveById(courseId);
        if (!course) {
          return res.status(404).json({ error: "Curso não encontrado" });
        }

        let user = await models.user.findByEmail(email);
        if (!user) {
          if (!password) {
            return res.status(400).json({ error: "Senha obrigatória para novo usuário" });
          }
          const userId = await models.user.create({
            name,
            email,
            passwordHash: hashPassword(password),
          });
          user = { id: userId, name, email };
        } else {
          if (!password || !verifyPassword(password, user.pass)) {
            return res.status(401).json({ error: "Credenciais inválidas" });
          }
        }

        const payment = paymentService.processCard(card);
        if (payment.status === "DENIED") {
          return res.status(400).json({ error: "Pagamento recusado" });
        }

        const enrollmentId = await models.enrollment.create(user.id, courseId);
        await models.payment.create(enrollmentId, course.price, payment.status);
        await models.audit.log(
          `Checkout curso ${courseId} por ${user.id} (card ****${payment.last4})`
        );

        return res.status(200).json({
          msg: "Sucesso",
          enrollment_id: enrollmentId,
        });
      } catch (error) {
        return next(error);
      }
    },
  };
}

function createReportController(models) {
  return {
    async financialReport(req, res, next) {
      try {
        const rows = await models.report.financialReport();
        const report = rows.map((row) => {
          const students = [];
          if (row.students_raw) {
            row.students_raw.split(",").forEach((entry) => {
              const [student, paid] = entry.split(":");
              if (student) {
                students.push({
                  student,
                  paid: Number(paid || 0),
                });
              }
            });
          }
          return {
            course: row.course,
            revenue: Number(row.revenue || 0),
            students,
          };
        });
        return res.json(report);
      } catch (error) {
        return next(error);
      }
    },
  };
}

function createUserController(models) {
  return {
    async deleteUser(req, res, next) {
      try {
        const changes = await models.user.deleteById(req.params.id);
        if (!changes) {
          return res.status(404).json({ error: "Usuário não encontrado" });
        }
        return res.json({
          message: "Usuário e dados relacionados removidos com sucesso",
        });
      } catch (error) {
        return next(error);
      }
    },
  };
}

module.exports = {
  createCheckoutController,
  createReportController,
  createUserController,
};
