import os
import time
import threading
from flask import Flask, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_migrate import Migrate
import cv2
import numpy as np

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), "instance/alerts.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")

# Database Model for storing alerts
class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(100))
    behavior_type = db.Column(db.String(100))
    location = db.Column(db.String(100))

# Initialize the database if not yet created
with app.app_context():
    db.create_all()

# YOLO Model Setup
net = cv2.dnn.readNet("./yolov4.weights", "./yolov4.cfg")
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# Load class labels
with open("./coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

# Function to initialize the camera
def initialize_camera():
    camera = cv2.VideoCapture(0)  # Use 0 for the default camera
    if not camera.isOpened():
        raise Exception("Could not open the camera.")
    return camera

# Global variable to store camera
camera = initialize_camera()

# Custom Logic for Misbehavior Detection
def detect_misbehavior(frame):
    height, width = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outputs = net.forward(output_layers)

    class_ids = []
    boxes = []
    confidences = []

    # Custom logic parameters
    people_positions = []  # Store coordinates of detected people
    detected_objects = {}   # To track other objects
    misbehaviors = []

    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            # Set a higher confidence threshold to avoid false positives
            if confidence > 0.7:  # Increase threshold from 0.5 to 0.7
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

                # Track people
                if classes[class_id] == "person":
                    people_positions.append((center_x, center_y))

                # Track objects
                if classes[class_id] not in detected_objects:
                    detected_objects[classes[class_id]] = [(center_x, center_y)]
                else:
                    detected_objects[classes[class_id]].append((center_x, center_y))

    # Custom misbehavior logic

    # 1. Detect multiple people close together (possible fight)
    if len(people_positions) > 1:  # Only check for proximity if more than one person is detected
        for i in range(len(people_positions)):
            for j in range(i + 1, len(people_positions)):
                distance = np.linalg.norm(np.array(people_positions[i]) - np.array(people_positions[j]))
                if distance < 100:  # If people are too close together
                    misbehaviors.append("Potential fight detected: people too close!")
                    break  # Exit the loop if misbehavior is detected

    # 2. Detect if a person is holding a dangerous object (e.g., knife, bottle)
    dangerous_objects = ["knife", "bottle"]
    if "person" in detected_objects:
        for obj in dangerous_objects:
            if obj in detected_objects:
                misbehaviors.append(f"Danger detected: Person holding a {obj}!")

    # 3. Avoid repeating the same misbehavior if nothing has changed
    if not misbehaviors:  # No misbehavior detected
        return []
    
    return misbehaviors


# Thread for YOLO processing
def yolo_detection_thread():
    global camera
    frame_count = 0
    previous_misbehavior = None

    while True:
        success, frame = camera.read()
        if not success:
            print("Warning: Couldn't read frame, skipping.")
            time.sleep(0.01)
            continue

        # Process every 10th frame for misbehavior
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

                    socketio.emit('alert', {'message': alert_message})

                previous_misbehavior = misbehaviors  # Update previous misbehavior
            else:
                previous_misbehavior = None  # Reset if no misbehavior detected

        time.sleep(0.03)  # Allow 30 FPS for YOLO processing

# Start YOLO detection in a separate thread
yolo_thread = threading.Thread(target=yolo_detection_thread, daemon=True)
yolo_thread.start()

# Function to stream video feed
def gen():
    global camera
    while True:
        success, frame = camera.read()

        if not success:
            print("Warning: Couldn't read frame, skipping.")
            time.sleep(0.01)
            continue

        # Encode frame to jpeg and yield it for streaming
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        time.sleep(0.016)  # 60 FPS streaming

@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Endpoint to get alerts
@app.route('/alerts', methods=['GET'])
def get_alerts():
    alerts = Alert.query.all()
    return jsonify([{'id': alert.id, 'timestamp': alert.timestamp, 'behavior_type': alert.behavior_type, 'location': alert.location} for alert in alerts])

if __name__ == '__main__':
    socketio.run(app, port=5000)
