```markdown
# EyeView

EyeView is an intelligent camera system designed to detect misbehavior in real time. It leverages YOLO (You Only Look Once) for object detection and Flask for backend functionality.

## Features

- Real-time video streaming
- Detection of potential fights based on proximity of people
- Alerts for dangerous objects being held by individuals
- Database integration to store alerts

## Note

This application is still undergoing improvements, and some features may be added or refined in future versions.

## License

This project is licensed under a **Proprietary License**.

**Proprietary License**  
Copyright © 2024 sahilhinge89, Parth2684. All Rights Reserved.

Permission is hereby granted to the owners of this repository only. No other person or organization is granted permission to copy, modify, merge, publish, distribute, sublicense, or sell copies of the Software or associated documentation files, without prior written permission from the copyright holders.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NONINFRINGEMENT. IN NO EVENT SHALL THE COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, ARISING FROM, OUT OF, OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

For further inquiries or permissions, please contact the repository owners.

## Requirements

To run this application, you need the following:

- Python 3.x
- Flask
- Flask-SocketIO
- Flask-CORS
- Flask-Migrate
- OpenCV
- NumPy

You can install the required packages using:

```bash
pip install -r requirements.txt
```

## YOLO Setup

The YOLO model is included in this repository:

- `yolov4.weights` - YOLO model weights
- `yolov4.cfg` - YOLO model configuration
- `coco.names` - Class labels for COCO dataset

These files can be found in the repository under the `/Backend` directory.

## Running the Application

1. Clone the repository:

   ```bash
   git clone https://github.com/sahilhinge89/EyeView.git
   cd EyeView
   ```

2. Ensure you have the required YOLO files in place:

   - Place `yolov4.weights`, `yolov4.cfg`, and `coco.names` in the `/Backend` directory.

3. Start the Flask application:

   ```bash
   python app.py
   ```

4. Open your browser and navigate to `http://localhost:5000/video_feed` to view the application.

## Frontend Setup

To start the frontend application:

1. Open another terminal and navigate to the `EyeView` directory:

   ```bash
   cd eye-view
   ```

2. Install the required dependencies:

   ```bash
   npm install
   ```

3. Start the frontend development server:

   ```bash
   npm start
   ```

4. Open your browser and navigate to `http://localhost:3000` to view the frontend interface.

## Usage

The application will start streaming video from the camera and will print alerts to the console when misbehavior is detected.

## Contributing

If you have suggestions or improvements, feel free to open an issue or submit a pull request.
```

This now includes the note that the application is a work in progress. Let us know if you need more adjustments!
