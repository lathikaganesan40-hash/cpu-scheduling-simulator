import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
import copy

# ---------------- Process Class ----------------
class Process:
    def __init__(self, pid, at, bt, pr=0):
        self.pid = pid
        self.at = at
        self.bt = bt
        self.pr = pr
        self.ct = 0
        self.tat = 0
        self.wt = 0


# ---------------- Scheduling Algorithms ----------------

# FCFS
def fcfs(processes):
    time = 0
    gantt = []
    processes.sort(key=lambda x: x.at)

    for p in processes:
        if time < p.at:
            time = p.at
        gantt.append((p.pid, time, p.bt))
        time += p.bt
        p.ct = time
        p.tat = p.ct - p.at
        p.wt = p.tat - p.bt
    return processes, gantt


# SJF Non-Preemptive
def sjf_np(processes):
    time = 0
    completed = []
    gantt = []

    while processes:
        ready = [p for p in processes if p.at <= time]
        if not ready:
            time += 1
            continue

        ready.sort(key=lambda x: x.bt)
        p = ready[0]
        processes.remove(p)

        gantt.append((p.pid, time, p.bt))
        time += p.bt

        p.ct = time
        p.tat = p.ct - p.at
        p.wt = p.tat - p.bt
        completed.append(p)

    return completed, gantt


# SJF Preemptive (SRTF)
def sjf_preemptive(processes):
    time = 0
    completed = []
    gantt = []
    remaining = {p.pid: p.bt for p in processes}

    while len(completed) < len(processes):
        ready = [p for p in processes if p.at <= time and remaining[p.pid] > 0]
        if not ready:
            time += 1
            continue

        ready.sort(key=lambda x: remaining[x.pid])
        p = ready[0]

        gantt.append((p.pid, time, 1))
        remaining[p.pid] -= 1
        time += 1

        if remaining[p.pid] == 0:
            p.ct = time
            p.tat = p.ct - p.at
            p.wt = p.tat - p.bt
            completed.append(p)

    return completed, gantt


# Priority Non-Preemptive
def priority_np(processes):
    time = 0
    completed = []
    gantt = []

    while processes:
        ready = [p for p in processes if p.at <= time]
        if not ready:
            time += 1
            continue

        ready.sort(key=lambda x: x.pr)
        p = ready[0]
        processes.remove(p)

        gantt.append((p.pid, time, p.bt))
        time += p.bt

        p.ct = time
        p.tat = p.ct - p.at
        p.wt = p.tat - p.bt
        completed.append(p)

    return completed, gantt


# Priority Preemptive
def priority_preemptive(processes):
    time = 0
    completed = []
    gantt = []
    remaining = {p.pid: p.bt for p in processes}

    while len(completed) < len(processes):
        ready = [p for p in processes if p.at <= time and remaining[p.pid] > 0]
        if not ready:
            time += 1
            continue

        ready.sort(key=lambda x: x.pr)
        p = ready[0]

        gantt.append((p.pid, time, 1))
        remaining[p.pid] -= 1
        time += 1

        if remaining[p.pid] == 0:
            p.ct = time
            p.tat = p.ct - p.at
            p.wt = p.tat - p.bt
            completed.append(p)

    return completed, gantt


# Round Robin
def round_robin(processes, q):
    time = 0
    queue = deque()
    gantt = []
    remaining = {p.pid: p.bt for p in processes}
    processes.sort(key=lambda x: x.at)
    i = 0
    completed = []

    while queue or i < len(processes):
        while i < len(processes) and processes[i].at <= time:
            queue.append(processes[i])
            i += 1

        if not queue:
            time += 1
            continue

        p = queue.popleft()
        exec_time = min(q, remaining[p.pid])

        gantt.append((p.pid, time, exec_time))
        time += exec_time
        remaining[p.pid] -= exec_time

        while i < len(processes) and processes[i].at <= time:
            queue.append(processes[i])
            i += 1

        if remaining[p.pid] > 0:
            queue.append(p)
        else:
            p.ct = time
            p.tat = p.ct - p.at
            p.wt = p.tat - p.bt
            completed.append(p)

    return completed, gantt


# ---------------- GUI ----------------
root = tk.Tk()
root.title("CPU Scheduling Simulator - Mini Project")
root.geometry("1200x750")

style = ttk.Style()
style.theme_use("clam")

style.configure("Treeview.Heading",
                background="#1e3d59",
                foreground="white",
                font=("Arial", 11, "bold"))

style.configure("Treeview",
                background="#f5f7fa",
                foreground="black",
                rowheight=28,
                fieldbackground="#f5f7fa")

style.map("Treeview",
          background=[("selected", "#ff9800")],
          foreground=[("selected", "white")])

tk.Label(root,
         text="CPU Scheduling Algorithm Simulator",
         font=("Arial", 20, "bold"),
         fg="#1e3d59").pack(pady=15)

main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

# LEFT PANEL
left_panel = tk.Frame(main_frame)
left_panel.pack(side="left", fill="y", padx=15)

num_procs = tk.IntVar(value=4)
algo_var = tk.StringVar(value="FCFS")

tk.Label(left_panel, text="Number of Processes").pack()
tk.Entry(left_panel, textvariable=num_procs, width=8).pack()

tk.Label(left_panel, text="Algorithm").pack(pady=5)
ttk.Combobox(left_panel,
             textvariable=algo_var,
             values=["FCFS",
                     "SJF (Non-Preemptive)",
                     "SJF (Preemptive)",
                     "Priority (Non-Preemptive)",
                     "Priority (Preemptive)",
                     "Round Robin"],
             state="readonly",
             width=25).pack()

tk.Label(left_panel, text="Quantum (RR)").pack()
quantum_entry = tk.Entry(left_panel, width=8)
quantum_entry.insert(0, "2")
quantum_entry.pack()

# RIGHT PANEL
right_panel = tk.Frame(main_frame)
right_panel.pack(side="right", fill="both", expand=True)

# RESULT TABLE
columns = ("PID", "AT", "BT", "Priority", "CT", "TAT", "WT")
result_table = ttk.Treeview(right_panel,
                            columns=columns,
                            show="headings",
                            height=8)

for col in columns:
    result_table.heading(col, text=col)
    result_table.column(col, width=90)

result_table.pack(pady=10)

# COMPARISON TABLE
tk.Label(right_panel,
         text="Algorithm Comparison",
         font=("Arial", 13, "bold"),
         fg="#1e3d59").pack()

comp_columns = ("Algorithm", "Avg WT", "Avg TAT")
comparison_table = ttk.Treeview(right_panel,
                                columns=comp_columns,
                                show="headings",
                                height=6)

for col in comp_columns:
    comparison_table.heading(col, text=col)
    comparison_table.column(col, width=180)

comparison_table.pack(pady=10)

comparison_table.tag_configure("best", background="#c8f7c5")

root.mainloop()
