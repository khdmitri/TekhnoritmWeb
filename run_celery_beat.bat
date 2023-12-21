@ECHO OFF
d:
cd d:\TekhnoritmWeb
venv38\Scripts\activate.bat & celery -A tekhnoritm_web beat -l info

