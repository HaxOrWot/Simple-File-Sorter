import sys
try:
    from plyer import notification as plyer_notify
except ImportError:
    plyer_notify = None

def notify(title: str, msg: str):
    if plyer_notify:
        plyer_notify.notify(title=title, message=msg, timeout=3)