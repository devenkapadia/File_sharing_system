# File Sharing System

## Overview
The File Sharing System is a Django-based web application that allows users to transfer ownership to other users, revoke ownership, and track transfer history. Built with Django REST Framework, it provides a secure API with authentication to manage file operations. The system includes an admin interface for managing users and files and supports auditing through transfer history.

### Features
- **File Management**: Upload and manage files via the Django admin interface.
- **Ownership Transfer**: Transfer file ownership to another user via API.
- **Ownership Revocation**: Original owners can revoke transferred files.
- **Transfer History**: Track all transfer and revocation actions.
- **Authentication**: Uses Django’s authentication with Basic Auth for API access.
- **Authorization**: Restricts actions to file owners or staff users.

## Setup Instructions

### Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/devenkapadia/File_sharing_system
   cd file_sharing_system
   ```

2. **Set Up Virtual Environment** (optional):
   ```bash
   python -m venv sharing
   source sharing/Scripts/activate  # Windows
   # source sharing/bin/activate  # Linux/Mac
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   Ensure `requirements.txt` includes:
   ```
   django==4.2
   djangorestframework==3.14
   ```

4. **Apply Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a Superuser**:
   ```bash
   python manage.py createsuperuser
   ```
   Example: Username `admin`, Password `password123`.

6. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```
   Access the app at `http://localhost:8000`.

## API Endpoints
All endpoints require authentication via Basic Auth (username and password).

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/api/files/` | GET | List all files (staff) or owned files (user). Optional `file_id` query param for specific file. | None | List of files or single file JSON |
| `/api/transfer/` | POST | Transfer file ownership to another user. | `{"file_id": int, "to_user_id": int}` | Success message and file details |
| `/api/revoke/` | GET | List files the user can revoke. | None | List of revocable files |
| `/api/revoke/` | POST | Revoke file ownership back to original owner. | `{"file_id": int}` | Success message and file details |
| `/api/transfer/history/` | GET | View transfer history for a file (`file_id` query param) or user’s files. | None | List of transfer history records |

## Usage

### Admin Interface
1. Access `http://localhost:8000/admin/` with superuser credentials (e.g., `admin`/`password123`).
2. Manage users under **Auth** > **Users**.
3. Manage files under **Transfer App** > **Files** (upload files, assign owners).
4. View transfer history under **Transfer App** > **Transfer Histories**.

### Postman Testing
1. Install Postman from [postman.com](https://www.postman.com/downloads/).
2. Create a collection (e.g., `File Sharing System`).
3. Add requests for each endpoint with:
   - **Authorization**: Basic Auth (e.g., `user_a`/`password123`).
   - **Headers**: `Content-Type: application/json` for POST requests.
4. Test endpoints and capture screenshots.

## Screenshots
### Users
![Users](docs/db_state/users.png) List of 4 users in admin interface.

### Files
![Files](docs/db_state/files.png) List of 3 files in admin interface.

### GET /api/files/
![GET /api/files/](docs/APIs/all_files1.png) List files via API of user 1.

### GET /api/files/?file_id=1
![GET /api/files/?file_id=1](docs/APIs/file_id.png) Get file based on ID.

### POST /api/transfer/
![POST /api/transfer/](docs/APIs/file_transfer.png) Transfer file ownership.

### GET /api/files/ (After ownership transfer)
![GET /api/files/](docs/APIs/all_files2.png) List files via API of user 2 (After ownership transfer).

### GET /api/transfer/history/
![GET /api/transfer/history/](docs/APIs/get_history.png) View transfer history with timestamp.

### GET /api/revoke/
![GET /api/revoke/](docs/APIs/get_revoke.png) List revocable files.

### POST /api/revoke/
![POST /api/revoke/](docs/APIs/post_revoke.png) Revoke file ownership.

### Transfer History
![Transfer History](docs/db_state/tranfer_history.png) Transfer and revoke records in the DB.

## Security
### Authentication
![Authentication](docs/security/auth.png) All the user APIs are secured, Basic Auth is needed for every operation by the user. User can only see his own files, transfer history etc.

### Forbidden Access
![Forbidden](docs/security/forbidden.png) One user is forbidden to see other user's files.

### Bad Request
![Bad Request](docs/security/bad_request.png) User cannot revoke ownership of the file which is not transferred or already revoked.
