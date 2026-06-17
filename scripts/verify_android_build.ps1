$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$androidDir = Join-Path $root "android-app"
$gradlew = Join-Path $androidDir "gradlew.bat"

if (Test-Path $gradlew) {
    Push-Location $androidDir
    try {
        & $gradlew assembleDebug
        exit $LASTEXITCODE
    } finally {
        Pop-Location
    }
}

$gradle = Get-Command gradle -ErrorAction SilentlyContinue
if ($gradle) {
    Push-Location $androidDir
    try {
        & $gradle.Source assembleDebug
        exit $LASTEXITCODE
    } finally {
        Pop-Location
    }
}

Write-Error "Android build verification requires android-app\gradlew.bat or a global gradle command."
exit 1
