def get_resolution():
    try:
        from screeninfo import get_monitors
        m = get_monitors()[0]
        return m.width, m.height
    except Exception:
        import pyautogui
        return pyautogui.size()
