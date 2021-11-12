import sys 

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget

# Create an instance of QApplication
app = QApplication(sys.argv)

# Create an instance of your application's GUI
window = QWidget()
window.setWindowTitle('PyQt5 App')
window.setGeometry(100, 100, 280, 80)
window.move(60, 15)
helloMsg = QLabel('<h1>pyView</h1>', parent=window)
helloMsg.move(60, 15)

# Show your application's GUI
window.show()

# Run your application's event loop (or main loop)
sys.exit(app.exec_())
