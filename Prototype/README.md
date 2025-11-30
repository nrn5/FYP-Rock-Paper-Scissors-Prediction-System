## Overview:
This is a prototype for an interactive RPS game that demonstrates the system architecture and game flow. The prototype currently uses keyboard input for player moves and a random move generator for for the computer.

The prototype is designed to test the core system components, prepare for full gesture integration, and provide a foundation for future UI improvements and AI modules.

## Requirements:
- Python 3.8+
- Libraries:
    - tkinter (for UI)
    - opencv (camera feed)
    - mediapipe (for gesture recognition)
    - pillow (for displaying frames in Tkinter)
    - psycopg2 (PostgreSQL database connection)
    - numpy (image/frame processing)
- a working webcam
- PostgreSQL database (basic connection tested - full persistence not yet implemented)

## Code Explanations:
### Presentation:
- Built using Tkinter
- Displays live camera feed, instructions, and round results
- extra window for win/loss/draw graph
- currently uses keyboard input instead of gestures
- handles frame updates from opencv and visualises hand landmarks using mediapipe

### Business:
- responsible for game logic and AI integration
- AI module currently generates random moves
- provides functions to determine winner of each round and amintain local statistics
- designed to later integrate predicitve AI (Markov and LSTM models) and use persistent gameplay history

### Persistence:
- PostgreSQL connection implemented
- repository for communication with database created and ready to be integrated into a business mapper

