import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque


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
def fcfs_scheduling(processes):
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


def sjf_scheduling(processes):
    time = 0
    completed = []
    gantt = []

    while processes:
        ready = [p for p in processes if p.at <= time]
        if not ready:
            time += 1
            continue

        ready.sort(key=lambda x: (x.bt, x.at))
        p = ready[0]
        processes.remove(p)

        gantt.append((p.pid, time, p.bt))
        time += p.bt
        p.ct = time
        p.tat = p.ct - p.at
        p.wt = p.tat - p.bt
        completed.append(p)

    return completed, gantt


def priority_scheduling(processes):
    time = 0
    completed = []
    gantt = []

    while processes:
        ready = [p for p in processes if p.at <= time]
        if not ready:
            time += 1
            continue

        ready.sort(key=lambda x: (x.pr, x.at))
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

        ready.sort(key=lambda x: (x.pr, x.at))
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
def get_process_input():
    processes = []
    try:
        for i in range(num_procs.get()):
            processes.append(Process(
                i + 1,
                int(arrival_entries[i].get()),
                int(burst_entries[i].get()),
                int(priority_entries[i].get())
            ))
    except:
        messagebox.showerror("Input Error", "Enter valid numeric values.")
        return None
    return processes


def run_simulation():
    original = get_process_input()
    if not original:
        return

    processes = [Process(p.pid, p.at, p.bt, p.pr) for p in original]
    algo = algo_var.get()

    if algo == "FCFS":
        result, gantt = fcfs_scheduling(processes)
    elif algo == "SJF":
        result, gantt = sjf_scheduling(processes)
    elif algo == "Priority":
        result, gantt = priority_scheduling(processes)
    elif algo == "Preemptive Priority":
        result, gantt = preemptive_priority(processes)
    else:
        q = int(quantum_entry.get())
        result, gantt = round_robin(processes, q)

    table.delete(*table.get_children())

    avg_wt = sum(p.wt for p in result) / len(result)
    avg_tat = sum(p.tat for p in result) / len(result)

    for p in result:
        table.insert("", "end",
                     values=(f"P{p.pid}", p.at, p.bt, p.pr,
                             p.ct, p.tat, p.wt))

    avg_label.config(text=f"Average WT: {avg_wt:.2f}    "
                          f"Average TAT: {avg_tat:.2f}")

    draw_gantt(gantt)

    auto_compare(original)


def auto_compare(original):
    comparison_table.delete(*comparison_table.get_children())

    algorithms = [
        ("FCFS", fcfs_scheduling),
        ("SJF", sjf_scheduling),
        ("Priority", priority_scheduling),
        ("Preemptive Priority", preemptive_priority),
    ]

    results = []

    for name, func in algorithms:
        processes = [Process(p.pid, p.at, p.bt, p.pr) for p in original]
        result, _ = func(processes)

        avg_wt = sum(p.wt for p in result) / len(result)
        avg_tat = sum(p.tat for p in result) / len(result)

        results.append((name, avg_wt, avg_tat))

    best_wt = min(results, key=lambda x: x[1])[1]

    for name, wt, tat in results:
        tag = "best" if wt == best_wt else ""
        comparison_table.insert("", "end",
                                values=(name,
                                        f"{wt:.2f}",
                                        f"{tat:.2f}"),
                                tags=(tag,))

    comparison_table.tag_configure("best",
                                    background="#d4edda",
                                    font=("Arial", 10, "bold"))


def draw_gantt(gantt):
    for widget in gantt_frame.winfo_children():
        widget.destroy()

    fig, ax = plt.subplots(figsize=(8, 2))

    for pid, start, duration in gantt:
        ax.barh(0, duration, left=start)
        ax.text(start + duration / 2, 0, f"P{pid}",
                ha='center', va='center', color='white')

    ax.set_title("Gantt Chart")
    ax.set_xlabel("Time")
    ax.set_yticks([])

    canvas = FigureCanvasTkAgg(fig, gantt_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()


# ---------------- GUI Layout ----------------
root = tk.Tk()
root.title("CPU Scheduling Simulator - Mini Project")
root.geometry("1150x720")

main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

left = tk.Frame(main_frame, padx=15)
left.pack(side="left", fill="y")

right = tk.Frame(main_frame)
right.pack(side="right", fill="both", expand=True)

bottom = tk.Frame(root)
bottom.pack(fill="x")

tk.Label(left, text="CPU Scheduling Simulator",
         font=("Arial", 15, "bold")).pack(pady=10)

num_procs = tk.IntVar(value=4)
algo_var = tk.StringVar(value="FCFS")

tk.Label(left, text="Number of Processes").pack()
tk.Entry(left, textvariable=num_procs, width=8).pack()

tk.Button(left, text="Create Fields",
          width=18, command=lambda: create_fields()).pack(pady=5)

tk.Label(left, text="Algorithm").pack()
ttk.Combobox(left, textvariable=algo_var,
             values=["FCFS", "SJF", "Priority",
                     "Preemptive Priority", "Round Robin"],
             state="readonly").pack()

tk.Label(left, text="Quantum (RR)").pack()
quantum_entry = tk.Entry(left, width=8)
quantum_entry.insert(0, "2")
quantum_entry.pack()

tk.Button(left, text="Run Simulation",
          bg="orange", width=18, height=2,
          command=run_simulation).pack(pady=10)

input_frame = tk.Frame(left)
input_frame.pack(pady=10)

arrival_entries = []
burst_entries = []
priority_entries = []

def create_fields():
    for widget in input_frame.winfo_children():
        widget.destroy()

    arrival_entries.clear()
    burst_entries.clear()
    priority_entries.clear()

    tk.Label(input_frame, text="PID").grid(row=0, column=0)
    tk.Label(input_frame, text="AT").grid(row=0, column=1)
    tk.Label(input_frame, text="BT").grid(row=0, column=2)
    tk.Label(input_frame, text="PR").grid(row=0, column=3)

    for i in range(num_procs.get()):
        tk.Label(input_frame, text=f"P{i+1}").grid(row=i+1, column=0)
        at = tk.Entry(input_frame, width=5)
        bt = tk.Entry(input_frame, width=5)
        pr = tk.Entry(input_frame, width=5)
        at.grid(row=i+1, column=1)
        bt.grid(row=i+1, column=2)
        pr.grid(row=i+1, column=3)

        arrival_entries.append(at)
        burst_entries.append(bt)
        priority_entries.append(pr)

# Result Table
columns = ("PID", "AT", "BT", "PR", "CT", "TAT", "WT")
scroll = ttk.Scrollbar(right)
scroll.pack(side="right", fill="y")

table = ttk.Treeview(right, columns=columns,
                     show="headings",
                     yscrollcommand=scroll.set)

scroll.config(command=table.yview)

for col in columns:
    table.heading(col, text=col)
    table.column(col, width=100)

table.pack(fill="both", expand=True)

avg_label = tk.Label(right, font=("Arial", 11, "bold"))
avg_label.pack(pady=5)

# Comparison Table
tk.Label(left, text="Algorithm Comparison",
         font=("Arial", 11, "bold")).pack(pady=10)

comparison_table = ttk.Treeview(left,
                                columns=("Algorithm", "Avg WT", "Avg TAT"),
                                show="headings",
                                height=5)

for col in ("Algorithm", "Avg WT", "Avg TAT"):
    comparison_table.heading(col, text=col)
    comparison_table.column(col, width=120)

comparison_table.pack()

# Gantt
gantt_frame = tk.Frame(bottom)
gantt_frame.pack(pady=10)

root.mainloop()
