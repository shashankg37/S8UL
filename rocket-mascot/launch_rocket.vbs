' Launch Rocket without a console window. This file is used by the Windows
' Startup shortcut and can also be double-clicked to start the mascot manually.
Option Explicit

Dim shell, fso, projectFolder, pythonw, command
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

projectFolder = fso.GetParentFolderName(WScript.ScriptFullName)
pythonw = projectFolder & "\.venv\Scripts\pythonw.exe"
If Not fso.FileExists(pythonw) Then
    pythonw = "pythonw.exe"
End If

shell.CurrentDirectory = projectFolder
command = Chr(34) & pythonw & Chr(34) & " " & Chr(34) & projectFolder & "\main.py" & Chr(34)
shell.Run command, 0, False
