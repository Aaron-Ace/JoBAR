#Upload file to google drive
#gdrive upload --parent 1HGLqiJNMjuZT4siqUxZtWhmsfY-5qGd0  /odoo/backups/dump_$(date +"%Y-%m-%d-%H-%M")*
echo "Starting upload backups to google drive..."
cd /odoo/backups && sh ./gdrive upload --parent 1HGLqiJNMjuZT4siqUxZtWhmsfY-5qGd0  /odoo/backups/dump_$(date +"%Y-%m-%d-%H-%M")*
echo "Compelete uplaod!"
