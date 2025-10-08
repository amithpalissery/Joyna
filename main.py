from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
from datetime import datetime
import re
import ast
import json

app = Flask(__name__)

# Load and preprocess data
def parse_emotion_log():
    try:
        data = []
        with open('emotion_log.txt', 'r') as file:
            for line in file:
                if line.strip():  # Skip empty lines
                    parts = line.split('|')
                    date_part = parts[0].split('Date:')[1].strip()
                    time_part = parts[1].split('Time:')[1].strip()
                    scores_part = parts[-1].split('Scores:')[1].strip()
                    
                    # Safely evaluate the scores string to convert it to a dictionary
                    try:
                        scores_dict = ast.literal_eval(scores_part)
                    except (ValueError, SyntaxError) as e:
                        print(f"Error parsing scores: {scores_part} - {str(e)}")
                        scores_dict = {}  # Default to an empty dictionary if parsing fails
                    
                    data.append({
                        'Date': date_part,
                        'Time': time_part,
                        'Scores': scores_dict
                    })
        
        df = pd.DataFrame(data)
        return df
    except FileNotFoundError:
        print("Warning: emotion_log.txt not found")
        return pd.DataFrame(columns=['Date', 'Time', 'Scores'])
    except Exception as e:
        print(f"Error reading emotion log: {str(e)}")
        return pd.DataFrame(columns=['Date', 'Time', 'Scores'])

# Load the emotion log
emotion_data = parse_emotion_log()

@app.route('/')
def home():
    total_interactions = get_total_interactions()
    print(f"Total Interactions: {total_interactions}")
    positive_percentage = calculate_positive_percentage()
    print(f"Positive Percentage: {positive_percentage}")
    active_days = calculate_active_days()
    print(f"Active Days: {active_days}")
    recent_activities = get_recent_activities()
    print(f"Recent Activities: {recent_activities}")
    
    return render_template('index.html',
                          total_interactions=total_interactions,
                          positive_percentage=positive_percentage,
                          active_days=active_days,
                          recent_activities=recent_activities)

@app.route('/emotion-log')
def show_emotion_log():
    return render_template('emotion_log.html')

@app.route('/chat-history')
def chat_history():
    return render_template('chat_history.html')

@app.route('/chat-summary/<path:date_str>')
def chat_summary(date_str):
    try:
        # Parse the incoming date string (format: MM/DD/YYYY)
        date_obj = datetime.strptime(date_str, '%m/%d/%Y')
        formatted_date = date_obj.strftime('%Y-%m-%d')
        
        try:
            # Read the emotion log with error handling
            df = pd.read_csv('emotion_log.txt', delimiter='|', skipinitialspace=True)
        except FileNotFoundError:
            return jsonify({
                "date": formatted_date,
                "sessions": [],
                "message": "No log file found"
            })
        
        # Clean and prepare the data
        df.columns = df.columns.str.strip()
        df['Date'] = df['Date'].str.strip()
        
        # Filter for the specific date
        daily_data = df[df['Date'] == formatted_date]
        
        if daily_data.empty:
            return jsonify({
                "date": formatted_date,
                "sessions": [],
                "message": "No data for this date"
            })
        
        sessions = []
        for _, row in daily_data.iterrows():
            try:
                # Extract scores from the string safely
                scores_str = row['Scores'].strip() if isinstance(row['Scores'], str) else '{}'
                scores_dict = eval(scores_str.replace("'", '"'))
                
                # Get the highest scoring emotion
                max_emotion = max(scores_dict.items(), key=lambda x: x[1])
                
                sessions.append({
                    "time": row['Time'].strip() if isinstance(row['Time'], str) else '',
                    "emotion": max_emotion[0],
                    "score": round(max_emotion[1], 2)
                })
            except Exception as row_error:
                print(f"Error processing row: {row_error}")
                continue
        
        return jsonify({
            "date": formatted_date,
            "sessions": sessions
        })
        
    except ValueError as e:
        print(f"Date parsing error: {str(e)}")
        return jsonify({"error": "Invalid date format"}), 400
    except Exception as e:
        print(f"Error in chat_summary: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health-report')
def health_report():
    return render_template('health_report.html')

@app.route('/logout')
def logout():
    return redirect(url_for('home'))

@app.route('/prevalent-emotion')
def prevalent_emotion():
    # Calculate prevalent emotion
    return jsonify({"emotion": "happy"})

@app.route('/weekly-transitions')
def weekly_transitions():
    try:
        if emotion_data.empty:
            return jsonify({"data": {}}), 200

        # Define emotion values
        emotion_values = {
            'angry': -1,
            'disgust': -1,
            'fear': -1,
            'sad': -1,
            'neutral': 0,
            'surprise': 1,
            'happy': 1
        }
        
        def get_prevalent_emotion(group):
            if group.empty:
                return 0
            try:
                last_scores = group.iloc[-1]['Scores']
                prevalent_emotion = max(last_scores.items(), key=lambda x: x[1])[0]
                return emotion_values.get(prevalent_emotion, 0)
            except Exception as e:
                print(f"Error in get_prevalent_emotion: {str(e)}")
                return 0
        
        # Group by week and get prevalent emotion
        weekly_data = emotion_data.groupby(pd.Grouper(key='Date', freq='W')).apply(get_prevalent_emotion)
        
        data_dict = {str(k.date()): int(v) for k, v in weekly_data.items() if pd.notnull(k)}
        
        print("Debug - weekly_data:", data_dict)
        return jsonify({"data": data_dict})
    except Exception as e:
        print(f"Error in weekly_transitions: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/monthly-transitions')
def monthly_transitions():
    try:
        if emotion_data.empty:
            return jsonify({"data": {}}), 200

        # Define emotion values
        emotion_values = {
            'angry': -1,
            'disgust': -1,
            'fear': -1,
            'sad': -1,
            'neutral': 0,
            'surprise': 1,
            'happy': 1
        }
        
        def get_prevalent_emotion(group):
            if group.empty:
                return 0
            try:
                last_scores = group.iloc[-1]['Scores']
                prevalent_emotion = max(last_scores.items(), key=lambda x: x[1])[0]
                return emotion_values.get(prevalent_emotion, 0)
            except Exception as e:
                print(f"Error in get_prevalent_emotion: {str(e)}")
                return 0
        
        # Group by month and get prevalent emotion
        monthly_data = emotion_data.groupby(pd.Grouper(key='Date', freq='M')).apply(get_prevalent_emotion)
        
        data_dict = {str(k.date()): int(v) for k, v in monthly_data.items() if pd.notnull(k)}
        
        print("Debug - monthly_data:", data_dict)
        return jsonify({"data": data_dict})
    except Exception as e:
        print(f"Error in monthly_transitions: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/daily-summary/<date>')
def daily_summary(date):
    try:
        # Read the emotion log
        df = pd.read_csv('emotion_log.txt', delimiter='|')
        
        # Convert the date strings to datetime
        df['Date'] = df['Date'].str.strip()
        
        # Filter for the specific date
        daily_data = df[df['Date'].str.contains(date)]
        
        if daily_data.empty:
            return jsonify({
                "date": date,
                "sessions": []
            })
        
        sessions = []
        for _, row in daily_data.iterrows():
            # Extract scores from the string
            scores_str = row['Scores'].strip()
            scores_dict = eval(scores_str)
            
            # Get the highest scoring emotion
            max_emotion = max(scores_dict.items(), key=lambda x: x[1])
            
            sessions.append({
                "time": row['Time'].strip(),
                "emotion": max_emotion[0],
                "score": round(max_emotion[1], 2)
            })
        
        return jsonify({
            "date": date,
            "sessions": sessions
        })
        
    except Exception as e:
        print(f"Error in daily_summary: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/session-history/<path:date_str>')
def session_history(date_str):
    try:
        # Parse the date string and handle potential format issues
        try:
            date_obj = datetime.strptime(date_str, '%m/%d/%Y')
            formatted_date = date_obj.strftime('%Y-%m-%d')
        except ValueError as e:
            print(f"Date parsing error: {str(e)}")
            return jsonify({"error": "Invalid date format"}), 400

        try:
            # Read the emotion log file
            with open('emotion_log.txt', 'r') as file:
                lines = file.readlines()
        except FileNotFoundError:
            return jsonify({
                "date": formatted_date,
                "sessions": [],
                "message": "No log file found"
            })

        sessions = []
        for line in lines:
            try:
                # Split the line by delimiter and clean whitespace
                parts = [part.strip() for part in line.split('|')]
                if len(parts) < 4:  # Skip invalid lines
                    continue

                line_date = parts[0].replace('Date:', '').strip()
                
                # Check if this line matches our target date
                if line_date == formatted_date:
                    time = parts[1].replace('Time:', '').strip()
                    scores_str = parts[-1].replace('Scores:', '').strip()
                    
                    # Safely evaluate the scores string
                    try:
                        scores_dict = ast.literal_eval(scores_str)
                    except:
                        continue
                    
                    # Get the highest scoring emotion
                    max_emotion = max(scores_dict.items(), key=lambda x: x[1])
                    
                    sessions.append({
                        "time": time,
                        "emotion": max_emotion[0],
                        "score": round(max_emotion[1], 2)
                    })
            except Exception as line_error:
                print(f"Error processing line: {line_error}")
                continue

        return jsonify({
            "date": formatted_date,
            "sessions": sessions
        })

    except Exception as e:
        print(f"Error in session_history: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/emotion-analysis/<path:date_str>')
def emotion_analysis(date_str):
    try:
        print(f"Received date string: {date_str}")
        
        # Handle URL-encoded date string
        date_str = date_str.replace('%2F', '/')
        
        # Try different date formats
        try:
            # Try MM/DD/YYYY
            date_obj = datetime.strptime(date_str, '%m/%d/%Y')
        except ValueError:
            try:
                # Try YYYY-MM-DD
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError as e:
                print(f"Date parsing error: {str(e)}")
                return jsonify({"error": "Invalid date format. Please use MM/DD/YYYY"}), 400
        
        # Format date for comparison - using a cross-platform compatible format
        formatted_date = f"{date_obj.month}/{date_obj.day}/{date_obj.year}"
        print(f"Formatted date for search: {formatted_date}")
        
        sessions = []
        try:
            with open('chat_history.txt', 'r', encoding='utf-8') as file:
                content = file.read()
                
                if not content.strip():
                    print("Empty chat history file")
                    return jsonify({
                        'date': formatted_date,
                        'sessions': []
                    })
                
                # Split content into blocks
                blocks = content.split('Timestamp: ')
                print(f"Found {len(blocks)} blocks in chat history")
                
                for block in blocks[1:]:  # Skip first empty block
                    try:
                        lines = block.strip().split('\n', 1)
                        if len(lines) < 2:
                            continue
                        
                        timestamp = lines[0].strip()
                        block_date = timestamp.split(',')[0].strip()
                        
                        print(f"Comparing dates - Block: {block_date}, Target: {formatted_date}")
                        
                        if block_date == formatted_date:
                            try:
                                # Extract time (HH:MM AM/PM)
                                time_part = timestamp.split(', ')[1]
                                time = ' '.join(time_part.split()[:2])
                                summary = lines[1].strip()
                                
                                if summary:
                                    sessions.append({
                                        'time': time,
                                        'summary': summary
                                    })
                                    print(f"Added session for {time}")
                            except Exception as e:
                                print(f"Error processing time/summary: {str(e)}")
                                continue
                    except Exception as e:
                        print(f"Error processing block: {str(e)}")
                        continue
                
                print(f"Successfully found {len(sessions)} sessions")
                return jsonify({
                    'date': formatted_date,
                    'sessions': sorted(sessions, key=lambda x: x['time'])
                })
                
        except FileNotFoundError:
            print("Chat history file not found")
            return jsonify({
                'date': formatted_date,
                'sessions': []
            })
        except Exception as e:
            print(f"Error reading chat history: {str(e)}")
            raise
            
    except Exception as e:
        print(f"Unexpected error in emotion_analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/emotion-analysis')
def show_emotion_analysis():
    return render_template('emotion_analysis.html')

def get_total_interactions():
    try:
        with open('chat_history.txt', 'r', encoding='utf-8') as file:
            content = file.read()
            # Count occurrences of the word 'Timestamp'
            total_count = content.count('Timestamp')
            return total_count
    except FileNotFoundError:
        print("Warning: chat_history.txt not found")
        return 0  # Return 0 if the file is not found
    except Exception as e:
        print(f"Error reading chat history: {str(e)}")
        return 0  # Return 0 in case of any other error

def calculate_positive_percentage():
    df = parse_emotion_log()
    if 'Scores' not in df.columns:
        print("Warning: 'Scores' column not found in DataFrame.")
        return 0.0  # Return 0.0 if the column is not found

    # Define positive emotions
    positive_emotions = ['happy', 'surprise', 'neutral']
    positive_count = 0

    # Count positive interactions based on the dominant emotion
    for index, row in df.iterrows():
        scores = row['Scores']
        if isinstance(scores, dict):  # Ensure scores is a dictionary
            # Determine the dominant emotion
            dominant_emotion = max(scores, key=scores.get)  # Get the emotion with the highest score
            if dominant_emotion in positive_emotions:  # Check if it's one of the positive emotions
                positive_count += 1

    total_count = len(df)
    percentage = (positive_count / total_count * 100) if total_count > 0 else 0
    return round(percentage, 2)  # Round to two decimal places

def get_recent_activities():
    try:
        with open('chat_history.txt', 'r', encoding='utf-8') as file:
            content = file.readlines()
            recent_activities = []
            for line in content[-5:]:  # Get the last 5 entries
                if line.strip():  # Skip empty lines
                    parts = line.split('Timestamp: ')
                    if len(parts) > 1:
                        timestamp = parts[1].strip()
                        summary = parts[0].strip()  # Assuming the summary is before the timestamp
                        recent_activities.append({
                            'time': timestamp,
                            'summary': summary
                        })
            return recent_activities
    except FileNotFoundError:
        print("Warning: chat_history.txt not found")
        return []  # Return an empty list if the file is not found
    except Exception as e:
        print(f"Error reading chat history: {str(e)}")
        return []  # Return an empty list in case of any other error

def calculate_active_days():
    try:
        with open('chat_history.txt', 'r', encoding='utf-8') as file:
            content = file.readlines()
            unique_dates = set()  # Use a set to store unique dates
            
            for line in content:
                if line.strip():  # Skip empty lines
                    # Assuming the date is in a specific format, e.g., "Timestamp: YYYY-MM-DD"
                    parts = line.split('Timestamp: ')
                    if len(parts) > 1:
                        date_str = parts[1].strip().split()[0]  # Extract the date part
                        unique_dates.add(date_str)  # Add the date to the set
            
            return len(unique_dates)  # Return the count of unique dates
    except FileNotFoundError:
        print("Warning: chat_history.txt not found")
        return 0  # Return 0 if the file is not found
    except Exception as e:
        print(f"Error reading chat history: {str(e)}")
        return 0  # Return 0 in case of any other error

if __name__ == '__main__':
    app.run(debug=True)
