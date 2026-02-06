from enum import IntEnum

from RealHand.real_hand_api import RealHandApi

from PyQt5.QtCore import QObject, Qt, pyqtSignal, QTimer, pyqtSlot

class HandWorker(QObject):
    error = pyqtSignal(str)
    
    def __init__(self, handedness, model, can):
        super().__init__()
        self._poll_timer = QTimer(self)
        self.reset_hand(handedness, model, can)

    @pyqtSlot()
    def start(self):
        self._poll_timer.start(200)

    @pyqtSlot(list)
    def set_position(self, pos: list):
        try:
            self.hand.finger_move(pos)
        except Exception as e:
            self.error.emit(str(e))

    @pyqtSlot(str, str, str)
    def reset_hand(self, handedness, model, can):
        print("Helllo!")
        print(model)
        try:
            self.hand = RealHandApi(handedness, model, "None", can)
        except Exception as e:
            print(f"Failed to initialize hand: {e}")

    def print_me():
        print("I'm printed")