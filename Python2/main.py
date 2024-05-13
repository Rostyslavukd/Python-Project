from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.window import Window
from kivy.utils import platform

from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.properties import StringProperty,NumericProperty
from random import shuffle, choice, randint
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore
from kivy.uix.popup import Popup
from kivy.base import stopTouchApp


class MenuScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
    
    def on_enter(self, *args):
        app.save_prog
       

class GameScreen(Screen):
    points = NumericProperty(0)
    
    def __init__(self, **kw):
        super().__init__(**kw)
        popup = Popup(title='Заголовок вікна',
                      content=Label(text='Текст Popup'))
        popup.open()

    def on_enter(self, *args):
        self.ids.planet.new_planet()
        return super().on_enter(*args)


class Planet(Image):

    is_anim= False
    hp = None
    planet = None
    planet_index = 0
    points = 0
    mult = 1

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and not self.is_anim:
            
            self.parent.parent.parent.points += (1*self.mult)
            self.points += (1*self.mult)
            self.hp -= 1

            if self.hp <= 0:
                self.break_planet()
                app.storage.put('progress', planet=self.planet)
            else:
                x = self.x
                y = self.y
                size =self.size.copy()
                anim = Animation(
                    size=(size[0]*1.2, size[1]*1.2), t='out_back', d=0.1) + Animation(size=(size[0], size[1]), d=.1)
                anim.start(self)
                self.is_anim = True
                anim.on_complete = lambda *arg: setattr(self, 'is_anim', False)

        return super().on_touch_down(touch)
    
    def new_planet(self, *args):

        Planet.planet = self.planet = app.LEVELS[randint(0, len(app.LEVELS)-1)]
        self.source = app.PLANETS[self.planet]['source']
        self.hp = app.PLANETS[self.planet]['hp']
        self.size = app.PLANETS[self.planet]['size']
        size = self.size.copy()
        self.size = size[0], size[1]
        self.center = self.parent.center
        anim = Animation(opacity = 1, d=0.3)
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
         # ("200dp", "200dp")},
         'Mercury': {"source": 'assets/planets/1.png', 'hp': 1, "size": (200, 200)},
         # ("200dp", "200dp")},
         'Venus': {"source": 'assets/planets/2.png', 'hp': 2, "size": (200, 200)},
          # ("200dp", "200dp")},
         'Earth': {"source": 'assets/planets/3.png', 'hp': 3, "size": (200, 200)},
          # ("200dp", "200dp")},
         'Mars': {"source": 'assets/planets/4.png', 'hp': 4, "size": (200, 200)},
         # ("200dp", "200dp")},
         'Jupiter': {"source": 'assets/planets/5.png', 'hp': 5, "size": (200, 200)},
         # ("200dp", "200dp")},
         'Saturn': {"source": 'assets/planets/6.png', 'hp': 6, "size": (200, 200)},
         # ("200dp", "200dp")},
         'Uranus': {"source": 'assets/planets/7.png', 'hp': 7, "size": (200, 200)},
         # ("200dp", "200dp")},
         'Neptune': {"source": 'assets/planets/8.png', 'hp': 10, "size": (200, 200)},
    }

    def save_prog(self):
        # print(Planet.planet)
        app.storage.put('progress', planet=Planet.planet,
                        hp=Planet.hp,
                        planet_index=Planet.planet_index,
                        mult=Planet.points)
        
    def build(self):
        global storage
        self.storage = JsonStore(self.user_data_dir+"storage.json")
        storage = self.storage
        sm = ScreenManager(transition=FadeTransition(duration=1))
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(GameScreen(name='game'))
        return sm
    
    def load_prog(self):
        return self.storage.get("progress")

if platform != 'android':
    Window.size = (400, 800)
    Window.left = 750
    Window.top = 100


app = MainApp()
app.run()