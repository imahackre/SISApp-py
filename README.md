# SISApp-py 🎓

Welcome to **SISApp-py**! This is a simple yet functional Student Information System built using Python. It's a database application using only locally stored CSV files.


## 🚀 What it Does

The app is divided into three main sections to keep data organized:

### 1. Students Tab
This is the core of the app. You can manage student profiles with the following attributes:
* **Details:** School ID, First Name, Last Name, Program, Year Level, and Gender.
* **Search:** Quick search across all student fields.
* **Filtering:** I've added a filter toggle so you can sort through students by **Gender, Year Level, or College**.

### 2. Programs Tab
Manages the different academic tracks available:
* **Attributes:** Program Code, Program Name, and the linked College Code.
* **Filter/Search:** Includes a search bar and a filter to view programs by specific Colleges.

### 3. Colleges Tab
The high-level organizational view:
* **Attributes:** College Code and College Name.

## ✨ Key Features I Included

* **No Setup Needed:** The program automatically creates the necessary CSV files on the first run. No need to manually set up a database.
* **Smart Sorting:** You can click any column header in the tables to instantly sort the data (A-Z or numerical).
* **Live Counters:** Each tab shows a "Records count" at the bottom so you always know exactly how many records are in your system, filtered or not.
* **CRUDL Ready:** Full support to **Add, Update, and Delete** entries across all three tabs.

## 🛡️ Data Integrity & Constraints
I implemented specific logic to ensure the database remains consistent and free of errors:

* **Deletion Protection:** To prevent "orphaned" data, the system **will not allow you to delete a College or Program** if there are still students enrolled or linked to them. 
* **Manual Updates:** Currently, deleting or changing a College/Program code does not automatically "cascade" or update linked students. Because of this, the app requires you to clear or move students/programs first before a parent record can be removed.
* **Auto-Database:** On the first run, the app automatically generates the required CSV files—no manual setup needed.
* **Live Counters:** Each tab features a live entry count to track how many records are currently stored.

## 💻 Getting Started

### Prerequisites
- Python 3.x
- `customtkinter` library

### Installation
1. **Clone the repo:**
   ```bash
   git clone [https://github.com/gitnsaen/SISApp-py.git](https://github.com/gitnsaen/SISApp-py.git)
   cd SISApp-py

2. **Install Dependencies:**
This app requires customtkinter for the UI.
   ```bash
   pip install customtkinter

3. **Run the App:**
   ```bash
   python main.py

## 📂 Data Structure
The app manages three interconnected CSV files:
- `students.csv`
- `programs.csv`
- `colleges.csv`

     
@gitnsaen
