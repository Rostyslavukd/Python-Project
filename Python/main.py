from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.window import Window
from kivy.utils import platform

from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.properties import StringProperty, NumericProperty
from random import shuffle, choice, randint
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore
from kivy.uix.popup import Popup
from kivy.base import stopTouchApp
from kivy.uix.widget import Widget

class MenuScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

    def on_enter(self, *args):
        app.save_prog


class GameScreen(Screen):
    points = NumericProperty(0)

    def on_enter(self, *args):
        data = app.load_prog()
        self.ids.planet.new_planet(data)
        return super().on_enter(*args)


    

class Planet(Image):
    # Останнє відоме значення points
    points = NumericProperty(0)

    # Останнє відоме значення planet
    planet = StringProperty('')

    is_anim = False
    hp = None

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and not self.is_anim:
            self.parent.parent.parent.points += (1 * self.mult)
            self.points += (1 * self.mult)

            # Перевірка, чи існує значення hp
            if self.hp is not None:
                # Зменшення hp тільки після завершення анімації
                def on_animation_complete(animation, widget):
                    widget.hp -= 1
                    if widget.hp <= 0:
                        widget.break_planet()
                        app.save_prog()

                # Створення анімації
                size = self.size.copy()
                anim = Animation(
                    size=(size[0] * 1.2, size[1] * 1.2), d=.1, t='out_back') + Animation(size=(size[0], size[1]), d=.1)
                anim.bind(on_complete=on_animation_complete)
                anim.start(self)
                self.is_anim = True

        return super().on_touch_down(touch)

    def new_planet(self, *args):
        data = app.load_prog()
        if data["planet"] is None:
            self.planet = choice(app.LEVELS)
            self.points = data['points']
        else:
            self.planet = data["planet"]
            self.points = data['points']
        
        # Оновлення значення points для поточного екземпляра Planet
        self.points = data['points']

        self.source = app.PLANETS[self.planet]['source']
        self.hp = app.PLANETS[self.planet]['hp']
        self.size = app.PLANETS[self.planet]['size']

        # Вивід даних для перевірки
        print("Data:", self.planet, self.source, self.hp, self.size)
        print("Data:", type(self.planet), type(
            self.source), type(self.hp), type(self.size))

        size = (self.size[0], self.size[1])
        self.size = size[0], size[1]
        self.center = self.parent.center
        anim = Animation(opacity=1, d=0.3)
        anim &= Animation(
            size=(self.size[0]/1.5, self.size[1]/1.5), d=.2, t='out_back')
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


class MainApp(App):
    storage = None
    SHOP = {"mult": 1}
    LEVELS = ['Mercury', 'Venus', 'Earth', 'Mars',
              'Jupiter', 'Saturn', 'Uranus', 'Neptune']
        
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
        app.storage.put('progress', planet=Planet.planet,
                        hp=Planet.hp,
                        planet_index=Planet.planet_index,
                        mult=Planet.mult,
                        points=Planet.points)
            
    def build(self):
        self.storage = JsonStore(self.user_data_dir+"storage.json")
        sm = ScreenManager(transition=FadeTransition(duration=1))
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(ShopScreen(name='shop'))
        return sm
        
    def load_prog(self):
        return self.storage.get("progress")

if platform != 'android':
    Window.size = (400, 800)
    Window.left = 750
    Window.top = 100

app = MainApp()
app.run()
