const express = require('express');
const multer = require('multer');
const cors = require('cors');

const app = express();
const PORT = 3001;

app.use(cors());
app.use(express.json());

const storage = multer.memoryStorage();
const upload = multer({ storage });

// Karar verdiğimiz, şu an dünyadaki en iyi modellerden biri olan TRELLIS
const TRELLIS_SPACE = "trellis-community/TRELLIS"; 

app.post('/api/forge', upload.single('image'), async (req, res) => {
  try {
    const { Client } = await import('@gradio/client');
    
    console.log("🚀 Görsel işleniyor, TRELLIS motoru ateşlendi...");
    
    // Gradio bağlantısı kuruluyor
    const client = await Client.connect(TRELLIS_SPACE);
    
    // Görseli Blob'a çevirip gönderiyoruz (Gradio client için gerekli)
    const imageBlob = new Blob([req.file.buffer], { type: req.file.mimetype });
    
    // TRELLIS parametreleri: Görsel, Seed, S3D Mode, Post-process
    const result = await client.predict("/process", [
      imageBlob,
      Math.floor(Math.random() * 100000), // Her seferinde farklı sonuç için random seed
      "Standard", 
      "Standard"
    ]);

    if (result && result.data) {
        // Gelen .glb dosyasının linkini alıyoruz
        const glbUrl = result.data[0].url;

        console.log("✅ Model hazır! .glb üretildi.");

        // Frontend'e başarılı cevabı dönüyoruz
        res.json({ 
            status: 'success', 
            modelUrl: glbUrl,
            format: 'glb',
            note: "Model hazır kanka! 3D yazıcın (Ender 3 V3) için Slicer'da .3mf olarak kaydedebilirsin."
        });
    } else {
        throw new Error("Motor cevap vermedi.");
    }

  } catch (error) {
    console.error("❌ Hata oluştu:", error);
    res.status(500).json({ error: "Motor şu an meşgul veya sıra var kanka, tekrar dene!" });
  }
});

app.listen(PORT, () => {
  console.log(`🔥 Atlas AI Backend Çalışıyor: http://localhost:${PORT}`);
});
