 param (
    $list,
    $result
 )

Write-Host $list
foreach ($computer in (get-content $list)) { 
  Try{  
    [system.net.Dns]::GetHostAddresses($computer) | Foreach-Object { 
      add-content -path $result -value "$computer,$($_.IPAddressToString)" 
    } 
  } Catch { 
    add-content -path $result -value "$computer,Cannot resolve hostname" 
  } 
}