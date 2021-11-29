@ECHO OFF
d:
cd d:\TekhnoritmWeb
venv\Scripts\activate.bat & celery -A tekhnoritm_web beat -l info

