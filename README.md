<div align="center">
  
# 🩺 PraDoc 
### Modern Full-Stack Healthcare Management Platform

> A scalable healthcare platform inspired by **Practo**, **Zocdoc**, **DocPlanner**, **Apollo 24|7**, and **Halodoc** that enables doctor discovery, appointment scheduling, secure video consultations, digital prescriptions, and patient health record management.

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![RabbitMQ](https://img.shields.io/badge/Rabbitmq-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white)](https://www.rabbitmq.com/)
[![Jitsi](https://img.shields.io/badge/Jitsi-1D76BA?style=for-the-badge&logo=jitsi&logoColor=white)](https://jitsi.org/)

</div>

---

## 📖 Overview

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

| Layer | Technology |
|--------|------------|
| Frontend | React + Vite |
| Backend | FastAPI |
| Database | PostgreSQL |
| Cache | Redis |
| Queue | RabbitMQ |
| ORM | SQLAlchemy |
| Authentication | JWT |
| Video | Jitsi Meet |
| API Documentation | OpenAPI / Swagger |
| Deployment | Docker |
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

## 💡 Why PraDoc?

PraDoc is designed as a modern telemedicine platform that demonstrates scalable software architecture using contemporary backend technologies.

The project focuses on:

- Clean Architecture
- Repository-Service Pattern
- Event-Driven Communication
- Secure Authentication
- High Performance APIs
- Scalable Healthcare Workflows

---

## Project Status
| Module | Status |
|---------|--------|
| Authentication | ✅ |
| Doctor Onboarding | ✅ |
| Patient Dashboard | ✅ |
| Appointment Booking | ✅ |
| Video Consultation | ✅ |
| Notifications | ✅ |
| Payments | 📅 Planned |
| AI Assistant | 📅 Planned |


## 📚 API Documentation

OpenAPI documentation:

http://localhost:8000/docs

ReDoc:

http://localhost:8000/redoc

## ⭐ Support

If you found this project helpful, consider giving it a ⭐ on GitHub.

Contributions, suggestions, and feedback are always welcome.
<!-- 
Built with ❤️ by Jinendra Kumar -->
