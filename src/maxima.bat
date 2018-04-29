@echo off

set arg0=%0
set arg1=%1
set arg2=%2
set arg3=%3
set arg4=%4
set arg5=%5
set arg6=%6
set arg7=%7
set arg8=%8
set arg9=%9

.\maxima\lib\maxima\5.27.0\binary-gcl\maxima.exe -eval "(cl-user::run)" -f -- %arg1% %arg2% %arg3% %arg4% %arg5% %arg6% %arg7% %arg8% %arg9%

