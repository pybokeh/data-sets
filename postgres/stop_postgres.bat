set PGDATA=%USERPROFILE%\apps\PostgreSQL15\data
"%~dp0\bin\pg_ctl" stop -D "%PGDATA%"
pause
