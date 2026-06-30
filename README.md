# freestyle-debugging-assistant(in short)
The app name is "debugr". Its to fix the problem in your code and if the code is working great then it flag it as PASS and gives its output and if the code is wrong then it flag as FAULT and explain you the problem. It also show your history to track your work easily.
# Project Theory
Your project is a desktop debugging assistant called debugr. It is built with Python and Tkinter. The app starts with an animated video index screen, then opens a main debugging workspace after the user clicks LET'S DEBUG.
The idea is simple: the user writes or pastes code, chooses a programming language, runs the code, and the app shows the output or error. If the code fails, the app can send the code and error message to an AI model, like Gemini, to explain what went wrong and suggest a fix.
Main Flow
The app opens with a splash/index page.
A background video plays behind the LET'S DEBUG button.
When the button is clicked, the video page closes.
The main debugger workspace opens.
The user chooses a language such as Python, JavaScript, Java, or C++.
The user writes code in the editor.
The app executes the code using the local compiler/runtime.
Output, errors, and AI analysis are shown in separate panels.
Previous runs can be saved in history.
Main Technologies Used
The project uses Python as the main programming language.
It uses Tkinter for the graphical user interface. Tkinter creates the window, buttons, text editor, dropdowns, panels, and history list.
It uses OpenCV, imported as cv2, to load and read the video frame by frame.
It uses Pillow, imported as PIL, to convert video frames into images that Tkinter can display.
It uses subprocess to run user code in different languages.
It uses tempfile to create temporary files safely when executing code.
It uses json to save and load execution history.
It optionally uses the Gemini API through google-genai for AI debugging explanations.
APIs / Libraries Needed
Required Python libraries:
pip install pillow opencv-python
Optional AI library:
pip install google-genai
Built-in Python modules, no install needed:
tkinter
subprocess
os
tempfile
json
datetime
External Requirements
For Python code execution:
Python must be installed
For JavaScript execution:
Node.js must be installed
For Java execution:
JDK must be installed, including javac and java
For C++ execution:
g++ compiler must be installed
For AI analysis:
Gemini API key must be available in your environment
google-genai package must be installed
Gemini API Role
The Gemini API is used only when code fails. The app sends:
The selected language
The user’s source code
The runtime error or stack trace
Then Gemini returns a short explanation of why the code crashed and how to fix it.
Without Gemini, the app still works as a normal debugger. It will run code and show errors, but the AI explanation panel will show an offline message.
Core Features
The project includes:
Video splash screen
LET'S DEBUG transition button
Code editor
Language selector
Theme selector
Run button
Clear button
Output/error panel
AI explanation panel
Runtime status panel
Execution history
Multiple themes
Support for Python, JavaScript, Java, and C++
System Requirements
Recommended setup:
Python 3.10 or newer
Windows operating system
Tkinter support
Pillow
OpenCV
Optional: Node.js
Optional: JDK
Optional: g++
Optional: Gemini API key
In short, debugr is a Python desktop app that combines a stylish animated interface with a practical code execution and AI-assisted debugging workspace.

