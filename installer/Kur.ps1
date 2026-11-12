param(
    [ValidateSet('Steam','Epic','GOG','EA','Game Pass')][string]$Platform,
    [string]$GameDirectory,
    [switch]$NoGui
)
$ErrorActionPreference = 'Stop'
$packageRoot = $PSScriptRoot

function Get-PatchHash([string]$LiteralPath, [string]$Algorithm = 'SHA256') {
    $stream = [IO.File]::OpenRead($LiteralPath)
    $sha = [Security.Cryptography.SHA256]::Create()
    try { return [pscustomobject]@{Hash=([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-','')} }
    finally { $sha.Dispose(); $stream.Dispose() }
}


function Install-Patch([string]$SelectedPlatform, [string]$SelectedDirectory) {
    $variant = if ($SelectedPlatform -in @('EA','Game Pass')) { 'EA-GamePass' } else { 'Steam-Epic-GOG' }
    if (-not (Test-Path -LiteralPath $SelectedDirectory -PathType Container)) { throw 'Oyun klasörü bulunamadı.' }
    $target = (Get-Item -LiteralPath $SelectedDirectory).FullName
    if (-not (Test-Path -LiteralPath (Join-Path $target 'data\layout.toc') -PathType Leaf)) {
        throw 'Seçilen ana oyun klasöründe data\layout.toc bulunamadı. SP klasörünü değil, ana oyun klasörünü seçin.'
    }
    $manifest = Get-Content -LiteralPath (Join-Path $packageRoot 'dosyalar.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    $rows = @($manifest | Where-Object { $_.variant -eq $variant })
    if ($rows.Count -ne 4) { throw 'Paket dosya listesi eksik.' }
    $sourceRoot = Join-Path $packageRoot $variant
    $otherLoader = if ($variant -eq 'EA-GamePass') { 'SP\version.dll' } else { 'SP\dxgi.dll' }
    $oldLoader = $null
    if (Test-Path -LiteralPath (Join-Path $target $otherLoader)) {
        $known = $manifest | Where-Object { $_.path.Replace('/','\') -eq $otherLoader }
        $loaderItem = Get-Item -LiteralPath (Join-Path $target $otherLoader) -Force
        if ($loaderItem.PSIsContainer -or ($loaderItem.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'Eski yükleyici normal dosya değil.' }
        if (-not $known -or (Get-PatchHash -LiteralPath $loaderItem.FullName).Hash -ne $known.sha256) {
            throw "Kaynağı bilinmeyen $otherLoader mevcut. Çakışmayı önlemek için bu dosyayı otomatik değiştirmiyorum."
        }
        $oldLoader = $otherLoader
    }
    foreach ($row in $rows) {
        if ($row.path -notmatch '^SP/[A-Za-z0-9_.-]+$') { throw 'Geçersiz paket yolu.' }
        $source = Join-Path $sourceRoot $row.path
        if ((Get-PatchHash -LiteralPath $source -Algorithm SHA256).Hash -ne $row.sha256) { throw "Paket doğrulaması başarısız: $($row.path)" }
    }
    foreach ($part in @($target, (Join-Path $target 'SP'))) {
        if ((Test-Path -LiteralPath $part) -and ((Get-Item -LiteralPath $part -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            throw 'Oyun veya SP klasörü bir bağlantı. Lütfen gerçek oyun klasörünü seçin.'
        }
    }
    $backup = Join-Path $target ('TurkceYama-Yedek-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [guid]::NewGuid().ToString('N').Substring(0,6))
    New-Item -ItemType Directory -Path $backup | Out-Null
    $state = @()
    foreach ($row in $rows) {
        $destination = Join-Path $target $row.path
        $existed = Test-Path -LiteralPath $destination
        if ($existed) {
            $item = Get-Item -LiteralPath $destination -Force
            if ($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw "Hedef normal dosya değil: $destination" }
            $saved = Join-Path $backup $row.path
            New-Item -ItemType Directory -Path (Split-Path $saved) -Force | Out-Null
            Copy-Item -LiteralPath $destination -Destination $saved
            if ((Get-PatchHash -LiteralPath $destination).Hash -ne (Get-PatchHash -LiteralPath $saved).Hash) { throw 'Yedek doğrulanamadı; oyun dosyaları değiştirilmedi.' }
        }
        $state += [pscustomobject]@{path=$row.path; existed=$existed; sha256=$row.sha256}
    }
    if ($oldLoader) {
        $oldPath = Join-Path $target $oldLoader
        $oldSaved = Join-Path $backup $oldLoader
        New-Item -ItemType Directory -Path (Split-Path $oldSaved) -Force | Out-Null
        Copy-Item -LiteralPath $oldPath -Destination $oldSaved
        if ((Get-PatchHash -LiteralPath $oldPath).Hash -ne (Get-PatchHash -LiteralPath $oldSaved).Hash) { throw 'Eski platform yükleyicisinin yedeği doğrulanamadı.' }
        $state += [pscustomobject]@{path=$oldLoader; existed=$true; sha256=$null; removed=$true}
    }
    [pscustomobject]@{platform=$SelectedPlatform; gameDirectory=$target; files=$state} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $backup 'kurulum-kaydi.json') -Encoding UTF8
    $changed = @()
    try {
        foreach ($row in $rows) {
            $destination = Join-Path $target $row.path
            New-Item -ItemType Directory -Path (Split-Path $destination) -Force | Out-Null
            $changed += $row.path
            Copy-Item -LiteralPath (Join-Path $sourceRoot $row.path) -Destination $destination -Force
            if ((Get-PatchHash -LiteralPath $destination -Algorithm SHA256).Hash -ne $row.sha256) { throw "Kopya doğrulanamadı: $($row.path)" }
        }
        if ($oldLoader) {
            $changed += $oldLoader
            Remove-Item -LiteralPath (Join-Path $target $oldLoader) -Force
        }
    } catch {
        $failure = $_.Exception.Message
        $rollbackErrors = @()
        foreach ($relative in $changed) {
            try {
                $destination = Join-Path $target $relative
                $entry = $state | Where-Object { $_.path -eq $relative }
                if ($entry.existed) { Copy-Item -LiteralPath (Join-Path $backup $relative) -Destination $destination -Force }
                elseif (Test-Path -LiteralPath $destination -PathType Leaf) { Remove-Item -LiteralPath $destination -Force }
            } catch { $rollbackErrors += $_.Exception.Message }
        }
        if ($rollbackErrors.Count) { throw "$failure`nGeri alma tam tamamlanamadı. Yedek: $backup`n$($rollbackErrors -join '`n')" }
        throw "$failure`nYazılan dosyalar geri alındı. Yedek: $backup"
    }
    return "4 dosya kopyalandı ve doğrulandı.`r`nPlatform: $SelectedPlatform`r`nYedek: $backup"
}

if ($NoGui) {
    if (-not $Platform -or -not $GameDirectory) { throw 'Platform ve GameDirectory gerekli.' }
    Install-Patch $Platform $GameDirectory
    exit
}

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[Windows.Forms.Application]::EnableVisualStyles()
$form = New-Object Windows.Forms.Form
$form.Text = 'Türkçe Yama V3 — Çevrimdışı Kurulum'
$form.ClientSize = New-Object Drawing.Size(640,250)
$form.StartPosition = 'CenterScreen'
$form.FormBorderStyle = 'FixedDialog'
$form.MaximizeBox = $false
$form.Font = New-Object Drawing.Font('Segoe UI',10)
$intro = New-Object Windows.Forms.Label
$intro.SetBounds(20,18,600,46)
$intro.Text = 'Oyunu kapatın. Platformu ve data\layout.toc dosyasını içeren ana oyun klasörünü seçin. Mevcut dosyalar önce yedeklenir.'
$platformBox = New-Object Windows.Forms.ComboBox
$platformBox.SetBounds(20,78,230,30)
$platformBox.DropDownStyle = 'DropDownList'
$platformBox.Items.AddRange(@('Steam','Epic','GOG','EA','Game Pass'))
$platformBox.SelectedIndex = 0
$pathBox = New-Object Windows.Forms.TextBox
$pathBox.SetBounds(20,125,470,30)
$browse = New-Object Windows.Forms.Button
$browse.SetBounds(500,122,120,34)
$browse.Text = 'Klasör seç'
$browse.Add_Click({
    $picker = New-Object Windows.Forms.FolderBrowserDialog
    $picker.Description = 'Ana oyun klasörünü seçin'
    if ($picker.ShowDialog() -eq 'OK') { $pathBox.Text = $picker.SelectedPath }
    $picker.Dispose()
})
$install = New-Object Windows.Forms.Button
$install.SetBounds(440,185,180,42)
$install.Text = 'Yedekle ve kur'
$install.Add_Click({
    $install.Enabled = $false
    try {
        $message = Install-Patch ([string]$platformBox.SelectedItem) $pathBox.Text
        [Windows.Forms.MessageBox]::Show($message,'Dosya kurulumu tamamlandı','OK','Information') | Out-Null
    } catch { [Windows.Forms.MessageBox]::Show($_.Exception.Message,'Kurulum tamamlanamadı','OK','Error') | Out-Null }
    finally { $install.Enabled = $true }
})
$form.Controls.AddRange(@($intro,$platformBox,$pathBox,$browse,$install))
[void]$form.ShowDialog()
$form.Dispose()
