import sys
try:
    from PySide6 import QtWidgets, QtCore, QtGui; QT_VERSION = 6
except ImportError:
    try:
        from PySide2 import QtWidgets, QtCore, QtGui; QT_VERSION = 2
    except ImportError:
        from PyQt5 import QtWidgets, QtCore, QtGui; QT_VERSION = 5
print(f"SmartFurnitureWB: Using Qt{QT_VERSION}")
