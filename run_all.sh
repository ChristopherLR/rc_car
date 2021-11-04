#!/bin/bash
sudo apt-get install -y screen
screen -dmS image_gen bash -c 'cd image_gen && poetry run start'
screen -dmS state_machine bash -c 'cd state_machine && poetry run start'
screen -dmS motor_driver bash -c 'cd motor_driver && poetry run start'
screen -dmS web-interface bash -c 'cd web-interface && poetry run start'
