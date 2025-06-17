This is our Collaboration Systems Project in the summer semester 2025. 

we use the gaze tracking library from EyeGestures- thank you!
work in progress


--------------


tracking.py is the actual project file - if you run it, it creates a .db file for storing the gaze tracking times (at the moment: nose, eyes, mouth)

How to?
---

First, clone the repo to your machine and move to the folder.
then activate the venv using <code> .\eyeenv\Scripts\Activate.ps1 </code>

you should see (venv) now in the terminal. 
next, use <code> pip install -r requirements.txt </code> and make sure everything is installed.
next, use <code> python tracking.py </code> to run the code.

there should appear a black screen first, calibrating with blue dots. 
then, the face image should appear and track your gaze (here are the problems at the moment)
