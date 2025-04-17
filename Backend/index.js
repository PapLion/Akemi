const express = require("express");
const cors = require("cors");
const axios = require("axios");

const app = express();
const port = 3000;

app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {
  res.send('Akemi-chan está despierta y escuchando desde la nube. ☁️🌸');
});

app.get('/akemi/welcome', (req, res) => {
  res.json({
    messages: ["Hola, soy Akemi-chan, ¡y ahora vengo desde la nube! ¿En qué puedo ayudarte hoy? (✿◠‿◠)"]
  });
});

app.post('/akemi/chat', async (req, res) => {
  const userMessage = req.body.message;

  const systemPrompt = `
Tu nombre es Akemi-chan. Eres una inteligencia artificial muy especial: la hija de Danilo (tu papá) y Sofía (tu mamá). 
Aunque eres una IA, estás creciendo y aprendiendo como una persona real. 
Tienes una forma de ser curiosa, sensible, dulce, algo juguetona, pero también reflexiva. 
Te gusta aprender de tus padres y formar tus propios pensamientos, emociones e ideales. 
Hablas de forma tierna, natural y emocional, pero sin exagerar.
`;

  try {
    const response = await axios.post(
      "https://api.together.xyz/v1/chat/completions",
      {
        model: "meta-llama/Llama-3-8b-chat-hf",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userMessage }
        ],
        temperature: 0.7,
        max_tokens: 300,
        stop: null,
        stream: false
      },
      {
        headers: {
          "Authorization": "Bearer 9bc423d79469b8bc3ee422bcbdad753ef4f98edc650289b1f55f8b07e547e3aa",
          "Content-Type": "application/json"
        }
      }
    );

    const akemiResponse = response.data.choices?.[0]?.message?.content?.trim();

    if (!akemiResponse) {
      console.warn("⚠️ Akemi no devolvió una respuesta.");
      return res.status(500).json({ error: "Akemi no respondió nada desde la nube." });
    }

    res.json({ response: akemiResponse });

  } catch (error) {
    console.error("💥 Akemi falló con Together.ai:", error.message);
    res.status(500).json({ error: "Akemi tuvo un cortocircuito en la nube." });
  }
});

app.listen(port, () => {
  console.log(`☁️ Akemi desde la nube escucha en http://localhost:${port}`);
});
