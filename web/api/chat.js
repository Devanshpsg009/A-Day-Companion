export default async function handler(req, res) {
    
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        
        const { messages, model } = req.body;

        
        const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                
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
        
        return res.status(200).json(data);

    } catch (error) {
        console.error("Backend Error:", error);
        return res.status(500).json({ error: "Something went wrong on the server." });
    }
}