from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.graphics import Color, Rectangle
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Line
from datetime import datetime
import os

class AlarmApp(App):
    def build(self):
        self.alarms = []  # List of alarms

        # Main layout
        self.main_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        with self.main_layout.canvas.before:
            Color(0, 0.5, 0, 1)  # Dark green background
            self.bg_rect = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
        self.main_layout.bind(size=self.update_bg_rect, pos=self.update_bg_rect)

        # Display current time
        self.current_time_label = Label(
            text=self.get_current_time(),
            size_hint=(1, 0.2),
            font_size=24,
            color=(0, 0, 0.5, 1),  # Dark blue text
        )
        self.main_layout.add_widget(self.current_time_label)

        # Update current time every second
        Clock.schedule_interval(self.update_current_time, 1)

        # Number of alarms
        self.title_label = Label(
            text="\nNumber of Alarms: 0",
            size_hint=(1, 0.2),
            font_size=20,
            color=(0, 0, 0.5, 1),  # Dark blue text
        )
        self.main_layout.add_widget(self.title_label)

        # Set alarm button
        self.set_alarm_button = Button(
            text="Set Alarm",
            size_hint=(1, 0.2),
            background_color=[0.6, 0.4, 0.8, 1],
            font_size=18,
        )
        self.set_alarm_button.bind(on_press=self.open_alarm_window)
        self.main_layout.add_widget(self.set_alarm_button)

        # Check alarms every second
        Clock.schedule_interval(self.check_alarms, 1)

        return self.main_layout

    def update_bg_rect(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos

    def get_current_time(self):
        return datetime.now().strftime("%I:%M:%S %p")  # 12-hour format with AM/PM

    def update_current_time(self, dt):
        self.current_time_label.text = self.get_current_time()

    def open_alarm_window(self, instance):
        self.alarm_window = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Input fields for time components
        time_layout = BoxLayout(orientation="horizontal", spacing=5, size_hint=(1, 0.2))

        self.hour_input = TextInput(
            hint_text="HH",
            size_hint=(0.15, 1),  # Smaller size
            multiline=False,
            font_size=18,
        )
        time_layout.add_widget(self.hour_input)

        self.minute_input = TextInput(
            hint_text="MM",
            size_hint=(0.15, 1),  # Smaller size
            multiline=False,
            font_size=18,
        )
        time_layout.add_widget(self.minute_input)

        self.second_input = TextInput(
            hint_text="SS",
            size_hint=(0.15, 1),
            multiline=False,
            font_size=18,
        )
        time_layout.add_widget(self.second_input)

        self.period_input = TextInput(
            hint_text="AM/PM",
            size_hint=(0.15, 1),
            multiline=False,
            font_size=18,
        )
        time_layout.add_widget(self.period_input)

        self.alarm_window.add_widget(time_layout)

        # Record sound button
        self.record_button = Button(
            text="Record Sound",
            size_hint=(1, 0.2),
            background_color=[0.6, 0.4, 0.8, 1],
            font_size=18,
        )
        self.record_button.bind(on_press=self.open_record_window)
        self.alarm_window.add_widget(self.record_button)

        # Save alarm button
        self.save_button = Button(
            text="Save Alarm",
            size_hint=(1, 0.2),
            background_color=[0.6, 0.4, 0.8, 1],
            font_size=18,
        )
        self.save_button.bind(on_press=self.save_alarm)
        self.alarm_window.add_widget(self.save_button)

        # Add alarm window to the main layout
        self.main_layout.clear_widgets()
        self.main_layout.add_widget(self.alarm_window)

    def open_record_window(self, instance):
        # Create a popup window for recording
        self.record_popup = Popup(title="Recording Sound", size_hint=(0.8, 0.5))

        record_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Add a visual effect for recording (e.g., moving lines)
        self.visualizer = Widget()
        with self.visualizer.canvas:
            Color(1, 0, 0, 1)
            self.line = Line(points=[0, 0, 50, 100, 100, 0], width=2)
        record_layout.add_widget(self.visualizer)

        # Start recording
        self.sound_file = f"alarm_sound_{len(self.alarms) + 1}.wav"
        os.system(f"arecord -d 10 -f cd {self.sound_file}")  # Record for 10 seconds

        # Close button
        close_button = Button(text="Stop Recording", size_hint=(1, 0.2))
        close_button.bind(on_press=self.close_record_popup)
        record_layout.add_widget(close_button)

        self.record_popup.content = record_layout
        self.record_popup.open()

    def close_record_popup(self, instance):
        self.record_popup.dismiss()

    def save_alarm(self, instance):
        hour = self.hour_input.text.strip()
        minute = self.minute_input.text.strip()
        second = self.second_input.text.strip()
        period = self.period_input.text.strip().upper()

        if hour.isdigit() and minute.isdigit() and second.isdigit() and period in ["AM", "PM"]:
            alarm_time = f"{hour.zfill(2)}:{minute.zfill(2)}:{second.zfill(2)} {period}"
            self.alarms.append({"time": alarm_time, "sound": self.sound_file})
            self.title_label.text = f"\nNumber of Alarms: {len(self.alarms)}"

        # Return to main layout
        self.main_layout.clear_widgets()
        self.main_layout.add_widget(self.current_time_label)
        self.main_layout.add_widget(self.title_label)
        self.main_layout.add_widget(self.set_alarm_button)

    def check_alarms(self, dt):
        current_time = datetime.now().strftime("%I:%M:%S %p")
        for alarm in self.alarms:
            if alarm["time"] == current_time:
                self.trigger_alarm(alarm)
                self.alarms.remove(alarm)
                self.title_label.text = f"\nNumber of Alarms: {len(self.alarms)}"

    def trigger_alarm(self, alarm):
        # Trigger alarm notification
        self.main_layout.clear_widgets()

        self.alarm_label = Label(
            text=f"Alarm! Time: {alarm['time']}",
            font_size=24,
            color=(1, 0, 0, 1),
        )
        self.main_layout.add_widget(self.alarm_label)

        # Start alternating background colors
        self.is_red = True
        self.alarm_event = Clock.schedule_interval(self.alternate_background, 0.5)

        # Play notification sound
        sound_file = alarm["sound"]
        if os.path.exists(sound_file):
            sound = SoundLoader.load(sound_file)
            if sound:
                sound.play()
        else:
            self.alarm_label.text += "\n(Sound file missing)"

    def alternate_background(self, dt):
        if self.is_red:
            self.main_layout.canvas.before.clear()
            with self.main_layout.canvas.before:
                Color(0, 0.5, 0, 1)  # Green
                self.bg_rect = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
        else:
            self.main_layout.canvas.before.clear()
            with self.main_layout.canvas.before:
                Color(1, 0, 0, 1)  # Red
                self.bg_rect = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
        self.is_red = not self.is_red

if __name__ == "__main__":
    AlarmApp().run()
