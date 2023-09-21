import pyautogui
import time

print("Move the mouse over the GUI element you want to inspect. You have 5 seconds.")
time.sleep(5)

position = pyautogui.position()
print(f"The cursor is at x = {position[0]}, y = {position[1]}")

