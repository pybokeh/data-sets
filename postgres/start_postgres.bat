@echo off
REM Uncomment/remove REM from the 3rd line below, then run it once and only once.  Then comment it out so that we don't run it again.
REM initdb -U postgres -W -E UTF8 -D %USERPROFILE%\apps\PostgreSQL15\data --auth=trust
set PGDATA=%USERPROFILE%\apps\PostgreSQL15\data
set PGPORT=5432
"%~dp0\bin\pg_ctl" -D "%PGDATA%" -o "-p %PGPORT%" -l logfile start
pause
