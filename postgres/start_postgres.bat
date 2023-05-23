REM You want to remove "REM" in the line containing the initdb command.  Run this .bat file once.  Then add REM back, then run the .bat file again.
@ECHO ON
@SET PATH="%~dp0\bin";%PATH%
@SET PGDATA=%~dp0\data
@SET PGDATABASE=postgres
@SET PGUSER=postgres
@SET PGPORT=5432
@SET PGLOCALEDIR=%~dp0\share\locale
REM initdb -U postgres -W -E UTF8 -D "%PGDATA%" --auth=trust
"%~dp0\bin\pg_ctl" -D "%PGDATA%" -o "-p %PGPORT%" -l logfile start
pause
