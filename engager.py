import sys
#Optmize this for the minimum requireements.
from PyQt6.QtWidgets import *
from PyQt6.QtCore import QTimer, QDate
from datetime import datetime
from filehandler import handler
from uuid import uuid4
taskl = handler("r", 0, "engager.json")
metrics = handler("r", 0, "metrics.json")


def render():
    #For the task display
    #Counts reversed the layout
    for i in reversed(range(window.task_displayo.layout.count())): 
        #Gets the widget from the index
        w = window.task_displayo.layout.itemAt(i).widget()
        #If it exists, then its deleted
        if w is not None:
            w.deleteLater()
    #Now in taskl
    for i in taskl:
        #Creates the task widget from the taskl dict and adds it to layout
        taskw = task(i)
        window.task_displayo.layout.addWidget(taskw)
    #For the combo box
    #Clears every option
    window.manageo.timero.select.clear()
    for i in taskl:
        #Adds every Element in taskl 
        window.manageo.timero.select.addItem(i["name"])\

def metricHandler(op):
    if op == "cTime":
        metrics["tTime"] +=1
        window.manageo.metrico.tTimeLabel.setText(f"Total seconds: {metrics["tTime"]}")

class metric(QFrame):
    def __init__(self):
        super().__init__()
        self.tTimeLabel = QLabel(f"Total seconds: {metrics["tTime"]}")

        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.tTimeLabel)

def calculateRTime(due_date):
    dueO = datetime.fromisoformat(due_date).date()
    today = datetime.now().date()
    delta = dueO - today
    return delta.days
def task_handler(index, operation):
    if operation == "add":
        def end(): 
            #Upon pressing OK, adds the inputs from the areas to taskl, then renders, then deletes the dialog
            taskl.append({"name": dialog.namei.text(), "due_date": dialog.datei.text(),"timeLeft": calculateRTime(dialog.datei.text()),"timeSpent": [0, 0, 0],"desc":dialog.desc.text(), "id": str(uuid4())})
            render()
            dialog.deleteLater()

        #Creates the dialog, sets and configures the widgets
        dialog = QDialog()
        dialog.namei = QLineEdit()
        dialog.desc = QLineEdit()
        dialog.datei = QDateEdit()
        dialog.datei.setDate(QDate().currentDate())
        dialog.datei.setCalendarPopup(True)
        dialog.datei.setDisplayFormat("yyyy-MM-dd")
        dialog.fin = QPushButton("OK")

        #Layout Configuration and adding the widgets
        namel = QLabel("Task Name:")
        descl = QLabel("Description:")
        datel = QLabel("Due Date:")
                  
        dialog.lay = QGridLayout()
        dialog.setLayout(dialog.lay)

        dialog.lay.addWidget(namel, 1, 0)        
        dialog.lay.addWidget(dialog.namei, 1, 1)

        dialog.lay.addWidget(descl, 2, 0)     
        dialog.lay.addWidget(dialog.desc, 2, 1)
  
        dialog.lay.addWidget(datel, 3, 0)
        dialog.lay.addWidget(dialog.datei, 3, 1)

        dialog.lay.addWidget(dialog.fin, 4, 0)


        #Adds function to the OK button and shows the dialog
        dialog.fin.clicked.connect(lambda: end())
        dialog.exec()
    elif operation == "del":
        try:
            #Takes the widget at the layout index and deletes it.
            window.task_displayo.layout.itemAt(index).widget().deleteLater()
            #Deletes from the list and renders
            taskl.pop(index)
            render()
        except (IndexError, AttributeError):
            display_popup("warning", "Add at least one task!")


    handler("w", taskl, "engager.json")

def display_popup(type, message):
    match type:
        case "warning":
            QMessageBox.warning(window, "WARNING", message)
        case "info":
            QMessageBox.information(window, "Information", message)
        case _:
            QMessageBox.warning(window, "WARNING", "This is our fault, something wrong has happened!") 

class task(QFrame):
    def __init__(self, td):
        super().__init__()

        #Basic Information setting.
        self.name = QLabel(td["name"])

        self.infob = QPushButton("Info")
        self.infob.clicked.connect(lambda: self.showInfo(td))


        #Delete button
        deleteb = QPushButton("Delete")

        #Connects the taskhandler to the extracted index.
        index = taskl.index(td)

        deleteb.clicked.connect(lambda: task_handler(index, "del"))

        #Adding to layout
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.name)
        layout.addWidget(self.infob)
        layout.addWidget(deleteb)
    
    def showInfo(self, td):

        info = f"""
            Description: {td["desc"]} \n
            Due Date: {td["due_date"]} \n
            Time Spent: {td["timeSpent"][0]:02d}:{td["timeSpent"][1]:02d}:{td["timeSpent"][2]:02d} \n
            Days Remaining: {calculateRTime(td["due_date"])} \n
            Task ID: {td["id"]}
        """
        display_popup("info", info)

class task_display(QFrame):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

#This will be the frame for the add button and timer for execution.
class manage(QFrame):
    def __init__(self):
        super().__init__()
        #Set the button and timer section
        self.timero = timerf()
        self.metrico = metric()
        self.addb = QPushButton("Add")
        self.addb.clicked.connect(lambda: task_handler(None,"add")) # the button will invoke the handler to add an task      
        #Creating and setting the layout
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.addb, 0, 0)
        self.layout.addWidget(self.metrico, 1, 0)
        self.layout.addWidget(self.timero, 0, 1)



class timerf(QFrame):
    def __init__(self):
        super().__init__()
        #The time list
        self.time = [0, 0, 0]
        #The timer object
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)

        #Sets the widgets
        self.timel = QLabel("00:00:00")
        self.start = QPushButton("Start")
        self.start.clicked.connect(self.begin)
        self.select = QComboBox(self)

        #Sets the layout of the widget
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.timel, 0, 0)
        self.layout.addWidget(self.start, 1, 0)
        self.layout.addWidget(self.select, 2, 0, 1, 3)


    def tick(self):
        metricHandler("cTime")
        self.time[2] += 1
        if self.time[2] == 60:
            self.time[2] = 0
            self.time[1] += 1
        if self.time[1] == 60:
            self.time[1] = 0
            self.time[0] += 1

        self.timel.setText(f"{self.time[0]:02d}:{self.time[1]:02d}:{self.time[2]:02d}")


    def pause_action(self):
        #Function for the "Pause button."
        #It alternates between the pause-resume, according to the state of counting bool.
        if self.counting:
            self.timer.stop()
            self.pause.setText("Resume")
            self.counting = False
        else:
            self.timer.start()
            self.pause.setText("Pause")
            self.counting = True



    def stop(self):
        self.pause_action()
        self.pause.deleteLater()
        self.stopb.deleteLater()

        #Resets the start button to it's initial function of beggining the loop
        self.start.clicked.disconnect()
        self.start.setText("Start")
        self.start.clicked.connect(self.begin)

        try: 
            i =self.select.currentIndex()
            taskl[i]["timeSpent"][0] += self.time[0]
            taskl[i]["timeSpent"][1] += self.time[1]
            taskl[i]["timeSpent"][2] += self.time[2]
            render()
        except IndexError:
            pass

        self.time = [0, 0 ,0]
        self.timel.setText(f"{self.time[0]:02d}:{self.time[1]:02d}:{self.time[2]:02d}")  


    def finish(self):
        #Pauses the timer, deletes the pause button
        self.pause_action()
        self.pause.deleteLater()
        self.stopb.deleteLater()

        #Removes the task
        try:
            task_handler(self.select.currentIndex(), "del")
        except IndexError:
            display_popup("warning", "Add at least one task!")

        #Resets the start button to it's initial function of beggining the loop
        self.start.clicked.disconnect()
        self.start.setText("Start")
        self.start.clicked.connect(self.begin)

        #Resets the time variable and renders
        self.time = [0, 0 , 0]        
        self.timel.setText(f"{self.time[0]:02d}:{self.time[1]:02d}:{self.time[2]:02d}")  

    def begin(self):
        self.counting = True
        #Changes the `Start` button function to finish the task execution
        self.start.clicked.disconnect()
        self.start.setText("FINISH")
        self.start.clicked.connect(self.finish)

        #Creates the pause button and adds it
        self.pause = QPushButton("Pause")
        self.pause.clicked.connect(self.pause_action)
        self.layout.addWidget(self.pause, 1, 1)

        #Creates the stop button and adds it
        self.stopb = QPushButton("Stop")
        self.stopb.clicked.connect(self.stop)
        self.layout.addWidget(self.stopb, 1, 2)

        self.timer.start(1000)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Engager")
        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout) 
        self.task_displayo = task_display()
        self.manageo = manage()
        layout.addWidget(self.task_displayo)
        layout.addWidget(self.manageo)
        self.show()


style = """
    QWidget {
        background-color: #2E2E2E;
        color: #FFFFFF;
        font-family: Arial;
    }

    QPushButton, QComboBox {
        background-color: #0078D7;
        color: white;
        border: 1px solid #005A9E;
        border-radius: 5px;
        padding: 5px;
    }
    QPushButton:hover {
        background-color: #005A9E;
    }
"""

app = QApplication(sys.argv)
app.setStyleSheet(style)
window = MainWindow()
render()
app.exec()
handler("w", taskl, "engager.json")
handler("w", metrics, "metrics.json")
