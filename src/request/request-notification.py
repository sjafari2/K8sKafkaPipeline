from flask import Flask

app = Flask(__name__)


@app.route('/notification', methods=['POST'])
def notification_received():
    print("Received notification from merge pod.")
    return "Notification received", 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
