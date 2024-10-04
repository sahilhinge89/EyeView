
# EyeView

EyeView is an intelligent camera system designed to detect misbehavior in real time. It leverages YOLO (You Only Look Once) for object detection and Flask for backend functionality.

## Features

- Real-time video streaming
- Detection of potential fights based on proximity of people
- Alerts for dangerous objects being held by individuals
- Database integration to store alerts

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

## Usage

The application will start streaming video from the camera and will print alerts to the console when misbehavior is detected. 

## Contributing

If you have suggestions or improvements, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/sahilhinge89/EyeView/blob/main/LICENSE) file for details.
```
