const express = require('express');
const multer = require('multer');
const cors = require('cors');
const fetch = require('node-fetch');

const app = express();
const PORT = 3001;

app.use(cors());
app.use(express.json());

const storage = multer.memoryStorage();
const upload = multer({ storage });

// Burası çok önemli: TripoSR motoruna doğrudan bağlantı
const TRIPOSR_SPACE = 'stabilityai/TripoSR';

app.post('/api/forge', upload.single('image'), async (req, res) => {
  try {
    const { Client } = await import('@gradio/client');
    
    // Gradio bağlantısını kuruyoruz
    const client = await Client.connect(TRIPOSR_SPACE);
    
    // Fotoğrafı gönderiyoruz
    const result = await client.predict("/process", [
      req.file.buffer // Görsel verisi
    ]);

    // Eğer veri geldiyse frontend'e gönder
    if (result && result.data) {
        res.json({ 
            status: 'success', 
            modelUrl: result.data[0].url 
        });
    } else {
        throw new Error("AI motoru boş cevap döndü.");
    }

  } catch (error) {
    console.error("Hata:", error);
    res.status(500).json({ error: "AI motoru şu an meşgul, lütfen tekrar dene kanka!" });
  }
});

app.listen(PORT, () => {
  console.log(`✅ Backend Sunucusu http://localhost:${PORT} üzerinde hazır!`);
});