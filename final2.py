import tkinter as tk
from tkinter import ttk
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
        self.ct = 0
        self.tat = 0
        self.wt = 0

# ---------------- Algorithms (Logic remains the same) ----------------
def fcfs(processes):
    time = 0
    gantt = []
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
        while i < len(processes) and processes[i].at <= time:
            queue.append(processes[i])
            i += 1
        if remaining[p.pid] > 0:
            queue.append(p)
        else:
            p.ct, p.tat = time, time - p.at
            p.wt = p.tat - p.bt
            completed.append(p)
    return completed, gantt

# ---------------- GUI FUNCTIONS ----------------

def create_fields():
    for widget in input_table_frame.winfo_children():
        widget.destroy()
    arrival_entries.clear()
    burst_entries.clear()
    priority_entries.clear()

    headers = ["PID", "Arrival", "Burst", "Priority"]
    for col, text in enumerate(headers):
        tk.Label(input_table_frame, text=text, bg="#eef2f7", font=("Arial", 9, "bold")).grid(row=0, column=col, padx=2)

    for i in range(num_procs.get()):
        tk.Label(input_table_frame, text=f"P{i+1}", bg="#eef2f7").grid(row=i+1, column=0)
        at, bt, pr = tk.Entry(input_table_frame, width=5), tk.Entry(input_table_frame, width=5), tk.Entry(input_table_frame, width=5)
        at.grid(row=i+1, column=1, pady=2)
        bt.grid(row=i+1, column=2, pady=2)
        pr.grid(row=i+1, column=3, pady=2)
        arrival_entries.append(at)
        burst_entries.append(bt)
        priority_entries.append(pr)

def draw_gantt(gantt):
    for widget in gantt_frame.winfo_children():
        widget.destroy()
    # Using a smaller figure to fit at the bottom center
    fig, ax = plt.subplots(figsize=(8, 1.8), dpi=100)
    colors = plt.cm.get_cmap('tab10', 10)
    
    for i, (pid, start, duration) in enumerate(gantt):
        ax.barh(0, duration, left=start, color=colors(pid % 10), edgecolor='black')
        ax.text(start + duration/2, 0, f"P{pid}", ha='center', va='center', color='white', fontweight='bold')
    
    ax.set_yticks([])
    ax.set_xlabel("Time Units")
    ax.set_title("Gantt Chart Execution Sequence", fontsize=10)
    fig.tight_layout()
    canvas = FigureCanvasTkAgg(fig, gantt_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(anchor="center")

def run_simulation():
    try:
        processes = []
        for i in range(num_procs.get()):
            processes.append(Process(i+1, int(arrival_entries[i].get()), int(burst_entries[i].get()), int(priority_entries[i].get())))
        
        algo = algo_var.get()
        if algo == "FCFS": result, gantt = fcfs(processes)
        elif algo == "SJF (Non-Preemptive)": result, gantt = sjf_np(processes)
        elif algo == "SJF (Preemptive)": result, gantt = sjf_preemptive(processes)
        elif algo == "Priority (Non-Preemptive)": result, gantt = priority_np(processes)
        elif algo == "Priority (Preemptive)": result, gantt = priority_preemptive(processes)
        else: result, gantt = round_robin(processes, int(quantum_entry.get()))

        for row in result_table.get_children(): result_table.delete(row)
        
        avg_wt = avg_tat = 0
        for p in sorted(result, key=lambda x: x.pid):
            result_table.insert("", "end", values=(f"P{p.pid}", p.at, p.bt, p.pr, p.ct, p.tat, p.wt))
            avg_wt += p.wt
            avg_tat += p.tat
        
        avg_wt /= len(result)
        avg_tat /= len(result)
        avg_label.config(text=f"Average Waiting Time: {avg_wt:.2f} | Average Turnaround Time: {avg_tat:.2f}", fg="#1e3d59")

        draw_gantt(gantt)
        auto_compare()
    except Exception as e:
        tk.messagebox.showerror("Input Error", "Please ensure all fields are filled with integers.")

def auto_compare():
    algorithms = ["FCFS", "SJF (Non-Preemptive)", "SJF (Preemptive)", "Priority (Non-Preemptive)", "Priority (Preemptive)", "Round Robin"]
    results = []
    base_processes = []
    for i in range(num_procs.get()):
        base_processes.append(Process(i+1, int(arrival_entries[i].get()), int(burst_entries[i].get()), int(priority_entries[i].get())))
    
    for algo in algorithms:
        procs = copy.deepcopy(base_processes)
        if algo == "FCFS": res, _ = fcfs(procs)
        elif algo == "SJF (Non-Preemptive)": res, _ = sjf_np(procs)
        elif algo == "SJF (Preemptive)": res, _ = sjf_preemptive(procs)
        elif algo == "Priority (Non-Preemptive)": res, _ = priority_np(procs)
        elif algo == "Priority (Preemptive)": res, _ = priority_preemptive(procs)
        else: res, _ = round_robin(procs, int(quantum_entry.get()))
        
        results.append((algo, sum(p.wt for p in res)/len(res), sum(p.tat for p in res)/len(res)))

    min_wt = min(r[1] for r in results)
    for row in comparison_table.get_children(): comparison_table.delete(row)
    for algo, wt, tat in results:
        tag = "best" if wt == min_wt else ""
        comparison_table.insert("", "end", values=(algo, f"{wt:.2f}", f"{tat:.2f}"), tags=(tag,))

# ---------------- GUI LAYOUT ----------------

root = tk.Tk()
root.title("CPU Scheduling Simulator")
root.geometry("1100x850")
root.configure(bg="#f0f4f8")

# Style configuration for Blue Theme
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview.Heading", background="#2c3e50", foreground="white", font=("Arial", 10, "bold"))
style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff", rowheight=25)
style.map("Treeview", background=[("selected", "#3498db")])

# Header
tk.Label(root, text="CPU SCHEDULING ALGORITHM SIMULATOR", font=("Helvetica", 18, "bold"), fg="#2c3e50", bg="#f0f4f8").pack(pady=15)

main_container = tk.Frame(root, bg="#f0f4f8")
main_container.pack(fill="both", expand=True, padx=20)

# LEFT PANEL (Inputs)
left_panel = tk.Frame(main_container, bg="#eef2f7", bd=2, relief="groove", padx=15, pady=15)
left_panel.pack(side="left", fill="y", padx=5)

tk.Label(left_panel, text="Step 1: Algorithm Config", font=("Arial", 11, "bold"), bg="#eef2f7").pack(pady=5)
algo_var = tk.StringVar(value="FCFS")
ttk.Combobox(left_panel, textvariable=algo_var, values=["FCFS", "SJF (Non-Preemptive)", "SJF (Preemptive)", "Priority (Non-Preemptive)", "Priority (Preemptive)", "Round Robin"], state="readonly").pack(fill="x", pady=2)

tk.Label(left_panel, text="Quantum (for RR):", bg="#eef2f7").pack(anchor="w")
quantum_entry = tk.Entry(left_panel)
quantum_entry.insert(0, "2")
quantum_entry.pack(fill="x", pady=2)

tk.Label(left_panel, text="Number of Processes:", bg="#eef2f7").pack(anchor="w", pady=(10, 0))
num_procs = tk.IntVar(value=4)
tk.Entry(left_panel, textvariable=num_procs).pack(fill="x", pady=2)

tk.Button(left_panel, text="CREATE FIELDS", bg="#3498db", fg="white", font=("Arial", 9, "bold"), command=create_fields).pack(fill="x", pady=10)

# Field Tabular Column (Step 2)
tk.Label(left_panel, text="Step 2: Enter Details", font=("Arial", 11, "bold"), bg="#eef2f7").pack(pady=5)
input_table_frame = tk.Frame(left_panel, bg="#eef2f7")
input_table_frame.pack()

tk.Button(left_panel, text="RUN SIMULATION", bg="#27ae60", fg="white", font=("Arial", 10, "bold"), height=2, command=run_simulation).pack(fill="x", pady=20)

arrival_entries, burst_entries, priority_entries = [], [], []
create_fields()

# RIGHT PANEL (Calculations & Comparison)
right_panel = tk.Frame(main_container, bg="#f0f4f8")
right_panel.pack(side="right", fill="both", expand=True, padx=10)

# Calculation Table
tk.Label(right_panel, text="Calculation Table", font=("Arial", 12, "bold"), fg="#2c3e50", bg="#f0f4f8").pack(anchor="w")
columns = ("PID", "AT", "BT", "Priority", "CT", "TAT", "WT")
result_table = ttk.Treeview(right_panel, columns=columns, show="headings", height=8)
for col in columns:
    result_table.heading(col, text=col)
    result_table.column(col, width=80, anchor="center")
result_table.pack(fill="x", pady=5)

avg_label = tk.Label(right_panel, text="", font=("Arial", 10, "italic"), bg="#f0f4f8")
avg_label.pack(pady=2)

# Algorithm Comparison Table (Below Calculation)
tk.Label(right_panel, text="Algorithm Efficiency Comparison", font=("Arial", 12, "bold"), fg="#2c3e50", bg="#f0f4f8").pack(anchor="w", pady=(15, 0))
comp_cols = ("Algorithm", "Avg WT", "Avg TAT")
comparison_table = ttk.Treeview(right_panel, columns=comp_cols, show="headings", height=6)
for col in comp_cols:
    comparison_table.heading(col, text=col)
    comparison_table.column(col, width=150, anchor="center")
comparison_table.tag_configure("best", background="#d4edda") # Green for best
comparison_table.pack(fill="x", pady=5)

# BOTTOM PANEL (Gantt Chart - Center)
gantt_container = tk.Frame(root, bg="#f0f4f8")
gantt_container.pack(fill="x", side="bottom", pady=20)

tk.Label(gantt_container, text="Visual Timeline (Gantt Chart)", font=("Arial", 12, "bold"), bg="#f0f4f8", fg="#2c3e50").pack()
gantt_frame = tk.Frame(gantt_container, bg="white", bd=1, relief="sunken")
gantt_frame.pack(pady=5)

root.mainloop()
