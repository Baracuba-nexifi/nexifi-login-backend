
from flask import Flask, request, redirect
import routeros_api
import traceback

app = Flask(__name__)

ROUTER_IP = '172.27.72.4'
ROUTER_USER = 'admin'
ROUTER_PASSWORD = 'admin'
ROUTER_PORT = 8728
LOGIN_PASSWORD = 'guest 123'

@app.route('/verify', methods=['POST'])
def verify():
    print("🔁 Entered verify()")

    mac_address = request.form.get('mac', '').strip()
    ip_address = request.form.get('ip', '').strip()
    password = request.form.get('password', '').strip()

    print(f"[DEBUG] Received: mac={mac_address}, ip={ip_address}, password length={len(password)}")
    print(f"[DEBUG] Comparing: '{password}' == '{LOGIN_PASSWORD}'")

    if not all([mac_address, ip_address, password]):
        print("[DEBUG] Missing parameters")
        return "Missing required parameters", 400

    if password != LOGIN_PASSWORD:
        print("[DEBUG] Invalid password")
        return "Invalid password", 403

    try:
        print(f"[DEBUG] Connecting to router {ROUTER_IP} on port {ROUTER_PORT}")
        connection = routeros_api.RouterOsApiPool(
            host=ROUTER_IP,
            username=ROUTER_USER,
            password=ROUTER_PASSWORD,
            port=ROUTER_PORT,
            plaintext_login=True
        )
        api = connection.get_api()
        hotspot = api.get_resource('/ip/hotspot/active')

        print(f"[DEBUG] Adding hotspot user: MAC={mac_address}, IP={ip_address}")
        hotspot.add(mac_address=mac_address, address=ip_address)

        connection.disconnect()
        return redirect('/success')

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        print(traceback.format_exc())
        return "Server error", 500

@app.route('/success')
def success():
    return "<html><body><h1>You're connected.</h1></body></html>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
