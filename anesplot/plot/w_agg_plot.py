# !/usr/bin/env python3
"""
Created on Thu Apr 28 14:41:15 2022

@author: cdesbois

list of function to choose, manipulate and combine the wave plot functions


"""
from typing import Optional
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog


class ChooseWave(QWidget):  # typing: ignore
    """ "Choose wave dialog."""

    def __init__(self, waves: list[str], num: int = 1) -> None:
        super().__init__()
        self.title = "choose the trace to plot"
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.waves = waves
        self.num = num
        self.select: Optional[str] = None
        self.init_ui()

    def init_ui(self) -> None:
        """Init GUI."""
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.get_choice()
        self.show()

    def get_choice(self) -> None:
        """Chhose dialog."""
        if self.num == 1:
            question = "choose first wave"
        if self.num == 2:
            question = "do you want a second one ?"

        items = self.waves
        item, ok_pressed = QInputDialog.getItem(
            self, "select", question, items, 0, False
        )
        if ok_pressed and item:
            print(item)
            self.select = str(item)


def select_wave_to_plot(waves: list[str]) -> list[str]:
    """Select the wave(s)."""
    # waves = ["wekg", "wap", "wco2"]
    selected_waves = []
    app = QApplication(sys.argv)
    for num in [1, 2]:
        dial = ChooseWave(waves, num)
        if dial.select:
            selected_waves.append(dial.select)
    del dial
    return selected_waves


# %%
if __name__ == "__main__":
    selections = select_wave_to_plot(["wekg", "wap", "wco2"])
    print(selections)
