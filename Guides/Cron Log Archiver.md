# Log Storage
Simple bash script that archives log files once a day.

## Script File
```
#!/bin/sh
cd /var/log/
tar cvzf "logs-$(date '+%Y%m%d%-H%M%S').tar.gz" log.* --remove-files > <home_dir>/out.txt
```

## Crontab (root)
```
sudo su
crontab -e
0 0 * * 0 . <home_dir>/<script_name>
```
