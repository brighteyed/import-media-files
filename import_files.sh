#!/bin/sh

echo -n "Importing photo... "
log_basename=`date +"%Y-%m-%d_%H-%M-%S"`.photo
python import_photo.py --src-dir=/source --out-dir=/output --log-file=/logs/$log_basename.json > /logs/$log_basename.log
echo "Done"

echo -n "Importing video... "
log_basename=`date +"%Y-%m-%d_%H-%M-%S"`.video
python import_video.py --src-dir=/source --out-dir=/output --log-file=/logs/$log_basename.json > /logs/$log_basename.log
echo "Done"