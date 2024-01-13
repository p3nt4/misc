param (
    $list,
    $result
 )

Write-Host $list
foreach ($computer in (get-content $list)) { 
  Try{  
    $value = Resolve-DnsName -Name $computer -DnsOnly -Type CNAME | Select-Object -First 1 | select -expandproperty namehost
    add-content -path $result -value "$computer,$value" 
  } Catch { 
    add-content -path $result -value "$computer,Cannot find cname" 
  } 
}