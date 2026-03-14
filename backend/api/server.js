import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.join(__dirname, '../../.env') });

const app = express();
const PORT = process.env.PORT || 4000;

app.use(cors());
app.use(express.json());

import { spawn } from 'child_process';

// Helper to run Python bridge
const runPythonModule = (module, lat, lon, location = '', extra = '') => {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python3', [
      path.join(__dirname, '../bridge.py'),
      module,
      lat,
      lon,
      location,
      extra
    ]);

    let dataString = '';
    pythonProcess.stdout.on('data', (data) => {
      dataString += data.toString();
    });

    let errorString = '';
    pythonProcess.stderr.on('data', (data) => {
      errorString += data.toString();
      console.error(`Python Error: ${data}`);
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Python process exited with code ${code}. Stderr: ${errorString}`));
        return;
      }
      try {
        // Find the JSON block in the output (in case of warnings)
        const jsonStart = dataString.indexOf('{');
        const jsonEnd = dataString.lastIndexOf('}');
        if (jsonStart === -1 || jsonEnd === -1) {
          throw new Error("No JSON object found in output");
        }
        const jsonContent = dataString.substring(jsonStart, jsonEnd + 1);
        resolve(JSON.parse(jsonContent));
      } catch (e) {
        reject(new Error(`Failed to parse Python output: ${dataString}. Error: ${e.message}`));
      }
    });
  });
};

// API Endpoints
app.get('/api/predict', async (req, res) => {
  const { module, lat, lon, location, extra } = req.query;
  
  if (!module || !lat || !lon) {
    return res.status(400).json({ error: 'Missing parameters (module, lat, lon required)' });
  }

  try {
    const result = await runPythonModule(module, lat, lon, location || '', extra || '');
    res.json(result);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to generate prediction', details: err.message });
  }
});

app.get('/api/search', async (req, res) => {
  const { q } = req.query;
  if (!q) return res.status(400).json({ error: 'Query parameter "q" is required' });

  try {
    const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q + ', India')}&limit=1&addressdetails=1`, {
      headers: {
        'User-Agent': 'GaiaOS-Dashboard'
      }
    });
    const data = await response.json();
    res.json(data);
  } catch (err) {
    console.error("Geocoding proxy error:", err);
    res.status(500).json({ error: 'Failed to fetch location data' });
  }
});

app.get('/api/status', async (req, res) => {
  try {
    const statusResult = await runPythonModule('status', 0, 0); // Need to handle status in bridge.py or just return online
    res.json({ status: 'GaiaOS Prediction Engine Online', bridge: 'Active' });
  } catch (err) {
    res.json({ status: 'GaiaOS Online', bridge: 'Offline/Wait' });
  }
});

app.listen(PORT, () => {
  console.log(`GaiaOS Prediction Engine running on port ${PORT}`);
});
