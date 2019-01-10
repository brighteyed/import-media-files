param (
    [Parameter(Mandatory=$true)][string]$takeout_dir,
    [Parameter(Mandatory=$true)][string]$import_dir,
    [Parameter(Mandatory=$true)][string]$albums_dir,
    [Parameter(Mandatory=$true)][string]$log_file,
    [Parameter(Mandatory=$true)][string]$ffmpeg_dir,
    [Parameter(Mandatory=$true)][string]$imported_photos_file
 )

$OutputEncoding = [System.Console]::OutputEncoding = [System.Console]::InputEncoding = [System.Text.Encoding]::UTF8;
${env:PYTHONIOENCODING}='UTF-8';

$ENV:PATH="$ENV:PATH;$ffmpeg_dir"

">>> IMPORT PHOTO" | Out-File $log_file
python .\import_photo.py --src-dir=$takeout_dir --out-dir=$import_dir --log-file=$imported_photos_file | Out-File -append $log_file
">>> DONE`n" | Out-File -append $log_file

">>> IMPORT VIDEO" | Out-File -append $log_file
python .\import_video.py --takeout-dir=$takeout_dir --out-dir=$import_dir | Out-File -append $log_file
">>> DONE`n" | Out-File -append $log_file

">>> CREATE ALBUMS METADATA"| Out-File -append $log_file
python .\albums_metadata.py --takeout-dir=$takeout_dir --out-dir=$import_dir | Out-File -append $log_file
">>> DONE`n" | Out-File -append $log_file

">>> CREATE ALBUMS" | Out-File -append $log_file
python .\create_albums.py --files-dir=$import_dir --metadata-dir=$import_dir --out-dir=$albums_dir | Out-File -append $log_file
">>> DONE`n" | Out-File -append  $log_file
