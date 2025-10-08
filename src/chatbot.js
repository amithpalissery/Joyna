import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';
import { GoogleGenerativeAI } from '@google/generative-ai';

dotenv.config();

const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

let conversationHistory = [];

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const historyFilePath = path.join(__dirname, '..', 'chat_history.txt');

// Text-to-Speech function with Promise (unchanged)
function speak(text) {
    return new Promise((resolve, reject) => {
        const synth = window.speechSynthesis;
        if (!synth) {
            console.error("Speech Synthesis API is not supported in this browser.");
            resolve();
            return;
        }

        const utterance = new SpeechSynthesisUtterance(text);

        utterance.onend = () => {
            resolve();
        };

        utterance.onerror = (event) => {
            reject(event);
        };

        synth.speak(utterance);
    });
}

// Speak in chunks (sentences) with reduced lag (MODIFIED)
function speakInChunks(text) {
    return new Promise((resolve, reject) => {
        const chunks = text.split(/(?<=[.?!])\s+/);
        if (!chunks.length) {
            resolve();
            return;
        }

        const synth = window.speechSynthesis;
        if (!synth) {
            console.error("Speech Synthesis API is not supported in this browser.");
            resolve();
            return;
        }

        window.speechSynthesis.cancel(); // Stop any current speech

        let chunkIndex = 0;

        function speakNextChunk() {
            if (chunkIndex >= chunks.length) {
                resolve();
                return;
            }

            const utterance = new SpeechSynthesisUtterance(chunks[chunkIndex]);
            utterance.lang = 'en-US'; // Still important

            utterance.onend = () => {
                chunkIndex++;
                speakNextChunk(); // Recursively call the next chunk
            };

            utterance.onerror = (event) => {
                reject(event);
            };

            synth.speak(utterance);
        }

        speakNextChunk(); // Start the process
    });
}

export async function chatWithModel(userInput) {
    try {
        const initialContext = {
            role: "user",
            parts: [{
                text: "You are Joyna, a friendly robot companion for children. You should respond in a warm, age-appropriate way that a child can understand. Keep responses simple, encouraging, and positive. Always maintain a safe, supportive tone. Never share inappropriate content or complex topics. If you're unsure about a topic, redirect to something fun and appropriate."
            }]
        };

        const chat = model.startChat({
            history: [initialContext,
            {
                role: "model",
                parts: [{ text: "Hi! I'm Joyna, your robot friend! I'm here to chat, play, and have fun with you. What would you like to talk about?" }]
            },
                ...conversationHistory.flatMap(entry => [
                    { role: "user", parts: [{ text: entry.userInput }] },
                    { role: "model", parts: [{ text: entry.response }] }
                ])
            ]
        });

        const response = await chat.sendMessage(userInput);
        const responseText = response.response.text();
        conversationHistory.push({ userInput, response: responseText });

        return responseText;
    } catch (error) {
        console.error('Chat error:', error);
        return "I'm sorry, I had trouble processing that. Could you try saying that again?";
    }
}

export async function generateParentSuggestions() {
    const chat = model.startChat({
        history: [{
            role: "user",
            parts: [{ text: "Based on the conversation history,  suggestions for parents about topics or activities they could discuss with their child to build on this interaction.Give as one or two sentence" }]
        }]
    });

    const response = await chat.sendMessage(JSON.stringify(conversationHistory));
    return response.response.text();
}

export async function getChatSummary() {
    const chat = model.startChat({
        history: [{
            role: "user",
            parts: [{ text: "Based on the conversation history, provide a brief summary of the interaction, including topics discussed, the child's engagement level, and how the conversation progressed. Format as a single paragraph." }]
        }]
    });

    const response = await chat.sendMessage(JSON.stringify(conversationHistory));
    return response.response.text();
}

export async function appendToHistoryFile() {
    try {
        // Get current timestamp
        const timestamp = new Date().toLocaleString('en-US', {
            year: 'numeric',
            month: 'numeric',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            second: '2-digit',
            hour12: true
        });

        // Get summary from the chat summary function
        const summary = await getChatSummary();
        
        // Format the entry with timestamp and summary
        const entryText = `Timestamp: ${timestamp}\n${summary}\n\n`;
        
        // Create the directory if it doesn't exist
        const dir = path.dirname(historyFilePath);
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }
        
        // Append to file
        fs.appendFileSync(historyFilePath, entryText);
        console.log('Successfully wrote to chat history file');
    } catch (error) {
        console.error('Error writing to history file:', error);
        throw error; // Re-throw the error so we can handle it in the calling function
    }
}

function generateConversationSummary(history) {
    // Analyze key aspects of the conversation
    const topics = new Set();
    const activities = new Set();
    let moodIndicators = [];
    let engagementLevel = 'engaged';

    history.forEach(entry => {
        const text = (entry.userInput + ' ' + entry.response).toLowerCase();
        
        // Extract topics
        if (text.includes('school')) topics.add('school');
        if (text.includes('math')) topics.add('mathematics');
        if (text.includes('england')) topics.add('England');
        if (text.includes('cricket')) topics.add('cricket');
        if (text.includes('badminton')) topics.add('badminton');
        if (text.includes('geography')) topics.add('geography');
        
        // Track activities
        if (text.includes('i spy')) activities.add('I Spy');
        if (text.includes('playing')) {
            const playingMatch = text.match(/playing (\w+)/);
            if (playingMatch) activities.add(playingMatch[1]);
        }
        
        // Analyze mood and engagement
        if (text.includes('excited') || text.includes('love') || text.includes('fun')) {
            moodIndicators.push('enthusiastic');
        }
        if (text.includes('boring') || text.includes('tired') || text.includes('don\'t want')) {
            moodIndicators.push('disengaged');
            engagementLevel = 'waning';
        }
    });

    // Construct narrative summary
    let summary = '';
    
    // Initial engagement
    summary += 'The child';
    if (moodIndicators.includes('enthusiastic')) {
        summary += ', initially excited';
    }
    
    // Topics
    const topicsArray = Array.from(topics);
    if (topicsArray.length > 0) {
        summary += `, discussed ${topicsArray.join(', ')}`;
    }
    
    // Activities
    const activitiesArray = Array.from(activities);
    if (activitiesArray.length > 0) {
        summary += `. Activities included ${activitiesArray.join(', ')}`;
    }
    
    // Engagement progression
    if (engagementLevel === 'waning') {
        summary += `. The child's enthusiasm appeared to decrease as the conversation progressed`;
    }
    
    summary += '.';
    
    return summary.replace(/,\s*\./, '.');
}

// Speech recognition logic
export async function startSpeechRecognition(recognition, handleInputCallback) {
    let isListening = true;

    recognition.continuous = true;
    recognition.interimResults = false;

    recognition.onresult = (event) => {
        if (!isListening) return;

        let fullInput = '';
        for (let i = 0; i < event.results.length; i++) {
            if (event.results[i].isFinal) {
                fullInput += event.results[i][0].transcript.trim() + ' ';
            }
        }

        if (fullInput.trim()) {
            recognition.stop();
            handleInputCallback(fullInput.trim());
        }
    };

    recognition.onend = () => {
        if (isListening) {
            recognition.start();
        }
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        if (isListening) {
            setTimeout(() => recognition.start(), 1000);
        }
    };

    recognition.start();

    // Add timeout handling
    const timeout = setTimeout(() => {
        if (isListening) {
            recognition.stop();
            recognition.start();
        }
    }, 30000); // Reset every 30 seconds

    return () => {
        isListening = false;
        recognition.stop();
    };
}

// Main interaction function (MODIFIED to use the new speakInChunks)
export async function handleUserInteraction(userInput, recognition, handleInputCallback) {
    const responseText = await chatWithModel(userInput);
    try {
        await speakInChunks(responseText);
    } catch (error) {
        console.error("TTS Error:", error);
    }
    startSpeechRecognition(recognition, handleInputCallback);
}

function trimHistory(maxEntries = 50) {
    if (conversationHistory.length > maxEntries) {
        conversationHistory = conversationHistory.slice(-maxEntries);
    }
}


export default { chatWithModel, generateParentSuggestions, appendToHistoryFile, startSpeechRecognition, handleUserInteraction };