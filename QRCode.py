from flask import Flask, render_template, redirect, url_for, session
import json, requests
import pyqrcode
import os, random, string
from wtforms import (StringField,RadioField,SelectField,SubmitField)

# 2 variables - current qrcode filename and old one
#Home page - check if qrcode parameter has some value otherwise reset the password


app = Flask(__name__)

apikey = "Enter the API Key here"

headers = {
		'x-cisco-meraki-api-key': str(apikey),
		'Content-Type': 'application/json'
	}
url = "https://api.meraki.com/api/v0/networks/network_id/ssids/0" # Replace network_id with the actual ID of the network



def change_psk():
    psk= "cisco"+str(random.randrange(1,100000))
    print("psk value: ", psk)

    payload = {
      "name": "SSID_Name", # Enter the SSID Name here
      "enabled": "true",
      "authMode": "psk",
      "encryptionMode": "wpa",
      "psk": psk
    }
    response = requests.put(url, data=json.dumps(payload), headers=headers)

    return psk


def gen_qrcode(psk):
	dir_path = os.path.dirname(os.path.realpath(__file__))
	file_path = os.path.join(dir_path, "static")
	random_filename = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
	#delete_this_file = "network"+str(random.randrange(1,10000))+".png"
	delete_this_file = str(random_filename)+".png"
	absolute_path=file_path+"/"+delete_this_file
	Wifi_Name="SSID_Name" # Enter the SSID Name here
	Wifi_Protocol = 'WPA'
	Wifi_Password = psk
	print("Wifi Password: ", Wifi_Password)
	QRCode = pyqrcode.create(F'WIFI:S:{Wifi_Name};T:{Wifi_Protocol};P:{Wifi_Password};;')
	QRCode.png(absolute_path, scale=5)
	print("Name of the QRCOde file: ", delete_this_file)
	return delete_this_file, file_path

delete_this_file = ""
current_file = ""

@app.route('/')
def home():
	global delete_this_file
	global current_file
	if current_file == "":
		psk = change_psk()
		current_file, file_path = gen_qrcode(psk)
		delete_this_file = current_file
		return render_template('home.html',current_file=current_file)
	else:
		return render_template('home.html',current_file=current_file)

@app.route('/QR_Code')
def QR_Code():
	global delete_this_file
	global current_file
	delete_this_file = current_file
	psk = change_psk()
	current_file, file_path = gen_qrcode(psk)
	os.remove(file_path+'/'+delete_this_file)
	return redirect(url_for('home'))

@app.route('/admin')
def admin():
    return render_template('admin.html')


if __name__ == '__main__':
    app.run(debug=True)
