WearUp Backend — PythonAnywhere deployment notes

This file contains quick, practical steps to deploy the Django backend to PythonAnywhere.

1) Create a virtualenv

# Use the Python version you want (e.g., 3.11)
python -m venv ~/venvs/wearup-backend
source ~/venvs/wearup-backend/bin/activate  # on PythonAnywhere's bash

2) Upload or clone your project into your home directory on PythonAnywhere

3) Install requirements

pip install -r /home/yourusername/path/to/Backend/requirements.txt

4) Environment variables

Set the following environment variables in the "Web" -> "Environment variables" section on PythonAnywhere, or export them in a .env when testing locally (use python-dotenv locally):

- DJANGO_SECRET_KEY (required)
- DJANGO_DEBUG (set to 0 in production)
- DJANGO_ALLOWED_HOSTS (comma-separated list, e.g., yourusername.pythonanywhere.com)
- DB_NAME
- DB_USER
- DB_PASSWORD
- DB_HOST
- DB_PORT

Example DB config (PythonAnywhere MySQL):
DB_NAME: yourusername$wearup
DB_USER: yourusername
DB_PASSWORD: <your password>
DB_HOST: <leave blank or set to 127.0.0.1 if using PA's MySQL>
DB_PORT: 3306

Note: The project currently defaults to MySQL (using pymysql). If you prefer SQLite for a simple deployment, change DATABASES in settings.py accordingly.

5) Static files

- Ensure STATIC_ROOT is set (the project uses STATIC_ROOT = BASE_DIR / 'staticfiles').
- Run collectstatic:

python manage.py collectstatic --noinput

- Configure the "Static files" section in the PythonAnywhere web dashboard to map the URL /static/ to the STATIC_ROOT path.
- For media files, either serve via PythonAnywhere's static mapping or use external storage (S3) in production.

6) WSGI configuration

- In the PythonAnywhere Web tab, point the WSGI file to your project's WSGI application.
- By default, PAWS uses the project's WSGI entry; adjust the path to the project if necessary.

7) Database migrations

python manage.py migrate

8) Admin user

python manage.py createsuperuser

9) Debug & logs

- Set DJANGO_DEBUG=0 for production.
- Check the error log and access log in the PythonAnywhere web dashboard if anything fails.

10) Notes & troubleshooting

- If you use `mysqlclient` instead of `pymysql`, that package requires system-level libraries. On PythonAnywhere, install the recommended package or use pymysql to avoid native build requirements.
- If you store secrets in a .env file locally, add it to .gitignore and use python-dotenv in development only. On PythonAnywhere, prefer the Web->Environment variables configuration.

If you want, I can update `settings.py` to use environment variables (DJANGO_SECRET_KEY, DJANGO_DEBUG, and DB_*), and add a tiny `.env.example` file. Would you like me to do that? (I can proceed now.)

Quick setup scripts
-------------------
I added helper scripts in this folder to make local setup and PythonAnywhere deployment easier.

PowerShell (Windows) - `setup_venv.ps1`:

1. Open PowerShell in the `Backend` folder and run:

	./setup_venv.ps1

2. The script will create a virtualenv in `venv` (inside `Backend`), activate it, and install requirements.

Bash (PythonAnywhere) - `setup_venv.sh`:

1. Upload the project to PythonAnywhere and open a Bash console there.
2. Run:

	bash setup_venv.sh

3. The script will create a virtualenv under `~/.virtualenvs/wearup-backend` (adjustable), activate it, and install requirements.

Files created for convenience:

- `.env.example` — shows environment variables you should set
- `.gitignore` — local ignore for `.env`, `venv/`, etc.
- `setup_venv.ps1` — PowerShell helper to create venv and install
- `setup_venv.sh` — Bash helper for PythonAnywhere

Follow the README steps above after running the scripts: set environment variables in PythonAnywhere Web UI, run migrations and collectstatic, and configure static/media paths in the Web tab.
