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
    mac_address = request.form.get('mac')
    ip_address = request.form.get('ip')
    password = request.form.get('password')

    print(f"[DEBUG] Received: mac={mac_address}, ip={ip_address}, password=<{len(password or '')} chars>")
    print(f"[DEBUG] Comparing password: '{password.strip()}' == '{LOGIN_PASSWORD}' → {password.strip() == LOGIN_PASSWORD}")


    if not all([mac_address, ip_address, password]):
        print("[DEBUG] Missing parameter")
        return "Missing required parameters", 400

    if password.strip() != LOGIN_PASSWORD:
        print("[DEBUG] Wrong password")
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
        hotspot.add(
            mac_address=mac_address,
            address=ip_address
        )

        connection.disconnect()
        print("[DEBUG] Success — redirecting to /success")
        return redirect('/success')

    except Exception as e:
        print(f"[ERROR] RouterOS API Error: {str(e)}")
        print(traceback.format_exc())
        return "Error", 500

@app.route('/success')
def success():
    return "<html><body><h1>You're connected.</h1></body></html>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
