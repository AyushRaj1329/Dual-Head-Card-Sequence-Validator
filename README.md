# Card Sequence Validator

The Card Sequence Validator is a desktop application designed to validate sequences of cards. It provides a user-friendly interface for managing card sequence files, configuring serial communication ports for scanner input and output, and monitoring validation processes in real-time.

## Features

*   **Intuitive User Interface:** Built with PyQt6, offering a clean and responsive design.
*   **Card Sequence File Management:** Supports loading and parsing card sequence data from `.cpd`, `.txt`, and `.csv` file formats.
*   **COM Port Configuration:** Easily set up and manage input and output serial ports for communication with external devices (e.g., card scanners).
*   **Real-time Scanning & Logging:** Monitor live scanner input and view validation logs directly within the application. Validation results ("OK", "NOT OK") trigger corresponding output signals to the configured COM port. When cards are skipped (user-approved jump), they are logged, but no output signal is sent.
*   **Theming:** Switch between dark and light themes for a personalized experience.

## Installation

To set up and run the Card Sequence Validator, follow these steps:

1.  **Obtain the source code:**
    If you received the source code as a ZIP file or similar archive, extract it to your desired location. Navigate into the extracted `card_Seq_valv3` directory.

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    ```

3.  **Activate the virtual environment:**
    *   **Windows:**
        ```bash
        .venv\Scripts\activate
        ```
    *   **macOS/Linux:**
        ```bash
        source .venv/bin/activate
        ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To start the application, activate your virtual environment and run the `main.py` file:

```bash
.venv\Scripts\activate # On Windows
# source .venv/bin/activate # On macOS/Linux
python main.py
```

Once the application launches, you can:
*   Configure COM ports for your scanner and output devices.
*   Load card sequence files (`.cpd`, `.txt`, `.csv`).
*   Start scanning and observe the validation results.

## Project Structure

```
card_Seq_valv3/
├───main.py                 # Main application entry point
├───requirements.txt        # Project dependencies
├───constants.py            # Application-wide constants
├───output_formats.json     # Defines output data formats
├───assets/                 # Application assets (icons, images)
│   ├───favicon.ico
│   ├───gear_loader.gif
│   ├───Icon.png
│   └───logo.png
└───src/
    ├───app_state.py        # Manages application state and settings
    ├───logic/
    │   ├───file_parser.py  # Handles parsing of different card sequence file types
    │   └───...
    ├───services/
    │   ├───com_writer.py   # Manages serial communication
    │   ├───utilities.py    # Utility functions (e.g., file parsing helpers)
    │   └───...
    └───ui/
        ├───main_application.py # Main window and UI logic
        ├───com_port_setup.py   # COM port configuration UI
        ├───file_management.py  # File management UI
        ├───scanner_logging.py  # Scanner logging UI
        ├───styles.py           # Application stylesheets
        ├───widgets.py          # Custom UI widgets
        └───...
```
