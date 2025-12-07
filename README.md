# School Library Management System

A comprehensive, Dockerized book management system designed for schools. It features a modern Streamlit UI, a robust FastAPI backend, PostgreSQL database, and automated ETL pipelines orchestrated by Apache Airflow.

## 🚀 Key Features

- **📚 Inventory Management**: Track books, categories, and storage locations.
- **👥 Teacher Management**: Manage borrowers and track their activity.
- **🔄 Automated Pipelines**: 
  - Bulk import books via CSV.
  - (Coming Soon) Auto-sync transactions from Google Sheets.
- **🔍 Smart Search**: Instantly find books by ID (e.g., "A-018") or title.
- **📊 Dashboard**: Real-time visualization of library status (Available, On Loan, Lost).
- **🔐 Secure Access**: JWT-based authentication for administrators.
- **🐳 Fully Containerized**: One-command deployment with Docker Compose.

---

## 🏗 Architecture

The system follows a microservices architecture:

| Service | Technology | Port | Description |
|---------|------------|------|-------------|
| **Frontend** | Streamlit | `8501` | User interface for librarians |
| **Backend** | FastAPI | `8000` | REST API handling logic & auth |
| **Database** | PostgreSQL | `5433` | Primary data storage |
| **ETL** | Python/Pandas | - | Data processing scripts |
| **Orchestrator** | Airflow | `8080` | Schedules and monitors pipelines |

---

## 🛠 Prerequisites

- **Docker Desktop**: Ensure it's installed and running.
- **Git**: For cloning the repository.
- **Python 3.11**: (Optional) For local development without Docker.

---

## ⚡️ Quick Start Guide

### 1. Clone the Repository
```bash
git clone <repository-url>
cd library_system
```

### 2. Configure Environment
Copy the example environment file:
```bash
cp .env.example .env
```
*Note: The default `.env` is pre-configured for local development. For production, update the passwords!*

### 3. Start All Services
Run the following command to build and start the system:
```bash
docker-compose up -d --build
```
*This may take a few minutes the first time as it builds the Docker images.*

### 4. Verify Installation
Check if all containers are running:
```bash
docker-compose ps
```
You should see `library_backend`, `library_frontend`, `library_postgres`, `airflow_webserver`, and `airflow_scheduler` in `Up` or `Healthy` state.

---

## 🖥 Accessing the System

| Application | URL | Default Credentials |
|-------------|-----|---------------------|
| **Library UI** | [http://localhost:8501](http://localhost:8501) | `admin` / `admin123` |
| **API Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) | - |
| **Airflow UI** | [http://localhost:8080](http://localhost:8080) | `admin` / `admin` |

---

## 📦 Data Management

### Importing Books via CSV
To bulk load books into the system:

1. **Prepare your CSV file**:
   Create a file (e.g., `my_books.csv`) with these headers:
   ```csv
   category_name,category_label,book_name,location
   Fiction,A,The Great Gatsby,Shelf A1
   Science,B,A Brief History of Time,Shelf B2
   ```

2. **Place the file**:
   Move your CSV file to the `data/` directory in the project root.
   ```bash
   mv my_books.csv data/books.csv
   ```

3. **Run the Import Pipeline**:
   Trigger the Airflow DAG to process the file:
   ```bash
   docker-compose exec airflow-scheduler airflow dags trigger import_books_csv
   ```
   *Alternatively, go to the Airflow UI (localhost:8080), find `import_books_csv`, and click the "Trigger DAG" button (▶️).*

### Managing Teachers
1. Log in to the **Library UI**.
2. Go to the **Admin** page.
3. Use the **Manage Teachers** tab to add new teachers.

---

## 👩‍💻 Development & Troubleshooting

### Project Structure
```
library_system/
├── backend/          # FastAPI application (Python 3.11)
├── frontend/         # Streamlit user interface
├── database/         # SQL init scripts & migrations
├── etl/             # Data processing scripts & Great Expectations
├── airflow/         # DAGs for orchestration
├── data/            # Shared directory for data files
└── docker-compose.yml
```

### Common Commands

**View Logs**
```bash
docker-compose logs -f backend    # Backend logs
docker-compose logs -f frontend   # Frontend logs
docker-compose logs -f airflow-scheduler # Airflow logs
```

**Restart a Service**
```bash
docker-compose restart frontend
```

**Reset Database** (⚠️ Destructive!)
```bash
docker-compose down -v
docker-compose up -d
```

### Troubleshooting Tips
- **Port Conflicts**: If port `5433` or `8080` is in use, modify `docker-compose.yml` to map to a different host port.
- **Database Connection**: If the backend fails to connect, ensure the `postgres` container is `Healthy`.
- **Airflow DAGs Missing**: It may take a minute for Airflow to parse new DAGs. Check the scheduler logs if they don't appear.

---

## 📜 License
