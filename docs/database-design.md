# Database Design & Schemas

VisiGuard AI utilizes MongoDB to manage user accounts, forensic scan trails, and security audit records.

---

## Entity-Relationship (ER) Overview

```text
  +------------------+             +------------------+
  |      User        |             |     Scan         |
  +------------------+             +------------------+
  | _id (ObjectId)   | <---------+ | _id (ObjectId)   |
  | email (String)   |             | userId (Ref)     |
  | password (String)|             | originalName     |
  | role (String)    |             | originalPath     |
  +------------------+             | elaPath          |
          |                        | fileSize         |
          |                        | threatScore      |
          v                        | status           |
  +------------------+             +------------------+
  |    AuditLog      |
  +------------------+
  | _id (ObjectId)   |
  | userId (Ref)     |
  | action (String)  |
  | details (String) |
  | ipAddress        |
  +------------------+
```

---

## Schema Reference

### 1. Users Collection
* Stores account login and access permissions.
* **Fields**:
  * `_id`: ObjectId (Unique identifier)
  * `email`: String (Unique, lowercase, validated email index)
  * `password`: String (Bcrypt salt-hashed payload)
  * `role`: Enum ['User', 'Admin', 'Security_Auditor']
  * `createdAt`: Date

### 2. Scans Collection
* Stores forensic evaluation outputs.
* **Fields**:
  * `_id`: ObjectId
  * `userId`: ObjectId (Ref: User, optional)
  * `originalName`: String
  * `originalPath`: String
  * `elaPath`: String
  * `fileSize`: Number
  * `threatScore`: Number
  * `status`: Enum ['Clean', 'Suspicious', 'Tampered']
  * `createdAt`: Date

### 3. AuditLogs Collection
* Persistent event logs for security auditing.
* **Fields**:
  * `_id`: ObjectId
  * `userId`: ObjectId (Ref: User, optional)
  * `action`: String
  * `details`: String
  * `ipAddress`: String
  * `userAgent`: String
  * `createdAt`: Date

---

## Indexing Recommendations
To optimize database performance as scan history grows, establish the following indexes:
* **Users**:
  * `db.users.createIndex({ "email": 1 }, { unique: true })`
* **Scans**:
  * `db.scans.createIndex({ "userId": 1, "createdAt": -1 })`
* **AuditLogs**:
  * `db.auditlogs.createIndex({ "createdAt": -1 })`

---

## Scaling & Sharding Strategy
For enterprise deployments with millions of scans monthly:
* **Sharding Key**: Shard the `Scans` and `AuditLogs` collection on `{ "userId": "hashed", "createdAt": 1 }`. This groups user data across server clusters while maintaining temporal query performance.
* **TTL Indexes**: Set Time-To-Live (TTL) indexes on `AuditLogs` to automatically purge records older than 90 days if compliance regulations permit.
