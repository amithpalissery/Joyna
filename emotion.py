import cv2
import numpy as np
from fer import FER
from collections import deque, Counter
import time
from datetime import datetime
import matplotlib.pyplot as plt
import os

# Initialize the emotion detector
detector = FER(mtcnn=True)

# Initialize webcam
cap = cv2.VideoCapture(0)

# Check if webcam is opened successfully
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Log file
log_file = "D:/Main project/Chatbot/emotion_log.txt"
output_folder = "emotion_session_data"
os.makedirs(output_folder, exist_ok=True)

# Variables for logging and session analysis
emotion_history = deque(maxlen=50)  # Stores emotions for ~5 seconds (assuming ~10 FPS)
current_emotion = None
emotion_start_time = None
session_emotions = Counter()  # To track emotion distribution for the session

def log_transition(from_emotion, to_emotion, duration, scores, timestamp):
    """
    Logs a transition from one emotion to another.
    """
    with open(log_file, "a") as file:
        log_entry = (
            f"Date: {timestamp.strftime('%Y-%m-%d')} | "
            f"Time: {timestamp.strftime('%H:%M:%S')} | "
            f"Transition: {from_emotion} -> {to_emotion} | "
            f"Duration: {duration:.2f}s | "
            f"Scores: {scores}\n"
        )
        file.write(log_entry)

def plot_emotion_distribution(emotion_counter):
    """
    Plots a pie chart of the emotion distribution for the session.
    """
    labels = list(emotion_counter.keys())
    sizes = list(emotion_counter.values())
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
    plt.title("Emotion Distribution for the Session")
    plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.
    plt.tight_layout()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = os.path.join(output_folder, f"emotion_distribution_{timestamp}.png")
    plt.savefig(file_path)
    print(f"Emotion distribution chart saved at: {file_path}")
    plt.show()

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break

        # Convert the frame to RGB for FER
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect emotions in the frame
        emotions = detector.detect_emotions(rgb_frame)
        if emotions:
            emotion_scores = emotions[0]["emotions"]  # Get the emotion probabilities
            dominant_emotion = max(emotion_scores, key=emotion_scores.get)
            emotion_history.append((dominant_emotion, emotion_scores, time.time()))
            session_emotions[dominant_emotion] += 1  # Update session emotion count

            # Check for emotion transition
            if current_emotion is None:
                current_emotion = dominant_emotion
                emotion_start_time = time.time()
            elif current_emotion != dominant_emotion:
                # Log the transition
                duration = time.time() - emotion_start_time
                timestamp = datetime.now()
                log_transition(
                    current_emotion, dominant_emotion, duration, emotion_scores, timestamp
                )
                # Update current emotion
                current_emotion = dominant_emotion
                emotion_start_time = time.time()

        # Calculate emotions for the past 5 seconds
        current_time = time.time()
        recent_emotions = [e for e in emotion_history if current_time - e[2] <= 5]

        if recent_emotions:
            # Aggregate the scores over the past 5 seconds
            aggregated_scores = {}
            for _, scores, _ in recent_emotions:
                for emotion, score in scores.items():
                    aggregated_scores[emotion] = aggregated_scores.get(emotion, 0) + score

            # Normalize the scores
            total_scores = sum(aggregated_scores.values())
            normalized_scores = {k: v / total_scores for k, v in aggregated_scores.items()}

            # Determine the most frequent emotion
            most_frequent_emotion = max(normalized_scores, key=normalized_scores.get)

            # Display the emotion and scores
            text = f"Emotion: {most_frequent_emotion} | Scores: {normalized_scores}"
            cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Display the video feed
        cv2.imshow("Emotion Detection", frame)

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    # Release the resources
    cap.release()
    cv2.destroyAllWindows()

    # Plot and save emotion distribution
    if session_emotions:
        plot_emotion_distribution(session_emotions)
