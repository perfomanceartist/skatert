#!/bin/bash
python3 /root/skatert/manage.py runserver 46.23.96.41:80
python3 /root/skatert/manage.py runserver_plus --cert-file /root/skatert/cert.pem --key-file /root/skatert/key.pem 46.23.96.41:443