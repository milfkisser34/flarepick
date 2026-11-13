
import os
from pathlib import Path

from modules.userdata import Userdata
from interface import Application
from database import Database

if __name__ == "__main__":
    userdata = Userdata(Path('userdata'))
    sqlite = Database(userdata.join("flarepick.sqlite3"))

    app = Application(userdata = userdata, database = sqlite)
    app.show()
