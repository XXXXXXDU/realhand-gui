import sys

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QGroupBox, QFormLayout, QMainWindow, QHBoxLayout, QSlider, QComboBox, QLineEdit
from PyQt5.QtCore import pyqtSignal, Qt
from realhand_gui.config.constants import _HAND_CONFIGS

class Realhand_GUI(QMainWindow):

    position_request = pyqtSignal(list)
    reset_hand = pyqtSignal(str, str, str)

    def __init__(self, model: str):
        super().__init__()
        self.model = model
        self.config = _HAND_CONFIGS[self.model]
        self.setWindowTitle("RealHand Controller")
        self.resize(900, 600)

        self.label = QLabel("Status: idle")
        self.btn = QPushButton("Press me")

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        # --- Top bar (top-left selector) ---
        topbar = QHBoxLayout()
        root.addLayout(topbar)

        # --- Hand Selector ---
        topbar.addWidget(QLabel("Hand:"))
        self.hand_combo = QComboBox()
        self.hand_combo.addItems(list(_HAND_CONFIGS.keys()))
        self.hand_combo.setCurrentText(self.model)
        self.hand_combo.currentTextChanged.connect(self.on_hand_changed)
        topbar.addWidget(self.hand_combo)

        topbar.addSpacing(12)

        # --- Side selector ---
        topbar.addWidget(QLabel("Side:"))
        self.handed_combo = QComboBox()
        self.handed_combo.addItems(["left", "right"])
        self.handed_combo.setCurrentText("left")  # or whatever default you want
        self.handed_combo.currentTextChanged.connect(self.on_hand_changed)
        topbar.addWidget(self.handed_combo)

        self.iface_edit = QLineEdit()
        self.iface_edit.setPlaceholderText("e.g. can0, can1, vcan0")
        self.iface_edit.setText("can0")
        # self.iface_edit.textChanged.connect(self.on_hand_changed)
        self.iface_edit.editingFinished.connect(self.on_hand_changed) # only when focus leaves
        topbar.addWidget(self.iface_edit)

        # --- Main row ---
        row = QHBoxLayout()
        root.addLayout(row)

        # --- Left: Sliders ---
        self.sliders_box = QGroupBox("Joint Sliders")
        row.addWidget(self.sliders_box, stretch=1)  # stretch=1 makes it take more space
        self.sliders_layout = QFormLayout(self.sliders_box)

        # --- Right: Presets ---
        self.presets_box = QGroupBox("Preset Positions")
        row.addWidget(self.presets_box, stretch=1)  # stretch=0 keeps it narrower
        self.presets_layout = QVBoxLayout(self.presets_box)

        self.populate_sliders()

        self.populate_presets()

    def on_hand_changed(self):
        self.reset_hand.emit(self.handed_combo.currentText(), self.hand_combo.currentText(), self.iface_edit.text())
        self.model = self.hand_combo.currentText()
        self.config = _HAND_CONFIGS[self.model]

        # clear layouts and rebuild
        self._clear_layout(self.sliders_layout)
        self._clear_layout(self.presets_layout)

        self.populate_sliders()
        self.populate_presets()

    def populate_sliders(self):
        self.joint_sliders = {}
        self.joint_value_labels = {}
        for idx, joint in enumerate(self.config.joint_names):
            vmin = 0
            vmax = 255
            v0   = self.config.init_pos[idx]

            slider = QSlider(Qt.Horizontal)
            slider.setRange(vmin, vmax)
            slider.setValue(v0)

            value_label = QLabel(str(v0))

            roww = QWidget()
            rowl = QHBoxLayout(roww)
            rowl.setContentsMargins(0, 0, 0, 0)
            rowl.addWidget(slider, stretch=1)
            rowl.addWidget(value_label)

            self.sliders_layout.addRow(joint, roww)

            self.joint_sliders[joint] = slider
            self.joint_value_labels[joint] = value_label

            slider.valueChanged.connect(self.joint_slider_cb)
            slider.valueChanged.connect(value_label.setNum)

    def joint_slider_cb(self):
        positions = []
        for joint in self.config.joint_names:
            positions.append(self.joint_sliders[joint].value())
        self.position_request.emit(positions)

    def populate_presets(self):
        self.preset_buttons = {}
        for idx, preset in enumerate(self.config.preset_actions):
            btn = QPushButton(preset)
            self.presets_layout.addWidget(btn)

            btn.clicked.connect(lambda checked=False, name=preset: self.btn_cb(name))

    def btn_cb(self, preset):
        positions = self.config.preset_actions[preset]
        self.position_request.emit(positions)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
            else:
                child_layout = item.layout()
                if child_layout is not None:
                    self._clear_layout(child_layout)
