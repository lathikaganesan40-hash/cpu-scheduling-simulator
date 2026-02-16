import tkinter as tk
from tkinter import ttk, filedialog
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
import copy

# ---------------- Process Class ----------------
class Process:
    def __init__(self, pid, at, bt, pr):
        self.pid = pid
        self.at = at
        self.bt = bt
        self.pr = pr
        self.ct = 0
        self.tat = 0
        self.wt = 0


# ---------------- Scheduling Algorithms ----------------
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


def sjf(processes):
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


def preemptive_priority(processes):
    time = 0
    gantt = []
    completed = []
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


def round_robin(processes, quantum):
    time = 0
    queue = deque()
    gantt = []
    completed = []
    remaining = {p.pid: p.bt for p in processes}

    processes.sort(key=lambda x: x.at)
    i = 0

    while queue or i < len(processes):
        while i < len(processes) and processes[i].at <= time:
            queue.append(processes[i])
            i += 1

        if not queue:
            time += 1
            continue

        p = queue.popleft()
        exec_time = min(quantum, remaining[p.pid])
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


# ---------------- GUI Functions ----------------
def create_fields():
    for widget in input_frame.winfo_children():
        widget.destroy()

    arrival_entries.clear()
    burst_entries.clear()
    priority_entries.clear()

    headers = ["PID", "Arrival", "Burst", "Priority"]
    for col, text in enumerate(headers):
        tk.Label(input_frame, text=text, bg="#eef2f7", font=("Arial", 10, "bold")).grid(row=0, column=col)

    for i in range(num_procs.get()):
        tk.Label(input_frame, text=f"P{i+1}", bg="#eef2f7").grid(row=i+1, column=0)
        at = tk.Entry(input_frame, width=6)
        bt = tk.Entry(input_frame, width=6)
        pr = tk.Entry(input_frame, width=6)
        at.grid(row=i+1, column=1)
        bt.grid(row=i+1, column=2)
        pr.grid(row=i+1, column=3)
        arrival_entries.append(at)
        burst_entries.append(bt)
        priority_entries.append(pr)


def draw_gantt(gantt):
    for widget in gantt_frame.winfo_children():
        widget.destroy()

    fig, ax = plt.subplots(figsize=(7, 2))
    for pid, start, duration in gantt:
        ax.barh(0, duration, left=start)
        ax.text(start + duration/2, 0, f"P{pid}", ha='center', va='center', color='white')
    ax.set_yticks([])
    ax.set_xlabel("Time")
    ax.set_title("Gantt Chart")
    canvas = FigureCanvasTkAgg(fig, gantt_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()


def run_simulation():
    processes = []
    for i in range(num_procs.get()):
        processes.append(Process(
            i+1,
            int(arrival_entries[i].get()),
            int(burst_entries[i].get()),
            int(priority_entries[i].get())
        ))

    algo = algo_var.get()

    if algo == "FCFS":
        result, gantt = fcfs(processes)
    elif algo == "SJF":
        result, gantt = sjf(processes)
    elif algo == "Priority":
        result, gantt = priority_np(processes)
    elif algo == "Preemptive Priority":
        result, gantt = preemptive_priority(processes)
    else:
        result, gantt = round_robin(processes, int(quantum_entry.get()))

    for row in table.get_children():
        table.delete(row)

    avg_wt = avg_tat = 0
    for p in result:
        table.insert("", "end", values=(f"P{p.pid}", p.at, p.bt, p.pr, p.ct, p.tat, p.wt))
        avg_wt += p.wt
        avg_tat += p.tat

    avg_wt /= len(result)
    avg_tat /= len(result)

    avg_label.config(text=f"Avg WT: {avg_wt:.2f}   Avg TAT: {avg_tat:.2f}")
    draw_gantt(gantt)
    auto_compare()


def auto_compare():
    algorithms = ["FCFS", "SJF", "Priority", "Preemptive Priority", "Round Robin"]
    results = []

    base_processes = []
    for i in range(num_procs.get()):
        base_processes.append(Process(
            i+1,
            int(arrival_entries[i].get()),
            int(burst_entries[i].get()),
            int(priority_entries[i].get())
        ))

    for algo in algorithms:
        processes = copy.deepcopy(base_processes)

        if algo == "FCFS":
            result, _ = fcfs(processes)
        elif algo == "SJF":
            result, _ = sjf(processes)
        elif algo == "Priority":
            result, _ = priority_np(processes)
        elif algo == "Preemptive Priority":
            result, _ = preemptive_priority(processes)
        else:
            result, _ = round_robin(processes, int(quantum_entry.get()))

        avg_wt = sum(p.wt for p in result) / len(result)
        avg_tat = sum(p.tat for p in result) / len(result)
        results.append((algo, avg_wt, avg_tat))

    min_wt = min(r[1] for r in results)

    for row in comparison_table.get_children():
        comparison_table.delete(row)

    comparison_table.config(height=len(results))

    for algo, wt, tat in results:
        if wt == min_wt:
            comparison_table.insert("", "end", values=(algo, f"{wt:.2f}", f"{tat:.2f}"), tags=("best",))
        else:
            comparison_table.insert("", "end", values=(algo, f"{wt:.2f}", f"{tat:.2f}"))


# ---------------- GUI Layout ----------------
root = tk.Tk()
root.title("CPU Scheduling Simulator - Mini Project")
root.geometry("1100x700")
root.configure(bg="#e8eef5")

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", rowheight=28)

# LEFT PANEL
left_frame = tk.Frame(root, bg="#eef2f7", padx=10, pady=10)
left_frame.pack(side="left", fill="y")

tk.Label(left_frame, text="Process Setup", bg="#eef2f7",
         font=("Arial", 14, "bold")).pack(pady=5)

num_procs = tk.IntVar(value=4)
algo_var = tk.StringVar(value="FCFS")

tk.Label(left_frame, text="Processes", bg="#eef2f7").pack()
tk.Entry(left_frame, textvariable=num_procs, width=6).pack()

tk.Button(left_frame, text="Create Fields",
          bg="#4a90e2", fg="white",
          font=("Arial", 10, "bold"),
          command=create_fields).pack(pady=5)

tk.Label(left_frame, text="Algorithm", bg="#eef2f7").pack()
ttk.Combobox(left_frame, textvariable=algo_var,
             values=["FCFS", "SJF", "Priority",
                     "Preemptive Priority", "Round Robin"],
             state="readonly").pack()

tk.Label(left_frame, text="Quantum (RR)", bg="#eef2f7").pack()
quantum_entry = tk.Entry(left_frame, width=6)
quantum_entry.insert(0, "2")
quantum_entry.pack()

tk.Button(left_frame, text="Run Simulation",
          bg="#ff9800", fg="white",
          font=("Arial", 11, "bold"),
          padx=10, pady=5,
          command=run_simulation).pack(pady=10)

# Comparison Table
tk.Label(left_frame, text="Algorithm Comparison",
         bg="#eef2f7", font=("Arial", 12, "bold")).pack()

comp_columns = ("Algorithm", "Avg WT", "Avg TAT")
comparison_table = ttk.Treeview(left_frame,
                                 columns=comp_columns,
                                 show="headings",
                                 height=5)

for col in comp_columns:
    comparison_table.heading(col, text=col)
    comparison_table.column(col, width=110)

comparison_table.tag_configure("best", background="#c8f7c5")
comparison_table.pack(pady=5)

# RIGHT PANEL
right_frame = tk.Frame(root, bg="#e8eef5")
right_frame.pack(side="right", fill="both", expand=True)

columns = ("PID", "AT", "BT", "Priority", "CT", "TAT", "WT")
table = ttk.Treeview(right_frame, columns=columns, show="headings")

for col in columns:
    table.heading(col, text=col)
    table.column(col, width=90)

scroll_y = ttk.Scrollbar(right_frame, orient="vertical", command=table.yview)
table.configure(yscroll=scroll_y.set)

scroll_y.pack(side="right", fill="y")
table.pack(side="left", fill="both", expand=True)

avg_label = tk.Label(root, font=("Arial", 11, "bold"), bg="#e8eef5")
avg_label.pack(pady=5)

# BOTTOM GANTT
gantt_frame = tk.Frame(root, bg="#e8eef5")
gantt_frame.pack(fill="x", pady=10)

input_frame = tk.Frame(left_frame, bg="#eef2f7")
input_frame.pack(pady=5)

arrival_entries = []
burst_entries = []
priority_entries = []

create_fields()

root.mainloop()
