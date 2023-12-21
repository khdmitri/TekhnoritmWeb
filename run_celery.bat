@ECHO OFF
cd d:\TekhnoritmWeb
venv38\Scripts\activate.bat & celery -A tekhnoritm_web worker -l info -P gevent
