# emotion_monitor.py
import cv2
import threading
from fer import FER
from collections import deque
import time
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

class EmotionMonitorService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmotionMonitorService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.emotion_detector = FER(mtcnn=True)
        self.cap = cv2.VideoCapture(0)
        self.is_running = True
        self.is_monitoring = False
        self.emotion_buffer = deque(maxlen=10)
        self.monitoring_duration = 0
        self.monitoring_start = 0
        
        if not self.cap.isOpened():
            raise RuntimeError("Could not open video capture device")
        
        self._initialized = True

    def run_video_display(self):
        """Main video loop - runs in main thread"""
        cv2.namedWindow('Emotion Monitor', cv2.WINDOW_NORMAL)
        
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            if self.is_monitoring:
                emotions = self.emotion_detector.detect_emotions(frame)
                if emotions:
                    emotion_dict = emotions[0]['emotions']
                    dominant = max(emotion_dict.items(), key=lambda x: x[1])
                    self.emotion_buffer.append(dominant)
                    cv2.putText(frame, f"Emotion: {dominant[0]}", 
                              (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                              1, (0, 255, 0), 2)
                    
                if time.time() - self.monitoring_start >= self.monitoring_duration:
                    self.is_monitoring = False
            else:
                cv2.putText(frame, "Ready", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow('Emotion Monitor', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.is_running = False
                break

    def start_monitoring(self, duration: float) -> bool:
        self.emotion_buffer.clear()
        self.monitoring_duration = duration
        self.monitoring_start = time.time()
        self.is_monitoring = True
        return True

    def get_dominant_emotion(self):
        if not self.emotion_buffer:
            return None

        emotion_counts = {}
        for emotion, score in self.emotion_buffer:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + score

        dominant = max(emotion_counts.items(), key=lambda x: x[1])
        return {
            'emotion': dominant[0],
            'score': dominant[1] / len(self.emotion_buffer),
            'confidence': len(self.emotion_buffer) / self.monitoring_duration
        }

    def stop(self):
        self.is_running = False
        self.cap.release()
        cv2.destroyAllWindows()

# Initialize service
emotion_service = EmotionMonitorService()

@app.route('/api/monitor/start', methods=['POST'])
def start_monitoring():
    try:
        data = request.get_json()
        duration = float(data.get('duration', 5.0))
        
        if emotion_service.start_monitoring(duration):
            return jsonify({
                'status': 'success',
                'message': f'Started monitoring for {duration} seconds'
            }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/monitor/result', methods=['GET'])
def get_result():
    try:
        emotion_data = emotion_service.get_dominant_emotion()
        if emotion_data:
            return jsonify({
                'status': 'success',
                'data': emotion_data
            }), 200
        return jsonify({
            'status': 'error',
            'message': 'No emotion data available'
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500