echo off
cls
rmdir /S /Q dist
copy ..\yogi.py .
copy ..\trace.py .
copy ..\dot_parser.py .
copy ..\pyparsing.py .
copy ..\pydot.py .
copy ..\query.py .

python -OO build.py py2exe --bundle 1

copy dist\yogi.exe dist\yogi_pe.exe
copy dist\yogi.exe dist\yogi_upx.exe
copy dist\yogi.exe dist\yogi_peupx.exe
upx -9 dist\yogi_upx.exe
pec2.exe /Cl:9 /Ko dist\yogi_pe.exe 
upx -9 dist\yogi_peupx.exe
pec2.exe /Cl:9 /Ko dist\yogi_peupx.exe 

del dist\yogi_pe.exe.pec2bac
del dist\yogi_peupx.exe.pec2bac
del yogi.py
del trace.py
del dot_parser.py
del pyparsing.py
del pydot.py
del query.py
rmdir /S /Q build
pause