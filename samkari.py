import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
import copy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------------- Process Class ----------------
class Process:
    def __init__(self, pid, at, bt, pr=0):
        self.pid = pid
        self.at = at
        self.bt = bt
        self.pr = pr
        self.ct = self.tat = self.wt = 0

# ---------------- Algorithms ----------------
def fcfs(processes):
    time, gantt = 0, []
    processes.sort(key=lambda x: x.at)
    for p in processes:
        if time < p.at: time = p.at
        gantt.append((p.pid, time, p.bt))
        time += p.bt
        p.ct = time
        p.tat = p.ct - p.at
        p.wt = p.tat - p.bt
    return processes, gantt

def sjf_np(processes):
    time, completed, gantt = 0, [], []
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

def sjf_preemptive(processes):
    time, completed, gantt = 0, [], []
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

def priority_np(processes):
    time, completed, gantt = 0, [], []
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

def priority_preemptive(processes):
    time, completed, gantt = 0, [], []
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

def round_robin(processes, q):
    time, queue, gantt, completed = 0, deque(), [], []
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
        exec_time = min(q, remaining[p.pid])
        gantt.append((p.pid, time, exec_time))
        time += exec_time
        remaining[p.pid] -= exec_time
        if remaining[p.pid] > 0:
            queue.append(p)
        else:
            p.ct = time
            p.tat = p.ct - p.at
            p.wt = p.tat - p.bt
            completed.append(p)
    return completed, gantt

# ---------------- Gantt Chart ----------------
def draw_gantt(gantt):
    for w in gantt_frame.winfo_children():
        w.destroy()

    fig, ax = plt.subplots(figsize=(12, 2), dpi=100)
    colors = plt.cm.tab20.colors

    for pid, start, dur in gantt:
        ax.barh(0, dur, left=start, color=colors[pid % 20], edgecolor="black")
        ax.text(start + dur/2, 0, f"P{pid}", ha="center", va="center", color="white", fontsize=9, fontweight="bold")

    ax.set_yticks([])
    ax.set_xlabel("Time Units", fontsize=10)
    ax.set_facecolor("#1e1e2f")
    fig.patch.set_facecolor("#1e1e2f")

    canvas = FigureCanvasTkAgg(fig, gantt_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)

# ---------------- GUI ----------------
root = tk.Tk()
root.title("CPU Scheduling Simulator – Advanced")
root.geometry("1200x850")
root.configure(bg="#1e1e2f")

style = ttk.Style()
style.theme_use("clam")

style.configure("Treeview",
                background="#2b2b3c",
                foreground="white",
                fieldbackground="#2b2b3c",
                rowheight=28)

style.configure("Treeview.Heading",
                background="#4e9cff",
                foreground="white",
                font=("Segoe UI", 10, "bold"))

style.map("Treeview", background=[("selected", "#4e9cff")])

title = tk.Label(root, text="CPU SCHEDULING ALGORITHM SIMULATOR",
                 font=("Segoe UI", 20, "bold"),
                 fg="#4e9cff", bg="#1e1e2f")
title.pack(pady=15)

main = tk.Frame(root, bg="#1e1e2f")
main.pack(fill="both", expand=True, padx=20)

left = tk.Frame(main, bg="#252536", bd=2, relief="ridge")
left.pack(side="left", fill="y", padx=10)

tk.Label(left, text="Configuration", fg="white", bg="#252536",
         font=("Segoe UI", 12, "bold")).pack(pady=10)

algo_var = tk.StringVar(value="FCFS")
ttk.Combobox(left, textvariable=algo_var,
             values=["FCFS", "SJF (Non-Preemptive)", "SJF (Preemptive)",
                     "Priority (Non-Preemptive)", "Priority (Preemptive)", "Round Robin"],
             state="readonly").pack(fill="x", padx=10)

tk.Label(left, text="Quantum", fg="white", bg="#252536").pack(pady=5)
quantum_entry = tk.Entry(left)
quantum_entry.insert(0, "2")
quantum_entry.pack(fill="x", padx=10)

tk.Label(left, text="Processes", fg="white", bg="#252536").pack(pady=5)
num_procs_entry = tk.Entry(left)
num_procs_entry.insert(0, "3")
num_procs_entry.pack(fill="x", padx=10)

def create_fields():
    for w in input_frame.winfo_children():
        w.destroy()
    arrival_entries.clear()
    burst_entries.clear()
    priority_entries.clear()

    n = int(num_procs_entry.get())
    headers = ["PID", "AT", "BT", "PR"]
    for c, h in enumerate(headers):
        tk.Label(input_frame, text=h, bg="#252536", fg="#4e9cff").grid(row=0, column=c)

    for i in range(n):
        tk.Label(input_frame, text=f"P{i+1}", bg="#252536", fg="white").grid(row=i+1, column=0)
        at = tk.Entry(input_frame, width=5)
        bt = tk.Entry(input_frame, width=5)
        pr = tk.Entry(input_frame, width=5)
        at.insert(0, "0")
        bt.insert(0, "1")
        pr.insert(0, "0")
        at.grid(row=i+1, column=1)
        bt.grid(row=i+1, column=2)
        pr.grid(row=i+1, column=3)
        arrival_entries.append(at)
        burst_entries.append(bt)
        priority_entries.append(pr)

tk.Button(left, text="CREATE", bg="#4e9cff", fg="white",
          font=("Segoe UI", 10, "bold"),
          command=create_fields).pack(fill="x", padx=10, pady=10)

input_frame = tk.Frame(left, bg="#252536")
input_frame.pack(pady=5)

def run():
    procs = []
    for i in range(len(arrival_entries)):
        procs.append(Process(i+1,
                             int(arrival_entries[i].get()),
                             int(burst_entries[i].get()),
                             int(priority_entries[i].get())))

    algo = algo_var.get()
    q = int(quantum_entry.get())

    if algo == "FCFS":
        res, gantt = fcfs(procs)
    elif algo == "SJF (Non-Preemptive)":
        res, gantt = sjf_np(procs)
    elif algo == "SJF (Preemptive)":
        res, gantt = sjf_preemptive(procs)
    elif algo == "Priority (Non-Preemptive)":
        res, gantt = priority_np(procs)
    elif algo == "Priority (Preemptive)":
        res, gantt = priority_preemptive(procs)
    else:
        res, gantt = round_robin(procs, q)

    for r in table.get_children():
        table.delete(r)

    for p in res:
        table.insert("", "end",
                     values=(f"P{p.pid}", p.at, p.bt, p.pr, p.ct, p.tat, p.wt))

    draw_gantt(gantt)

tk.Button(left, text="RUN SIMULATION",
          bg="#2ecc71", fg="white",
          font=("Segoe UI", 11, "bold"),
          command=run).pack(fill="x", padx=10, pady=15)

right = tk.Frame(main, bg="#1e1e2f")
right.pack(side="right", fill="both", expand=True)

cols = ("PID", "AT", "BT", "PR", "CT", "TAT", "WT")
table = ttk.Treeview(right, columns=cols, show="headings", height=12)
for c in cols:
    table.heading(c, text=c)
    table.column(c, anchor="center", width=80)
table.pack(fill="x", pady=10)

gantt_frame = tk.Frame(right, bg="#1e1e2f")
gantt_frame.pack(fill="x", pady=10)

arrival_entries = []
burst_entries = []
priority_entries = []

create_fields()
root.mainloop()
