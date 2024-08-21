import sys
from PyQt5 import QtWidgets
from Config_Creator import Ui_Cookie_Config_Developer  # Replace with the actual class name in your generated file
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtGui import QKeySequence
from PyQt5 import QAxContainer
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QUrl, Qt, QTimer, pyqtSignal, pyqtSlot, QThread, QThreadPool, QBasicTimer, QTimerEvent, QMessageLogContext, QtMsgType, QRect
from PyQt5.QtWidgets import QApplication, QScrollArea, QLineEdit, QHBoxLayout, QShortcut, QMainWindow, QListWidget, QDockWidget, QPlainTextEdit, QLCDNumber, QWidget, QVBoxLayout, QTextBrowser, QFileDialog, QTextEdit, QComboBox, QPushButton, QMessageBox, QFrame, QInputDialog, QLabel, QCheckBox, QScrollBar, QDialogButtonBox, QDialog, QGridLayout, QMenu, QAction, QTabBar, QRadioButton
from PyQt5.QtXml import QDomDocument
from PyQt5.QtGui import QDesktopServices, QTextCursor, QTextDocument, QColor, QCursor, QTextCharFormat, QIcon, QPainter, QTextOption
import requests
import os
import time



class SearchDialog(QDialog):
    def __init__(self, parent=None):
        super(SearchDialog, self).__init__(parent)
        self.setWindowTitle("Search")
        self.setGeometry(100, 100, 300, 100)
        
        self.search_label = QLabel("Find:")
        self.search_input = QLineEdit(self)
        
        self.search_button = QPushButton("Search", self)
        self.search_button.clicked.connect(self.accept)

        layout = QHBoxLayout()
        layout.addWidget(self.search_label)
        layout.addWidget(self.search_input)
        layout.addWidget(self.search_button)
        
        self.setLayout(layout)
    
    def get_search_term(self):
        return self.search_input.text()
    def set_result_count(self, count):
        self.result_label.setText(f"Occurrences: {count}")






class MainWindow(QtWidgets.QMainWindow, Ui_Cookie_Config_Developer):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # This method is defined in the generated file
        self.load_cookies_button.clicked.connect(self.load_cookies_function)
        self.send_request_button.clicked.connect(self.send_request)
        self.shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+F"), self)
        self.shortcut.activated.connect(self.open_search_dialog)
        self.enable_captures_checkBox.stateChanged.connect(self.enable_capture_frame)
        self.save_config_button.clicked.connect(self.save_config)
        self.current_cursor_position = 0
    def enable_capture_frame(self, state):
        # Enable or disable specific widgets based on the checkbox state
        self.capture_1_after.setEnabled(state == Qt.Checked)
        self.capture_1_before.setEnabled(state == Qt.Checked)
        self.capture_2_after.setEnabled(state == Qt.Checked)
        self.capture_2_before.setEnabled(state == Qt.Checked)
        self.capture_3_after.setEnabled(state == Qt.Checked)
        self.capture_3_before.setEnabled(state == Qt.Checked)
        self.capture_value_response_textedit.setEnabled(state == Qt.Checked)
        # Update the result count in the search dialog
        self.search_dialog.set_result_count(occurrences)
        self.load_config_button.clicked.connect(self.load_config_function)
        self.toolButton.clicked.connect(self.openDialog)
        self.setCentralWidget(self.toolButton)
        self.tray_icon.show()
        # Create context menu
        tray_menu = QMenu(self)
        open_action = QAction("Open", self)
        minimize_action = QAction("Minimize", self)
        close_action = QAction("Close", self)

        tray_menu.addAction(open_action)
        tray_menu.addAction(minimize_action)
        tray_menu.addAction(close_action)

        self.tray_icon.setContextMenu(tray_menu)
        
        
        
        
        
        

########## Search Function in Response #############
    def open_search_dialog(self):
        # Create and show the search dialog
        search_dialog = SearchDialog(self)
        
        # Calculate the center position of the main window
        main_window_rect = self.geometry()
        dialog_rect = search_dialog.geometry()
        
        # Set the dialog's position to the center of the main window
        center_x = main_window_rect.x() + (main_window_rect.width() - dialog_rect.width()) // 2
        center_y = main_window_rect.y() + (main_window_rect.height() - dialog_rect.height()) // 2
        search_dialog.move(center_x, center_y)
        
        # Execute the dialog and check if it was accepted
        if search_dialog.exec_() == QDialog.Accepted:
            search_term = search_dialog.get_search_term()
            self.search_in_text_edit(search_term)
    
    def search_in_text_edit(self, search_term):
        # Clear previous highlights
        cursor = self.http_response_textEdit.textCursor()
        cursor.setPosition(0)
        self.http_response_textEdit.setTextCursor(cursor)

        # Highlight format
        format = QtGui.QTextCharFormat()
        format.setBackground(QtGui.QBrush(QtGui.QColor("yellow")))

        # Find all occurrences of the search term
        occurrences = 0
        while not cursor.isNull() and not cursor.atEnd():
            cursor = self.http_response_textEdit.document().find(search_term, cursor)
            if not cursor.isNull():
                occurrences += 1
                cursor.mergeCharFormat(format)



        # If occurrences are found, start searching from the beginning
        if occurrences > 0:
            self.find_next(search_term)

    def find_next(self, search_term):
        # Move the cursor to the current position
        cursor = self.http_response_textEdit.textCursor()
        cursor.setPosition(self.current_cursor_position)
        self.http_response_textEdit.setTextCursor(cursor)

        # Find the next occurrence
        cursor = self.http_response_textEdit.document().find(search_term, cursor)
        if not cursor.isNull():
            # Highlight the found text
            self.current_cursor_position = cursor.position()
            self.http_response_textEdit.setTextCursor(cursor)
        else:
            # Reset to start if no more occurrences
            self.current_cursor_position = 0
########################################################




########## Drag and Drop Function ##########
    def dragEnterEvent(self, event):
        # Accept the drag event if it contains URLs (files)
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        # Handle the drop event to load the file
        if not self.validate_domain():
            return

        urls = event.mimeData().urls()
        if urls:
            file_name = urls[0].toLocalFile()
            if file_name.endswith('.txt'):
                self.load_cookies_from_file(file_name)
########################################################









    def send_request(self):
        # Get the URL and request type
        url = self.http_url_request_textedit.toPlainText().strip()
        request_type = self.get_or_post_combobox.currentText()
        valid_response_text = self.valid_response_text.toPlainText().strip()
    
        if not url:
            QMessageBox.warning(self, "Input Error", "Please enter a URL.")
            return
    
        try:
            # Prepare headers
            headers = {}
            
            if self.user_agent_checkbox.isChecked():
                user_agent = self.user_agent_combobox.currentText().strip()
                headers['User-Agent'] = user_agent
            
            if self.accept_checkbox.isChecked():
                accept = self.accept_combobox.currentText().strip()
                headers['Accept'] = accept
            
            if self.content_type_checkbox.isChecked():
                content_type = self.content_type_combobox.currentText().strip()
                headers['Content-Type'] = content_type
    
            # Send the HTTP request based on the selected method
            if request_type == "GET":
                response = requests.get(url, headers=headers)
            elif request_type == "POST":
                response = requests.post(url, headers=headers)
            else:
                QMessageBox.warning(self, "Request Error", "Unsupported request type.")
                return
    
            # Display the response in the text edit
            response_text = response.text
            self.http_response_textEdit.setPlainText(response_text)
    
            # Check for valid response text
            if valid_response_text:
                if valid_response_text in response_text:
                    QMessageBox.information(self, "Validation", "The response contains the valid text. Cookies are valid.")
                else:
                    QMessageBox.warning(self, "Validation", "The response does not contain the valid text. Cookies may not be valid.")
    
            # Extract content based on the delimiters
            def extract_content(before, after, text):
                if before in text and after in text:
                    start = text.find(before) + len(before)
                    end = text.find(after, start)
                    return text[start:end].strip()
                return ""
    
            results = []
            # Extract text from QTextEdit objects
            capture_1_before = self.capture_1_before.toPlainText().strip()
            capture_1_after = self.capture_1_after.toPlainText().strip()
    
            if capture_1_before and capture_1_after:
                result = extract_content(capture_1_before, capture_1_after, response_text)
                if result:
                    results.append(f"Capture 1: {result}")
    
            # Display the results in the capture_value_response_textedit
            if results:
                self.capture_value_response_textedit.setText("; ".join(results))
            else:
                self.capture_value_response_textedit.setText("No captures found.")
    
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Request Error", f"An error occurred: {e}")
        
    

################################ Cookies ##########################################

    def load_cookies_function(self):
        # Check if the domain is entered
        if not self.validate_domain():
            return

        # Open a file dialog to select a .txt file
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Cookie File", "", "Text Files (*.txt);;All Files (*)", options=options)
        
        if file_name:
            self.load_cookies_from_file(file_name)

    def validate_domain(self):
        # Validate that the domain field is not empty
        domain = self.cookie_domain_edit.toPlainText().strip()
        if not domain:
            QMessageBox.warning(self, "Input Error", "Please enter a DOMAIN VALUE  before loading a file.")
            return False
        return True

    def load_cookies_from_file(self, file_name):
        try:
            # Read the file and count the lines matching the domain
            with open(file_name, 'r') as file:
                lines = file.readlines()
                domain = self.cookie_domain_edit.toPlainText().strip()
                matching_lines = [line for line in lines if domain in line]
    
            # Update the QLCDNumber with the number of matching lines
            num_matching_lines = len(matching_lines)
            self.total_cookies_lcdNumber.display(num_matching_lines)
    
            # Display a message box with the number of cookies found and the domain
            QMessageBox.information(
                self,
                "Cookies Found",
                f"Number of cookies found for domain '{domain}': {num_matching_lines}"
            )
    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
################################################################################
############################  Config Loading Function#############################
    
    def load_config_function(self):
        # Create a message box
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Load Configuration")
        msg_box.setText("How do you want to load your configuration as?")
        
        # Add buttons for options
        project_button = msg_box.addButton("Project", QMessageBox.ActionRole)
        cash_button = msg_box.addButton("CA$H file", QMessageBox.ActionRole)
        cancel_button = msg_box.addButton(QMessageBox.Cancel)
        
        # Execute the message box and wait for user interaction
        msg_box.exec_()
        
        # Determine which button was clicked and perform the corresponding action
        if msg_box.clickedButton() == project_button:
            self.load_as_project()
        elif msg_box.clickedButton() == cash_button:
            self.load_as_cash_file()
        elif msg_box.clickedButton() == cancel_button:
            # Optional: Handle cancel action if needed
            pass
    
    def load_as_project(self):
        # Implement the logic to load configuration as a Project
        print("Loading configuration as Project...")
        # Add your loading logic here
    
    def load_as_cash_file(self):
        # Implement the logic to load configuration as a CA$H file
        print("Loading configuration as CA$H file...")
        # Add your loading logic here



########################## Config Saving Functions ##########################
    def save_config(self):
        # Get the configuration values from the UI
        project_name = self.save_config_textedit.toPlainText().strip()
        domain = self.cookie_domain_edit.toPlainText().strip()
        pars_after = self.capture_1_after.toPlainText().strip()
        pars_before = self.capture_1_before.toPlainText().strip()
        capture_1_before = self.capture_1_before.toPlainText().strip()
        capture_1_after = self.capture_1_after.toPlainText().strip()
        capture_2_before = self.capture_2_before.toPlainText().strip()
        capture_2_after = self.capture_2_after.toPlainText().strip()
        capture_3_before = self.capture_3_before.toPlainText().strip()
        capture_3_after = self.capture_3_after.toPlainText().strip()
        method = self.get_or_post_combobox.currentText().strip()
        url = self.http_url_request_textedit.toPlainText().strip()
        url_capture = self.url_capture_textedit.toPlainText().strip()
        response_valide = self.valid_response_text.toPlainText().strip()
    
        # Extract values from combo boxes
        user_agent = self.user_agent_combobox.currentText().strip()
        accept = self.accept_combobox.currentText().strip()
        content_type = self.content_type_combobox.currentText().strip()
        referer = self.referer_combobox.currentText().strip()
        x_content_type_options = self.x_content_type_options_combobox.currentText().strip()
        x_requested_with = self.x_requested_with_combobox.currentText().strip()
        creator = self.creator_config_textedit.toPlainText().strip()

        AddHeader1 = self.header_1_function.toPlainText().strip()
        AddHeader2 = self.header_2_function.toPlainText().strip()
        AddHeader3 = self.header_3_function.toPlainText().strip()
        AddHeader4 = self.header_4_function.toPlainText().strip()
        AddHeader5 = self.header_5_function.toPlainText().strip()
        Header1 = self.header_1_value.toPlainText().strip()
        Header2 = self.header_2_value.toPlainText().strip()
        Header3 = self.header_3_value.toPlainText().strip()
        Header4 = self.header_4_value.toPlainText().strip()
        Header5 = self.header_5_value.toPlainText().strip()
        
        
        
        # Prompt the user to choose how to save the configuration
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Save Configuration")
        msg_box.setText("How do you want to save your configuration?")
        project_button = msg_box.addButton("Project", QMessageBox.ActionRole)
        cash_button = msg_box.addButton("CA$H file", QMessageBox.ActionRole)
        msg_box.addButton(QMessageBox.Cancel)
        msg_box.exec_()
    
        # Determine which button was clicked and build the configuration content accordingly
        if msg_box.clickedButton() == project_button:
            config_content = f"""[Project Settings]
ProjectName={project_name}

[Request Settings]
Domain={domain}
ResponseValide={response_valide}
Header5={AddHeader5}={Header5}
Header4={AddHeader4}={Header4}
Header3={AddHeader3}={Header3}
Header2={AddHeader2}={Header2}
Header1={AddHeader1}={Header1}
AddHeader5=False
AddHeader4=False
AddHeader3=False
AddHeader2=False
AddHeader1=False
X-Requested-With={x_requested_with}
Referer={referer}
ContentType={content_type}
Accept={accept}
UserAgent={user_agent}
Body=
URL={url}
Method={method}

[Parser Settings]
ParsURL={url_capture}
ParsBefore={capture_1_before}
ParsAfter={capture_1_after}
UseParser=False
MethodParser=One
UseURL=False
"""
            self.save_to_file(config_content, "Project Files (*.proj)")
        elif msg_box.clickedButton() == cash_button:
            config_content = f"""[CA$H Settings]
ProjectName={project_name}

[Request Settings]
Domain={domain}
ResponseValide={response_valide}
Header5={Header5}
Header4={Header4}
Header3={Header3}
Header2={Header2}
Header1={Header1}
AddHeader5={AddHeader5}
AddHeader4={AddHeader4}
AddHeader3={AddHeader3}
AddHeader2={AddHeader2}
AddHeader1={AddHeader1}
X-Requested-With={x_requested_with}
Referer={referer}
ContentType={content_type}
Accept={accept}
UserAgent={user_agent}
Body=
URL={url}
Method={method}

[Parser Settings]
ParsURL={url_capture}
Capture1Before={capture_1_before}
Capture1After={capture_1_after}
Capture2Before={capture_2_before}
Capture2After={capture_2_after}
Capture3Before={capture_3_before}
Capture3After={capture_3_after}
UseParser=False
MethodParser=One
UseURL=False

[Security]
CreatorID={creator}
Checksum=
"""
            self.save_to_file(config_content, "CA$H Files (*.cash)")

    def save_to_file(self, content, file_filter):
        # Open a file dialog to save the file
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Configuration", "", file_filter, options=options)
        if file_name:
            with open(file_name, 'w') as file:
                file.write(content)
            QMessageBox.information(self, "Saved", "Configuration saved successfully.")


    def save_as_project(self, config_text):
        # Open a file dialog to save as a project file
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save as Project", "", "Project Files (*.proj);;All Files (*)", options=options)
        if file_name:
            with open(file_name, 'w') as file:
                file.write(config_text)
            QMessageBox.information(self, "Saved", "Configuration saved as a project file.")
    
    def save_as_cash_file(self, config_text):
        # Open a file dialog to save as a CA$H file
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save as CA$H File", "", "CA$H Files (*.cash);;All Files (*)", options=options)
        if file_name:
            with open(file_name, 'w') as file:
                file.write(config_text)
            QMessageBox.information(self, "Saved", "Configuration saved as a CA$H file.")
########################################################################




################## TOOL BUTTON  DEV DIALOG WINDOW ##########################
    def openDialog(self):
        # Open the dialog window
        dialog = CustomDialog(self)
        dialog.exec_()

class CustomDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set up the dialog window
        self.setWindowTitle("Dialog with Tabs")
        self.setGeometry(100, 100, 400, 300)

        # Create a QVBoxLayout
        layout = QVBoxLayout(self)

        # Create a QTabWidget
        tabWidget = QTabWidget(self)

        # Create the first page
        firstPage = QWidget()
        firstPageLayout = QVBoxLayout()
        firstPageLayout.addWidget(QLabel("This is the first page."))
        firstPage.setLayout(firstPageLayout)

        # Create the second page
        secondPage = QWidget()
        secondPageLayout = QVBoxLayout()
        
        # Developer contact information
        contactLabel = QLabel("Developer Contact: developer@example.com")
        secondPageLayout.addWidget(contactLabel)

        # Version number
        versionLabel = QLabel("Version: 1.0.0")
        secondPageLayout.addWidget(versionLabel)

        # Update button
        updateButton = QPushButton("Check for Updates")
        updateButton.clicked.connect(self.checkForUpdates)
        secondPageLayout.addWidget(updateButton)

        secondPage.setLayout(secondPageLayout)

        # Add pages to the tab widget
        tabWidget.addTab(firstPage, "Page 1")
        tabWidget.addTab(secondPage, "Page 2")

        # Add the tab widget to the dialog layout
        layout.addWidget(tabWidget)

    def checkForUpdates(self):
        # Placeholder function for update logic
        print("Checking for updates...")
########################################################################

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()