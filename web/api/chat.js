export default async function handler(req, res) {
    // 1. Only allow POST requests
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        // 2. Get the user's message from the frontend
        const { messages, model } = req.body;

        // 3. Send the request to OpenRouter using your hidden SECRETS
        const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                // process.env.OPENROUTER_API_KEY pulls your secret key securely from Vercel
                "Authorization": `Bearer ${process.env.OPENROUTER_API_KEY}`, 
                "HTTP-Referer": "https://day-companion.vercel.app",
                "X-Title": "A DAY COMPANION"
            },
            body: JSON.stringify({
                model: model,
                messages: messages,
                temperature: 0.7,
                max_tokens: 2000
            })
        });

        const data = await response.json();
        
        // 4. Send the AI's response back to your frontend
        return res.status(200).json(data);

    } catch (error) {
        console.error("Backend Error:", error);
        return res.status(500).json({ error: "Something went wrong on the server." });
    }
}