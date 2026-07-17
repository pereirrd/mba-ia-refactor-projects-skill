const crypto = require("crypto");
const sqlite3 = require("sqlite3").verbose();
const { settings } = require("../config/settings");

function hashPassword(password) {
  const salt = crypto.randomBytes(16).toString("hex");
  const derived = crypto.scryptSync(String(password), salt, 64).toString("hex");
  return `${salt}:${derived}`;
}

function verifyPassword(password, stored) {
  if (!stored || !stored.includes(":")) {
    return stored === password;
  }
  const [salt, hash] = stored.split(":");
  const derived = crypto.scryptSync(String(password), salt, 64).toString("hex");
  const hashBuf = Buffer.from(hash, "hex");
  const derivedBuf = Buffer.from(derived, "hex");
  if (hashBuf.length !== derivedBuf.length) {
    return false;
  }
  return crypto.timingSafeEqual(hashBuf, derivedBuf);
}

function createDatabase() {
  const db = new sqlite3.Database(settings.databasePath);

  function run(sql, params = []) {
    return new Promise((resolve, reject) => {
      db.run(sql, params, function onRun(err) {
        if (err) {
          reject(err);
          return;
        }
        resolve({ lastID: this.lastID, changes: this.changes });
      });
    });
  }

  function get(sql, params = []) {
    return new Promise((resolve, reject) => {
      db.get(sql, params, (err, row) => {
        if (err) {
          reject(err);
          return;
        }
        resolve(row);
      });
    });
  }

  function all(sql, params = []) {
    return new Promise((resolve, reject) => {
      db.all(sql, params, (err, rows) => {
        if (err) {
          reject(err);
          return;
        }
        resolve(rows);
      });
    });
  }

  async function init() {
    await run("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, pass TEXT)");
    await run("CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)");
    await run("CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)");
    await run("CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)");
    await run("CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)");

    const userCount = await get("SELECT COUNT(*) AS total FROM users");
    if (userCount.total === 0) {
      await run("INSERT INTO users (name, email, pass) VALUES (?, ?, ?)", [
        "Leonan",
        "leonan@fullcycle.com.br",
        hashPassword("123"),
      ]);
      await run("INSERT INTO courses (title, price, active) VALUES (?, ?, ?)", [
        "Clean Architecture",
        997.0,
        1,
      ]);
      await run("INSERT INTO courses (title, price, active) VALUES (?, ?, ?)", [
        "Docker",
        497.0,
        1,
      ]);
      await run("INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", [1, 1]);
      await run(
        "INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)",
        [1, 997.0, "PAID"]
      );
    }
  }

  return { db, run, get, all, init };
}

module.exports = { createDatabase, hashPassword, verifyPassword };
