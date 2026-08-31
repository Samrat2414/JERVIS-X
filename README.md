# JERVIS X

[![Automated Tests](https://github.com/Samrat2414/JERVIS-X/actions/workflows/tests.yml/badge.svg)](https://github.com/Samrat2414/JERVIS-X/actions/workflows/tests.yml)


JERVIS X is a modular Python personal AI assistant that combines voice interaction, desktop utilities, engineering calculations, system monitoring, and end-to-end job application intelligence.

The project is designed as a practical portfolio application for Python development, automation, data handling, and AI-assisted workflows.

## Project Status

Active development. The core assistant, calculator, ECE engineering tools, animated desktop GUI, voice interaction, system monitoring, and Job Application Intelligence module are functional.

## Key Features

### Personal AI Assistant

- Text and voice command processing
- Context-aware conversation handling
- AI fallback for general questions
- Date, time, greetings, and everyday assistant commands
- Modular command routing

### Calculator and ECE Tools

- Arithmetic and scientific calculations
- Square root, trigonometry, logarithms, factorial, and powers
- Ohm's law calculations
- Electrical power calculations
- Frequency from time period
- Series and parallel resistance

### Desktop Experience

- Animated CustomTkinter dashboard
- Voice input with SpeechRecognition and PyAudio
- Text-to-speech responses with pyttsx3
- Live system and performance information
- Windows-focused automation architecture

### Job Application Intelligence

- Add, view, search, filter, sort, and delete applications
- Track status, priority, notes, and status history
- Schedule follow-ups with due and overdue reminders
- Schedule interviews with date, time, and mode
- Track interview preparation topics and progress
- Save interview results and recruiter feedback
- Track offers, annual CTC, location, and joining date
- Accept, decline, or negotiate offers
- Track joining and onboarding checklists
- Track 30-day career growth goals
- Export applications to CSV
- Create and restore JSON backups
- Generate statistics, recommendations, and best-next-action reports
- Display all tracker commands through a built-in help center

## Example Commands

```text
calculate 25 * 48
power voltage 12 current 2
parallel resistance 10 20

add job application Example Company | Python Developer
update application status 1 | Under Review
set application priority 1 | High
set application follow up date 1 | 05-09-2026
schedule application interview 1 | 05-09-2026 | 11:00 AM | Online
job application report
job application commands
```

## Job Application Workflow

```text
Applied
  -> Under Review
  -> Shortlisted
  -> Interview
  -> Offer
  -> Joined
  -> Onboarding
  -> Career Growth
```

## Project Structure

```text
JERVIS-X/
|-- main.py
|-- requirements.txt
|-- README.md
|-- core/
|   |-- brain.py
|   |-- router.py
|   |-- calculator.py
|   |-- engineering.py
|   `-- job_application_intelligence.py
|-- gui/
|   `-- app.py
|-- data/
|   `-- job_applications.json
|-- exports/
`-- backups/
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Samrat2414/JERVIS-X.git
cd JERVIS-X
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run JERVIS X

Command-line mode:

```powershell
python main.py
```

Animated GUI:

```powershell
python gui\app.py
```

Type `exit` to close the command-line assistant.

## Data and Exports

- Application data is stored locally in `data/job_applications.json`.
- CSV exports are written to `exports/job_applications.csv`.
- Application backups are written to the `backups/` directory.
- Generated data and backups may contain personal information and should not be committed publicly.

## Technology Stack

- Python
- CustomTkinter and Tkinter
- SpeechRecognition and PyAudio
- pyttsx3
- psutil
- JSON and CSV
- Git and GitHub

## Roadmap

- Wake-word activation: "Hey JERVIS"
- Expanded PC automation
- Smart file management
- Document intelligence
- Computer vision
- Coding assistant
- Plugin architecture
- Stronger permissions and security controls
- Automated tests and continuous integration

## Author

Sahariyar Chowdhury  
GitHub: [Samrat2414](https://github.com/Samrat2414)

## Disclaimer

JERVIS X is a personal learning and portfolio project. Review commands before allowing the assistant to perform file, system, or network operations.

## Windows Download

Download the latest ready-to-run Windows version:

[Download the Latest Windows Release](https://github.com/Samrat2414/JERVIS-X/releases/latest)

1. Download `JERVIS-X-Windows.zip`.
2. Extract the ZIP file.
3. Double-click `JERVIS-X.exe`.

### Verify the Windows Download

Run:

```powershell
Get-FileHash .\JERVIS-X-Windows.zip -Algorithm SHA256
```

Download `JERVIS-X-Windows.zip.sha256` from the same release and confirm that both hashes match.

## Command-Line Options
Run system diagnostics:

```powershell
python main.py --diagnostics

Launch the JERVIS-X GUI:

```powershell
python main.py
```

Show command-line help:

```powershell
python main.py --help
```

Show the installed version:

```powershell
python main.py --version
```

Unknown options return a clear error message and exit code `2`.
