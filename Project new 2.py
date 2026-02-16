import tkinter as tk
from tkinter import ttk, filedialog
import copy
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import utils

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
    completed, gantt = [], []
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
    completed, gantt = [], []
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

# ---------------- Metrics ----------------
def calculate_cpu_utilization(gantt):
    busy_time = sum(duration for _, _, duration in gantt)
    total_time = max(start + duration for _, start, duration in gantt)
    return (busy_time / total_time) * 100

def calculate_throughput(processes):
    total_time = max(p.ct for p in processes)
    return len(processes) / total_time

# ---------------- Animated Gantt ----------------
def draw_gantt_animated(gantt):
    for widget in gantt_frame.winfo_children():
        widget.destroy()

    fig, ax = plt.subplots(figsize=(7,2))
    ax.set_yticks([])
    ax.set_xlabel("Time")
    ax.set_title("Gantt Chart")

    canvas = FigureCanvasTkAgg(fig, gantt_frame)
    canvas.get_tk_widget().pack()
    canvas.draw()

    index = 0

    def animate():
        nonlocal index
        if index >= len(gantt):
            return
        pid, start, duration = gantt[index]
        ax.barh(0, duration, left=start)
        ax.text(start+duration/2, 0, f"P{pid}", ha='center', va='center', color='white')
        canvas.draw()
        index += 1
        root.after(300, animate)

    animate()

# ---------------- Dark Mode ----------------
dark_mode = False
def toggle_dark_mode():
    global dark_mode
    dark_mode = not dark_mode
    bg = "#1e1e1e" if dark_mode else "#f0f4f8"
    fg = "white" if dark_mode else "black"
    root.configure(bg=bg)
    left_frame.configure(bg=bg)
    right_frame.configure(bg=bg)
    gantt_frame.configure(bg=bg)

# ---------------- PDF Report ----------------
def save_pdf_report():
    file = filedialog.asksaveasfilename(defaultextension=".pdf")
    if not file:
        return

    doc = SimpleDocTemplate(file)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("CPU Scheduling Project Report", styles['Title']))
    elements.append(Spacer(1, 12))

    data = [["PID","AT","BT","PR","CT","TAT","WT"]]
    for row in table.get_children():
        data.append(table.item(row)['values'])

    t = Table(data)
    t.setStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.grey),
        ('GRID',(0,0),(-1,-1),1,colors.black)
    ])

    elements.append(t)
    doc.build(elements)

# ---------------- Simulation ----------------
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

    for p in result:
        table.insert("", "end", values=(p.pid,p.at,p.bt,p.pr,p.ct,p.tat,p.wt))

    cpu_util = calculate_cpu_utilization(gantt)
    throughput = calculate_throughput(result)

    metrics_label.config(text=f"CPU Utilization: {cpu_util:.2f}%   Throughput: {throughput:.2f}")

    draw_gantt_animated(gantt)

# ---------------- GUI Layout ----------------
root = tk.Tk()
root.title("Advanced CPU Scheduling Simulator")
root.geometry("1200x750")
root.configure(bg="#f0f4f8")

left_frame = tk.Frame(root, bg="#f0f4f8", padx=15)
left_frame.pack(side="left", fill="y")

right_frame = tk.Frame(root, bg="#f0f4f8")
right_frame.pack(side="right", fill="both", expand=True)

gantt_frame = tk.Frame(root, bg="#f0f4f8")
gantt_frame.pack(side="bottom", fill="x", pady=10)

tk.Label(left_frame, text="Controls", font=("Arial",14,"bold"), bg="#f0f4f8").pack(pady=5)

num_procs = tk.IntVar(value=4)
algo_var = tk.StringVar(value="FCFS")

tk.Label(left_frame, text="Processes", bg="#f0f4f8").pack()
tk.Entry(left_frame, textvariable=num_procs, width=6).pack()

tk.Button(left_frame, text="Dark Mode Toggle", command=toggle_dark_mode,
          width=20, pady=5).pack(pady=5)

tk.Label(left_frame, text="Algorithm", bg="#f0f4f8").pack()
ttk.Combobox(left_frame, textvariable=algo_var,
             values=["FCFS","SJF","Priority","Preemptive Priority","Round Robin"],
             state="readonly").pack()

tk.Label(left_frame, text="Quantum", bg="#f0f4f8").pack()
quantum_entry = tk.Entry(left_frame,width=6)
quantum_entry.insert(0,"2")
quantum_entry.pack()

tk.Button(left_frame, text="Run Simulation", width=20, pady=8,
          bg="#ff9800", command=run_simulation).pack(pady=10)

tk.Button(left_frame, text="Save PDF Report", width=20, pady=5,
          bg="#4caf50", command=save_pdf_report).pack(pady=5)

columns=("PID","AT","BT","PR","CT","TAT","WT")
table=ttk.Treeview(right_frame,columns=columns,show="headings")
for col in columns:
    table.heading(col,text=col)
    table.column(col,width=90)

scroll=ttk.Scrollbar(right_frame,orient="vertical",command=table.yview)
table.configure(yscroll=scroll.set)
scroll.pack(side="right",fill="y")
table.pack(fill="both",expand=True)

metrics_label=tk.Label(root,font=("Arial",11,"bold"),bg="#f0f4f8")
metrics_label.pack(pady=5)

arrival_entries=[]
burst_entries=[]
priority_entries=[]

root.mainloop()
