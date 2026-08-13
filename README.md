# Smart Hostel Laundry Slot Booking System

A complete Flask + SQLite web application for hostel students to reserve washing-machine slots and for administrators to manage machines and bookings.

## Project overview

The application replaces manual laundry-room queues with a persistent slot-booking system. Students can register, sign in, see machine availability, select a date and predefined time slot, book a machine, review bookings, and cancel eligible upcoming bookings. Administrators have a protected dashboard for machine management, availability control, booking search/filtering, and basic statistics.

## Features

- Student registration, login and logout
- Session-based authentication with role-based authorization
- Werkzeug password hashing; plain-text passwords are never stored
- Student dashboard with today's date, machine availability and bookings
- Laundry date picker and fixed time slots
- Machine/slot availability indication
- Booking confirmation and persistent SQLite storage
- Personal booking history and cancellation
- Admin dashboard with machine and booking statistics
- Admin add/edit/delete machine actions
- Admin enable/disable machine status
- Admin booking search and status filtering
- Server-side and client-side validation
- Database unique constraint on `machine_id + booking_date + slot`
- Maximum two confirmed bookings per student per day
- Prevents past dates and already-started cancellations
- Prevents inactive-machine bookings
- Ownership checks for student cancellation
- Responsive, mobile-friendly UI
- `data-testid` attributes on important controls
- Render/Gunicorn deployment configuration
- Safe repeatable seed script

## Technology stack

- Python 3.11+
- Flask
- SQLite
- Flask-SQLAlchemy / SQLAlchemy
- HTML, CSS, Vanilla JavaScript
- Jinja templates
- Werkzeug password hashing
- python-dotenv
- Gunicorn for Render deployment

No React, Node.js, npm, Docker, MongoDB, PostgreSQL, or external APIs are required.

## Project structure

```text
smart-hostel-laundry/
├── app.py
├── models.py
├── config.py
├── seed.py
├── requirements.txt
├── .env.example
├── .gitignore
├── Procfile
├── render.yaml
├── README.md
├── services/
│   └── booking_service.py
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── booking.html
│   ├── admin.html
│   └── error.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        ├── app.js
        ├── student.js
        ├── booking.js
        └── admin.js
```

## Installation — Windows + VS Code

### 1. Open the project in VS Code

1. Extract `smart-hostel-laundry.zip`.
2. Open VS Code.
3. Select **File → Open Folder**.
4. Select the extracted `smart-hostel-laundry` folder.

### 2. Open the integrated terminal

In VS Code select **Terminal → New Terminal**.

### 3. Create a virtual environment

```powershell
python -m venv .venv
```

### 4. Activate the virtual environment

PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell execution policy blocks activation, use Command Prompt in the VS Code terminal:

```cmd
.venv\Scripts\activate
```

### 5. Install dependencies

```powershell
pip install -r requirements.txt
```

### 6. Configure environment variables

Copy `.env.example` to `.env` and replace the development secret with your own long random value.

For local development, the application defaults to SQLite, so `DATABASE_URL` may be omitted. Do not commit `.env`.

### 7. Seed the database

With the environment activated:

```powershell
python seed.py
```

Or without activating the environment:

```powershell
.venv\Scripts\python.exe seed.py
```

The seed script is safe to run repeatedly and does not duplicate the demo accounts or machines.

### 8. Start the application

With the environment activated:

```powershell
python app.py
```

Or without activation:

```powershell
.venv\Scripts\python.exe app.py
```

### 9. Open the application

Open:

```text
http://127.0.0.1:5000
```

## Demo credentials

### Student

```text
Email: student@example.com
Password: Student@123
```

### Admin

```text
Email: admin@example.com
Password: Admin@123
```

## Fixed laundry slots

- 06:00 AM - 07:00 AM
- 07:00 AM - 08:00 AM
- 08:00 AM - 09:00 AM
- 05:00 PM - 06:00 PM
- 06:00 PM - 07:00 PM
- 07:00 PM - 08:00 PM
- 08:00 PM - 09:00 PM
- 09:00 PM - 10:00 PM

The seed creates four machines. Washing Machine 3 starts inactive.

## Business rules

1. Only authenticated students can create or cancel student bookings.
2. Admin endpoints require the admin role.
3. Students cannot access admin pages or admin APIs.
4. Students can cancel only their own bookings.
5. A machine must be active to be booked.
6. Booking dates cannot be in the past.
7. A same-day slot cannot be booked after its start time.
8. A student can have at most two confirmed bookings on one date.
9. A student cannot hold two confirmed bookings for the same time slot.
10. A confirmed machine/date/slot combination is protected by a database-level unique index (SQLite partial unique index), allowing a cancelled booking to release the slot while retaining cancellation history.
11. Cancelled bookings release the machine/date/slot because the uniqueness rule is applied to the booking row while booking logic checks only confirmed rows.
12. Cancellation is rejected once the booking start time has passed.
13. Booking rules are enforced by the backend and cannot be bypassed by editing browser JavaScript.
14. Passwords are stored only as Werkzeug-generated password hashes.

## API overview

All JSON endpoints return a `success` field and a clear `message` where appropriate.

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| POST | `/api/register` | Public | Register a student |
| POST | `/api/login` | Public | Authenticate a user |
| POST | `/api/logout` | Authenticated | End the session |
| GET | `/api/me` | Authenticated | Current user |
| GET | `/api/machines` | Authenticated | List machines |
| GET | `/api/slots` | Authenticated | List fixed slots |
| POST | `/api/bookings` | Student | Create booking |
| GET | `/api/bookings` | Student | List own bookings |
| DELETE | `/api/bookings/<id>` | Student | Cancel own booking |
| GET | `/api/admin/bookings` | Admin | Search/filter all bookings |
| POST | `/api/admin/machines` | Admin | Add machine |
| PUT | `/api/admin/machines/<id>` | Admin | Edit machine |
| DELETE | `/api/admin/machines/<id>` | Admin | Delete machine |
| PATCH | `/api/admin/machines/<id>/status` | Admin | Enable/disable machine |

## Database setup

The application creates the required tables automatically with `db.create_all()` when it starts. `seed.py` creates the demo accounts and initial machines. Local SQLite data is stored in `hostel_laundry.db` and is ignored by Git.

## GitHub instructions

From the project directory:

```powershell
git init
git add .
git commit -m "Initial Smart Hostel Laundry project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/smart-hostel-laundry.git
git push -u origin main
```

Replace the remote URL with your own GitHub repository. Do not commit `.env` or the SQLite database.

## Render deployment

This repository includes `Procfile` and `render.yaml`.

### Option 1: Blueprint deployment

1. Push the project to GitHub.
2. In Render, create a new Blueprint and select the repository.
3. Render reads `render.yaml`.
4. The build command installs `requirements.txt`.
5. Gunicorn starts the Flask application with `gunicorn app:app`.
6. `SECRET_KEY` is generated by Render from the configuration.

### Important SQLite note

SQLite is persistent only within the lifetime/storage characteristics of the deployed filesystem. For a production multi-instance or durable database deployment, use a managed database and set `DATABASE_URL` to that database. This project itself does not require PostgreSQL locally and does not include PostgreSQL-specific code.

## Security notes

- Passwords are hashed using Werkzeug.
- Production secrets are supplied through environment variables.
- `.env` is ignored by Git.
- Sessions use HTTPOnly and SameSite cookies.
- Admin routes enforce the admin role on the server.
- Student booking operations enforce ownership on the server.
- Database uniqueness prevents concurrent duplicate confirmed machine/date/slot bookings while cancelled history can remain stored.
- Sensitive exception details are not returned to users.

## Troubleshooting

### `python` is not recognized

Install Python 3.11+ and enable **Add Python to PATH**, then reopen VS Code.

### PowerShell will not activate `.venv`

Use Command Prompt in VS Code:

```cmd
.venv\Scripts\activate
```

You can also run every command without activation:

```cmd
.venv\Scripts\python.exe seed.py
.venv\Scripts\python.exe app.py
```

### `ModuleNotFoundError`

Make sure dependencies are installed into the same interpreter used to start Flask:

```cmd
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Port 5000 is already in use

Stop the other Flask process, or run the app from Python with a different port by modifying the local `app.run()` port. Do not expose debug mode in production.

### Demo login does not work

Run:

```cmd
.venv\Scripts\python.exe seed.py
```

Then restart the application.

### Database looks empty after deleting it

Run the seed command again. The database and tables are recreated automatically.

### Changes do not appear

Refresh the browser and restart Flask after Python-side changes.

## Running application summary

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python seed.py
python app.py
```

Then visit `http://127.0.0.1:5000`.
