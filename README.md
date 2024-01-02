# Squid Games

Squid Games is an open-source platform that enables users to host coding quizzes and competitions. Whether you're conducting job interviews, facilitating coding challenges for educational purposes, or organizing coding competitions, Squid Games provides a flexible framework for creating and managing coding assessments.

## Features

- **Scalable and Extensible:** Easily scale and customize the platform to meet your specific needs. The modular design allows for the addition of new coding quizzes and games.

- **Server-Client Architecture:** The platform consists of a server component responsible for managing player profiles, hosting game modules, producing quizzes, and benchmarking solutions. The client component enables players to implement solutions in Python, handling authentication, quiz retrieval, solver invocation, and solution submission.

- **Simple Game Integration:** Adding new coding quizzes is straightforward. Simply implement a Python class with two functions, and follow the guidelines outlined in `adding_games.md` under the server directory.

## Getting Started

To get started with Squid Games, follow these steps:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/squid-games.git

2. **Install Dependencies:**
   ```bash
   cd squid-games\server
   pip install -r requirements.txt

   Current repo assumes you'll be using MS SQL via ODBC 17 drivers. Unless you choose to deploy a different DB, you may need to follow
   these steps to install the MS ODBC drivers:
   https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/install-microsoft-odbc-driver-sql-server-macos?view=sql-server-ver16
   On Apple M1/M2 you may need to install pyodbc with https://github.com/mkleehammer/pyodbc/issues/885
   
2. **Setup Database:**
   ```bash
   TODO
   
4. **Run the Server Locally:**
   ```bash
   python server/main.py --adminDBPassword password

4. **Run the Client:**
   ```bash
   python client/game_client.py --username name --password password
