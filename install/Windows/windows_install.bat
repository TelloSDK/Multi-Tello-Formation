echo=1/*>nul&@cls
@echo off
setlocal enableDelayedExpansion
::runas administrator
%1 start "" mshta vbscript:CreateObject("Shell.Application").ShellExecute("cmd.exe","/c %~s0 ::","","runas",1)(window.close)&&exit
cls
::setlocal
call :setdir
call :configx86orx64
set extract=extract
set pythonLib="C:\Python27\Lib\site-packages\"
set /a maxRetry=3
set /a retryCount=0
echo ------------------------------------------------------

::-------------------down python2.7 and install-------------------
echo ------------------------------------------------------
echo                Downloading python2.7                  
echo ------------------------------------------------------
::此条注册表项用于开启ssl、tls多个版本的支持，用于解决python官网拒绝访问的问题
REG ADD "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v SecureProtocols /t REG_DWORD /d 2728 /f >nul
set /a retryCount=0

if exist %pythonPackage% goto :downpythoninstall
:downpython
call :down %pythonDown% %pythonPackage%
:downpythoninstall
call :installmsiPackage %pythonPackage%
::添加python2.7环境变量
::由于wmic不会即时生效，所以进行set
echo %PATH%|findstr "c:\python27" >nul
if %errorlevel% neq 0 (
	wmic ENVIRONMENT where "name='PATH' and username='<system>'" set VariableValue="%PATH%;c:\python27"
	set "path=%path%;c:\python27;"
)
echo %PATHEXT%|findstr ".PY;.PYM" >nul
if %errorlevel% neq 0 (
	wmic ENVIRONMENT where "name='PATHEXT' and username='<system>'" set VariableValue="%PATHEXT%;.PY;.PYM"
	set "pathext=%pathext%;.PY;.PYM;"
)
:downpythonend
::-------------------python pip的安装-------------------
echo ------------------------------------------------------
echo                   Downloading pip                    
echo ------------------------------------------------------
if exist %pipPackage% goto :downpipinstall
:downpip
call :down %pipDown% %pipPackage%
:downpipinstall
python %pipPackage%
python -m pip install -U pip
:downpipend
python -m pip install --upgrade pip
::-------------------python-numpy python-matplotlib opencv-python的安装（pip方式）-------------------
echo ------------------------------------------------------
echo                  Downloading netifaces                    
echo ------------------------------------------------------
python -m pip install netifaces
echo ------------------------------------------------------
echo                Downloading netaddr                 
echo ------------------------------------------------------
python -m pip install netaddr
echo ------------------------------------------------------
:copydependencies
pause
goto :eof

::-----------------下面是目录切换定义区域------------------
::在管理员模式执行时，默认路径变更，此处将目录切换回来
:setdir
set char=%~dp0%
%char:~0,2%
cd  %~dp0%
goto :eof

::-----------------下面是版本函数定义区域------------------
:configx86orx64
IF %PROCESSOR_ARCHITECTURE% == AMD64 (
	set versionFlag=win64
) else ( 
	set versionFlag=win32
)

echo Windows Version: %versionFlag%
if %versionFlag%==win64 (
	set pythonDown="https://www.python.org/ftp/python/2.7.15/python-2.7.15.amd64.msi"
	set pythonPackage=python-2.7.15.amd64.msi

	set pipDown="https://bootstrap.pypa.io/get-pip.py"
	set pipPackage=get-pip.py
	
) else (
	set pythonDown="https://www.python.org/ftp/python/2.7.15/python-2.7.15.msi"
	set pythonPackage=python-2.7.15.msi

	set pipDown="https://bootstrap.pypa.io/get-pip.py"
	set pipPackage=get-pip.py
)

goto :eof

::-----------------下面是下载函数定义区域------------------
:down
echo Source:      "%~1"
echo Destination: "%~f2"
echo Start downloading "%~2"...
cscript -nologo -e:jscript "%~f0" "download" "%~1" "%~2"
::echo Download "%~2" OK!
echo ------------------------------------------------------
goto :eof

::-----------------下面是解压函数定义区域------------------
:unpack
echo Source:      "%~f1"
echo Destination: "%~f2"
echo Start unpacking "%~1"...
cscript -nologo -e:jscript "%~f0" "unpack" "%~1" "%~2" "%~dp0"
echo Unpack "%~1" OK!
echo ------------------------------------------------------
goto :eof
::-----------------下面是安装函数定义区域------------------
:installmsiPackage
echo Source:      "%~f1"
echo Strat installing "%~f1"...
msiexec /i "%~f1" /passive
echo install "%~1" OK!
echo ------------------------------------------------------
goto :eof
*/

function download(DownSource, DownDestination)
{
	var DownPost
	,DownGet;
	 
	DownDestination=DownDestination.toLowerCase();
	DownSource=DownSource.toLowerCase();
	//DownPost = new ActiveXObject("Msxml2"+String.fromCharCode(0x2e)+"ServerXMLHTTP");
	//DownPost = new ActiveXObject("Microsoft"+String.fromCharCode(0x2e)+"XMLHTTP");
	//DownPost.setOption(2, 13056);
	var DownPost=null; 
	try{ 
		DownPost=new XMLHttpRequest(); 
	}catch(e){ 
		try{ 
			DownPost=new ActiveXObject("Msxml2.XMLHTTP"); 
			DownPost.setOption(2, 13056);
		}catch(ex){ 
			try{ 
				DownPost=new ActiveXObject("Microsoft.XMLHTTP"); 
			}catch(e3){ 
				DownPost=null; 
			} 
		} 
	} 
	DownPost.open("GET",DownSource,0);
	DownPost.send();
	DownGet = new ActiveXObject("ADODB"+String.fromCharCode(0x2e)+"Stream");
	DownGet.Mode = 3;
	DownGet.Type = 1; 
	DownGet.Open(); 
	DownGet.Write(DownPost.responseBody);
	DownGet.SaveToFile(DownDestination,2); 
}

function unpack(PackedFileSource, UnpackFileDestination, ParentFolder)
{
	var FileSysObject = new Object
	,ShellObject = new ActiveXObject("Shell.Application")
	,intOptions = 4 + 16
	,DestinationObj
	,SourceObj;
	
	if (!UnpackFileDestination) UnpackFileDestination = '.';
	var FolderTest = ShellObject.NameSpace(ParentFolder + UnpackFileDestination);
	FileSysObject = ShellObject.NameSpace(ParentFolder);
	while (!FolderTest) 
	{
		WSH.Echo ('Unpack Destination Folder Not Exist, Creating...');
		FileSysObject.NewFolder(UnpackFileDestination);
		FolderTest = ShellObject.NameSpace(ParentFolder + UnpackFileDestination);
		if (FolderTest) 
		WSH.Echo('Unpack Destination Folder Created.');
	}
	DestinationObj = ShellObject.NameSpace(ParentFolder + UnpackFileDestination); 
	SourceObj = ShellObject.NameSpace(ParentFolder + PackedFileSource);
    for (var i = 0; i < SourceObj.Items().Count; i++) 
	{
		try {
			if (SourceObj) {
				WSH.Echo('Unpacking ' + SourceObj.Items().Item(i) + '... ');
				DestinationObj.CopyHere(SourceObj.Items().Item(i), intOptions);
				WSH.Echo('Unpack ' + SourceObj.Items().Item(i) + ' Done.');
			}
		}
		catch(e) {
			WSH.Echo('Failed: ' + e);
		}
	}
}

switch (WScript.Arguments(0)){
	case "download":
		download(WScript.Arguments(1), WScript.Arguments(2));
		break;
	case "unpack":
		unpack(WScript.Arguments(1), WScript.Arguments(2), WScript.Arguments(3));
		break;
	default:
}
	
