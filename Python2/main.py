from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.properties import StringProperty, NumericProperty
from random import randint
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore
from kivy.uix.popup import Popup

class MenuScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

    def on_enter(self, *args):
        app.save_prog()

    def show_settings(self):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Додайте елементи у вікно настройок, наприклад, поле для введення нового значення життя планет
        hp_input = TextInput(hint_text='Enter new planet HP', multiline=False)
        content.add_widget(hp_input)

        # Додайте кнопку для збереження змін і закриття вікна
        save_button = Button(text='Save', size_hint_y=None, height=40)
        content.add_widget(save_button)

        # Створіть Popup і покажіть його
        popup = Popup(title='Settings', content=content, size_hint=(None, None), size=(400, 400))
        popup.open()

        def save_settings(instance):
            # Отримайте значення HP і змініть життя планет
            new_hp = int(hp_input.text) if hp_input.text else None
            if new_hp is not None:
                planet = app.root.get_screen('game').ids.planet
                if planet:
                    planet.hp = new_hp
                    planet.new_planet()

            popup.dismiss()

        save_button.bind(on_release=save_settings)


class GameScreen(Screen):
    points = NumericProperty(0)

    def __init__(self, **kw):
        super().__init__(**kw)

    def on_enter(self, *args):
        data = app.load_prog()
        planet = self.ids.planet
        if planet:
            planet.new_planet(data)
        return super().on_enter(*args)


class Planet(Image):
    points = NumericProperty(0)
    is_anim = False
    hp = None
    planet = None
    planet_index = 0
    mult = 1

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and not self.is_anim:
            screen_manager = App.get_running_app().root
            game_screen = screen_manager.get_screen('game')
            game_screen.points += (1*self.mult)
            self.points += (1*self.mult)
            self.parent.parent.points = self.points
            self.hp -= 1

            if self.hp <= 0:
                self.parent.parent.points = self.points
                self.break_planet()
                app.save_prog()
            else:
                x = self.x
                y = self.y
                size = self.size.copy()
                anim = Animation(size=(size[0]*1.2, size[1]*1.2), d=.1, t='out_back') + Animation(size=(size[0], size[1]), d=.1)
                anim.start(self)
                self.is_anim = True
                anim.on_complete = lambda *arg: setattr(self, 'is_anim', False) 
                self.new_planet()
        return super().on_touch_down(touch)

    def new_planet(self, *args):
        data = app.load_prog()
        if data["planet"] is None:
            self.planet = app.LEVELS[randint(0, len(app.LEVELS)-1)]
            self.points = data['points']
        else:
            self.planet = data["planet"]
            self.points = data['points']

        self.parent.parent.parent.points = self.points
        self.hp = app.PLANETS[self.planet]['hp']
        self.source = app.PLANETS[self.planet]['source']
        self.size = app.PLANETS[self.planet]['size']
        size = (self.size[0], self.size[1])
        self.size = size[0], size[1]
        self.center = self.parent.center
        anim = Animation(opacity=1, d=0.3)
        anim &= Animation(size=(self.size[0]/1.5, self.size[1]/1.5), d=.2, t='out_back')
        anim &= Animation(center=self.parent.center, d=.3)
        anim.start(self)
        anim.on_complete = lambda *arg: setattr(self, 'is_anim', False)

    def break_planet(self):
        self.is_anim = True
        anim = Animation(size=(self.size[0]*2, self.size[1]*2), d=.2)
        anim &= Animation(center=self.parent.center, d=.2)
        anim &= Animation(opacity=0, d=.3)

        anim.start(self)
        anim.on_complete = Clock.schedule_once(self.new_planet, .5)


class ShopScreen(Screen):
    pass


class MainApp(App):
    storage = None
    SHOP = {"mult": 1}
    LEVELS = ['Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']
        
    PLANETS = {
         'Mercury': {"source": 'assets/planets/1.png', 'hp': 1, "size": (200, 200)},
         'Venus': {"source": 'assets/planets/2.png', 'hp': 2, "size": (200, 200)},
         'Earth': {"source": 'assets/planets/3.png', 'hp': 3, "size": (200, 200)},
         'Mars': {"source": 'assets/planets/4.png', 'hp': 4, "size": (200, 200)},
         'Jupiter': {"source": 'assets/planets/5.png', 'hp': 5, "size": (200, 200)},
         'Saturn': {"source": 'assets/planets/6.png', 'hp': 6, "size": (200, 200)},
         'Uranus': {"source": 'assets/planets/7.png', 'hp': 7, "size": (200, 200)},
         'Neptune': {"source": 'assets/planets/8.png', 'hp': 10, "size": (200, 200)},
    }

    def save_prog(self):
        hp = int(Planet.hp) if Planet.hp is not None else 0
        mult = int(Planet.mult) if Planet.mult is not None else 0
        points = int(Planet.points) if Planet.points is not None else 0

        app.storage.put('progress', 
                        planet=Planet.planet,
                        hp=hp,
                        planet_index=Planet.planet_index,
                        mult=mult,
                        points=points)


            
    def build(self):
        # Ініціалізуємо сховище, якщо воно ще не було створено
        self.storage = JsonStore('progress.json')
        sm = ScreenManager(transition=FadeTransition(duration=1))
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(ShopScreen(name='shop'))
        return sm

        
    def load_prog(self):
        if self.storage.exists("progress"):
            return self.storage.get("progress")
        else:
            return {"planet": None, "hp": None, "planet_index": None, "mult": None, "points": 0}

if __name__ == '__main__':
    app = MainApp()
    app.run()
