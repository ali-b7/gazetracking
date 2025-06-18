This is our Collaboration Systems Project in the summer semester 2025. 

we use the gaze tracking library from EyeGestures- thank you!
work in progress


--------------


tracking.py is the actual project file - if you run it, it creates a .db file for storing the gaze tracking times (at the moment: nose, eyes, mouth)

How to?
---

 Clone the repo to your local machine:
 <code> git clone </code>

Create a virtual environment and install requirements:

<code> python -m venv eyeenv </code>
<code> eyeenv\Scripts\activate </code>
<code> pip install -r requirements.txt </code>

Run your app:

python tracking.py

there should appear a black screen first, calibrating with blue dots. 
then, the face image should appear and track your gaze (here are the problems at the moment)


