@ECHO OFF
d:
cd d:\TekhnoritmWeb
venv38\Scripts\activate.bat & daphne -b 0.0.0.0 -p 8000 tekhnoritm_web.asgi:application
