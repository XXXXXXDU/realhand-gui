import sys
from importlib import resources

from realhand_gui.utils import load_yaml
from realhand_gui.gui import Realhand_GUI
from realhand_gui.robot_worker import HandWorker

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import QThread

def main():
    print("hello world")
    app = QApplication(sys.argv)

    config_path = resources.files("realhand_gui").joinpath("config", "setting.yaml")
    hand_config = load_yaml(config_path)

    # Make an API object for the specified hand
    model = hand_config["REAL_HAND"]["MODEL"]
    handedness = hand_config["REAL_HAND"]["HANDEDNESS"]
    can = hand_config["REAL_HAND"]["CAN"]

    # Add api worker to new thread
    thread = QThread()
    worker = HandWorker(handedness, model, can)
    worker.moveToThread(thread)
    thread.started.connect(worker.start)
    thread.start()

    gui = Realhand_GUI(model)
    gui.show()

    # Set poisition callback
    gui.position_request.connect(worker.set_position)
    gui.reset_hand.connect(worker.reset_hand)

    exit_code = app.exec_()
    thread.quit()
    thread.wait()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()