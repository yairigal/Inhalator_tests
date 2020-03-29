import pyautogui

screen_x, screen_y = pyautogui.size()

def click_configure_alerts_btn():
    pyautogui.click(screen_x / 2, screen_y * 0.9)

def