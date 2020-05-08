Add-Type -AssemblyName System.Windows.Forms;
$clip = [System.Windows.Forms.Clipboard]::GetText();
$head = '-----VALID BASE64-----';
if ($clip -Match $head) {
    $SaveFileDialog = New-Object System.Windows.Forms.SaveFileDialog;
    $rc = $SaveFileDialog.ShowDialog();
    if ($rc -eq [System.Windows.Forms.DialogResult]::OK) {
        $data = $clip.Replace($head, '');
        [IO.File]::WriteAllBytes($SaveFileDialog.FileName, [Convert]::FromBase64String($data));
    }
    [System.Windows.Forms.Clipboard]::SetText(' ');
}
else {
    $OpenFileDialog = New-Object System.Windows.Forms.OpenFileDialog;
    $rc = $OpenFileDialog.ShowDialog();
    if ($rc -eq [System.Windows.Forms.DialogResult]::OK) {
        $temp = [Convert]::ToBase64String([IO.File]::ReadAllBytes($OpenFileDialog.FileName));
        [System.Windows.Forms.Clipboard]::SetText($head + $temp);
    }
}
