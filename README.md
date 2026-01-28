sudo apt install gunicorn
sudo gunicorn -b 0.0.0.0:31000 bsbf:app
