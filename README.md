Here’s a more detailed README setup to guide your friends through the installation, setup, and playing process:

---

# Blackjack Game Setup and Installation

This document provides instructions on how to set up and play the Blackjack game.

## Prerequisites
Before you begin, make sure you have the following installed on your system:

- **Python** (version 3.6 or higher)
- **Git** (optional for cloning the repository)

If you do not have Python installed, you can download it from the official site: [Python Downloads](https://www.python.org/downloads/).

---

## 1. **Installation and Setup**

### For Windows Users:

1. **Clone the repository or download the project files** to your desired directory.
2. **Navigate to the project folder**:
   - Open Command Prompt (CMD) and run the following command:
     ```sh
     cd path\to\your\project
     ```

3. **Set up a virtual environment**:
   - Run the following command to create a virtual environment:
     ```sh
     py -m venv .venv
     ```

4. **Activate the virtual environment**:
   - Run this command to activate the virtual environment:
     ```sh
     .venv\Scripts\activate
     ```

   If `py` doesn't work, try using `python` or `python3` instead.

5. **Install dependencies**:
   - Once the virtual environment is activated, install the required dependencies by running:
     ```sh
     pip install -r requirements.txt
     ```

---

### For Mac Users:

1. **Clone the repository or download the project files** to your desired directory.
2. **Navigate to the project folder**:
   - Open Terminal and run the following command:
     ```sh
     cd /path/to/your/project
     ```

3. **Set up a virtual environment**:
   - Run the following command to create a virtual environment:
     ```sh
     py -m venv .venv
     ```

4. **Activate the virtual environment**:
   - Run this command to activate the virtual environment:
     ```sh
     source .venv/bin/activate
     ```

5. **Install dependencies**:
   - Once the virtual environment is activated, install the required dependencies by running:
     ```sh
     pip install -r requirements.txt
     ```

---

## 2. **Playing the Game**

### Running the Game

1. After completing the setup, **run the game** by executing the `VisualBoard.py` script:
   - For Windows or Mac, simply run:
     ```sh
     python VisualBoard.py
     ```

### Game Controls

Once the game is running, you can interact with it using the following keybindings:

- **Q**: Leave the game
- **Spacebar**: Hit (draw a card)
- **S**: Stand (end your turn)
- **D**: Double (double your bet and draw one more card)
- **R**: Ready (ready to start a new game)
- **E**: Start or End the game (depending on the state)

---

## 3. **Additional Notes**

- **Virtual Environment**: It is recommended to use the virtual environment to avoid conflicts with system-wide Python packages.
- **Dependencies**: All dependencies required to run the game are listed in `requirements.txt`. This file is automatically created by running `pip freeze > requirements.txt` after installing all necessary packages.

---

If you encounter any issues or need help, feel free to reach out!

---

Let me know if you need anything else for your README!