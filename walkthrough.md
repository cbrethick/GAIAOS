# Deploying GaiaOS to Vercel

GaiaOS is now ready for deployment to Vercel using a serverless-native architecture. This ensures that the Python AI prediction engine runs reliably in the cloud.

## Deployment Steps

1.  **Push to GitHub**:
    Ensure all your latest changes are pushed to your repository:
    ```bash
    git add .
    git commit -m "Configure Vercel serverless architecture"
    git push origin main
    ```

2.  **Connect to Vercel**:
    - Go to [vercel.com](https://vercel.com) and import your `GAIAOS_A1` repository.
    - Vercel will automatically detect the Vite frontend and Python API.

3.  **Configure Environment Variables**:
    In the Vercel Dashboard, go to **Settings > Environment Variables** and add the following keys from your [.env](file:///Users/rethickcb/Desktop/OS/.env) file:
    - `NASA_FIRMS_KEY`
    - `OPEN_METEO_BASE`
    - `OPEN_METEO_HIST`
    - `OPEN_METEO_FLOOD`
    - `OPEN_METEO_AQ`
    - `NOMINATIM_BASE`
    - `OVERPASS_BASE`
    - `NASA_POWER_BASE`

4.  **Deploy**:
    Click **Deploy**. Vercel will build the frontend and provision the serverless Python functions.

## Local Testing with Vercel CLI

If you want to test the serverless functions on your machine before pushing:
1.  Install Vercel CLI: `npm i -g vercel`
2.  Run: `vercel dev`
3.  Navigate to `http://localhost:3000/dashboard`

## Architecture Note
The project now uses a unified [api/predict.py](file:///Users/rethickcb/Desktop/OS/api/predict.py) endpoint. This replaces the old `localhost:4000` Express server in production, providing a more robust and scalable way to run Earth Intelligence AI.
