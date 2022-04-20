@echo off
call C:\Users\%username%\PycharmProjects\schedule_composer_api\venv\Scripts\activate.bat
py C:\Users\%username%\PycharmProjects\schedule_composer_api\manage.py wipedata
deactivate