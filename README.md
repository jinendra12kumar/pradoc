<div align="center">
  
# 🩺 PraDoc — Modern Healthcare Platform

**A FullStack healthcare management platform inspired by systems like Practo, Zocdoc,DocPlanner, Apollo24/7 and HaloDoc, designed to streamline interactions between patients, healthcare providers, and administrators.**

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![RabbitMQ](https://img.shields.io/badge/Rabbitmq-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white)](https://www.rabbitmq.com/)
[![Jitsi](https://img.shields.io/badge/Jitsi-1D76BA?style=for-the-badge&logo=jitsi&logoColor=white)](https://jitsi.org/)

</div>

---

## 📖 Project Goal

The goal of this project is to build a scalable, highly robust healthcare platform that enables patients to discover doctors, schedule appointments, manage medical records, receive digital prescriptions, participate in remote video consultations, and access healthcare services through a modern, secure, and user-friendly interface.

---

## ✨ Features

### 🔐 Authentication & User Management
* **JWT-based authentication** with secure role-based access control (RBAC).
* **Patient Registration** with email/OTP verification.
* **Doctor Onboarding** with multi-step profile creation and document uploads.
* **Admin Access** for platform-wide management.

### 🔍 Doctor Discovery
* **Advanced Search:** Find doctors by specialization, availability, and name.
* **Rich Filters:** Filter by years of experience, consultation fee, and clinic location.
* **Detailed Profiles:** View doctor qualifications, verified badges, clinic details, and patient reviews.

### 📅 Appointment Management
* **Real-time Booking:** Slot-based scheduling with concurrency handling.
* **Status Tracking:** Lifecycle management (Pending → Confirmed → Completed / Cancelled / No-Show).
* **Flexible Modes:** Support for both **In-Clinic** and **Online (Video)** consultations.

### 🎥 Telemedicine & Video Consultation
* **Embedded Jitsi Meet:** In-app video calls using the Jitsi External API (no redirect).
* **Virtual Waiting Rooms:** Patients wait securely until the doctor initiates the session.
* **Automated Status:** Meetings automatically mark appointments as completed upon ending.

### 🛡️ Comprehensive Admin Panel
* **Stats Dashboard:** Live metrics on revenue, total users, and appointment breakdowns.
* **Doctor Verification:** Review submitted credentials and approve/reject doctor profiles.
* **User Management:** Enable or disable patient and doctor accounts.
* **Moderation:** Review and manage patient feedback/ratings.
* **Health Articles:** Built-in CMS to publish and manage health related blog articles.

### 🧑‍⚕️ Doctor Dashboard
* **Schedule Management:** View today's queue and upcoming appointments.
* **Prescription Generation:** Create, manage, and download digital prescriptions for patients.
* **Patient History:** Access a patient's past consultations and medical records securely.

### 👤 Patient Dashboard
* **Appointment Tracking:** Manage upcoming and past appointments.
* **Medical Records:** Securely upload, store, and view lab reports and health documents.
* **Prescription History:** Access medicine dosages, durations, and downloadable PDFs.
* **Ratings & Reviews:** Leave feedback for doctors post-consultation.

### 🔔 Notifications System (Event-Driven)
* **Real-time Alerts:** Appointment reminders, booking confirmations, and prescription updates.
* **Robust Architecture:** Powered by RabbitMQ for asynchronous event handling and email dispatch.

---

## 🛠️ Tech Stack

### Backend
* **Framework:** FastAPI (Python)
* **Database:** PostgreSQL (with SQLAlchemy ORM & Alembic for migrations)
* **Caching & Locks:** Redis
* **Message Broker:** RabbitMQ
* **Security:** JWT Authentication, Passlib (Bcrypt)

### Frontend
* **Library:** React.js (Vite)
* **State Management:** React Query (Server state), Zustand / Context API (Client state)
* **Styling:** Custom Modern CSS & Tailwind CSS (Responsive, dark/light themes)
* **HTTP Client:** Axios / Native Fetch
* **Video SDK:** Jitsi Meet External API

### Infrastructure & Architecture
* **RESTful APIs** adhering to strict OpenAPI schemas.
* **Repository-Service Pattern** for clean backend logic separation.
* **Event-Driven Architecture** for decoupling notifications and heavy tasks.
* **Dockerized Deployment** for consistent cross-environment builds.

---

## 📂 Project Structure

```text
pradoc/
├── backend/
│   ├── app/           # FastAPI application & API routers (v1)
│   ├── core/          # Configuration, Security, Database setup
│   ├── dependencies/  # Auth guards, DB sessions
│   ├── models/        # SQLAlchemy Database Models
│   ├── repositories/  # Data access layer
│   ├── services/      # Business logic (Appointments, Video, Admin, etc.)
│   └── main.py        # Application entry point
├── frontend/
│   ├── public/        # Static assets
│   ├── src/
│   │   ├── api/       # API integration functions
│   │   ├── components/# Reusable UI components
│   │   ├── context/   # Global React context (Auth)
│   │   ├── pages/     # Page-level components (Admin, Doctor, Patient, Auth)
│   │   └── App.jsx    # Application routing (React Router)
└── docs/              # System documentation & implementation plans
```

---

<div align="center">
  <i>Built with ❤️ for modern healthcare.</i>
</div>
