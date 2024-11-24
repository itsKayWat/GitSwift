import sys
import os
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from github import Github, GithubException
from datetime import datetime
import json
from pathlib import Path

# Enable High DPI scaling
if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

# Supported licenses mapping
LICENSES = {
    "MIT License": "mit",
    "Apache License 2.0": "apache-2.0",
    "GNU General Public License v3.0": "gpl-3.0",
    "BSD 3-Clause License": "bsd-3-clause",
}

class GitHubUploader(QtWidgets.QWidget):
    def __init__(self):
        try:
            super().__init__()
            self.github = None
            self.user = None
            self.tokens_file = Path.home() / '.github_tokens.json'
            
            self.load_tokens()
            self.initUI()
        except Exception as e:
            print(f"Initialization error: {e}")
            raise

    def load_tokens(self):
        """Load saved tokens from file"""
        self.tokens = {}
        if self.tokens_file.exists():
            try:
                with open(self.tokens_file, 'r') as f:
                    self.tokens = json.load(f)
            except Exception as e:
                print(f"Error loading tokens: {e}")
                self.save_tokens()

    def save_tokens(self):
        """Save tokens to file"""
        try:
            with open(self.tokens_file, 'w') as f:
                json.dump(self.tokens, f)
        except Exception as e:
            print(f"Error saving tokens: {e}")

    def initUI(self):
        self.setWindowTitle('GitHub Project Uploader')
        self.setGeometry(100, 100, 700, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #2e2e2e;
                color: #ffffff;
                font-family: Arial;
                font-size: 14px;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #3e3e3e;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px;
            }
            QPushButton {
                background-color: #5e5e5e;
                color: #ffffff;
                border: none;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #7e7e7e;
            }
            QLabel {
                color: #ffffff;
            }
        """)

        layout = QtWidgets.QVBoxLayout()

        # GitHub Token
        token_layout = QtWidgets.QHBoxLayout()
        token_label = QtWidgets.QLabel("GitHub Token:")
        
        self.token_combo = QtWidgets.QComboBox()
        self.token_combo.setEditable(True)
        self.token_combo.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.InsertAtTop)
        # Only add valid tokens from the saved tokens
        valid_tokens = []
        for name, token in self.tokens.items():
            if token.strip():  # Only add if token value is not empty
                valid_tokens.append(name)
        self.token_combo.addItems(valid_tokens)
        self.token_combo.setCurrentText("")
        self.token_combo.currentIndexChanged.connect(self.token_selected)
        
        self.delete_token_button = QtWidgets.QPushButton("Delete Token")
        self.delete_token_button.clicked.connect(self.delete_token)
        self.delete_token_button.setEnabled(False)  # Disable until a saved token is selected
        
        self.save_token_checkbox = QtWidgets.QCheckBox("Save Token")
        self.save_token_checkbox.setChecked(False)  # Default to unchecked
        
        token_layout.addWidget(token_label)
        token_layout.addWidget(self.token_combo)
        token_layout.addWidget(self.delete_token_button)
        token_layout.addWidget(self.save_token_checkbox)
        layout.addLayout(token_layout)

        # Authenticate Button
        self.auth_button = QtWidgets.QPushButton("Authenticate")
        self.auth_button.clicked.connect(self.authenticate)
        layout.addWidget(self.auth_button)

        # Project Directory Selection
        dir_layout = QtWidgets.QHBoxLayout()
        dir_label = QtWidgets.QLabel("Project Directory:")
        self.dir_input = QtWidgets.QLineEdit()
        self.dir_input.setReadOnly(True)
        self.dir_button = QtWidgets.QPushButton("Browse")
        self.dir_button.clicked.connect(self.browse_directory)
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(self.dir_button)
        layout.addLayout(dir_layout)

        # Repository Name
        repo_layout = QtWidgets.QHBoxLayout()
        repo_label = QtWidgets.QLabel("Repository Name:")
        self.repo_input = QtWidgets.QLineEdit()
        repo_layout.addWidget(repo_label)
        repo_layout.addWidget(self.repo_input)
        layout.addLayout(repo_layout)

        # Visibility
        visibility_layout = QtWidgets.QHBoxLayout()
        visibility_label = QtWidgets.QLabel("Visibility:")
        self.private_checkbox = QtWidgets.QCheckBox("Private Repository")
        visibility_layout.addWidget(visibility_label)
        visibility_layout.addWidget(self.private_checkbox)
        layout.addLayout(visibility_layout)

        # Description
        desc_layout = QtWidgets.QHBoxLayout()
        desc_label = QtWidgets.QLabel("Description:")
        self.desc_input = QtWidgets.QLineEdit()
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.desc_input)
        layout.addLayout(desc_layout)

        # License Selection
        license_layout = QtWidgets.QHBoxLayout()
        license_label = QtWidgets.QLabel("License:")
        self.license_combo = QtWidgets.QComboBox()
        self.license_combo.addItems(LICENSES.keys())
        license_layout.addWidget(license_label)
        license_layout.addWidget(self.license_combo)
        layout.addLayout(license_layout)

        # Author Name
        author_layout = QtWidgets.QHBoxLayout()
        author_label = QtWidgets.QLabel("Author Name:")
        self.author_input = QtWidgets.QLineEdit()
        author_layout.addWidget(author_label)
        author_layout.addWidget(self.author_input)
        layout.addLayout(author_layout)

        # Upload Button
        self.upload_button = QtWidgets.QPushButton("Upload to GitHub")
        self.upload_button.clicked.connect(self.upload_to_github)
        self.upload_button.setEnabled(False)
        layout.addWidget(self.upload_button)

        # Status Display
        self.status_display = QtWidgets.QTextEdit()
        self.status_display.setReadOnly(True)
        layout.addWidget(self.status_display)

        self.setLayout(layout)

    def log_status(self, message):
        self.status_display.append(f"{datetime.now().strftime('%H:%M:%S')}: {message}")

    def authenticate(self):
        token = self.token_combo.currentText().strip()
        
        # If the entered text is a saved token name, get its actual token value
        if token in self.tokens:
            token = self.tokens[token]
            
        if not token:
            QtWidgets.QMessageBox.warning(self, "Input Error", 
                "Please enter your GitHub Personal Access Token.\n\n"
                "To create a token with correct permissions:\n"
                "1. Go to GitHub Settings -> Developer Settings -> Personal Access Tokens\n"
                "2. Generate new token (classic)\n"
                "3. Select these scopes: repo, workflow, write:packages, delete:packages")
            return
            
        try:
            self.github = Github(token)
            self.user = self.github.get_user()
            
            # Test token permissions by trying to list repos
            self.user.get_repos()
            
            # Save token if checkbox is checked
            if self.save_token_checkbox.isChecked():
                username = self.user.login
                
                # Check if this token already exists
                existing_token_name = None
                for name, saved_token in self.tokens.items():
                    if saved_token == token:
                        existing_token_name = name
                        break
                
                # Update existing token with new timestamp or create new entry
                token_name = f"{username} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                if existing_token_name:
                    # Remove old entry
                    del self.tokens[existing_token_name]
                    # Remove from combo box
                    index = self.token_combo.findText(existing_token_name)
                    if index >= 0:
                        self.token_combo.removeItem(index)
                
                # Add/Update token
                self.tokens[token_name] = token
                self.save_tokens()
                
                # Update combo box
                self.token_combo.clear()
                self.token_combo.addItems(self.tokens.keys())
                self.token_combo.setCurrentText(token_name)
            
            self.log_status(f"Authenticated as {self.user.login}")
            self.upload_button.setEnabled(True)
            QtWidgets.QMessageBox.information(self, "Success", f"Authenticated as {self.user.login}")
            
        except GithubException as e:
            error_message = e.data.get('message', str(e)) if hasattr(e, 'data') else str(e)
            if "401" in str(e):
                error_message = "Invalid token. Please check your token and try again."
            elif "403" in str(e):
                error_message = ("Insufficient permissions. Please create a new token with these scopes:\n"
                               "- repo (all repo permissions)\n"
                               "- workflow\n"
                               "- write:packages\n"
                               "- delete:packages")
            
            self.log_status(f"Authentication failed: {error_message}")
            QtWidgets.QMessageBox.critical(self, "Authentication Failed", 
                f"Failed to authenticate:\n\n{error_message}")
        except Exception as e:
            self.log_status(f"Authentication failed: {str(e)}")
            QtWidgets.QMessageBox.critical(self, "Authentication Failed", 
                f"An unexpected error occurred:\n\n{str(e)}")

    def token_selected(self, index):
        """Handle token selection from combo box"""
        current_text = self.token_combo.currentText()
        
        # If the current text is a key in our tokens dictionary
        if current_text in self.tokens:
            self.delete_token_button.setEnabled(True)
        else:
            # Check if the current text is a token value
            is_token_value = any(token == current_text for token in self.tokens.values())
            self.delete_token_button.setEnabled(is_token_value)

    def delete_token(self):
        """Delete the currently selected token"""
        current_text = self.token_combo.currentText()
        
        # Find the token name (key) that matches either the name or the value
        token_to_delete = None
        for name, token in self.tokens.items():
            if name == current_text or token == current_text:
                token_to_delete = name
                break
        
        if token_to_delete:
            reply = QtWidgets.QMessageBox.question(
                self,
                'Confirm Deletion',
                f'Are you sure you want to delete the saved token "{token_to_delete}"?',
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )
            
            if reply == QtWidgets.QMessageBox.Yes:
                # Delete from the dictionary
                del self.tokens[token_to_delete]
                # Save the updated tokens
                self.save_tokens()
                # Clear and repopulate the combo box with valid tokens
                self.token_combo.clear()
                self.token_combo.addItems(self.tokens.keys())
                self.token_combo.setCurrentText("")
                # Disable delete button
                self.delete_token_button.setEnabled(False)
                
                self.log_status(f"Token '{token_to_delete}' deleted successfully")
        else:
            QtWidgets.QMessageBox.warning(
                self,
                "Delete Token",
                "Please select a saved token to delete."
            )

    def browse_directory(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if directory:
            self.dir_input.setText(directory)

    def validate_repo_name(self, name):
        # Remove any whitespace
        name = name.strip()
        
        # Check if name is empty
        if not name:
            return False, "Repository name cannot be empty"
        
        # Check for valid characters (letters, numbers, hyphens, underscores)
        if not all(c.isalnum() or c in '-_' for c in name):
            return False, "Repository name can only contain letters, numbers, hyphens, and underscores"
        
        # Check length
        if len(name) > 100:
            return False, "Repository name cannot be longer than 100 characters"
        
        return True, name

    def upload_to_github(self):
        if not self.github or not self.user:
            QtWidgets.QMessageBox.warning(self, "Authentication Error", "Please authenticate first.")
            return

        project_path = self.dir_input.text().strip()
        repo_name = self.repo_input.text().strip()
        description = self.desc_input.text().strip()
        author = self.author_input.text().strip()
        is_private = self.private_checkbox.isChecked()

        # Validate inputs
        if not all([project_path, repo_name, author]):
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please fill in all required fields.")
            return

        # Validate repository name
        is_valid, result = self.validate_repo_name(repo_name)
        if not is_valid:
            QtWidgets.QMessageBox.warning(self, "Input Error", result)
            return
        repo_name = result

        # Clean description
        if description:
            description = ''.join(char for char in description if char >= ' ').strip()
            description = ' '.join(description.split())
            
            if len(description) > 350:
                QtWidgets.QMessageBox.warning(self, "Input Error", 
                    "Description must be 350 characters or less.\n"
                    f"Current length: {len(description)} characters")
                return

        try:
            # Create repository
            self.log_status(f"Creating {'private' if is_private else 'public'} repository...")
            repo = self.user.create_repo(
                name=repo_name,
                description=description if description else None,
                private=is_private,
                auto_init=True
            )

            self.log_status(f"Repository created: {repo.html_url}")

            # Upload files
            self.log_status("Uploading files...")
            self.upload_directory(repo, project_path)
            
            self.log_status("Project uploaded successfully!")
            QtWidgets.QMessageBox.information(self, "Success", 
                f"Project uploaded successfully!\nRepository URL: {repo.html_url}")
            
        except GithubException as e:
            error_message = e.data.get('message', str(e)) if hasattr(e, 'data') else str(e)
            if isinstance(e.data, dict) and 'errors' in e.data:
                error_details = '\n'.join([f"- {err.get('message', '')}" for err in e.data['errors']])
                error_message = f"{error_message}\n\nDetails:\n{error_details}"
            
            self.log_status(f"Error: {error_message}")
            QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred:\n\n{error_message}")
        except Exception as e:
            self.log_status(f"Error: {str(e)}")
            QtWidgets.QMessageBox.critical(self, "Error", f"An unexpected error occurred:\n\n{str(e)}")

    def upload_directory(self, repo, directory_path):
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, directory_path)
                
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                try:
                    repo.create_file(
                        relative_path,
                        f"Add {relative_path}",
                        content
                    )
                    self.log_status(f"Uploaded: {relative_path}")
                except Exception as e:
                    self.log_status(f"Failed to upload {relative_path}: {str(e)}")

def main():
    try:
        app = QtWidgets.QApplication(sys.argv)
        uploader = GitHubUploader()
        uploader.show()
        app.uploader = uploader
        return app.exec_()
    except Exception as e:
        print(f"Error in main: {str(e)}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        return 1

if __name__ == '__main__':
    sys.exit(main())