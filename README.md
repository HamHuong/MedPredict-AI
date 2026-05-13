# MedPredict AI — Hệ thống Dự đoán Tái nhập viện

> Hệ thống dự đoán nguy cơ tái nhập viện 30 ngày sử dụng dữ liệu MIMIC-IV Demo và Machine Learning.

## 🏗️ Kiến trúc Hệ thống

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Frontend      │────▶│   Backend API    │────▶│   ML Service     │
│   React + Vite  │     │   FastAPI :8000   │     │   FastAPI :8001  │
│   :5173         │     │                  │     │                  │
└─────────────────┘     └────────┬─────────┘     └────────┬─────────┘
                                 │                         │
                        ┌────────▼─────────┐     ┌────────▼─────────┐
                        │   PostgreSQL     │     │   MLflow         │
                        │   :5432          │     │   :5000          │
                        └──────────────────┘     └──────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed and running
- Git

### 1. Clone và cấu hình

```bash
cp .env.example .env
```

### 2. Chạy với Docker Compose

```bash
docker-compose up --build
```

### 3. Import dữ liệu MIMIC-IV

```bash
# Sau khi database đã khởi tạo xong
docker-compose exec backend python -c "
import sys; sys.path.insert(0, '/app')
exec(open('/data/import_mimic.py').read())
"
# Hoặc chạy trực tiếp trên máy local:
cd database
python import_mimic.py
```

### 4. Truy cập hệ thống

| Service | URL | Mô tả |
|---------|-----|--------|
| Frontend | http://localhost:5173 | Giao diện React |
| Backend API | http://localhost:8000/api/docs | Swagger API docs |
| MLflow | http://localhost:5000 | ML Experiment Tracking |
| PostgreSQL | localhost:5432 | Database |

### 5. Đăng nhập

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Admin |
| doctor | doctor123 | Doctor |

## 📁 Cấu trúc Project

```
CK_CNM/
├── backend/           # FastAPI Backend API
├── ml_service/        # ML Inference & Training Service
├── frontend/          # React + Vite Frontend
├── database/          # SQL schemas & import scripts
├── docker-compose.yml # Container orchestration
├── .env.example       # Environment template
└── README.md
```

## 🔧 Tính năng

- **Dashboard**: Tổng quan bệnh nhân, dự đoán, metrics
- **Quản lý Bệnh nhân**: Xem danh sách, chi tiết bệnh nhân, lịch sử nhập viện
- **Dự đoán AI**: Dự đoán nguy cơ tái nhập viện 30 ngày với SHAP explanation
- **Admin Panel**: Quản lý users, ML models, retraining, monitoring
- **MLOps**: MLflow tracking, model versioning, automated retraining

## 🛠️ Tech Stack

- **Frontend**: React 18, Vite, Recharts, React Router
- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **ML**: scikit-learn, XGBoost, SHAP, MLflow
- **Database**: PostgreSQL 15
- **Containerization**: Docker, Docker Compose
