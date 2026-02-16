
# 🖥 CPU Scheduling Simulator

> A GUI-based Operating Systems project that simulates and compares classical CPU scheduling algorithms with real-time performance metrics.

##  Overview

The **CPU Scheduling Simulator** is a desktop application developed in Python that provides an interactive environment to simulate, analyze, and compare multiple CPU scheduling algorithms.

It enables users to visualize how scheduling strategies influence:

* Completion Time (CT)
* Waiting Time (WT)
* Turnaround Time (TAT)
* Average Performance Metrics
* Execution Order of Processes

This project bridges theoretical OS concepts with practical simulation.

##  Objectives

* To implement core CPU scheduling algorithms.
* To analyze algorithm efficiency using performance metrics.
* To provide an interactive GUI for real-time simulation.
* To compare algorithm performance under identical input conditions.


##  Key Features

* Interactive GUI using Tkinter
* Dynamic process input table
* Multiple scheduling algorithm support
* Automatic metric computation (CT, WT, TAT)
* Average Waiting Time & Turnaround Time calculation
* Algorithm comparison table
* Clean tabular result visualization

## Algorithms Implemented

| Algorithm   | Type           | Description                            |
| ----------- | -------------- | -------------------------------------- |
| FCFS        | Non-Preemptive | Executes processes in order of arrival |
| SJF         | Non-Preemptive | Executes shortest burst time first     |
| SRTF        | Preemptive     | Preemptive version of SJF              |
| Round Robin | Preemptive     | Time-slice based fair scheduling       |



##  Performance Metrics Calculated

* **Completion Time (CT)**
* **Turnaround Time (TAT) = CT – AT**
* **Waiting Time (WT) = TAT – BT**
* **Average Waiting Time**
* **Average Turnaround Time**



## Tech Stack

* **Language:** Python 3
* **GUI Framework:** Tkinter
* **Version Control:** Git
* **Repository Hosting:** GitHub

---

## 🖼 Project Interface

| Process Input             | Simulation Result          | Comparison Table               |
| ------------------------- | -------------------------- | ------------------------------ |
| ![Input](screenshot1.png) | ![Result](screenshot2.png) | ![Comparison](screenshot3.png) |

---

## ▶️ Installation & Execution

### 1️⃣ Clone the Repository

git clone https://github.com/lathikaganesan40-hash/cpu-scheduling-simulator.git

### 2️⃣ Navigate to Project Directory

cd cpu-scheduling-simulator

### 3️⃣ Run the Application

python cpu_scheduling_simulator.py

> Ensure Python 3.x is installed.


## Project Structure

cpu-scheduling-simulator/
│
├── cpu_scheduling_simulator.py
├── screenshot1.png
├── screenshot2.png
├── screenshot3.png
└── README.md


## Sample Execution Flow

1. Select scheduling algorithm
2. Enter number of processes
3. Provide arrival time & burst time
4. Click "Run Simulation"
5. View calculated metrics and comparison results


## Academic Relevance

This simulator demonstrates:

* Preemptive vs Non-Preemptive Scheduling
* Context Switching impact
* Starvation and fairness concepts
* Scheduling efficiency comparison

## Future Improvements

* Add graphical Gantt Chart visualization
* Add Priority Scheduling implementation
* Add export-to-PDF report feature
* Convert to web-based version (Flask / Django)

## Authors

* Lathika G
* Pothumani A
* Sankara Narayani T

B.E – Computer Science and Engineering
II Year


