# GitSwift

![GitHub](https://img.shields.io/github/license/yourusername/GitSwift)
![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15.4-green)

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Requirements](#requirements)
- [Example Use Case](#example-use-case)
- [Contributing](#contributing)
- [License](#license)

## Introduction

GitSwift is a user-friendly GUI application designed to simplify the process of uploading your local projects to GitHub. Whether you're a seasoned developer or just starting out, GitSwift provides an intuitive interface to manage your repositories, handle authentication tokens securely, and ensure your code is hosted effortlessly.

## Features

- **Secure Token Management:** Save and manage multiple GitHub Personal Access Tokens.
- **Easy Repository Creation:** Create new repositories with descriptions, visibility settings, and license options.
- **Seamless File Uploads:** Upload your project files directly to GitHub with just a few clicks.
- **User-Friendly Interface:** Built with PyQt5 for a smooth and responsive user experience.
- **Error Handling & Status Logs:** Receive real-time feedback and status updates during the upload process.

## Installation

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/yourusername/GitSwift.git
    ```
2. **Navigate to the Project Directory:**
    ```bash
    cd GitSwift
    ```
3. **Install Required Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. **Run the Application:**
    ```bash
    python "GitSwift.py"
    ```
2. **Authenticate:**
    - Enter your GitHub Personal Access Token.
    - Optionally save the token for future use.
3. **Select Project Directory:**
    - Browse and select the local project folder you wish to upload.
4. **Configure Repository Settings:**
    - Specify repository name, description, visibility, and license.
5. **Upload to GitHub:**
    - Click on the "Upload to GitHub" button to initiate the upload process.
6. **Monitor Status:**
    - View real-time status updates in the status display area.

## Requirements

Ensure you have Python 3.6 or higher installed. Install the necessary packages using the following commands: 

bash
pip install PyQt5
pip install PyGithub


## Example Use Case

**Scenario:** You're a freelance developer working on a client's project locally. Once the project is complete, you want to upload it to GitHub for version control and future collaboration.

**Steps:**
1. Open GitSwift and authenticate with your GitHub account.
2. Select the client's project directory.
3. Enter a repository name, add a description, choose visibility, and select an appropriate license.
4. Click "Upload to GitHub" and monitor the upload status.
5. Once completed, share the repository link with your client for access and collaboration.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the [MIT License](LICENSE).