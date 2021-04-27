import tkinter as tk
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk, ImageGrab

import python_matlab
from python_matlab import *
from PIL.ImageTk import PhotoImage
from itertools import groupby
from ctypes import windll, byref, create_unicode_buffer, create_string_buffer
import tkinter.font as font
from tkinter.ttk import Progressbar
import pyglet
import os


pyglet.font.add_file("Fonts/aleo-bold-webfont.ttf")




# This class is the parent class for all pages. It initialises a frame that is used as the window
class Page(tk.Frame):
    background_colour = "#FFFFFF"
    program = Program()
    # Creates a tkinter frame
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

    # Called when the current page is opened. It displays the current frame
    def show(self):
        self.lift()

    # Opens a new window that displays all help information for when the user is stuck
    def get_help(self):
        helpWindow = tk.Toplevel(self)


        # set window size
        helpWindow.geometry("1200x500")
        helpWindow.title("Help")

        #content
        label_help_getting_introduction = tk.Label(helpWindow, font=("Helvetica", 10), justify="left", text="The purpose of this application is to allow creators to produce sheet music from their own sound file.\nAll that is required is an audio file and this application will produce the corresponding sheet music that is required.\nCompositions can then be saved as an image or even exported as a MIDI file.")

        label_help_getting_started = tk.Label(helpWindow, justify="left", font=("Helvetica", 20), text="Getting Started")
        label_help_add_features = tk.Label(helpWindow, justify="left", font=("Helvetica", 20), text="Additional Features")

        label_help_getting_started_content = tk.Label(helpWindow, font=("Helvetica", 10), justify="left", text="To begin a new composition, select the \"New Score\" page.\nThen, fill in the details on your composition, including the key and time signature and add your audio file with the browse button and then select \"New Score\".\nYou will then be navigated to the main screen where you can view your composition. To add a music file, select \"Import\".\nThis will open up your file explorer where you can select your .WAV, .M4A or .MP3 file.\nAfter selecting your file, allow some time for your file to be processed and displayed on the screen.\nYou will then be able to view your composition as sheet music.\nYou can add multiple sound files sequentially to create a longer composition")
        label_help_add_features_content = tk.Label(helpWindow, font=("Helvetica", 10), justify="left", text="To start a new composition, select the \"New Score\" button from the main screen. This will give you the option to start again with different options.\nTo save your composition, select the \"Export\" button and choose whether you would like to save it as a MIDI file, or an image (PDF or PNG).\nAfter selecting either of these options, you can select where you want your file to be save and what you want to name it.")

        label_help_getting_introduction.pack(side="top", anchor="w", expand=False, padx=0, pady=0)
        label_help_getting_started.pack(side="top", anchor="w", expand=False, padx=0, pady=2)
        label_help_getting_started_content.pack(side="top", anchor="w", expand=False, padx=0, pady=0)
        label_help_add_features.pack(side="top", anchor="w", expand=False, padx=0, pady=2)
        label_help_add_features_content.pack(side="top", anchor="w", expand=False, padx=0, pady=0)




# This is the main page. The purpose of this page is to allow the user to create a composition and display it on a canvas.
# It also exports the composition
class Composition_Page(Page):
    notes = []
    curr_x_position = 0  # The x position
    curr_y_position = 574 # The y position in pixels
    x = 340
    bar_count = 0 # This keeps track on how far across the bar we are
    bars = []
    staves = [] # Contains the images of each staff
    positions = []
    note_lengths = {} # A dictionary that stores the length of each note
    pos = -1

    beats_in_bar = 4 # Default beats in a bar

    page_count = 1 #keeps track of how many pages have been created


    final_composition = []

    # This function creates the layout of the page.
    # It creates the top nav bar and a canvas below that features a scrollbar.
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)


        self.load_images()

        buttonframe = tk.Frame(self, relief="sunken", highlightbackground="black", highlightcolor="black", highlightthickness=2)
        buttonframe.configure(background="#DDDDDD")

        buttonframe.pack(side="top", fill="x", expand=False)

        # code for scrollbars
        # taken from: https://stackoverflow.com/questions/7727804/tkinter-using-scrollbars-on-a-canvas
        self.canvas = tk.Canvas(self,width=1800, height=1000, scrollregion=(0,0,1800,1600))
        hbar = tk.Scrollbar(self.canvas, orient="horizontal")
        hbar.pack(side="bottom", fill="x")
        hbar.config(command=self.canvas.xview)
        vbar = tk.Scrollbar(self, orient="vertical")
        vbar.pack(side="right", fill="y")
        vbar.config(command=self.canvas.yview)
        self.canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)


        a = self.canvas.create_rectangle(200, 20, 1400, 1500, fill='white', width=2)

        self.staves.append(self.canvas.create_image(800, 300, image=self.staff_image, anchor='center'))

        # Creating a photoimage object to use image
        global icon_menu
        global icon_new
        global icon_help
        icon_menu = PhotoImage(file=r"images/UI/menu-48.png")
        icon_new = PhotoImage(file=r"images/UI/new.png")
        icon_help = PhotoImage(file=r"images/UI/help-48.png")
        menu_button = tk.Button(buttonframe, image=icon_menu,#text='Menu',
                               command=lambda: main.show_page(main.p3))
        menu_button.pack(side="left")

        new_button = tk.Button(buttonframe, image=icon_new,
                                          command=lambda: main.new_page())
        new_button.pack(side="left")

        help_button = tk.Button(buttonframe, image=icon_help, command=lambda: self.get_help())

        help_button.pack(side="left")

        input_filepath_button = tk.Button(buttonframe, text='Import', command=lambda: self.get_filename(), height=3, activebackground = "#DDDDDD")

        input_filepath_button.pack(side="left", fill="both")


        # Code for export dropdown menu
        # Taken from: https://www.tutorialspoint.com/python/tk_menu.htm
        mb = tk.Menubutton(buttonframe, text="Export...", relief="raised", activebackground = "#DDDDDD")

        mb.menu = tk.Menu(mb, tearoff=0)
        mb["menu"] = mb.menu

        # Binds dropdown items and assigns functions to them
        mb.menu.add_command(label="as MIDI", command=lambda : self.program.create_MIDI_file(tk.filedialog.asksaveasfilename(defaultextension=".mid")))
        mb.menu.add_command(label="as image", command=lambda: self.save_as_image())
        mb.menu.add_separator()
        mb.menu.add_command(label="Preferences", command=lambda : self.set_MIDI_preferences())
        mb.pack(side="left", fill="both")


        self.tempo = tk.Label(self.canvas, text="", bg="#FFFFFF", font=("Courier", 12))



        self.canvas.pack(side="top", fill="both", expand=True)


    # Sets the value of a variable in a function in another script
    def set_MIDI_values(self, tempo, sustain, volume, prefWindow):
        self.program.tempo = int(tempo)
        if volume>127:
            volume=127
        self.program.volume = volume
        if sustain=="Short":
            self.program.duration = 2
        elif sustain=="Long":
            self.program.duration = 4
        else:
            self.program.duration = 3
        prefWindow.destroy()

    # Opens a window that lets the user set parameters that define the volume and tempo of the MIDI file
    def set_MIDI_preferences(self):
        prefWindow = tk.Toplevel(self)
        entry_int = tk.IntVar()
        entry_int.set(self.program.tempo)
        volume_int = tk.IntVar()
        volume_int.set(self.program.volume)

        # set window size
        prefWindow.geometry("650x290")
        prefWindow.title("MIDI Preferences") # set window title

        label_title = tk.Label(prefWindow, text="MIDI Preferences", font=("Helvetica", 20), height=2)

        tempo_frame = tk.Frame(prefWindow, relief="sunken")
        label_tempo = tk.Label(prefWindow, text="Tempo (BPM):", font=("Helvetica", 16))
        entry_tempo = tk.Entry(prefWindow, textvariable=entry_int)

        volume_frame = tk.Frame(prefWindow, relief="sunken")
        label_volume = tk.Label(prefWindow, text="Volume (max 127):", font=("Helvetica", 16))
        entry_volume = tk.Entry(prefWindow, textvariable=volume_int)

        button_frame = tk.Frame(prefWindow, relief="sunken")
        save_changes_button = tk.Button(prefWindow, text='Apply Changes', command=lambda: self.set_MIDI_values(entry_tempo.get(), sustain_variable.get(), volume_int.get(), prefWindow), height=4, width=15)
        cancel_button = tk.Button(prefWindow, text='Cancel',
                                        command=lambda: prefWindow.destroy(), height=4, width=15)


        label_title.grid(column=0,row=0,columnspan=5, pady=1, padx=10, sticky="new")
        #tempo_frame.pack(side="top", anchor="center", expand=True, padx=0, pady=10)
        label_tempo.grid(column=0, row= 1,pady=1, padx=10, sticky="news")
        entry_tempo.grid(column=1, row=1,pady=1, padx=10, sticky="news")

        #volume_frame.pack(side="top", anchor="center", expand=True, padx=0, pady=10)
        label_volume.grid(column=0, row=3,pady=1, padx=10, sticky="news")
        entry_volume.grid(column=1,row=3,pady=1, padx=10, sticky="news")
        #label_max_volume.pack(side="left", expand=False, padx=2, pady=10)
        #button_frame.pack(side="bottom", anchor="e", expand=False, padx=10, pady=10)

        sustain_frame = tk.Frame(prefWindow, relief="sunken")
        #sustain_frame.grid(column=0,columnspan=3, pady=1, padx=10, sticky="new")
        label_sustain = tk.Label(prefWindow, text="Sustain:",
                                  font=("Helvetica", 16))
        label_sustain.grid(column=0,row=4, pady=1, padx=10, sticky="news")

        sustain_variable = tk.StringVar(prefWindow)
        sustain_variable.set("Normal")  # set default value to normal

        sustain_dropdown = tk.OptionMenu(prefWindow, sustain_variable, "Short", "Normal", "Long")  # Define the options for the dropdown menu
        sustain_dropdown.config(width=10, height=1, font=("Helvetica", 12))

        sustain_dropdown.grid(column=1, row=4, pady=1, padx=10, sticky="ew")


        save_changes_button.grid(column=3,row=5, pady=(10,0), padx=10, sticky="news")
        cancel_button.grid(column=4,row=5, pady=(10,0), padx=10, sticky="news")



    # Creates an image by converting the canvas to a .eps file and then converting that to a .png file
    # Labels are removed as the eps file cannot save text in labels
    def save_as_image(self):
        save_name = tk.filedialog.asksaveasfilename(defaultextension=".png", filetypes=(("png", "*.png"),("pdf", "*.pdf")))
        if save_name:
            self.canvas.yview_moveto(0)
            if hasattr(self, 'title'):
                title = self.title["text"]
                self.title["text"] = ""
            if hasattr(self, 'comp'):
                comp = self.comp["text"]
                self.comp["text"]=""
            if hasattr(self, 'tempo'):
                tempo = self.tempo["text"]
                self.tempo["text"] = ""



            file_name, ext = os.path.splitext(save_name)
            self.canvas.postscript(file=file_name + ".eps", height=2050)  # save canvas as encapsulated postscript
            img = Image.open(file_name + ".eps")
            img.save(save_name, ext.lower()[1:], quality=99)
            if 'title' in locals(): self.title["text"]=title
            if 'comp' in locals(): self.comp["text"] = comp
            if 'tempo' in locals(): self.tempo["text"] = tempo

    # Asks for an audio file and calls a function to get the notes. It only calls the function
    # if the filename is not empty
    def get_filename(self):

        filename = askopenfilename(parent=root, filetypes=[("Sound files", ".WAV .MP3 .M4A")]) # allows user to enter file from local space
        if filename:
            self.process_file(filename)
            self.program.final_comp = self.final_composition

    # Creates global variables that contain images of notes, clefs, etc.
    def load_images(self):
        self.staff_image = tk.PhotoImage(file="images/stave.png")
        self.note_images = [None] * 5
        self.note_images[0] = tk.PhotoImage(file="images/notes/Quaver single.png")
        self.note_images[1] = tk.PhotoImage(file="images/notes/Crotchet.png")
        self.note_images[2] = tk.PhotoImage(file="images/notes/Minim.png")
        self.photo_sharp = tk.PhotoImage(file="images/Sharp.png")
        self.note_images[3] = tk.PhotoImage(file="images/notes/Minim dotted.png")
        self.note_images[4] = tk.PhotoImage(file="images/notes/Semibreve.png")
        self.clef = tk.PhotoImage(file="images/Treble clef.png")


        self.bars.append(Bar())
        self.bar_images = tk.PhotoImage(file="images/barlines/Barline.png")


    # This function calls a function in another script that calculates all of the notes
    # It then calls another function that parses and displays the notes
    def process_file(self, filepath):

        pitches = self.program.calculate_pitches(filepath)
        self.calculate_note_lengths(pitches)

    # Creates a label that displays the title, composer or tempo of the composition that was passed in as a parameter
    # It also sets the tempo of the MIDI file to the value if it is valid
    def add_label(self, value, type):
        if type==0:# If type is a title
            self.title = tk.Label(self.canvas, text=value, bg="#FFFFFF", font=("Courier", 35))
            self.canvas.create_window(780, 100, anchor='center', window=self.title, height=150)
        elif type==1: # If type is a composer
            self.comp = tk.Label(self.canvas, text=value, bg="#FFFFFF", font=("Courier", 15))
            self.canvas.create_window(1150, 190, anchor='center', window=self.comp, height=50)
        else: # If type is tempo
            self.tempo = tk.Label(self.canvas, text="tempo = " + value, bg="#FFFFFF", font=("Courier", 12))
            self.canvas.create_window(300, 190, anchor='center', window=self.tempo, height=50)
            if value.isnumeric():
                self.program.tempo = int(value)

    # Displays the correct time signature corresponding to the parameter passed in
    def add_time_sig(self, time_sig_int):
        if time_sig_int=="":
            time_sig_int='4-4'
        filepath = "images/Time Signatures/" + time_sig_int + ".png"
        self.time_sig_image = tk.PhotoImage(file=filepath)
        time_sig = self.canvas.create_image(50, 10, image=self.time_sig_image, anchor='nw')
        self.canvas.move(time_sig, 370, 255)
        self.beats_in_bar=int(time_sig_int[0])
        self.curr_x_position=2

    # Displays the correct key signature corresponding to the parameter passed in
    # Displays the correct number of sharps in the correct places
    def add_key_sig(self, key_sig):
        self.key_sig = key_sig
        order_of_keys = ["C", "G", "D", "A", "E", "B", "F#", "C#"] # Order of keys in a key signature
        self.key_images = [None]*7
        y_positions = [50,75,42,68,93,58,85]
        for key in range(len(order_of_keys)):
            if key_sig == order_of_keys[key]:# If we have reached the correct key, do not print any more sharps
                return
            self.key_images[key] = self.canvas.create_image(0, 0, image=self.photo_sharp, anchor='nw')
            self.canvas.move(self.key_images[key], 340 + key*12, y_positions[key]+self.curr_y_position-400)

    # Adds an accidental at the correct position
    def add_accidental(self, note_type, position):
        if note_type==0: #if type is a sharp
            accidental = self.canvas.create_image(50, 10, image=self.photo_sharp, anchor='nw')
            self.canvas.move(accidental, position[0], position[1])

    #Converts array of notes at positions into a 2D array where each list is a different beat. It also filters notes above a certain threshold
    #code taken from: https://stackoverflow.com/questions/30825535/split-a-list-into-chunks-determined-by-a-separator
    def split_notes_into_chunks(self, positions):
        chunks = []
        x = 0
        chunks.append([])  # create an empty chunk to which we'd append in the loop
        for i in positions:

            if i != '.':
                split = i.split("/")
                if int(split[1])<8:
                    chunks[x].append(i)
                else:
                    chunks.append([]) # If note it too low, starta new list
            else: # If a full stop is reached, start a new list
                x += 1
                chunks.append([])
        return chunks

    # Displays clef and bar line when a composition is newly made
    def display_start_images(self):
        clef = self.canvas.create_image(50, 10, image=self.clef, anchor='nw')
        self.canvas.move(clef, 250, 245)
        self.add_barline(240)
        self.add_barline(1248)

    # This function Figures out the length of each note and creates a dictionary to store the lengths.
    # It also removes repeats of the same note
    def calculate_note_lengths(self, positions):
        parsed_positions = self.split_notes_into_chunks(positions) # Get a 2D variable containing notes

        position_group_i = 0
        note_length_dict = {}
        final_positions = []
        counter = 0
        for position_group in parsed_positions: # Loop through every list of notes
            parsed_positions[position_group_i] = list(dict.fromkeys(parsed_positions[position_group_i]))

            for position in parsed_positions[position_group_i]: # loop through every note in current beat
                note_length = 1
                curr_position_group = position_group_i+1
                #Keep on moving through beats if the current note is present and keep track of number of occurrences
                while parsed_positions[curr_position_group].count(position) > 0:
                    parsed_positions[curr_position_group].remove(position) # Remove the repeat so the same note isn't printed multiple times
                    note_length+=1
                    curr_position_group +=1
                note_length_dict[str(counter)+position] = note_length # Set the note length in a dictionary, adding an ID at the start as different notes can be the same pitch
                final_positions.append(position)
            counter+=1
            final_positions.append(".") # Add a separator to the list of notes to indicate the next beat
            position_group_i+=1
        self.note_lengths = note_length_dict
        self.positions = final_positions
        self.program.final_comp+=final_positions # Add the notes to the python_matlab script so the MIDI has a copy of the notes
        self.display_note(final_positions, note_length_dict)

    # This function adds a barline to the position passed in on the current staff
    def add_barline(self, x_pos):
        self.bars[len(self.bars)-1] = self.canvas.create_image(50, 10, image= self.bar_images, anchor='nw')
        self.canvas.move(self.bars[len(self.bars) - 1], x_pos, self.curr_y_position - 318)

    # When a new composition has been initiated or the end of the current staff has been reached, a new one is created by calling this line
    # It displays an image of a staff and adds bar lines and the key sig by calling functions
    def add_staff(self):
        self.curr_y_position += 200
        self.canvas.create_image(800, self.curr_y_position-274, image=self.staff_image, anchor='center')
        self.canvas.create_image(310, self.curr_y_position-320, image=self.clef, anchor='nw')
        self.add_barline(240)
        self.add_barline(1248)
        self.add_key_sig(self.key_sig)

    def insert_new_page(self):
        self.canvas.create_rectangle(200, self.curr_y_position-20, 1400, self.curr_y_position+1260, fill='white', width=2)
        self.canvas.configure(scrollregion=(0,0,1800, self.curr_y_position+ 2000))
        self.curr_y_position+=130
        self.page_count+=1

   # This function displays the note in the correct position, adding a bar line if required
    def display_note(self, notes_list, note_length_dict):
        self.final_composition += notes_list
        parsed_positions = self.split_notes_into_chunks(notes_list) # get a 2D list containing all of the notes

        note_length_dict_counter = 0
        self.pos += 1
        position_group_counter = 0
        for position_group in parsed_positions: # Loop through every list item

            if self.bar_count >= self.beats_in_bar: # If we are at the end of a bar

                if self.x > 1050: # If we are at the end of a staff
                    if self.curr_y_position >self.page_count*1400: # If we are at the end of the sheet music
                        self.insert_new_page()
                    self.curr_x_position = -1
                    self.add_staff() # Add a new staff
                    self.bar_count = 0
                    self.pos = 0
                    self.x = 200

                    # get the index of the last non empty list and if that position is reached, then return
                    # This ensures that the end of the composition is not a bunch of empty bars and the next
                    # imported file follows directly after
                    if (next(len(parsed_positions) - i for i, j in enumerate(reversed(parsed_positions), 1) if j != []) < position_group_counter):
                        return

                else: # If we arnt at the end of a staff, add a barline
                    self.curr_x_position += 1
                    self.add_barline(self.x + 40)
                    self.bar_count = self.bar_count - self.beats_in_bar
                    self.curr_x_position += 2

            if position_group !=[]: # If the current beat is not empty
                self.pos+=1
                for note in position_group: # Loop through every note in the current beat

                    self.curr_x_position = self.pos+1
                    parsed_position = note.split('/') # Split the note so the first part is the note and the second is the octave
                    if 7 > int(parsed_position[1]) > 3: #if note is in range
                        self.notes.append(Note(note))
                        if note_length_dict[str(note_length_dict_counter)+note]> self.beats_in_bar-self.bar_count: #if note length is too large for bar
                            # calculate the remainder of the note that will continue after the bar line
                            remainder = note_length_dict[str(note_length_dict_counter)+note]-(self.beats_in_bar-self.bar_count)
                            # Call function to add the remainder of the tied note to the list of notes
                            note_length_dict, parsed_positions = self.add_tied_note(note_length_dict,
                                                                                    note_length_dict_counter + (self.beats_in_bar - self.bar_count),
                                                                                    parsed_positions, note, remainder)
                            note_length_dict[
                                str(note_length_dict_counter) + note] = self.beats_in_bar - self.bar_count

                        # Create an image of the correct note depending on the length of it
                        self.notes[len(self.notes) - 1] = self.canvas.create_image(50, 10, image=self.note_images[note_length_dict[str(note_length_dict_counter)+note]],anchor='nw')

                        parsed_position[0]+=" "
                        offset = self.get_offset(parsed_position[0])
                        self.x = 340 + self.curr_x_position * 40 # Calculate the x coordinate of the note
                        y = (-(ord(parsed_position[0][0]) - 65) * 9 - (int(parsed_position[1]) + offset) * 63) + self.curr_y_position # Calculate y coordinate of the note

                        if parsed_position[0][1] == "#": # If current note is a sharp, add an accidental
                            self.add_accidental(0, [self.x-25,y+28])

                        if note_length_dict[str(note_length_dict_counter)+note]==4:  # Reposition a semibreve as it is a different size to the other notes
                            y += 37
                        self.canvas.move(self.notes[len(self.notes) - 1], self.x, y)
                        if y-self.curr_y_position>=-270 and note_length_dict[str(note_length_dict_counter)+note]<4: # Add ledger lines if the note is a middle C or below

                            self.canvas.create_line(x + 45, y + 54, x + 73, y + 54, fill="black", width=2)


                self.pos = self.curr_x_position


            position_group_counter+=1
            note_length_dict_counter += 1
            self.bar_count+=1



    # This function adds a tied note at the start of the next bar. This means that the note will be treated as a normal note when it is reached
    def add_tied_note(self, note_length_dict, new_pos, parsed_positions, note, remainder):
        note_length_dict[str(new_pos) + note] = remainder # Add the note to the dictionary with the correct length
        parsed_positions.append([]) #This ensures there is no out of range error
        parsed_positions[new_pos].append(note)

        return note_length_dict, parsed_positions

    # As the new octave begins at C and not A, this function checks whether the position will need to change
    def get_offset(self, note):

        if note[0] == 'A' or note[0] == 'B':  # As the number of the octave increases at C, we need to reduce the octave if the letter is an A or B
            offset = 1
        else:
            offset = 0
        return offset


# This is the class for the title page. It is a child to the page class and displays the start screen
class Title_Page(Page):
    FR_PRIVATE = 0x10
    FR_NOT_ENUM = 0x20

    #Creates the layout for the page including the buttons and the title
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.configure(background=self.background_colour) # Set background colour

        # Create a label for the title in the specified font
        label = tk.Label(self, text="Cadenza Score", font = ("Aleo",50), fg = "#DD4433", bg = self.background_colour, anchor = "n")

        label.grid(column=0,columnspan=3, pady=1, padx=10, sticky="new")

        # Create frames for borders of buttons
        border_color_1 = tk.Frame(self, background="red")
        border_color_2 = tk.Frame(self, background="red")
        border_color_3 = tk.Frame(self, background="red")

        # Create the new score button
        btn_new_score = tk.Button(border_color_1,text='New Score',  command=lambda: main.new_page(),highlightthickness=4, relief="flat", background=self.background_colour, height = 2)
        btn_new_score.pack(padx=2, pady=2, expand=True, fill="both")
        border_color_1.grid(column = 0, row=1, pady=(30,80), padx=500, sticky="new")

        # Create the help button
        btn_help = tk.Button(border_color_2, text='Help', command=lambda: self.get_help(),highlightthickness=4, relief="flat", background=self.background_colour, height = 2)
        btn_help.pack(padx=2, pady=2, expand=True, fill="both")
        border_color_2.grid(column=0, row=2, pady=(0, 80), padx=500, sticky="new")

        # Create the quit button
        btn_quit = tk.Button(border_color_3, text='Quit', command=lambda: root.destroy(), highlightthickness=4, relief="flat", background=self.background_colour, height = 2)
        btn_quit.pack(padx=2, pady=2, expand=True, fill="both")
        border_color_3.grid(column=0, row=3, pady=(0, 80), padx=500, sticky="new")

        # define font
        myFont = font.Font(family='Aleo', size=20, weight='bold')
        btn_new_score['font'] = myFont
        btn_new_score['fg'] = "#DD4433"
        btn_help['font'] = myFont
        btn_help['fg'] = "#DD4433"
        btn_quit['font'] = myFont
        btn_quit['fg'] = "#DD4433"
        self.grid_columnconfigure(0, minsize=80, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.configure(background = self.background_colour)




# This class displays the new score page. It supplies text boxes and buttons and takes the user to the composition page
class New_Score_Page(Page):
    # Creates the layout for the page including the buttons, entry boxes, and dropdowns
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.configure(background=self.background_colour)
        top_padding = tk.Frame(self,height=3, bg="#FFFFFF")
        top_padding.grid(row=0, pady=20, sticky="new")

        # Create variables for the text boxes
        entry_text_title = tk.StringVar()
        entry_text_composer = tk.StringVar()
        entry_text_tempo = tk.StringVar()
        entry_text_filepath = tk.StringVar()

        #title label and input
        label_title = tk.Label(self, text="Title:", height=3, width=30, bg="#FFFFFF", font=("Helvetica", 16))
        label_title.grid(column=0, row=1, pady=1, padx=10, sticky="nsw")

        entry_title = tk.Entry(self, width=40, textvariable=entry_text_title, highlightthickness=2)
        entry_title.grid(column=1, row=1, pady=30, padx=10, ipady=8, columnspan=3, sticky="nsw")

        #composer label and input
        label_composer = tk.Label(self, text="Composer:", height=3, width=30, bg="#FFFFFF", font=("Helvetica", 16))
        label_composer.grid(column=0, row=2, pady=1, padx=10, sticky="nsw")

        entry_composer = tk.Entry(self, width=40, textvariable=entry_text_composer, highlightthickness=2)
        entry_composer.grid(column=1, row=2, pady=30, padx=10, ipady=8, columnspan=3, sticky="nsw")

        #tempo label and input
        label_tempo = tk.Label(self, text="Tempo(bpm):", height=3, width=30, pady=10, bg="#FFFFFF", font=("Helvetica", 16))
        label_tempo.grid(column=0, row=3, pady=1, padx=10, sticky="nsw")

        entry_tempo = tk.Entry(self, width=40, textvariable=entry_text_tempo, highlightthickness=2)
        entry_tempo.grid(column=1, row=3, pady=30, padx=10, ipady=8, columnspan=3, sticky="nsw")

        #time sig label and dropdown
        label_time_sig = tk.Label(self, text="Time Signature:", height=3, width=30, pady=10, bg="#FFFFFF", font=("Helvetica", 16))
        label_time_sig.grid(column=0, row=4, pady=1, padx=10, sticky="nsw")

        time_variable = tk.StringVar(self)
        time_variable.set("4/4")  # set default value to 4/4

        time_dropdown = tk.OptionMenu(self, time_variable, "3/4", "4/4") # Define the options for the dropdown menu
        time_dropdown.config(width=10, height=1, font=("Helvetica", 14))

        time_dropdown.grid(column=1, row=4, pady=40, padx=10, sticky="nsw", columnspan=2)


        #key sig label and dropdown
        label_key_sig = tk.Label(self, text="Key Signature:", height=3, width=30, pady=10, bg="#FFFFFF", font=("Helvetica", 16))
        label_key_sig.grid(column=0, row=5, pady=1, padx=10, sticky="nsw")

        key_variable = tk.StringVar(self)
        key_variable.set("C")  # set default value to C major

        key_note = tk.OptionMenu(self, key_variable, "A", "B", "C", "C#", "D", "E", "F#", "G") # Define options for dropdown menu
        major_label = tk.Label(self, text="major", bg="#FFFFFF", font=("Helvetica", 16))
        key_note.config(width=5, height=1, font=("Helvetica", 14))

        key_note.grid(column=1, row=5, pady=40, padx=(10,0), sticky="nsw")
        major_label.grid(column=2, row=5, pady=1, padx=0, sticky="nsw")

        middle_frame = tk.Frame(self, bg="black", width=4)
        middle_frame.grid(column=4, row=1, rowspan=5, pady=10, padx=90, sticky="nsw")

        #right column audio file label and input
        label_filepath = tk.Label(self, text="Audio file:", height=3, width=30, pady=10, bg="#FFFFFF", font=("Helvetica", 16))
        label_filepath.grid(column=5, row=1, pady=1, padx=10, sticky="nes")


        button_browse = tk.Button(self, text='Browse', height=2, width=8, relief="ridge",highlightthickness=4, # Browse button that opens the file explorer
                                     command=lambda: self.set_file(entry_filepath), bg="#FFFFFF", font=("Helvetica", 10))
        button_browse.grid(column=6, row=2, pady=10, padx=0, sticky="nes")

        entry_filepath = tk.Entry(self, width=30, textvariable=entry_text_filepath, highlightthickness=2) # Add an alternative entry for filepath
        entry_filepath.grid(column=5, row=2, pady=10, padx=0, sticky="nesw")


        # Create composition button that calls character_limit function
        button_new_score = tk.Button(self, text='Create composition', height=5, width=30,relief="ridge",highlightthickness=8,
                                     command=lambda: self.character_limit(entry_text_title, entry_text_composer, entry_text_tempo, key_variable,
                                                                          time_variable, entry_text_filepath), bg="#FFFFFF", font=("Helvetica", 16))
        button_new_score.grid(column=5, row=5, pady=1, columnspan=2, padx=50, sticky="nes")

    # Opens up the file explorer for the audio file and sets the entry variable to the path
    def set_file(self, entry):
        entry.delete(0, "end")
        entry.insert(0, askopenfilename(parent=root, filetypes=[("Sound files", ".WAV .MP3 .M4A")]))

    # Checks if entry variables are correct length and formats these by adding new lines
    def character_limit(self, title, composer, tempo, key_variable, time_variable, filepath):
        if len(title.get())>90:
            title.set("Title must be less than 90 characters")
        else:
            if len(title.get())>60:
                title.set(title.get()[:60] + '\n' + title.get()[60:])
            if len(title.get())>30:
                title.set(title.get()[:30] + '\n' + title.get()[30:])
            if len(composer.get()) > 60:
                composer.set("Composer must be less than 60 characters")
            else:
                if len(composer.get()) > 30:
                    composer.set(composer.get()[:30] + '\n' + composer.get()[30:])
                if len(tempo.get()) > 30:
                    tempo.set("Tempo must be less than 90 characters")
                else:
                    # When entries are correct length, create new score
                    main.new_score(title.get(), time_variable.get(), key_variable.get(), composer.get(), tempo.get(), filepath.get())


# This is the main class, it creates a frame for all other pages to fit into and also initialises the classes
class MainView(tk.Frame):
    # Creates all the pages and places them in the window
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.page_comp = Composition_Page(self)
        self.page_title = Title_Page(self)
        self.page_new_score = New_Score_Page(self)


        bottomframe = tk.Frame(self, relief = "sunken", height=20)
        bottomframe.configure(background="#FDFDFD")
        self.container = tk.Frame(self)

        #buttonframe.pack(side="top", fill="x", expand=False)
        bottomframe.pack(side = "bottom", fill="x", expand=False)

        self.container.pack(side="top", fill="both", expand=True)

        self.page_comp.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
        self.page_title.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
        self.page_new_score.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)

        self.page_title.show()

    # Shows the page that was passed in as a parameter
    def show_page(self, page):
        self.page_comp.grid_remove()
        self.page_title.grid_remove()
        self.page_new_score.grid_remove()

        page.lift()

    # Opens the new score page
    def new_page(self):

        self.page_comp.grid_remove()
        self.page_title.grid_remove()
        self.page_new_score.grid_remove()

        self.page_new_score.lift()

    # Opens the composition page and adds the starting images such as the title and staff
    def new_score(self, title, time_sig, key_sig, composer, tempo, filepath):
        self.page_comp.grid_remove()
        self.page_comp = Composition_Page(self)
        self.page_comp.final_composition = []
        self.page_comp.program.final_comp = []
        self.page_comp.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
        self.page_new_score.grid_remove()
        self.page_comp.grid_remove()
        self.page_title.grid_remove()
        self.page_comp.lift()
        if title:self.page_comp.add_label(title,0)
        if composer:self.page_comp.add_label(composer,1)
        if tempo: self.page_comp.add_label(tempo,2)
        self.page_comp.add_time_sig(time_sig.replace("/", "-"))
        self.page_comp.display_start_images()
        self.page_comp.add_key_sig(key_sig)
        if filepath:

            self.page_comp.process_file(filepath)


# This if statement works as a main function
if __name__ == "__main__":
    root = tk.Tk() # Creates a TKinter window
    root.configure(background='black')
    root.title("Cadenza Score") # Names the window
    main = MainView(root)
    main.pack(side="top", fill="both", expand=True)
    root.wm_geometry("1750x700") # Sets window size
    root.mainloop() # Start main loop
