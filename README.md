# indeed_job_applier

### Environment Set up (Only need to do once)

1. Download Python if not installed. Check with:

```code
python3 --version
```

2. Start up venv in the folder

```code
python3 -m venv venv
```

3. Source it

```code
source venv/bin/activate
```

4. Install Requirements

```code
pip install -r requirements.txt
```

### Running script, need to do both steps whenever you decide to restart script
1. Start up chrome in debug mode on port 1559.

Mac:

```code
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=1559 --user-data-dir=/tmp/chrome-debug
```

PC:

```code
C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=1559 --user-data-dir="C:\temp\chrome_debug_profile
```

2. Run this command:

```code
python3 chrome_box.py
```
