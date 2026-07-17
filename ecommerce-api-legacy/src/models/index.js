function createUserModel(db) {
  return {
    findByEmail(email) {
      return db.get("SELECT id, name, email, pass FROM users WHERE email = ?", [email]);
    },
    findById(id) {
      return db.get("SELECT id, name, email FROM users WHERE id = ?", [id]);
    },
    async create({ name, email, passwordHash }) {
      const result = await db.run(
        "INSERT INTO users (name, email, pass) VALUES (?, ?, ?)",
        [name, email, passwordHash]
      );
      return result.lastID;
    },
    async deleteById(id) {
      await db.run("DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)", [id]);
      await db.run("DELETE FROM enrollments WHERE user_id = ?", [id]);
      const result = await db.run("DELETE FROM users WHERE id = ?", [id]);
      return result.changes;
    },
  };
}

function createCourseModel(db) {
  return {
    findActiveById(id) {
      return db.get("SELECT * FROM courses WHERE id = ? AND active = 1", [id]);
    },
    listAll() {
      return db.all("SELECT * FROM courses ORDER BY id");
    },
  };
}

function createEnrollmentModel(db) {
  return {
    async create(userId, courseId) {
      const result = await db.run(
        "INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)",
        [userId, courseId]
      );
      return result.lastID;
    },
  };
}

function createPaymentModel(db) {
  return {
    async create(enrollmentId, amount, status) {
      const result = await db.run(
        "INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)",
        [enrollmentId, amount, status]
      );
      return result.lastID;
    },
  };
}

function createAuditModel(db) {
  return {
    async log(action) {
      await db.run(
        "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
        [action]
      );
    },
  };
}

function createReportModel(db) {
  return {
    async financialReport() {
      return db.all(
        `
        SELECT
          c.title AS course,
          COALESCE(SUM(CASE WHEN p.status = 'PAID' THEN p.amount ELSE 0 END), 0) AS revenue,
          GROUP_CONCAT(
            CASE
              WHEN u.name IS NOT NULL THEN u.name || ':' || COALESCE(p.amount, 0)
              ELSE NULL
            END
          ) AS students_raw
        FROM courses c
        LEFT JOIN enrollments e ON e.course_id = c.id
        LEFT JOIN users u ON u.id = e.user_id
        LEFT JOIN payments p ON p.enrollment_id = e.id
        GROUP BY c.id, c.title
        ORDER BY c.id
        `
      );
    },
  };
}

module.exports = {
  createUserModel,
  createCourseModel,
  createEnrollmentModel,
  createPaymentModel,
  createAuditModel,
  createReportModel,
};
