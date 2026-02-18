from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, StringProperty, NumericProperty, ObjectProperty, BooleanProperty
from kivy.uix.popup import Popup
from kivy.clock import Clock
import json
import os
from datetime import date

class HabitWidget(BoxLayout):
    habit_index = NumericProperty(0)
    habit_name = StringProperty('')
    completed = BooleanProperty(False)
    toggle_callback = ObjectProperty(None)
    delete_callback = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.habit_index = kwargs.pop('habit_index', 0)
        self.habit_name = kwargs.pop('habit_name', '')
        self.completed = kwargs.pop('completed', False)
        self.toggle_callback = kwargs.pop('toggle_callback', None)
        self.delete_callback = kwargs.pop('delete_callback', None)

    def toggle(self, value):
        if self.toggle_callback:
            self.toggle_callback(self.habit_index, value)

    def delete(self):
        if self.delete_callback:
            self.delete_callback(self.habit_index)


class AddHabitPopup(Popup):
    habit_name = StringProperty('')
    add_callback = ObjectProperty(None)

    def __init__(self, add_callback, **kwargs):
        super().__init__(**kwargs)
        self.add_callback = add_callback
        self.title = "Новая привычка"
        self.size_hint = (0.8, 0.3)

    def add_habit(self):
        if self.habit_name.strip():
            self.add_callback(self.habit_name.strip())
            self.dismiss()
            self.habit_name = ''

class HabitRoot(BoxLayout):
    habits_data = ListProperty([])
    today = StringProperty('')
    progress_value = NumericProperty(0)
    progress_max = NumericProperty(1)
    progress_text = StringProperty('Прогресс: 0/0')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.today = date.today().strftime("%d.%m.%Y")

        self.load_habits()
        self.update_progress()
        Clock.schedule_once(lambda dt: self.update_habits_list(), 0.1)

    def load_habits(self):
        if os.path.exists('habits.json'):
            try:
                with open('habits.json', 'r', encoding='utf-8') as f:
                    self.habits_data = json.load(f)
            except Exception as e:
                print(f"Ошибка загрузки: {e}")
                self.create_default_habits()
        else:
            self.create_default_habits()

    def create_default_habits(self):
        self.habits_data = [
            {"name": "Утренняя зарядка", "completed": False},
            {"name": "Чтение 15 минут", "completed": False},
            {"name": "Выпить 2л воды", "completed": False}
        ]
        self.save_habits()

    def save_habits(self):
        try:
            with open('habits.json', 'w', encoding='utf-8') as f:
                json.dump(self.habits_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения: {e}")

    def update_habits_list(self):
        habits_container = self.ids.habits_container
        habits_container.clear_widgets()

        for i, habit in enumerate(self.habits_data):
            habit_widget = HabitWidget(
                habit_index=i,
                habit_name=habit['name'],
                completed=habit['completed'],
                toggle_callback=self.toggle_habit,
                delete_callback=self.delete_habit
            )
            habits_container.add_widget(habit_widget)

    def get_completed_count(self):
        count = 0
        for habit in self.habits_data:
            if isinstance(habit, dict) and habit.get('completed', False):
                count += 1
        return count

    def update_progress(self):
        total = len(self.habits_data)
        completed = self.get_completed_count()

        self.progress_max = total if total > 0 else 1
        self.progress_value = completed
        self.progress_text = f"Прогресс: {completed}/{total}"

    def toggle_habit(self, index, value):
        if 0 <= index < len(self.habits_data):
            self.habits_data[index]['completed'] = value
            self.update_progress()
            self.save_habits()
            self.update_habits_list()

    def delete_habit(self, index):
        if 0 <= index < len(self.habits_data):
            self.habits_data.pop(index)
            self.update_progress()
            self.update_habits_list()
            self.save_habits()

    def add_new_habit(self, name):
        new_habit = {
            "name": name,
            "completed": False
        }
        self.habits_data.append(new_habit)
        self.update_progress()
        self.update_habits_list()
        self.save_habits()

    def show_add_popup(self):
        popup = AddHabitPopup(self.add_new_habit)
        popup.open()

class HabitTrackerApp(App):
    def build(self):
        return HabitRoot()


if __name__ == '__main__':
    HabitTrackerApp().run()