from flask import Flask, request, jsonify
from flask_cors import CORS
from agent.emotion_monitor import EmotionMonitorService

import threading

# Initialize Flask app
app = Flask(__name__)
CORS(app) 

# Initialize emotion monitor service
emotion_service = EmotionMonitorService()

@app.route('/api/monitor/start', methods=['POST'])
def start_monitoring():
    """Start monitoring emotions"""
    try:
        data = request.get_json()
        duration = float(data.get('duration', 5.0))
        
        if emotion_service.start_monitoring(duration):
            return jsonify({
                'status': 'success',
                'message': f'Started monitoring for {duration} seconds'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to start monitoring'
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    
@app.route('/api/monitor/result', methods=['GET'])
def get_result():
    """Get the emotional response result"""
    try:
        emotion_data = emotion_service.get_dominant_emotion()
        
        # TODO: Can potentially make confusion indicators more sensitive by just treating
        # it as if confusion exists when we see neutral, surprise, and anger all in one buffer or something
        if emotion_data:
            # Determine if follow-up is needed
            confusion_indicators = {
                'neutral': 0.7,
                'surprise': 0.6,
                'fear': 0.5,
                'sad': 0.5
            }
            
            needs_followup = (
                emotion_data['emotion'] in confusion_indicators and 
                emotion_data['score'] > confusion_indicators[emotion_data['emotion']]
            )
            
            return jsonify({
                'status': 'success',
                'data': {
                    'emotion': emotion_data,
                    'needs_followup': needs_followup
                }
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'No emotion data available'
            }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# LLM Translation Route 


# Emotion Recognition Route


# Run the app
if __name__ == '__main__':
    # Start Flask in a daemon thread
    flask_thread = threading.Thread(
        target=lambda: app.run(host='127.0.0.1', port=5000, debug=False)
    )
    flask_thread.daemon = True
    flask_thread.start()
    
    # Run OpenCV in main thread
    try:
        emotion_service.run_video_display()
    finally:
        emotion_service.stop()