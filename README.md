# Hospital AI (Django) – ICU 180-day Mortality Risk

This is a production-ready *starter* Django project that:
- Manages Patients + Encounters
- Lets nurses enter structured ICU observations (features used by your model)
- Generates a 180-day mortality risk prediction using a saved scikit-learn Pipeline (.joblib)
- Records an audit trail for clinical accountability

## 1) Setup (local)

```bash
python -m venv .venv
source .venv/bin/activate   # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_groups
python manage.py createsuperuser
python manage.py runserver
```

Open:
- App: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

Login with your superuser and create users, then assign them to groups:
- Nurse
- Doctor
- Admin

## 2) Add  trained model

From your notebook you should have:
- XGBoost_mortality_180days.joblib

Copy it to:
`risk/ml_models/XGBoost_mortality_180days.joblib`

Or set an environment variable:
`ML_MODEL_PATH=/absolute/path/to/joblib`

## 3) Notes for real hospital deployment

- Use PostgreSQL (not SQLite)
- Put behind HTTPS (nginx) + gunicorn
- Enable 2FA 
- Configure backups + retention
- Integrate with HIS/LIS for automatic vitals/labs ingestion

## 4) Clinical disclaimer

This tool is for decision support only and must be validated in your local setting.
