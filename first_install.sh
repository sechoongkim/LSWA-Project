#!/bin/bash
set +x
virtualenv env -p python3
source ./env/bin/activate
pip3 install -r requirements.txt
deactivate
