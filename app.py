from flask import Flask, request, redirect, make_response
import routeros_api
import traceback

app = Flask(__name__)

# Router connection configuration
ROUTER_IP = '172.27.72.4'       # Set your MikroTik router's ZeroTier IP
ROUTER_USER = 'admin'           # RouterOS username
ROUTER_PASSWORD = 'admin'       # RouterOS password
ROUTER_PORT = 8728

LOGIN_PASSWORD = 'guest 123'    # Password users must enter to get access

@app.route('/verify', methods=['POST'])
def verify():
    mac_address = request.form.get('mac')
    ip_address = request.form.get('ip')
    password = request.form.get('password')
    
    if not all([mac_address, ip_address, password]):
        return "Missing required parameters", 400
    
    if password.strip() != LOGIN_PASSWORD:
        return "Invalid password", 403
    
    try:
        connection = routeros_api.RouterOsApiPool(
            host=ROUTER_IP,
            username=ROUTER_USER,
            password=ROUTER_PASSWORD,
            port=ROUTER_PORT,
            plaintext_login=True
        )
        api = connection.get_api()
        
        hotspot = api.get_resource('/ip/hotspot/active')
        hotspot.add(
            mac_address=mac_address,
            address=ip_address
        )
        
        connection.disconnect()
        return redirect('/success')
    
    except Exception as e:
        print(f"RouterOS API Error: {str(e)}")
        print(traceback.format_exc())
        return "Error", 500

@app.route('/success')
def success():
    return "<html><body><h1>You're connected.</h1></body></html>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
