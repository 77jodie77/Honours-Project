import time
import matlab.engine
import tkinter as tk
from midiutil import MIDIFile


# This class is the backend of the system, it does not display any information to the user. It calls the MATLAB function and creates the MIDI file
class Program:

    # MIDI variables
    tempo = 60  # In BPM
    volume = 100  # 0-127, as per the MIDI standard
    duration = 1  # In beats

    final_comp=[]

    eng = matlab.engine.start_matlab()

    # This function searches the list of frequencies for the frequency passed in and returns the corresponding note
    def return_note(self, freq, freq_table, notes_table):
        for i in range(len(freq_table)):
            if notes_table[i] == "B/8": # If the end of the list is reached, return the final item
                return notes_table[i], i
            if float(str(freq)) < (float(freq_table[i + 1]) + float(
                    freq_table[i])) / 2:  # if sample is less than the average between two frequencies
                return notes_table[i], i
                pass
        return 0

    # Loops through every frequency and calls a function to identify the note
    def get_notes(self, frequencies, freq_table, notes_table):
        notes_played = [None] * len(frequencies)
        for freq in range(len(frequencies)): # Loop through every frequency
            curr_note, pos = self.return_note(frequencies[freq], freq_table, notes_table)
            notes_played[freq] = pos # Set the note to the note returned
        return notes_played  # Return base note

    # Calls the MATLAB function which returns a list of frequencies. It uses these values to identify the notes from the harmonics
    # By determining all of the possible notes and checking if it matches the list returned
    def calculate_pitches(self, filename):

        played_notes = []

        try:
         peak_x, peak_y = self.eng.harmonicFreq(filename, nargout=2) # Call the MATLAB function using a MATLAB engine API
        except:
            return [] #If there is an error return an empty list
        freq_table_notes = []
        freq_table_freqs = []


        f = open("Frequencies.txt", "r") # This file is a dictionary of frequencies and their corresponding notes
        counter = 0
        for line in f: # Loop through every line of the file
            parts = line.split(',')

            freq_table_notes.append(parts[0]) # append the notes to a list
            freq_table_freqs.append(parts[1].replace('\n', '')) # Append the frequencies to a list
            counter += 1
        played_array = self.get_notes(peak_x[0], freq_table_freqs, freq_table_notes) # Call a function that returns a list of the identified harmonics
        for note in peak_x[0]:  # loop through every note sample
            if 0 < note < 999999:
                harmonics_est = [None] * 6
                for harmonic_no in range(0, 6):
                    harmonics_est[harmonic_no] = note * (harmonic_no + 1) # Predict the next 6 harmonics in the sequence

                estimated_array = self.get_notes(harmonics_est, freq_table_freqs, freq_table_notes) # get the notes of these predicted harmonics

                found = True
                for i in estimated_array: # Loop through every prediction
                    if played_array.count(i) < 1: # If array does not contain the predicted harmonic, then it isnt a valid note
                        found = False
                if found: # If found is still true, the note is valid
                    splitted_str = freq_table_notes[estimated_array[0]].split("/")
                    if 3<int(splitted_str[1])<6:
                        played_notes.append(freq_table_notes[estimated_array[0]]) # append the note to a list of played notes

            elif note>999998:
                played_notes.append(".") # If a note is not present, then the next sample is started

        return played_notes

    # This function returns the MIDI number that corresponds to the note passed in by using the frequency dictionary
    def get_MIDI_number(self, note):
        f = open("Frequencies.txt", "r")
        midi_pitch=12
        for line in f: # Loop through every line
            parts = line.split(',')
            if parts[0]==note: # If note matches, return number
                return midi_pitch

            midi_pitch+=1


        return -1

    # Uses the MIDI util library to convert the list of notes into a MIDI file
    # Code taken from: https://pypi.org/project/MIDIUtil/
    def create_MIDI_file(self, filepath):
        if filepath:
            notes = self.final_comp
            degrees = [60, 62, 64, 65, 67, 69, 71, 72]  # MIDI note number

            time = 0  # In beats

            MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created automatically)
            MyMIDI.addTempo(0, 0, self.tempo*4)


            for note in notes: # Loop through every note
                if note == ".":# If a full stop is found, move onto the next beat
                    time+=1
                else:
                    curr_note = self.get_MIDI_number(note) # Get the corresponding MIDI note
                    if curr_note<92:
                        MyMIDI.addNote(0, 0, self.get_MIDI_number(note), time, self.duration, self.volume) # Add the note with the variables chosen by the user


            with open(filepath, "wb") as output_file:
                MyMIDI.writeFile(output_file) # Write the MIDI file at the given filepath

# Contains information on a bar
class Bar:
    position = 0
    notes = []
    image = 0


# Contains information on a note
class Note:
    pitch = 0
    type = 0
    position = 0
    image = 0
    accidental = 0

    def __init__(self, pitch):
        self.pitch = pitch
