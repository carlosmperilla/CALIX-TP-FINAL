# CALIX-TP-FINAL
## Como desplegar el TP en local
```sh
git clone https://github.com/carlosmperilla/CALIX-TP-FINAL.git
cd CALIX-TP-FINAL
python -m venv calix_venv
calix_venv\Scripts\activate
pip install -r requirements.txt
```
### Iniciar API
```sh
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Iniciar BOT
```sh
python init_bot.py
```
