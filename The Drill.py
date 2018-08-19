# Software for firearm manual training
# under GNU GPL v3 license


from functools import partial
from threading import Timer
import webbrowser
import datetime
import pickle
import random
import json
import os

import tkinter.ttk as ttk
from tkinter import font
from tkinter import *
import simpleaudio as sa


LAYOUT_OF_POSITIONS_AND_COMMANDS =    [                                                                                 # layout of positions and commands - base for object hierarchy
                                        {
                                            "name": "standing_position",
                                            "commands": [
                                                            "contact_front", "contact_right", "contact_left",
                                                            "contact_rear", "contact_rear_over_right_arm",
                                                            "contact_rear_over_left_arm", "jam", "fast_reload",
                                                            "tactical reload"
                                                        ]
                                        },
                                        {
                                            "name": "kneeling_high_position",
                                            "commands": [
                                                            "contact_front", "contact_right", "contact_left",
                                                            "contact_rear", "contact_rear_over_right_arm",
                                                            "contact_rear_over_left_arm", "jam", "fast_reload",
                                                            "tactical reload"
                                                        ]
                                        },
                                        {
                                            "name": "kneeling_low_position",
                                            "commands": [
                                                            "contact_front", "contact_right", "contact_left",
                                                            "contact_rear", "contact_rear_over_right_arm",
                                                            "contact_rear_over_left_arm", "jam", "fast_reload",
                                                            "tactical reload"
                                                        ]
                                        },
                                        {
                                            "name": "crouching_position",
                                            "commands": [
                                                            "contact_front", "contact_right", "contact_left",
                                                            "contact_rear", "contact_rear_over_right_arm",
                                                            "contact_rear_over_left_arm", "jam", "fast_reload",
                                                            "tactical reload"
                                                        ]
                                        },
                                        {
                                            "name": "prone_position",
                                            "commands": [
                                                            "contact_front", "contact_right", "contact_left",
                                                            "contact_rear", "contact_rear_over_right_arm",
                                                            "contact_rear_over_left_arm", "jam", "fast_reload",
                                                            "tactical reload"
                                                        ]
                                        }
                                    ]
LANGUAGE = ""
TRANSLATIONS = {}


def get_state_of_spinboxes(parent_par, settings_par):

    widget_id = str(parent_par).split(".")[-1]                                                                          # doing that, because can't get "name" parameter through widget.cget("name") (can do for widget.cget("state"))

    if "spinbox" in widget_id:
        widget_state = parent_par.get()
        new_setting = {widget_id: widget_state}
        settings_par.update(new_setting)

    children = parent_par.children.values()

    for child in children:
        get_state_of_spinboxes(parent_par=child, settings_par=settings_par)


def set_state_of_spinboxes(parent_par, settings_par):

    widget_id = str(parent_par).split(".")[-1]                                                                          # doing that, because can't get "name" parameter through widget.cget("name") (can do for widget.cget("state"))

    if "spinbox" in widget_id:
        parent_par.delete(0, "end")
        new_setting = settings_par[widget_id]
        parent_par.insert(0, new_setting)

    children = parent_par.children.values()

    for child in children:
        set_state_of_spinboxes(parent_par=child, settings_par=settings_par)


def get_state_of_objects(objects_par, settings_par):

    for object in objects_par:
        object_id = object.get_id()
        object_state = object.is_selected()
        new_setting = {object_id: object_state}
        settings_par.update(new_setting)

        try:
            objects = object.get_objects()

            get_state_of_objects(objects_par=objects, settings_par=settings_par)

        except:
            pass


def set_state_of_objects(objects_par, settings_par):

    for object in objects_par:
        object_id = object.get_id()
        new_setting = settings_par[object_id]
        object.set_state(new_setting)

        try:
            objects = object.get_objects()

            set_state_of_objects(objects_par=objects, settings_par=settings_par)

        except:
            pass


class Position(object):

    def __init__(self, parent_par, position_name_par, position_number_par, layout_of_commands_par):

        self.__name = TRANSLATIONS[LANGUAGE][position_name_par]
        self.__id = "".join(("position_", str(position_number_par)))
        self.__sound_filename = "".join((LANGUAGE, "_", position_name_par, ".wav"))

        self.__all_commands = []
        self.__selected_commands = []
        self.__active_command = None

        self.__create_widget(parent_par=parent_par, position_number_par=position_number_par)
        self.__create_commands_with_widgets(layout_of_commands_par=layout_of_commands_par,
                                            position_number_par=position_number_par, parent_par=parent_par)

    def __create_widget(self, parent_par, position_number_par):

        self.__label = Label(parent_par, text=self.__name)
        self.__label.grid(row=0, column=(position_number_par * 3) + 1, columnspan=2, sticky=W)

        self.__is_selected = BooleanVar(value=True)
        self.__checkbox = ttk.Checkbutton(parent_par, variable=self.__is_selected, command=self.__switch_commands_states,
                                          name="".join(("checkbox_", str(position_number_par))))
        self.__checkbox.grid(row=0, column=(position_number_par * 3))

    def __create_commands_with_widgets(self, layout_of_commands_par, position_number_par, parent_par):

        for command_number, command_name in enumerate(layout_of_commands_par):
            new_command = VisibleCommand(parent_par=parent_par, command_name_par=command_name,
                                         position_number_par=position_number_par, command_number_par=command_number)

            self.__all_commands.append(new_command)

    def __switch_commands_states(self):

        for command in self.__all_commands:
            command.switch_state()

    def switch_state(self):

        if self.__label["state"] == NORMAL:
            self.__label["state"] = DISABLED
            self.__checkbox["state"] = DISABLED

        else:
            self.__label["state"] = NORMAL
            self.__checkbox["state"] = NORMAL

        if self.__is_selected.get():
            self.__switch_commands_states()

    def is_selected(self):

        return self.__is_selected.get()

    def check_selection_of_commands(self):

        del self.__selected_commands[:]

        for command in self.__all_commands:
            if command.is_selected():
                self.__selected_commands.append(command)

    def play_position_sound(self):

        print(self.__name)

        file_path = "".join((os.getcwd(), "/sounds/", LANGUAGE, "/", self.__sound_filename))
        position_sound = sa.WaveObject.from_wave_file(file_path)
        position_sound.play()

    def get_position_name(self):

        return self.__name

    def get_command_name(self):

        return self.__active_command.get_command_name()

    def draw_command(self):

        self.__active_command = random.choice(self.__selected_commands)

    def play_command_sound(self):

        self.__active_command.play_command_sound()

    def get_objects(self):

        return self.__all_commands

    def get_id(self):

        return self.__id

    def set_state(self, state_par):

        old_state = self.__is_selected.get()

        self.__is_selected.set(state_par)

        if self.__is_selected.get() != old_state:
            self.__switch_commands_states()

    def get_number_of_selected_commands(self):

        return len(self.__selected_commands)


class Command(object):

    def __init__(self, command_name_par):

        self._name = TRANSLATIONS[LANGUAGE][command_name_par]
        self.__sound_filename = "".join((LANGUAGE, "_", command_name_par, ".wav"))

    def play_command_sound(self):

        print(self._name)

        file_path = "".join((os.getcwd(), "/sounds/", LANGUAGE, "/", self.__sound_filename))
        command_sound = sa.WaveObject.from_wave_file(file_path)
        command_sound.play()

    def get_command_name(self):

        return self._name


class VisibleCommand(Command):

    def __init__(self, parent_par, command_name_par, position_number_par, command_number_par):

        super(VisibleCommand, self).__init__(command_name_par=command_name_par)

        self.__id = "".join(("command_", str(position_number_par), "_", str(command_number_par)))

        self.__create_widget(parent_par=parent_par, position_number_par=position_number_par,
                             command_number_par=command_number_par)

    def __create_widget(self, parent_par, position_number_par, command_number_par):

        self.__label = Label(parent_par, text=self._name)
        self.__label.grid(row=command_number_par + 1, column=(position_number_par * 3) + 2, sticky=W)                     # +1, because in row 0 is name of position

        self.__is_selected = BooleanVar(value=True)
        self.__checkbox = ttk.Checkbutton(parent_par, variable=self.__is_selected,
            name="".join(("checkbox_", str(position_number_par), "_", str(command_number_par))))
        self.__checkbox.grid(row=command_number_par + 1, column=(position_number_par * 3) + 1)

    def switch_state(self):

        if self.__label["state"] == NORMAL:
            self.__label["state"] = DISABLED
            self.__checkbox["state"] = DISABLED

        else:
            self.__label["state"] = NORMAL
            self.__checkbox["state"] = NORMAL

    def is_selected(self):

        return self.__is_selected.get()

    def get_id(self):

        return self.__id

    def set_state(self, state_par):

        self.__is_selected.set(state_par)


class Application(Frame):

    def __init__(self, master):

        super(Application, self).__init__(master)
        self.grid()

        self.__saved_settings_file_name = "saved_settings.dat"
        self.__default_settings_file_name = "default_settings.dat"

        self.__all_positions = []
        self.__selected_positions = []
        self.__active_position = None

        self.__is_set_in_progress = False

        self.__duration_of_giving_command = 2
        self.__duration_to_begin = 0
        self.__duration_of_set = 0
        self.__duration_of_position = 0
        self.__duration_of_command = 0
        self.__duration_of_break = 0
        self.__number_of_sets = 0

        self.__duration_to_begin_remain = 0
        self.__duration_of_set_remain = 0
        self.__duration_of_position_remain = 0
        self.__duration_of_command_remain = 0
        self.__duration_of_break_remain = 0
        self.__number_of_sets_remain = 0

        self.__duration_of_position_max = 0
        self.__duration_of_position_min = 0
        self.__duration_of_command_max = 0
        self.__duration_of_command_min = 0

        self.__moment_of_start = None
        self.__moment_of_begin_set = None
        self.__moment_of_give_position = None
        self.__moment_of_give_command = None
        self.__moment_of_begin_break = None

        self.__timer_of_display_duration_loop = None
        self.__timer_of_workout_loop = None

        self.__load_language()
        self.__load_translations()

        self.__selected_language = StringVar(self)
        self.__selected_language.set(LANGUAGE)

        self.__command_up = Command("up")
        self.__command_down = Command("down")

        self.__create_widgets()
        self.__disable_widgets_when_start()

    def __load_language(self):

        global LANGUAGE

        file_with_selected_language = open("selected_language.txt", "r")
        LANGUAGE = file_with_selected_language.read()
        file_with_selected_language.close()

    def __save_language(self):

        if self.__selected_language.get() != LANGUAGE:
            file_with_selected_language = open("selected_language.txt", "w")
            file_with_selected_language.write(self.__selected_language.get())
            file_with_selected_language.close()

            self.__entry_of_given_command["state"] = NORMAL
            self.__entry_of_given_command.delete(0, "end")
            self.__entry_of_given_command.insert(0, TRANSLATIONS[self.__selected_language.get()]["restart_command"])

    def __load_translations(self):

        global TRANSLATIONS

        file_with_translations = open("translations.json", "r")
        string_with_translations = file_with_translations.read()
        file_with_translations.close()

        TRANSLATIONS = json.loads(string_with_translations)

    def __create_widgets(self):

        self.__create_widgets_of_positions_and_commands()
        self.__create_widgets_of_setting_parameters()
        self.__create_widgets_of_display_parameters()
        self.__create_widgets_of_display_commands()
        self.__create_widgets_of_select_language()
        self.__create_widgets_of_buttons()
        self.__create_widgets_of_informations()

    def __create_widgets_of_positions_and_commands(self):

        self.__create_frame_for_positions_and_commands()
        self.__create_positionss_with_commands_and_widgets(
            layout_of_positions_and_commands_par=LAYOUT_OF_POSITIONS_AND_COMMANDS)

    def __create_frame_for_positions_and_commands(self):

        self.__label_frame_for_positions_and_commands = \
            ttk.LabelFrame(self, text=TRANSLATIONS[LANGUAGE]["label_frame_for_positions_and_commands"])
        self.__label_frame_for_positions_and_commands.grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 0))

        self.__frame_for_positions_and_commands = Frame(self.__label_frame_for_positions_and_commands)                  # Frame inside LabelFrame, because in LabelFrame ipadx and ipady not working in every direction, but only to the right and down. LabelFrame don't support tuplets in padx (padx=(x, y) for internal widgets)
        self.__frame_for_positions_and_commands.grid(padx=5, pady=5)

    def __create_positionss_with_commands_and_widgets(self, layout_of_positions_and_commands_par):

        for position_number, position in enumerate(layout_of_positions_and_commands_par):
            new_position = Position(position_name_par=position["name"], position_number_par=position_number,
                                    layout_of_commands_par=position["commands"],
                                    parent_par=self.__frame_for_positions_and_commands)

            self.__all_positions.append(new_position)

    def __create_widgets_of_setting_parameters(self):

        self.__create_frame_for_setting_parameters()
        self.__create_labels_of_setting_parameters()
        self.__create_widgets_of_setting_duration_to_begin()
        self.__create_widgets_of_setting_duration_of_set()
        self.__create_widgets_of_setting_duration_of_position()
        self.__create_widgets_of_setting_duration_of_command()
        self.__create_widgets_of_setting_duration_of_break()
        self.__create_widgets_of_setting_number_of_sets()

    def __create_frame_for_setting_parameters(self):

        self.__label_frame_for_setting_parameters = \
            ttk.LabelFrame(self, text=TRANSLATIONS[LANGUAGE]["label_frame_for_setting_parameters"])
        self.__label_frame_for_setting_parameters.grid(row=1, column=0, rowspan=3, padx=(10, 5), pady=(10, 0))

        self.__frame_for_setting_parameters = Frame(self.__label_frame_for_setting_parameters)                          # Frame inside LabelFrame, because in LabelFrame ipadx and ipady not working in every direction, but only to the right and down. LabelFrame don't support tuplets in padx (padx=(x, y) for internal widgets)
        self.__frame_for_setting_parameters.grid(padx=5, pady=5)

    def __create_labels_of_setting_parameters(self):

        self.__label_of_value_base = Label(self.__frame_for_setting_parameters,
                                           text=TRANSLATIONS[LANGUAGE]["label_of_value_base"])
        self.__label_of_value_base.grid(row=0, column=0, columnspan=2, sticky=W)

        self.__label_of_randomization = Label(self.__frame_for_setting_parameters,
                                              text=TRANSLATIONS[LANGUAGE]["label_of_randomization"])
        self.__label_of_randomization.grid(row=0, column=3, columnspan=3, sticky=W)

    def __create_widgets_of_setting_duration_to_begin(self):

        self.__label_of_duration_to_begin_base = Label(self.__frame_for_setting_parameters,
                                                       text=TRANSLATIONS[LANGUAGE]["label_of_duration_to_begin_base"])
        self.__label_of_duration_to_begin_base.grid(row=1, column=0, sticky=W, padx=(15, 5))
        self.__spinbox_of_duration_to_begin = Spinbox(self.__frame_for_setting_parameters, from_=3, to=9999,
                                                      width=6, justify="right", name="spinbox_0",
                                                      command=self.__correct_input_settings)
        self.__spinbox_of_duration_to_begin.grid(row=1, column=1, padx=(0, 5))

        self.__label_of_duration_to_begin_minus = Label(self.__frame_for_setting_parameters, text="-")
        self.__label_of_duration_to_begin_minus.grid(row=1, column=3, sticky=W, padx=(15, 5))
        self.__spinbox_of_duration_to_begin_minus = Spinbox(self.__frame_for_setting_parameters, from_=0, to=9999,
                                                            width=6, justify="right", name="spinbox_1",
                                                            command=self.__correct_input_settings)
        self.__spinbox_of_duration_to_begin_minus.grid(row=1, column=4)

        self.__label_of_duration_to_begin_plus = Label(self.__frame_for_setting_parameters, text="+")
        self.__label_of_duration_to_begin_plus.grid(row=1, column=5, sticky=W, padx=(10, 5))
        self.__spinbox_of_duration_to_begin_plus = Spinbox(self.__frame_for_setting_parameters, from_=0, to=9999,
                                                           width=6, justify="right", name="spinbox_2",
                                                           command=self.__correct_input_settings)
        self.__spinbox_of_duration_to_begin_plus.grid(row=1, column=6)

    def __create_widgets_of_setting_duration_of_set(self):

        self.__label_of_duration_of_set_base = Label(self.__frame_for_setting_parameters,
                                                     text=TRANSLATIONS[LANGUAGE]["label_of_duration_of_set_base"])
        self.__label_of_duration_of_set_base.grid(row=2, column=0, sticky=W, padx=(15, 5))
        self.__spinbox_of_duration_of_set = Spinbox(self.__frame_for_setting_parameters, from_=3, to=9999,
                                                    width=6, justify="right", name="spinbox_3",
                                                    command=self.__correct_input_settings)
        self.__spinbox_of_duration_of_set.grid(row=2, column=1, padx=(0, 5))

        self.__label_of_duration_of_set_minus = Label(self.__frame_for_setting_parameters, text="-")
        self.__label_of_duration_of_set_minus.grid(row=2, column=3, sticky=W, padx=(15, 5))
        self.__spinbox_of_duration_of_set_minus = Spinbox(self.__frame_for_setting_parameters, from_=0, to=9999,
                                                          width=6, justify="right", name="spinbox_4",
                                                          command=self.__correct_input_settings)
        self.__spinbox_of_duration_of_set_minus.grid(row=2, column=4)

        self.__label_of_duration_of_set_plus = Label(self.__frame_for_setting_parameters, text="+")
        self.__label_of_duration_of_set_plus.grid(row=2, column=5, sticky=W, padx=(10, 5))
        self.__spinbox_of_duration_of_set_plus = Spinbox(self.__frame_for_setting_parameters, from_=0, to=9999,
                                                         width=6, justify="right", name="spinbox_5",
                                                         command=self.__correct_input_settings)
        self.__spinbox_of_duration_of_set_plus.grid(row=2, column=6)

    def __create_widgets_of_setting_duration_of_position(self):

        self.__label_of_duration_of_position_base = Label(self.__frame_for_setting_parameters,
            text=TRANSLATIONS[LANGUAGE]["label_of_duration_of_position_base"])
        self.__label_of_duration_of_position_base.grid(row=3, column=0, sticky=W, padx=(15, 5))
        self.__spinbox_of_duration_of_position = Spinbox(self.__frame_for_setting_parameters, from_=3, to=9999,
                                                         width=6, justify="right", name="spinbox_6",
                                                         command=self.__correct_input_settings)
        self.__spinbox_of_duration_of_position.grid(row=3, column=1, padx=(0, 5))

        self.__label_of_duration_of_position_minus = Label(self.__frame_for_setting_parameters, text="-")
        self.__label_of_duration_of_position_minus.grid(row=3, column=3, sticky=W, padx=(15, 5))
        self.__spinbox_of_duration_of_position_minus = Spinbox(self.__frame_for_setting_parameters, from_=0, to=9999,
                                                               width=6, justify="right", name="spinbox_7",
                                                               command=self.__correct_input_settings)
        self.__spinbox_of_duration_of_position_minus.grid(row=3, column=4)

        self.__label_of_duration_of_position_plus = Label(self.__frame_for_setting_parameters, text="+")
        self.__label_of_duration_of_position_plus.grid(row=3, column=5, sticky=W, padx=(10, 5))
        self.__spinbox_of_duration_of_position_plus = Spinbox(self.__frame_for_setting_parameters, from_=0, to=9999,
                                                              width=6, justify="right", name="spinbox_8",
                                                              command=self.__correct_input_settings)
        self.__spinbox_of_duration_of_position_plus.grid(row=3, column=6)

    def __create_widgets_of_setting_duration_of_command(self):

        self.__label_of_duration_of_command_base = Label(self.__frame_for_setting_parameters,
            text=TRANSLATIONS[LANGUAGE]["label_of_duration_of_command_base"])
        self.__label_of_duration_of_command_base.grid(row=4, column=0, sticky=W, padx=(15, 5))
        self.__spinbox_of_duration_of_command = Spinbox(self.__frame_for_setting_parameters, from_=3, to=9999,
                                                        width=6, justify="right", name="spinbox_9",
                                                        command=self.__correct_input_settings)
        self.__spinbox_of_duration_of_command.grid(row=4, column=1, padx=(0, 5))

        self.__label_of_duration_of_command_minus = Label(self.__frame_for_setting_parameters, text="-")
        self.__label_of_duration_of_command_minus.grid(row=4, column=3, sticky=W, padx=(15, 5))
        self.__spinbox_of_duration_of_command_minus = Spinbox(self.__frame_for_setting_parameters, from_=0, to=9999,
                                                              width=6, justify="right", name="spinbox_10",
                                                              command=self.__correct_input_settings,)
        self.__spinbox_of_duration_of_command_minus.grid(row=4, column=4)

        self.__label_of_duration_of_command_plus = Label(self.__frame_for_setting_parameters, text="+")
        self.__label_of_duration_of_command_plus.grid(row=4, column=5, sticky=W, padx=(10, 5))
        self.__spinbox_of_duration_of_command_plus = Spinbox(self.__frame_for_setting_parameters, from_=0, to=9999,
                                                             width=6, justify="right", name="spinbox_11",
                                                             command=self.__correct_input_settings)
        self.__spinbox_of_duration_of_command_plus.grid(row=4, column=6)

    def __create_widgets_of_setting_duration_of_break(self):

        self.__label_of_duration_of_break_base = Label(self.__frame_for_setting_parameters,
                                                       text=TRANSLATIONS[LANGUAGE]["label_of_duration_of_break_base"])
        self.__label_of_duration_of_break_base.grid(row=5, column=0, sticky=W, padx=(15, 5))
        self.__spinbox_of_duration_of_break = Spinbox(self.__frame_for_setting_parameters, from_=3, to=9999,
                                                      width=6, justify="right", name="spinbox_12",
                                                      command=self.__correct_input_settings)
        self.__spinbox_of_duration_of_break.grid(row=5, column=1, padx=(0, 5))

        self.__label_of_duration_of_break_minus = Label(self.__frame_for_setting_parameters, text="-")
        self.__label_of_duration_of_break_minus.grid(row=5, column=3, sticky=W, padx=(15, 5))
        self.__spinbox_of_duration_of_break_minus = Spinbox(self.__frame_for_setting_parameters, from_=0, to=9999,
                                                            width=6, justify="right", name="spinbox_13",
                                                            command=self.__correct_input_settings)
        self.__spinbox_of_duration_of_break_minus.grid(row=5, column=4)

        self.__label_of_duration_of_break_plus = Label(self.__frame_for_setting_parameters, text="+")
        self.__label_of_duration_of_break_plus.grid(row=5, column=5, sticky=W, padx=(10, 5))
        self.__spinbox_of_duration_of_break_plus = Spinbox(self.__frame_for_setting_parameters, from_=0, to=9999,
                                                           width=6, justify="right", name="spinbox_14",
                                                           command=self.__correct_input_settings)
        self.__spinbox_of_duration_of_break_plus.grid(row=5, column=6)

    def __create_widgets_of_setting_number_of_sets(self):

        self.__label_of_number_of_sets_base = Label(self.__frame_for_setting_parameters,
                                                    text=TRANSLATIONS[LANGUAGE]["label_of_number_of_sets_base"])
        self.__label_of_number_of_sets_base.grid(row=6, column=0, sticky=W, padx=(15, 5))
        self.__spinbox_of_number_of_sets = Spinbox(self.__frame_for_setting_parameters, from_=1, to=9999, width=6,
                                                   justify="right", name="spinbox_15",
                                                   command=self.__correct_input_settings)
        self.__spinbox_of_number_of_sets.grid(row=6, column=1, padx=(0, 5))

        self.__label_of_number_of_sets_minus = Label(self.__frame_for_setting_parameters, text="-")
        self.__label_of_number_of_sets_minus.grid(row=6, column=3, sticky=W, padx=(15, 5))
        self.__spinbox_of_number_of_sets_minus = Spinbox(self.__frame_for_setting_parameters, from_=0, to=9999,
                                                         width=6, justify="right", name="spinbox_16",
                                                         command=self.__correct_input_settings)
        self.__spinbox_of_number_of_sets_minus.grid(row=6, column=4)

        self.__label_of_number_of_sets_plus = Label(self.__frame_for_setting_parameters, text="+")
        self.__label_of_number_of_sets_plus.grid(row=6, column=5, sticky=W, padx=(10, 5))
        self.__spinbox_of_number_of_sets_plus = Spinbox(self.__frame_for_setting_parameters, from_=0, to=9999,
                                                        width=6, justify="right", name="spinbox_17",
                                                        command=self.__correct_input_settings)
        self.__spinbox_of_number_of_sets_plus.grid(row=6, column=6)

    def __create_widgets_of_display_parameters(self):

        self.__create_frame_for_display_parameters()
        self.__create_labels_of_display_parameters()
        self.__create_widgets_of_display_duration_to_begin()
        self.__create_widgets_of_display_duration_of_set()
        self.__create_widgets_of_display_duration_of_position()
        self.__create_widgets_of_display_duration_of_command()
        self.__create_widgets_of_display_duration_of_break()
        self.__create_widgets_of_display_number_of_sets()

    def __create_frame_for_display_parameters(self):

        self.__label_frame_for_display_parameters = \
            ttk.LabelFrame(self, text=TRANSLATIONS[LANGUAGE]["label_frame_for_display_parameters"])
        self.__label_frame_for_display_parameters.grid(row=1, column=1, rowspan=3, padx=5, pady=(10, 0))

        self.__frame_for_display_parameters = Frame(self.__label_frame_for_display_parameters)                          # Frame inside LabelFrame, because in LabelFrame ipadx and ipady not working in every direction, but only to the right and down. LabelFrame don't support tuplets in padx (padx=(x, y) for internal widgets)
        self.__frame_for_display_parameters.grid(padx=5, pady=5)

    def __create_labels_of_display_parameters(self):

        self.__label_of_value_drawn = Label(self.__frame_for_display_parameters,
                                            text=TRANSLATIONS[LANGUAGE]["label_of_value_drawn"])
        self.__label_of_value_drawn.grid(row=0, column=0, columnspan=2, sticky=W)

        self.__label_of_remain = Label(self.__frame_for_display_parameters,
                                       text=TRANSLATIONS[LANGUAGE]["label_of_remain"])
        self.__label_of_remain.grid(row=0, column=2, columnspan=2, sticky=W)

    def __create_widgets_of_display_duration_to_begin(self):

        self.__label_of_duration_to_begin_actual = Label(self.__frame_for_display_parameters,
                                                         text=TRANSLATIONS[LANGUAGE]["label_of_duration_to_begin_base"])
        self.__label_of_duration_to_begin_actual.grid(row=1, column=0, sticky=W, padx=(15, 5))

        self.__entry_of_duration_to_begin_drawn = Entry(self.__frame_for_display_parameters, width=6,
                                                        justify="center", bg=self.cget('bg'))
        self.__entry_of_duration_to_begin_drawn.grid(row=1, column=1, padx=(0, 5))

        self.__entry_of_duration_to_begin_remain = Entry(self.__frame_for_display_parameters, width=6,
                                                         justify="center", bg=self.cget('bg'))
        self.__entry_of_duration_to_begin_remain.grid(row=1, column=2, padx=(15, 0))

    def __create_widgets_of_display_duration_of_set(self):

        self.__label_of_duration_of_set_actual = Label(self.__frame_for_display_parameters,
                                                       text=TRANSLATIONS[LANGUAGE]["label_of_duration_of_set_base"])
        self.__label_of_duration_of_set_actual.grid(row=2, column=0, sticky=W, padx=(15, 5))

        self.__entry_of_duration_of_set_drawn = Entry(self.__frame_for_display_parameters, width=6,
                                                      justify="center", bg=self.cget('bg'))
        self.__entry_of_duration_of_set_drawn.grid(row=2, column=1, padx=(0, 5))

        self.__entry_of_duration_of_set_remain = Entry(self.__frame_for_display_parameters, width=6,
                                                       justify="center", bg=self.cget('bg'))
        self.__entry_of_duration_of_set_remain.grid(row=2, column=2, padx=(15, 0))

    def __create_widgets_of_display_duration_of_position(self):

        self.__label_of_duration_of_position_actual = \
            Label(self.__frame_for_display_parameters, text=TRANSLATIONS[LANGUAGE]["label_of_duration_of_position_base"])
        self.__label_of_duration_of_position_actual.grid(row=3, column=0, sticky=W, padx=(15, 5))

        self.__entry_of_duration_of_position_drawn = Entry(self.__frame_for_display_parameters, width=6,
                                                           justify="center", bg=self.cget('bg'))
        self.__entry_of_duration_of_position_drawn.grid(row=3, column=1, padx=(0, 5))

        self.__entry_of_duration_of_position_remain = Entry(self.__frame_for_display_parameters, width=6,
                                                            justify="center", bg=self.cget('bg'))
        self.__entry_of_duration_of_position_remain.grid(row=3, column=2, padx=(15, 0))

    def __create_widgets_of_display_duration_of_command(self):

        self.__label_of_duration_of_command_actual = \
            Label(self.__frame_for_display_parameters, text=TRANSLATIONS[LANGUAGE]["label_of_duration_of_command_base"])
        self.__label_of_duration_of_command_actual.grid(row=4, column=0, sticky=W, padx=(15, 5))

        self.__entry_of_duration_of_command_drawn = Entry(self.__frame_for_display_parameters, width=6,
                                                          justify="center", bg=self.cget('bg'))
        self.__entry_of_duration_of_command_drawn.grid(row=4, column=1, padx=(0, 5))

        self.__entry_of_duration_of_command_remain = Entry(self.__frame_for_display_parameters, width=6,
                                                           justify="center", bg=self.cget('bg'))
        self.__entry_of_duration_of_command_remain.grid(row=4, column=2, padx=(15, 0))

    def __create_widgets_of_display_duration_of_break(self):

        self.__label_of_duration_of_break_actual = Label(self.__frame_for_display_parameters,
                                                         text=TRANSLATIONS[LANGUAGE]["label_of_duration_of_break_base"])
        self.__label_of_duration_of_break_actual.grid(row=5, column=0, sticky=W, padx=(15, 5))

        self.__entry_of_duration_of_break_drawn = Entry(self.__frame_for_display_parameters, width=6,
                                                        justify="center", bg=self.cget('bg'))
        self.__entry_of_duration_of_break_drawn.grid(row=5, column=1, padx=(0, 5))

        self.__entry_of_duration_of_break_remain = Entry(self.__frame_for_display_parameters, width=6,
                                                         justify="center", bg=self.cget('bg'))
        self.__entry_of_duration_of_break_remain.grid(row=5, column=2, padx=(15, 0))

    def __create_widgets_of_display_number_of_sets(self):

        self.__label_of_number_of_sets_actual = Label(self.__frame_for_display_parameters,
                                                      text=TRANSLATIONS[LANGUAGE]["label_of_number_of_sets_base"])
        self.__label_of_number_of_sets_actual.grid(row=6, column=0, sticky=W, padx=(15, 5))

        self.__entry_of_number_of_sets_drawn = Entry(self.__frame_for_display_parameters, width=6,
                                                     justify="center", bg=self.cget('bg'))
        self.__entry_of_number_of_sets_drawn.grid(row=6, column=1, padx=(0, 5))

        self.__entry_of_number_of_sets_remain = Entry(self.__frame_for_display_parameters, width=6, justify="center",
                                                      bg=self.cget('bg'))
        self.__entry_of_number_of_sets_remain.grid(row=6, column=2, padx=(15, 0))

    def __create_widgets_of_display_commands(self):

        self.__label_frame_for_given_commands = \
            ttk.LabelFrame(self, text=TRANSLATIONS[LANGUAGE]["label_frame_for_given_commands"])
        self.__label_frame_for_given_commands.grid(row=1, column=2, padx=(5, 10), pady=(10, 0))
        self.__frame_for_given_commands = Frame(self.__label_frame_for_given_commands)                                  # Frame inside LabelFrame, because in LabelFrame ipadx and ipady not working in every direction, but only to the right and down. LabelFrame don't support tuplets in padx (padx=(x, y) for internal widgets)
        self.__frame_for_given_commands.grid(padx=5, pady=5)

        self.__label_of_given_position = \
            Label(self.__frame_for_given_commands, text=TRANSLATIONS[LANGUAGE]["label_of_given_position"])
        self.__label_of_given_position.grid(row=0, column=0, sticky=W, padx=(0, 5))
        self.__entry_of_given_position = Entry(self.__frame_for_given_commands, width=30,
                                               justify="center", bg=self.cget('bg'))
        self.__entry_of_given_position.grid(row=0, column=1)

        self.__label_of_given_command = \
            Label(self.__frame_for_given_commands, text=TRANSLATIONS[LANGUAGE]["label_of_given_command"])
        self.__label_of_given_command.grid(row=1, column=0, sticky=W, padx=(0, 5))
        self.__entry_of_given_command = Entry(self.__frame_for_given_commands, width=30,
                                              justify="center", bg=self.cget('bg'))
        self.__entry_of_given_command.grid(row=1, column=1)

    def __create_widgets_of_select_language(self):

        self.__label_frame_for_select_language = \
            ttk.LabelFrame(self, text=TRANSLATIONS[LANGUAGE]["label_frame_for_select_languege"])
        self.__label_frame_for_select_language.grid(row=2, column=2, padx=(5, 10), pady=(10, 0), sticky=N)
        self.__frame_for_select_language = Frame(self.__label_frame_for_select_language)
        self.__frame_for_select_language.grid(padx=5, pady=5)

        self.__label_of_actual_language = \
            Label(self.__frame_for_select_language, text=TRANSLATIONS[LANGUAGE]["label_of_actual_language"])
        self.__label_of_actual_language.grid(row=0, column=0, sticky=W, padx=(0, 5))

        self.__combobox_of_select_language = ttk.Combobox(self.__frame_for_select_language, width=35,
                                                          textvariable=self.__selected_language,
                                                          values=sorted(list(TRANSLATIONS.keys())))
        self.__combobox_of_select_language.grid(row=0, column=1)
        self.__combobox_of_select_language.bind("<<ComboboxSelected>>", lambda _: self.__save_language())

    def __create_widgets_of_buttons(self):

        self.__frame_for_buttons = Frame(self)
        self.__frame_for_buttons.grid(row=3, column=2, rowspan=2, padx=(5, 10), pady=(20, 15))

        self.__button_load = ttk.Button(self.__frame_for_buttons, text=TRANSLATIONS[LANGUAGE]["button_load"], width=12,
                                        command=partial(self.__load_settings, self.__saved_settings_file_name))
        self.__button_load.grid(row=0, column=0, padx=5, pady=5)

        self.__button_save = ttk.Button(self.__frame_for_buttons, text=TRANSLATIONS[LANGUAGE]["button_save"], width=12,
                                        command=self.__save_settings)
        self.__button_save.grid(row=0, column=1, padx=5, pady=5)

        self.__button_reset = ttk.Button(self.__frame_for_buttons, text=TRANSLATIONS[LANGUAGE]["button_reset"],width=12,
                                         command=partial(self.__load_settings, self.__default_settings_file_name))
        self.__button_reset.grid(row=0, column=2, padx=5, pady=5)

        self.__button_start = ttk.Button(self.__frame_for_buttons, text=TRANSLATIONS[LANGUAGE]["button_start"], width=12,
                                         command=self.__start_workout)
        self.__button_start.grid(row=1, column=0, padx=5, pady=5)

        self.__button_stop = ttk.Button(self.__frame_for_buttons, text=TRANSLATIONS[LANGUAGE]["button_stop"], width=12,
                                        command=self.__abort_workout)
        self.__button_stop.grid(row=1, column=1, padx=5, pady=5)

        self.__button_donate = ttk.Button(self.__frame_for_buttons, text=TRANSLATIONS[LANGUAGE]["button_donate"], width=12,
                                          command=self.__open_donation_url)
        self.__button_donate.grid(row=1, column=2, padx=5, pady=5)

    def __create_widgets_of_informations(self):

        self.__label_frame_for_informations = ttk.LabelFrame(self,
                                                             text=TRANSLATIONS[LANGUAGE]["label_frame_for_informations"])
        self.__label_frame_for_informations.grid(row=4, column=0, columnspan=2, padx=(10, 5), pady=10, sticky=NW)

        self.__frame_for_informations = ttk.Frame(self.__label_frame_for_informations)
        self.__frame_for_informations.grid(padx=5, pady=5)

        self.__label_of_contact = Label(self.__frame_for_informations, text=TRANSLATIONS[LANGUAGE]["label_of_contact"])
        self.__label_of_contact.grid(row=0, column=0, padx=(0, 5))

        self.__entry_of_mail = Entry(self.__frame_for_informations, width=27, justify="left", bg=self.cget('bg'),
                                     borderwidth=0)
        self.__entry_of_mail.grid(row=0, column=1)
        self.__entry_of_mail.insert(0, "bug-rancher@protonmail.com")

        self.__label_of_newest_version = Label(self.__frame_for_informations,
                                               text=TRANSLATIONS[LANGUAGE]["label_of_newest_version"])
        self.__label_of_newest_version.grid(row=0, column=2, padx=(15, 5))

        self.__label_of_website = Label(self.__frame_for_informations, cursor="hand2",
                                        text=TRANSLATIONS[LANGUAGE]["label_of_website"])
        self.__label_of_website.grid(row=0, column=3)

        font_of_link = font.Font(self.__label_of_website, self.__label_of_website.cget("font"))
        font_of_link.configure(underline=True)
        self.__label_of_website.configure(font=font_of_link)

        self.__label_of_website.bind("<Button-1>", lambda _: self.__open_release_url())

    def __disable_widgets_when_start(self):

        for child in self.__frame_for_display_parameters.children.values():
            child["state"] = DISABLED

        for child in self.__frame_for_given_commands.children.values():
            child["state"] = DISABLED

        self.__button_stop["state"] = DISABLED

    def __switch_widgets_state_when_start(self):

        for position in self.__all_positions:
            position.switch_state()

        for child in self.__frame_for_setting_parameters.children.values():
            child["state"] = DISABLED

        for child in self.__frame_for_display_parameters.children.values():
            child["state"] = NORMAL

        for child in self.__frame_for_given_commands.children.values():
            child["state"] = NORMAL

        for child in self.__frame_for_select_language.children.values():
            child["state"] = DISABLED

        self.__button_load["state"] = DISABLED
        self.__button_save["state"] = DISABLED
        self.__button_reset["state"] = DISABLED
        self.__button_start["state"] = DISABLED
        self.__button_stop["state"] = NORMAL
        self.__button_donate["state"] = DISABLED

    def __switch_widgets_state_when_stop(self):

        for postawa in self.__all_positions:
            postawa.switch_state()

        for child in self.__frame_for_setting_parameters.children.values():
            child["state"] = NORMAL

        for child in self.__frame_for_display_parameters.children.values():
            child["state"] = DISABLED

        for child in self.__frame_for_given_commands.children.values():
            child["state"] = DISABLED

        for child in self.__frame_for_select_language.children.values():
            child["state"] = NORMAL

        self.__button_load["state"] = NORMAL
        self.__button_save["state"] = NORMAL
        self.__button_reset["state"] = NORMAL
        self.__button_start["state"] = NORMAL
        self.__button_stop["state"] = DISABLED
        self.__button_donate["state"] = NORMAL

    def __correct_input_settings(self):

        self.__check_if_is_digit_and_in_spinbox_range()
        self.__check_if_in_value_range()

    def __check_if_is_digit_and_in_spinbox_range(self):

        spinboxes_to_check = [self.__spinbox_of_duration_to_begin, self.__spinbox_of_duration_to_begin_minus,
                              self.__spinbox_of_duration_to_begin_plus, self.__spinbox_of_duration_of_set,
                              self.__spinbox_of_duration_of_set_minus, self.__spinbox_of_duration_of_set_plus,
                              self.__spinbox_of_duration_of_position, self.__spinbox_of_duration_of_position_minus,
                              self.__spinbox_of_duration_of_position_plus, self.__spinbox_of_duration_of_command,
                              self.__spinbox_of_duration_of_command_minus, self.__spinbox_of_duration_of_command_plus,
                              self.__spinbox_of_duration_of_break, self.__spinbox_of_duration_of_break_minus,
                              self.__spinbox_of_duration_of_break_plus, self.__spinbox_of_number_of_sets,
                              self.__spinbox_of_number_of_sets_minus, self.__spinbox_of_number_of_sets_plus]

        for spinbox_to_check in spinboxes_to_check:

            input_value = spinbox_to_check.get()

            if not input_value.isdigit():
                spinbox_to_check.delete(0, "end")
                spinbox_to_check.insert(0, int(spinbox_to_check.cget("from")))

            elif float(input_value) < spinbox_to_check.cget("from"):
                spinbox_to_check.delete(0, "end")
                spinbox_to_check.insert(0, int(spinbox_to_check.cget("from")))

            elif float(input_value) > spinbox_to_check.cget("to"):
                spinbox_to_check.delete(0, "end")
                spinbox_to_check.insert(0, int(spinbox_to_check.cget("to")))

    def __check_if_in_value_range(self):

        if (int(self.__spinbox_of_duration_to_begin_minus.get()) > int(self.__spinbox_of_duration_to_begin.get())
                                                                   - int(self.__spinbox_of_duration_to_begin.cget("from"))):
            self.__spinbox_of_duration_to_begin_minus.delete(0, "end")
            self.__spinbox_of_duration_to_begin_minus.insert(0, int(self.__spinbox_of_duration_to_begin.get())
                                                                - int(self.__spinbox_of_duration_to_begin.cget("from")))

        if int(self.__spinbox_of_duration_of_set_minus.get()) > (int(self.__spinbox_of_duration_of_set.get())
                                                                 - self.__spinbox_of_duration_of_position.cget("from")):
            self.__spinbox_of_duration_of_set_minus.delete(0, "end")
            self.__spinbox_of_duration_of_set_minus.insert(0, int(self.__spinbox_of_duration_of_set.get())
                                                              - int(self.__spinbox_of_duration_of_position.cget("from")))

        if (int(self.__spinbox_of_duration_of_position.get()) > int(self.__spinbox_of_duration_of_set.get())
                                                                - int(self.__spinbox_of_duration_of_set_minus.get())):
            self.__spinbox_of_duration_of_position.delete(0, "end")
            self.__spinbox_of_duration_of_position.insert(0, int(self.__spinbox_of_duration_of_set.get())
                                                             - int(self.__spinbox_of_duration_of_set_minus.get()))

        if (int(self.__spinbox_of_duration_of_position_minus.get()) > int(self.__spinbox_of_duration_of_position.get())
                                                                      - int(self.__spinbox_of_duration_of_command.cget("from"))):
            self.__spinbox_of_duration_of_position_minus.delete(0, "end")
            self.__spinbox_of_duration_of_position_minus.insert(0, int(self.__spinbox_of_duration_of_position.get())
                                                                   - int(self.__spinbox_of_duration_of_command.cget("from")))

        if (int(self.__spinbox_of_duration_of_position_plus.get()) > int(self.__spinbox_of_duration_of_set.get())
                                                                     - int(self.__spinbox_of_duration_of_set_minus.get())
                                                                     - int(self.__spinbox_of_duration_of_position.get())):
            self.__spinbox_of_duration_of_position_plus.delete(0, "end")
            self.__spinbox_of_duration_of_position_plus.insert(0, int(self.__spinbox_of_duration_of_set.get())
                                                                  - int(self.__spinbox_of_duration_of_set_minus.get())
                                                                  - int(self.__spinbox_of_duration_of_position.get()))

        if (int(self.__spinbox_of_duration_of_command.get()) > int(self.__spinbox_of_duration_of_position.get())
                                                               - int(self.__spinbox_of_duration_of_position_minus.get())):
            self.__spinbox_of_duration_of_command.delete(0, "end")
            self.__spinbox_of_duration_of_command.insert(0, int(self.__spinbox_of_duration_of_position.get())
                                                            - int(self.__spinbox_of_duration_of_position_minus.get()))

        if (int(self.__spinbox_of_duration_of_command_minus.get()) > int(self.__spinbox_of_duration_of_command.get())
                                                                     - int(self.__spinbox_of_duration_of_command.cget("from"))):
            self.__spinbox_of_duration_of_command_minus.delete(0, "end")
            self.__spinbox_of_duration_of_command_minus.insert(0, int(self.__spinbox_of_duration_of_command.get())
                                                                  - int(self.__spinbox_of_duration_of_command.cget("from")))

        if (int(self.__spinbox_of_duration_of_command_plus.get()) > int(self.__spinbox_of_duration_of_position.get())
                                                                    - int(self.__spinbox_of_duration_of_position_minus.get())
                                                                    - int(self.__spinbox_of_duration_of_command.get())):
            self.__spinbox_of_duration_of_command_plus.delete(0, "end")
            self.__spinbox_of_duration_of_command_plus.insert(0, int(self.__spinbox_of_duration_of_position.get())
                                                                 - int(self.__spinbox_of_duration_of_position_minus.get())
                                                                 - int(self.__spinbox_of_duration_of_command.get()))

        if (int(self.__spinbox_of_duration_of_break_minus.get()) > int(self.__spinbox_of_duration_of_break.get())
                                                                   - int(self.__spinbox_of_duration_of_break.cget("from"))):
            self.__spinbox_of_duration_of_break_minus.delete(0, "end")
            self.__spinbox_of_duration_of_break_minus.insert(0, int(self.__spinbox_of_duration_of_break.get())
                                                                - int(self.__spinbox_of_duration_of_break.cget("from")))

        if (int(self.__spinbox_of_number_of_sets_minus.get()) > int(self.__spinbox_of_number_of_sets.get())
                                                                - int(self.__spinbox_of_number_of_sets.cget("from"))):
            self.__spinbox_of_number_of_sets_minus.delete(0, "end")
            self.__spinbox_of_number_of_sets_minus.insert(0, int(self.__spinbox_of_number_of_sets.get())
                                                             - int(self.__spinbox_of_number_of_sets.cget("from")))

    def __save_settings(self):

        settings = {}

        get_state_of_spinboxes(self, settings_par=settings)
        get_state_of_objects(objects_par=self.__all_positions, settings_par=settings)

        saved_settings_file = open("saved_settings.dat", "wb")
        pickle.dump(settings, saved_settings_file)
        saved_settings_file.close()

    def __load_settings(self, saved_settings_file_name_par):

        if os.path.isfile(saved_settings_file_name_par):
            saved_settings_file = open(saved_settings_file_name_par, "rb")
            settings = pickle.load(saved_settings_file)
            saved_settings_file.close()

            set_state_of_spinboxes(self, settings_par=settings)
            set_state_of_objects(objects_par=self.__all_positions, settings_par=settings)

    def __draw_value(self, value_base_par, value_minus_par, value_plus_par):

        deviation_minus = 0 - value_minus_par

        deviation = random.randrange(deviation_minus, value_plus_par + 1, 1)

        return value_base_par + deviation

    def __draw_duration_to_begin(self):

        value_base = int(self.__spinbox_of_duration_to_begin.get())
        value_minus = int(self.__spinbox_of_duration_to_begin_minus.get())
        value_plus = int(self.__spinbox_of_duration_to_begin_plus.get())

        self.__duration_to_begin = self.__draw_value(value_base_par=value_base, value_minus_par=value_minus,
                                                     value_plus_par=value_plus)

    def __draw_duration_of_set(self):

        value_base = int(self.__spinbox_of_duration_of_set.get())
        value_minus = int(self.__spinbox_of_duration_of_set_minus.get())
        value_plus = int(self.__spinbox_of_duration_of_set_plus.get())

        self.__duration_of_set = self.__draw_value(value_base_par=value_base, value_minus_par=value_minus,
                                                   value_plus_par=value_plus)

        print("duration of set:", self.__duration_of_set)

    def __draw_duration_of_position(self):

        value_base = int(self.__spinbox_of_duration_of_position.get())
        value_minus = int(self.__spinbox_of_duration_of_position_minus.get())
        value_plus = int(self.__spinbox_of_duration_of_position_plus.get())

        if len(self.__selected_positions) == 1:
            self.__duration_of_position = self.__duration_of_set_remain

        else:
            self.__duration_of_position = self.__draw_value(value_base_par=value_base, value_minus_par=value_minus,
                                                            value_plus_par=value_plus)

        print("duration of position:", self.__duration_of_position)

    def __draw_duration_of_command(self):

        value_base = int(self.__spinbox_of_duration_of_command.get())
        value_minus = int(self.__spinbox_of_duration_of_command_minus.get())
        value_plus = int(self.__spinbox_of_duration_of_command_plus.get())

        if self.__duration_of_position_remain > 0 and self.__active_position.get_number_of_selected_commands() == 0:
            self.__duration_of_command = self.__duration_of_position_remain

        else:
            self.__duration_of_command = self.__draw_value(value_base_par=value_base, value_minus_par=value_minus,
                                                           value_plus_par=value_plus)

        print("duration of command:", self.__duration_of_command)

    def __draw_duration_of_break(self):

        value_base = int(self.__spinbox_of_duration_of_break.get())
        value_minus = int(self.__spinbox_of_duration_of_break_minus.get())
        value_plus = int(self.__spinbox_of_duration_of_break_plus.get())

        self.__duration_of_break = self.__draw_value(value_base_par=value_base, value_minus_par=value_minus,
                                                     value_plus_par=value_plus)

        self.__moment_of_begin_break = datetime.datetime.now()

        print("duration of break:", self.__duration_of_break)

    def __draw_number_of_sets(self):

        value_base = int(self.__spinbox_of_number_of_sets.get())
        value_minus = int(self.__spinbox_of_number_of_sets_minus.get())
        value_plus = int(self.__spinbox_of_number_of_sets_plus.get())

        self.__number_of_sets = self.__draw_value(value_base_par=value_base, value_minus_par=value_minus,
                                                  value_plus_par=value_plus)

        self.__number_of_sets_remain = self.__number_of_sets

        print("number of sets:", self.__number_of_sets)

    def __draw_position(self):

        if len(self.__selected_positions) == 1:
            self.__active_position = self.__selected_positions[0]

        else:
            while True:
                new_position = random.choice(self.__selected_positions)

                if new_position != self.__active_position:
                    self.__active_position = new_position

                    break

    def __update_duration_remain(self):

        self.__update_duration_to_begin_remain()
        self.__update_duration_of_set_remain()
        self.__update_duration_of_position_remain()
        self.__update_duration_of_command_remain()
        self.__update_duration_of_brake_remain()

    def __update_duration_to_begin_remain(self):

        if not self.__moment_of_start:
            self.__duration_to_begin_remain = 0

        else:
            duration_remain = (self.__duration_to_begin - (datetime.datetime.now()
                                                           - self.__moment_of_start).total_seconds())

            if duration_remain > 0:
                self.__duration_to_begin_remain = duration_remain

            else:
                self.__duration_to_begin_remain = 0

    def __update_duration_of_set_remain(self):

        if not self.__moment_of_begin_set:
            self.__duration_of_set_remain = 0

        else:
            duration_remain = (self.__duration_of_set - (datetime.datetime.now()
                                                         - self.__moment_of_begin_set).total_seconds())

            if duration_remain > 0:
                self.__duration_of_set_remain = duration_remain

            else:
                self.__duration_of_set_remain = 0

    def __update_duration_of_position_remain(self):

        if not self.__moment_of_give_position:
            self.__duration_of_position_remain = 0

        else:
            duration_remain = (self.__duration_of_position - (datetime.datetime.now()
                                                              - self.__moment_of_give_position).total_seconds())

            if self.__duration_of_set_remain >= duration_remain > 0:
                self.__duration_of_position_remain = duration_remain

            elif duration_remain > self.__duration_of_set_remain:
                self.__duration_of_position_remain = self.__duration_of_set_remain

            else:
                self.__duration_of_position_remain = 0

    def __update_duration_of_command_remain(self):

        if not self.__moment_of_give_command:
            self.__duration_of_command_remain = 0

        else:
            duration_remain = (self.__duration_of_command - (datetime.datetime.now()
                                                             - self.__moment_of_give_command).total_seconds())

            if duration_remain > self.__duration_of_position_remain and self.__duration_of_position_remain != 0:
                self.__duration_of_command_remain = self.__duration_of_position_remain

            elif duration_remain > 0:
                self.__duration_of_command_remain = duration_remain

            else:
                self.__duration_of_command_remain = 0

    def __update_duration_of_brake_remain(self):

        if not self.__moment_of_begin_break:
            self.__duration_of_break_remain = 0

        else:
            duration_remain = (self.__duration_of_break - (datetime.datetime.now()
                                                           - self.__moment_of_begin_break).total_seconds())

            if duration_remain > 0:
                self.__duration_of_break_remain = duration_remain

            else:
                self.__duration_of_break_remain = 0

    def __start_display_duration_loop(self):

        self.__timer_of_display_duration_loop = Timer(1, self.__start_display_duration_loop)
        self.__timer_of_display_duration_loop.start()

        self.__display_duration_drawn()
        self.__display_duration_remain()

    def __display_duration_drawn(self):

        self.__entry_of_duration_to_begin_drawn.delete(0, "end")
        self.__entry_of_duration_to_begin_drawn.insert(0, self.__duration_to_begin)

        self.__entry_of_duration_of_set_drawn.delete(0, "end")
        self.__entry_of_duration_of_set_drawn.insert(0, self.__duration_of_set)

        self.__entry_of_duration_of_position_drawn.delete(0, "end")
        self.__entry_of_duration_of_position_drawn.insert(0, round(self.__duration_of_position))

        self.__entry_of_duration_of_command_drawn.delete(0, "end")
        self.__entry_of_duration_of_command_drawn.insert(0, round(self.__duration_of_command))

        self.__entry_of_duration_of_break_drawn.delete(0, "end")
        self.__entry_of_duration_of_break_drawn.insert(0, self.__duration_of_break)

        self.__entry_of_number_of_sets_drawn.delete(0, "end")
        self.__entry_of_number_of_sets_drawn.insert(0, self.__number_of_sets)

    def __display_duration_remain(self):

        self.__entry_of_duration_to_begin_remain.delete(0, "end")
        self.__entry_of_duration_to_begin_remain.insert(0, round(self.__duration_to_begin_remain))

        self.__entry_of_duration_of_set_remain.delete(0, "end")
        self.__entry_of_duration_of_set_remain.insert(0, round(self.__duration_of_set_remain))

        self.__entry_of_duration_of_position_remain.delete(0, "end")
        self.__entry_of_duration_of_position_remain.insert(0, round(self.__duration_of_position_remain))

        self.__entry_of_duration_of_command_remain.delete(0, "end")
        self.__entry_of_duration_of_command_remain.insert(0, round(self.__duration_of_command_remain))

        self.__entry_of_duration_of_break_remain.delete(0, "end")
        self.__entry_of_duration_of_break_remain.insert(0, round(self.__duration_of_break_remain))

        self.__entry_of_number_of_sets_remain.delete(0, "end")
        self.__entry_of_number_of_sets_remain.insert(0, self.__number_of_sets_remain)

    def __start_workout(self):

        self.__check_selection_of_positions()
        self.__check_selection_of_commands()

        if len(self.__selected_positions) > 0:
            self.__switch_widgets_state_when_start()
            self.__reset_values()

            self.__moment_of_start = datetime.datetime.now()
            self.__calculate_duration_max_and_min()
            self.__draw_duration_to_begin()
            self.__draw_number_of_sets()

            self.__start_display_duration_loop()
            self.__start_workout_loop()

    def __calculate_duration_max_and_min(self):

        self.__duration_of_position_max = (int(self.__spinbox_of_duration_of_position.get())
                                           + int(self.__spinbox_of_duration_of_position_plus.get()))
        self.__duration_of_position_min = (int(self.__spinbox_of_duration_of_position.get())
                                           - int(self.__spinbox_of_duration_of_position_minus.get()))

        self.__duration_of_command_max = (int(self.__spinbox_of_duration_of_command.get())
                                          + int(self.__spinbox_of_duration_of_command_plus.get()))
        self.__duration_of_command_min = (int(self.__spinbox_of_duration_of_command.get())
                                          - int(self.__spinbox_of_duration_of_command_minus.get()))

    def __reset_values(self):

        self.__duration_to_begin = 0
        self.__duration_of_set = 0
        self.__duration_of_position = 0
        self.__duration_of_command = 0
        self.__duration_of_break = 0
        self.__number_of_sets = 0

        self.__duration_of_set_remain = 0
        self.__duration_of_position_remain = 0
        self.__duration_of_command_remain = 0
        self.__duration_of_break_remain = 0
        self.__number_of_sets_remain = 0

        self.__duration_of_position_max = 0
        self.__duration_of_position_min = 0
        self.__duration_of_command_max = 0
        self.__duration_of_command_min = 0

        self.__moment_of_start = None
        self.__moment_of_begin_set = None
        self.__moment_of_give_position = None
        self.__moment_of_give_command = None
        self.__moment_of_begin_break = None

        self.__is_set_in_progress = False

    def __check_selection_of_positions(self):

        del self.__selected_positions[:]

        for position in self.__all_positions:
            if position.is_selected():
                self.__selected_positions.append(position)

    def __check_selection_of_commands(self):

        for position in self.__selected_positions:
            position.check_selection_of_commands()

    def __start_workout_loop(self):

        self.__timer_of_workout_loop = Timer(0.1, self.__start_workout_loop)
        self.__timer_of_workout_loop.start()

        self.__update_duration_remain()

        if self.__duration_to_begin_remain <= 0:

            if (self.__number_of_sets_remain > 0 and self.__duration_of_set_remain <=0
                    and self.__duration_of_position_remain <= 0 and self.__duration_of_command_remain <= 0
                    and self.__duration_of_break_remain <= 0 and not self.__is_set_in_progress):

                self.__begin_set()

            elif (self.__number_of_sets_remain > 0 and self.__duration_of_set_remain <= 0
                  and self.__duration_of_position_remain <= 0 and self.__duration_of_command_remain <= 0
                  and self.__duration_of_break_remain <= 0 and self.__is_set_in_progress):

                self.__begin_break()

            elif (self.__duration_of_set_remain > self.__duration_of_giving_command
                  and self.__duration_of_position_remain <= 0 and self.__duration_of_command_remain <= 0
                  and self.__duration_of_break_remain <= 0):

                self.__give_position()

            elif (self.__duration_of_position_remain > self.__duration_of_giving_command
                  and self.__duration_of_command_remain <= 0 and self.__duration_of_break_remain <= 0):

                self.__give_command()

            elif (self.__number_of_sets_remain <= 0 and self.__duration_of_set_remain <= 0
                  and self.__duration_of_position_remain <= 0 and self.__duration_of_command_remain <= 0
                  and self.__duration_of_break_remain <= 0):

                self.__end_workout()

    def __begin_set(self):

        self.__is_set_in_progress = True

        self.__moment_of_begin_set = datetime.datetime.now()
        self.__draw_duration_of_set()
        self.__update_duration_remain()

        self.__moment_of_give_command = datetime.datetime.now()
        self.__draw_duration_of_command()
        self.__update_duration_remain()

        self.__command_up.play_command_sound()
        self.__entry_of_given_command.delete(0, "end")
        self.__entry_of_given_command.insert(0, self.__command_up.get_command_name())

        self.__number_of_sets_remain -= 1

    def __begin_break(self):

        self.__is_set_in_progress = False

        self.__moment_of_begin_break = datetime.datetime.now()
        self.__draw_duration_of_break()

        self.__command_down.play_command_sound()
        self.__entry_of_given_position.delete(0, "end")
        self.__entry_of_given_command.delete(0, "end")
        self.__entry_of_given_command.insert(0, self.__command_down.get_command_name())

    def __give_position(self):

        self.__draw_position()
        self.__active_position.play_position_sound()
        self.__entry_of_given_position.delete(0, "end")
        self.__entry_of_given_command.delete(0, "end")
        self.__entry_of_given_position.insert(0, self.__active_position.get_position_name())

        self.__moment_of_give_position = datetime.datetime.now()
        self.__draw_duration_of_position()
        self.__update_duration_remain()

        self.__moment_of_give_command = datetime.datetime.now()
        self.__draw_duration_of_command()
        self.__update_duration_remain()

    def __give_command(self):

        self.__active_position.draw_command()
        self.__active_position.play_command_sound()
        self.__entry_of_given_command.delete(0, "end")
        self.__entry_of_given_command.insert(0, self.__active_position.get_command_name())

        self.__moment_of_give_command = datetime.datetime.now()
        self.__draw_duration_of_command()
        self.__update_duration_remain()

    def __end_workout(self):

        self.__command_down.play_command_sound()
        self.__abort_workout()

    def __abort_workout(self):

        self.__cancel_timers()
        self.__clear_entries()
        self.__switch_widgets_state_when_stop()

    def __cancel_timers(self):

        timers_to_cancel = [self.__timer_of_display_duration_loop, self.__timer_of_workout_loop]

        for timer in timers_to_cancel:
            try:
                timer.cancel()
            except:
                pass

    def __clear_entries(self):

        self.__entry_of_duration_to_begin_drawn.delete(0, "end")
        self.__entry_of_duration_of_set_drawn.delete(0, "end")
        self.__entry_of_duration_of_position_drawn.delete(0, "end")
        self.__entry_of_duration_of_command_drawn.delete(0, "end")
        self.__entry_of_duration_of_break_drawn.delete(0, "end")
        self.__entry_of_number_of_sets_drawn.delete(0, "end")

        self.__entry_of_duration_to_begin_remain.delete(0, "end")
        self.__entry_of_duration_of_set_remain.delete(0, "end")
        self.__entry_of_duration_of_position_remain.delete(0, "end")
        self.__entry_of_duration_of_command_remain.delete(0, "end")
        self.__entry_of_duration_of_break_remain.delete(0, "end")
        self.__entry_of_number_of_sets_remain.delete(0, "end")

        self.__entry_of_given_position.delete(0, "end")
        self.__entry_of_given_command.delete(0, "end")

    def __open_donation_url(self):

        webbrowser.open("https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=ESLD4GLMAZJL2",
                        new=0, autoraise=True)

    def __open_release_url(self):

        webbrowser.open("https://github.com/bug-rancher/the_drill/releases", new=0, autoraise=True)


# Create main window
root = Tk()

# Modify window
root.title("The Drill v1.0.1")
root.resizable(False, False)

# add a main frame
app = Application(root)
app.grid()

# start loop of events
root.mainloop()