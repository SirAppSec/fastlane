# Fast Lane Price Tracker
store prices of the fastLane and perform analysis to determine the optimal time to leave the house

# Install
```
python -m venv venv
pip install requests beautifulsoup4 flask matplotlib schedule pandas

source myenv/bin/activate

```
# Run
```
python main.py
```
And browse to http://127.0.0.1:5000/ 
# Dev
setup githook for pre-push
```
chmod +x scripts/pre-push

ln -s ../../scripts/pre-push .git/hooks/pre-push
```
# Docker
run and build
```
docker build -t fastlane-scraper .
docker run -p 5000:5000 fastlane-scraper
```
