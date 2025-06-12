@echo off
setlocal enabledelayedexpansion

:: Initialize variables
set "configFile=case_config.txt"
set "backupLocation="

:: Check for config file and load backup location
if exist "%configFile%" (
    for /f "usebackq delims=" %%A in ("%configFile%") do (
        set "backupLocation=%%A"
    )
)

:: Verify backup location is accessible
if defined backupLocation (
    echo Verifying backup location: %backupLocation%
    if not exist "%backupLocation%\" (
        echo Backup location not accessible.
        set "backupLocation="
    )
)

:: If no valid backup location, prompt user to select one
if not defined backupLocation (
    echo No valid backup location configured.
    call :select_backup_location
    if not defined backupLocation (
        echo No backup location selected. Some functions may not work.
        pause
    )
)

:MENU
cls
echo ========================================
echo           CASE MANAGEMENT MENU
echo ========================================
echo [1] Create a new case
echo [2] Archive an existing case
echo [3] Change backup location
echo [0] Exit
echo ========================================
echo Current backup location: %backupLocation%
echo ========================================
set /p choice="Enter your choice: "

if "%choice%"=="1" goto CREATE_CASE
if "%choice%"=="2" goto ARCHIVE_CASE
if "%choice%"=="3" goto CHANGE_BACKUP
if "%choice%"=="0" exit
goto MENU

:CREATE_CASE
cls
set /p caseName="Enter the case name: "
mkdir "%caseName%"
mkdir "%caseName%\01 - Evidence"
mkdir "%caseName%\02 - Case"
mkdir "%caseName%\03 - Malware"
mkdir "%caseName%\03 - Extracted Evidence"
type nul > "%caseName%\Keywords.txt"
echo Case folders created successfully!
pause
start explorer "%cd%\%caseName%"
goto MENU

:ARCHIVE_CASE
cls
if not defined backupLocation (
    echo Backup location not configured.
    call :select_backup_location
    if not defined backupLocation (
        echo Cannot proceed without backup location.
        pause
        goto MENU
    )
)

echo Listing all folders in the current directory...
setlocal
set index=0
for /d %%D in (*) do (
    set /a index+=1
    set "folder[!index!]=%%D"
    echo [!index!] %%D
)

if "!index!"=="0" (
    echo No folders found.
    pause
    goto MENU
)

set /p selected="Enter the number of the folder to archive: "
set "targetFolder=!folder[%selected%]!"

if not defined targetFolder (
    echo Invalid selection.
    pause
    goto MENU
)

echo Launching save dialog for archive destination...
set "zipTempFile=__zip_dest.tmp"
powershell -Command "$SaveDialog = New-Object -ComObject Shell.Application; $File = $SaveDialog.BrowseForFolder(0, 'Select backup location for the ZIP file:', 0, '%backupLocation%'); if ($File) { [IO.File]::WriteAllText('%zipTempFile%', $File.Self.Path) }"

if not exist "%zipTempFile%" (
    echo Operation cancelled or no folder selected.
    pause
    goto MENU
)

set /p zipFolder=<%zipTempFile%
del %zipTempFile%

set "zipPath=%zipFolder%\%targetFolder%.zip"
echo Archiving folder: !targetFolder!
echo Destination: !zipPath!

powershell -Command "Compress-Archive -Path '!targetFolder!\' -DestinationPath '!zipPath!'"

if exist "!zipPath!" (
    echo Archive created successfully: !zipPath!
    echo Deleting original folder...
    rmdir /s /q "!targetFolder!"
    echo Done.
) else (
    echo Failed to create archive.
)

pause
goto MENU

:CHANGE_BACKUP
call :select_backup_location
if defined backupLocation (
    echo New backup location set: %backupLocation%
    pause
)
goto MENU

:select_backup_location
cls
echo Please select the backup location...
set "tempFile=__backup_location.tmp"
powershell -Command "$Folder = (New-Object -ComObject Shell.Application).BrowseForFolder(0, 'Select Case Backup Location', 0, '').Self.Path; if ($Folder) { [IO.File]::WriteAllText('%tempFile%', $Folder) }"

if exist "%tempFile%" (
    set /p "backupLocation=" < "%tempFile%"
    del "%tempFile%"
    
    if not exist "%backupLocation%\" (
        echo Invalid location selected.
        set "backupLocation="
        pause
        goto :eof
    )
    
    echo %backupLocation% > "%configFile%"
    echo Backup location saved to config file.
) else (
    echo No location selected.
)
goto :eof