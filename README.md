# indeed_job_applier

## Environment setup (one-time)

Install Python if not already present.

- macOS / Linux:

```bash
python3 --version
```

- Windows (Command Prompt / PowerShell):

```powershell
python --version
```

Create and activate a virtual environment:

- macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

- Windows (PowerShell):

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

- Windows (cmd):

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

Install project dependencies:

```bash
pip install -r requirements.txt
```

## Running the script

Every time you run the automation you'll need to start Chrome with remote debugging enabled, then run the Python script. The remote debugging port in the command below must match the address used by `start_chrome()` (default: `127.0.0.1:1559`).

- macOS (example):

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=1559 --user-data-dir=/tmp/chrome-debug
```

- Windows (PowerShell example):

```powershell
& 'C:\Program Files\Google\Chrome\Application\chrome.exe' --remote-debugging-port=1559 --user-data-dir='C:\temp\chrome_debug_profile'
```

- Windows (cmd example):

```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=1559 --user-data-dir="C:\temp\chrome_debug_profile"
```

Notes:
- Use a separate `--user-data-dir` to avoid interfering with your primary Chrome profile.
- If Chrome is already running, close it first or use a distinct `user-data-dir` path to avoid a profile-in-use error.

Run the script (use `python` or `python3` depending on your environment):

```bash
python3 chrome_box.py
```

On Windows you may need to run `python chrome_box.py` instead of `python3`.

