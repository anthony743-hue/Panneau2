import tkinter as tk
from app.controller.appareil_form_controller import AppareilFormController


class AppareilFormApp(AppareilFormController):
    pass


def run_app():
    root = tk.Tk()
    AppareilFormApp(root)
    root.mainloop()
