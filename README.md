## Joyna: The AI-Driven Companion for Social and Emotional Development

A sophisticated AI-powered companion designed to foster emotional intelligence, empathy, and social-emotional development in children through real-time, adaptive interactions. Joyna leverages multimodal data—including facial expressions and vocal cues—to provide personalized, context-aware emotional support and engagement.

-----

## 🌟 Features

Joyna integrates cutting-edge AI and ML technologies to create a dynamic and empathetic user experience:

**Multimodal Emotion Detection:** Real-time analysis of a child's emotional state by combining **Facial Expression Analysis** (using DeepFace/MTCNN) and **Speech Sentiment Analysis**
**Adaptive Conversational AI:** Powered by the **Google Gemini API** , Joyna generates emotionally appropriate, age-specific, and contextually relevant responses
**Personalized Interaction:** The system dynamically adjusts its conversation and suggested activities (e.g., comforting words for sadness, engaging storytelling for happiness) based on the child's detected emotion
**Parental Analytics Dashboard:** A Flask-based web application that provides parents with a comprehensive overview of the child's emotional trends, session summaries, and conversation history.
**Speech Processing:** Utilizes the Google Speech API for **Automatic Speech Recognition (ASR)** to transcribe child speech and the SpeechSynthesis API for natural-sounding **Text-to-Speech (TTS)** output.

-----

## 🛠️ Technology Stack

| Component | Technology / API | Role |
| :--- | :--- | :--- |
| **Conversational AI / NLP** | Google Gemini API (Generative AI) |Core chat logic and contextual sentiment analysis |
| **Facial Emotion Detection** | DeepFace, MTCNN, OpenCV |Computer vision models for real-time face and emotion classification. |
| **Backend & Dashboard** | Python, Flask, JavaScript |Main programming language, web application framework for the dashboard. |
| **Speech Recognition** | SpeechRecognition API (Google Speech) | Converts spoken input to text (ASR). |
| **Response Output** | SpeechSynthesis API | Generates verbal, natural-sounding audio responses (TTS). |

-----

## 📂 System Architecture

The Joyna system follows a structured pipeline for interaction:

1. **Input Capture:** Microphone records speech, and the webcam captures video for facial expressions.
2.  **Data Processing:** Speech is converted to text via ASR. NLP and emotion detection algorithms (including facial analysis) determine the child's sentiment and intent.
3.  ]**Response Generation:** The Gemini-powered conversational AI uses the detected emotion and conversation history to generate an emotionally appropriate response.
4.  **Output & Logging:** Response is delivered via TTS and logged. Interaction summaries and emotion statistics are logged for the parental dashboard.

A detailed workflow diagram is available in the `docs/` folder:

> 

-----

## 🚀 Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

  * Python 3.x
  * A webcam and microphone (required for real-time multimodal detection)
  * A Google API Key with access to the **Gemini API**

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/joyna-ai-companion.git
    cd joyna-ai-companion
    ```

2.  **Create and activate a virtual environment (recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables:**
    Create a file named `.env` in the root directory and add your API key:

    ```
    # Replace YOUR_GEMINI_API_KEY with your actual key
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    ```

### Running the Application

Joyna involves two main components: the core AI engine for real-time interaction and the Parental Dashboard.

1.  **Run the Emotion detection file:**

    ```bash
    python emotion_detection.py
    ```
2.  **Run the Core AI Engine:**

    ```bash
    python main.py
    ```

3.  **Run the Parental Dashboard:**
    In a separate terminal, start the Flask application:

    ```bash
    python main.py
    ```

    Access the dashboard in your browser at `http://127.0.0.1:5000` (default Flask port).

-----

## 🛑 Limitations and Future Scope

### Current Limitations

  * **Hardware Dependence:** Relies on external webcam/microphone for emotion detection.
  * **Lighting Conditions:** Facial emotion accuracy can be affected by poor or extreme lighting.
  * **Language Support:** Currently supports **English only**.

### Future Enhancements (Roadmap)

   **Embedded System Integration:** Transition to a **Raspberry Pi-based embedded system** for on-device processing to enhance portability and autonomy.
    **Advanced Emotion Detection:** Integrate **3D facial analysis** and deep learning-based **prosody analysis** to capture more subtle emotional nuances.
   **Multilingual Support:** Expansion to include additional languages to broaden accessibility.
   **Database Integration:** Migrate from lightweight text-file logging to a **NoSQL database** for more structured and efficient data storage.


-----

## ⚖️ License

This project is licensed under the MIT License - see the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.

-----


<img width="1920" height="1080" alt="Screenshot 2025-02-16 161335" src="https://github.com/user-attachments/assets/eaaf14c2-2aee-4095-bb5f-c8774225b1d8" />
