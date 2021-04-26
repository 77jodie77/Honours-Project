import unittest
import python_matlab
import app_gui
from app_gui import *


class MyTestCase(unittest.TestCase):
    def test_something(self):
        program = Program()
        self.assertEqual(program.get_MIDI_number("A/6"),93)
        self.assertEqual(program.get_MIDI_number("D#/4/Eb4"), 63)
        self.assertEqual(program.get_MIDI_number("C/5"), 72)
        self.assertEqual(program.calculate_pitches("sounds/eb.wav")[0],"D#/5/Eb5")
        a_chord = program.calculate_pitches("sounds/a_chord.wav")
        self.assertEqual(a_chord[0], "A/4")
        self.assertEqual(a_chord[1], "C#/5/Db5")
        self.assertEqual(a_chord[2], "E/5")



if __name__ == '__main__':
    unittest.main()
