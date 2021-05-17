@echo off

set ROOT_DIR=D:\dev\AVIDPyWorkflow\rework_ng\Utilities\pdc++\General
set DEVICE_DIR=D:\dev\AVIDPyWorkflow\rework_ng\Utilities\pdc++\Resources\TestData

REM * path to the xml description of the ct header
set XMLIO_SCHEMA_STYLESHEET_PATH=%DEVICE_DIR%\xml\
REM * electron density threshold of the skin to recognize the surface entry
set SKINTHRESHOLD=0.4

REM * optional environment variables
REM * writes an additional dose cube with absolute dose values
set DC_WRITE_ABS_DOSE_CUBE=1
REM * Usually the CT image is reduced in its dimension (by decreasing its resolution)
REM * to reduce calculation times. If this reduction should be skipped and a dose cube
REM * with the dimension of the CT image should be created, set this variable. This
REM * will lead to a slower run time by a factor of 4-8.
set DC_USE_BIG_DOSECUBE=1

set hour=%time:~0,2%
set hour=%hour: =0% 
set hour=%hour: =%
set full_date=%date:~10,4%%date:~4,2%%date:~7,2%-%hour%%time:~3,2%%time:~6,2%

set DATA_DIR=%ROOT_DIR%\data
set BIN_DIR=%ROOT_DIR%\bin
set PATH=%BIN_DIR%;%PATH%

@echo ON

REM virtuos usage: PDC.exe <pat> <planNo> <pathToPat> <patSeries>.ctx [ <patSeries>.vdx --numThreads=NUM --useDefaultDevices --useDefaultBaseData ]
REM * test series
set pat=
set img=
set vdx=
set plan_no=777
set plan_base=%pat%%plan_no%

set PATIENT_DIR=%DATA_DIR%\%pat%
set FULL_LOGFILE=%PATIENT_DIR%\%pat%%plan_no%_%full_date%.log

Call CMD /C Call %BIN_DIR%\PDC.exe %pat%_ %plan_no% %PATIENT_DIR% %img% %vdx% --numThreads=16

