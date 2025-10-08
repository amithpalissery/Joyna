import express from 'express';
import { fileURLToPath } from 'url';
import path from 'path';
import { chatWithModel, generateParentSuggestions, appendToHistoryFile } from './chatbot.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const port = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static('public'));

// Chat endpoint
app.post('/chat', async (req, res) => {
    try {
        const userInput = req.body.message;
        const response = await chatWithModel(userInput);
        res.json({ response });
    } catch (error) {
        console.error('Error processing chat:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Parent suggestions endpoint
app.get('/parent-suggestions', async (req, res) => {
    try {
        const suggestions = await generateParentSuggestions();
        res.json({ suggestions });
    } catch (error) {
        console.error('Error generating suggestions:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Append chat history endpoint
app.post('/append-history', async (req, res) => {
    try {
        await appendToHistoryFile();
        res.json({ success: true });
    } catch (error) {
        console.error('Error appending history:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});