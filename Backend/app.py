import os
import time
import threading
from flask import Flask, Response, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_migrate import Migrate
import cv2
import numpy as np
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), "instance/alerts.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Change this to a more secure key

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")
jwt = JWTManager(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)  # Store hashed passwords

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(100))
    behavior_type = db.Column(db.String(100))
    location = db.Column(db.String(100))

# Initialize the database if not yet created
with app.app_context():
    db.create_all()

# Add signup route
@app.route('/signup', methods=['POST'])
def signup():
    username = request.json.get('username')
    password = request.json.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username already exists"}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User created successfully"}), 201

# Add login route
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200

    return jsonify({"msg": "Bad username or password"}), 401

# Protect routes with JWT
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# YOLO Model Setup
net = cv2.dnn.readNet("./yolov4.weights", "./yolov4.cfg")
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# Global variables for camera, YOLO thread, client count, and last access time
camera = None
yolo_thread = None
active_clients = 0  # Track the number of active clients
last_access_time = None  # Track the last access time
timeout_duration = 10  # Time in seconds before releasing the camera

# Function to initialize the camera
def initialize_camera():
    global camera
    camera = cv2.VideoCapture(0)  # Change to 1 if using an external camera

    if not camera.isOpened():
        print("Error: Could not open the camera.")
        raise Exception("Could not open the camera.")

    print("Camera initialized successfully.")

# Function to release the camera
def release_camera():
    global camera
    if camera is not None and camera.isOpened():
        camera.release()
        camera = None
        print("Camera released.")

# Custom Logic for Misbehavior Detection
def detect_misbehavior(frame):
    height, width = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outputs = net.forward(output_layers)

    class_ids = []
    boxes = []
    confidences = []
    people_positions = []  # Store coordinates of detected people
    misbehaviors = []

    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > 0.8:  # Adjusted confidence threshold
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                # Define x and y using the center coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # Apply Non-Maximum Suppression
    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.8, 0.4)

    # Filter boxes and update people positions
    if len(indices) > 0:
        for i in indices.flatten():
            box = boxes[i]
            x, y, w, h = box
            people_positions.append((x + w // 2, y + h // 2))

    print(f"Detected persons: {len(people_positions)}, Positions: {people_positions}")

    # Detect multiple people close together (possible fight)
    if len(people_positions) > 1:
        for i in range(len(people_positions)):
            for j in range(i + 1, len(people_positions)):
                distance = np.linalg.norm(np.array(people_positions[i]) - np.array(people_positions[j]))

                if distance < 100:  # Distance threshold
                    misbehaviors.append("Potential fight detected: people too close!")
                    break

    # Dangerous objects detection
    dangerous_objects = ["knife", "bottle"]
    if "person" in class_ids:
        for obj in dangerous_objects:
            if obj in classes:
                misbehaviors.append(f"Danger detected: Person holding a {obj}!")

    return misbehaviors if misbehaviors else []

# Thread for YOLO processing
def yolo_detection_thread():
    global camera
    frame_count = 0
    previous_misbehavior = None

    while True:
        if camera is None or not camera.isOpened():
            print("Warning: Camera not initialized, waiting for re-initialization.")
            time.sleep(0.5)
            continue

        success, frame = camera.read()
        if not success:
            print("Warning: Couldn't read frame, skipping.")
            time.sleep(0.01)
            continue

        frame_count += 1
        if frame_count % 10 == 0:
            misbehaviors = detect_misbehavior(frame)

            if misbehaviors and misbehaviors != previous_misbehavior:
                for alert_message in misbehaviors:
                    print(alert_message)

                    with app.app_context():
                        new_alert = Alert(timestamp=time.strftime('%Y-%m-%d %H:%M:%S'), behavior_type=alert_message, location="Unknown")
                        db.session.add(new_alert)
                        db.session.commit()

                    alert_type = "danger" if "fight" in alert_message else "warning"
                    socketio.emit('alert', {'message': alert_message, 'type': alert_type})

                previous_misbehavior = misbehaviors
            else:
                previous_misbehavior = None

        time.sleep(0.03)  # Allow 30 FPS for YOLO processing

# Function to stream video feed
def gen():
    global camera
    while True:
        if camera is None or not camera.isOpened():
            print("Warning: Camera not initialized for streaming, waiting for re-initialization.")
            time.sleep(0.5)
            continue

        success, frame = camera.read()

        if not success:
            print("Warning: Couldn't read frame, skipping.")
            time.sleep(0.01)
            continue

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        time.sleep(0.016)  # 60 FPS streaming

# Background thread to check for client timeout
def check_for_timeout():
    global last_access_time, active_clients
    while True:
        time.sleep(1)
        if active_clients == 0:
            if last_access_time is not None and (time.time() - last_access_time) > timeout_duration:
                release_camera()
                print("Camera released due to timeout.")

# Video feed route
@app.route('/video_feed')
def video_feed():
    global camera, active_clients, last_access_time

    if active_clients == 0:  # Initialize camera if it's the first client
        try:
            initialize_camera()
            print("Starting YOLO detection thread.")
            yolo_thread = threading.Thread(target=yolo_detection_thread, daemon=True)
            yolo_thread.start()
        except Exception as e:
            return jsonify({"msg": str(e)}), 500

    active_clients += 1  # Increment active client count
    last_access_time = time.time()  # Update last access time
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Stop video feed route
@app.route('/stop_video_feed', methods=['POST'])
def stop_video_feed():
    global active_clients
    active_clients -= 1  # Decrement active client count
    if active_clients == 0:  # Release camera if no active clients
        release_camera()
    return jsonify({"msg": "Stopped video feed."}), 200

# Start the timeout checker thread
timeout_checker_thread = threading.Thread(target=check_for_timeout, daemon=True)
timeout_checker_thread.start()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
