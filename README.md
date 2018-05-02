# datax-sdr-project
Searching E-T is a project that we started as a part Berkeley SETI Research Center with the guidance of Steve Croft, who is a researcher in the department of Astronomy and an outreach specialist for the open project of Breakthrough Listen. Data from the automated planet finder and the Green Bank observatory telescopes are flowing into Breakthrough Listen’s public archive. This is an initiative to find extra-terrestrial intelligence. 
One part of our project is to classify whether the FM stations that we found are playing music or not music in real-time. We labelled data into 4 classes including music, noise,talking and no sound.
Many things can be done further by identifying other signals like WiFi, GPS, and capture a wider spectrum. We can also work on identifying the different genres of music while it is being played in an FM station. Understanding all the known signals will give rise to finding the unknown, and the search continues.

# How to run
To run the project, make sure you have installed python 3.6:

```python datax_alien.py```

The program uses GQRX to record and decoded signals to audio file. You can download GQRX here:

http://gqrx.dk/

Make sure you have set the .wave output to the tmp/ folder of this project. 
The program will search for a .wav file in tmp/ folder in order to identify signals.

You will also needed to turn on "remoted control via TCP" option, and have GQRX listen to port 7356.

