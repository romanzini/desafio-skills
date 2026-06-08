const sqlite3 = require('sqlite3').verbose();
const crypto = require('crypto');

let _db = null;

function getDb() {
    if (!_db) {
        _db = new sqlite3.Database(':memory:');
    }
    return _db;
}

// Promise wrappers that preserve lastID context
function run(db, sql, params = []) {
    return new Promise((resolve, reject) => {
        db.run(sql, params, function (err) {
            if (err) reject(err);
            else resolve({ lastID: this.lastID, changes: this.changes });
        });
    });
}

function get(db, sql, params = []) {
    return new Promise((resolve, reject) => {
        db.get(sql, params, (err, row) => {
            if (err) reject(err);
            else resolve(row);
        });
    });
}

function all(db, sql, params = []) {
    return new Promise((resolve, reject) => {
        db.all(sql, params, (err, rows) => {
            if (err) reject(err);
            else resolve(rows || []);
        });
    });
}

// Secure password hashing using built-in crypto (scrypt)
function hashPassword(password) {
    const salt = crypto.randomBytes(16).toString('hex');
    const hash = crypto.scryptSync(password, salt, 64).toString('hex');
    return `${salt}:${hash}`;
}

function checkPassword(password, storedHash) {
    const [salt, hash] = storedHash.split(':');
    if (!salt || !hash) return false;
    const verifyHash = crypto.scryptSync(password, salt, 64).toString('hex');
    return hash === verifyHash;
}

async function initDb() {
    const db = getDb();
    await new Promise((resolve) => {
        db.serialize(async () => {
            await run(db, "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)");
            await run(db, "CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)");
            await run(db, "CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)");
            await run(db, "CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)");
            await run(db, "CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)");

            // Seed data with properly hashed passwords
            await run(db, "INSERT INTO users (name, email, pass) VALUES (?, ?, ?)",
                ['Leonan', 'leonan@fullcycle.com.br', hashPassword('123')]);
            await run(db, "INSERT INTO courses (title, price, active) VALUES (?, ?, ?)",
                ['Clean Architecture', 997.00, 1]);
            await run(db, "INSERT INTO courses (title, price, active) VALUES (?, ?, ?)",
                ['Docker', 497.00, 1]);
            await run(db, "INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", [1, 1]);
            await run(db, "INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)",
                [1, 997.00, 'PAID']);
            resolve();
        });
    });
}

module.exports = { getDb, initDb, run, get, all, hashPassword, checkPassword };
