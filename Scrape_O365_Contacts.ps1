$wshell = New-Object -ComObject wscript.shell;
Sleep 2
$wshell.AppActivate('People - Hyslop, Jacquline R - Outlook — Mozilla Firefox')
Add-Type -MemberDefinition '[DllImport("user32.dll")] public static extern void mouse_event(int flags, int dx, int dy, int cButtons, int info);' -Name U32 -Namespace W;
while($true){
sleep -Milliseconds 1000;
#$wshell.SendKeys('{LButton}')
#Click-MouseButton left
#import mouse_event

#left mouse click
[W.U32]::mouse_event(0x0800,0,0,-63,0);
$wshell.SendKeys('{Down}')
}


































