@echo off

:: Checking if there is at least 9 arguments
if "%~9"=="" (
    echo "No 9th argument"
    goto :EOF
)

:: Get the directory of the batch file
set "targetPath=%~dp0"

:: Remove trailing backslash if it exists
if "%targetPath:~-1%"=="\" set "targetPath=%targetPath:~0,-1%"

:: Get the parent directory
for %%I in ("%targetPath%") do set "parentPath=%%~dpI"

:: Remove trailing backslash if it exists
if "%parentPath:~-1%"=="\" set "parentPath=%parentPath:~0,-1%"

:: Set the output file
set "outputStatistics=statistics.txt"

(
    echo Number of drivers in the championship:   %1
    echo Number of engine manufacturers:          %2
    echo Number of images:                        %3
    echo Number of identified images:             %4
    echo Number of unidentified images:           %5
    echo Size of all images:                      %6
    echo Average size of images:                  %7
    echo Highest resolution image:                %8
    echo Lowest resolution image:                 %9
) > "%parentPath%\%outputStatistics%"

echo Statistics saved to %parentPath%\%outputStatistics%
