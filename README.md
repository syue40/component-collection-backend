# Component Collection Backend
This small Flask application is used as the backend for the Component Collection application. It has some basic functionality for querying a PostgreSQL database. It also has methods for modifying user data stored in the database, as well as methods for sending emails when requested.

The database I'm currently using for this project is a copy of the popular DVD Rental database. I currently have a copy of the database running locally, but have plans to deploy a copy to Azure.

Also in the works are the backend functions for managing new users/login/sign-up.

### Quick Start Guide
1. Please ensure both Python and pip are installed (pip/python --version)
2. Clone this repository to your local device via link or ```git clone https://github.com/syue40/component-collection-backend.git```
3. Spin up a venv in the root repository (https://docs.python.org/3/library/venv.html)
4. Install the required dependencies with ```pip install -r requirements.txt```
5. In the root folder, run ```python app.py``` (```flask run``` also works if you have it installed already)
6. By default this applet runs on ```http://localhost:5000/``` 


### Below is a copy of the ERD for the DVD Rental Database
<img src="dvd-erd.png" width="500" height="600"></img>


### Here is the File Structure for the Backend 
```
┣📦config 
┣ ┗ 📜flask_config.py
┣📦utils
┣ ┗ 📜dao.py
┣📦routes
┣ ┣ 📜auth.py
┣ ┗ 📜portfolio.py
┣📜app.py
┣📜requirements.txt
┣📜README.md
 ```
