Set WshShell = CreateObject("WScript.Shell")
Dim objFSO
Set objFSO = CreateObject("Scripting.FileSystemObject")
Dim CurrentDirectory
WshShell.Run chr(34) & objFSO.GetAbsolutePathName(".") & "\run.bat" & Chr(34), 0
Set WshShell = Nothing