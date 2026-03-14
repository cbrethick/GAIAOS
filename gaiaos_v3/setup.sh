#!/bin/bash
echo "======================================"
echo "  GaiaOS — Real Data Edition"
echo "  Mac Setup"
echo "======================================"
python3 -m venv gaiaos_env
source gaiaos_env/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
[ ! -f .env ] && cp .env.template .env && echo ".env created"
echo ""
echo "Setup complete! Now:"
echo "  1. Add your free NASA FIRMS key to .env"
echo "  2. Run:  source gaiaos_env/bin/activate"
echo "  3. Run:  streamlit run app.py"
