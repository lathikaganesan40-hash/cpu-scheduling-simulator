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
        self.ct, self.tat, self.wt = 0, 0, 0

# ---------------- Algorithms (Optimized for Large Data) ----------------
def fcfs(processes):
    time, gantt = 0, []
    processes.sort(key=lambda x: x.at)
    for p in processes:
        if time < p.at: time = p.at
        gantt.append((p.pid, time, p.bt))
        time += p.bt
        p.ct, p.tat = time, time - p.at
        p.wt = p.tat - p.bt
    return processes, gantt

def sjf_np(processes):
    time, completed, gantt = 0, [], []
    while processes:
        ready = [p for p in processes if p.at <= time]
        if not ready:
            time = min(p.at for p in processes)
            continue
        ready.sort(key=lambda x: x.bt)
        p = ready[0]
        processes.remove(p)
        gantt.append((p.pid, time, p.bt))
        time += p.bt
        p.ct, p.tat = time, time - p.at
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
            p.ct, p.tat = time, time - p.at
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
        p.ct, p.tat = time, time - p.at
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
            p.ct, p.tat = time, time - p.at
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
            time = processes[i].at
            continue
        p = queue.popleft()
        exec_time = min(q, remaining[p.pid])
        gantt.append((p.pid, time, exec_time))
        time += exec_time
        remaining[p.pid] -= exec_time
        while i < len(processes) and processes[i].at <= time:
            queue.append(processes[i])
            i += 1
        if remaining[p.pid] > 0: queue.append(p)
        else:
            p.ct, p.tat = time, time - p.at
            p.wt = p.tat - p.bt
            completed.append(p)
    return completed, gantt

# ---------------- GUI FUNCTIONS ----------------

def create_fields():
    for widget in input_table_frame.winfo_children(): widget.destroy()
    arrival_entries.clear(); burst_entries.clear(); priority_entries.clear()
    
    headers = ["PID", "Arrival", "Burst", "Priority"]
    for col, text in enumerate(headers):
        tk.Label(input_table_frame, text=text, bg="#eef2f7", font=("Arial", 9, "bold")).grid(row=0, column=col, padx=5)

    for i in range(num_procs.get()):
        tk.Label(input_table_frame, text=f"P{i+1}", bg="#eef2f7").grid(row=i+1, column=0)
        at, bt, pr = tk.Entry(input_table_frame, width=5), tk.Entry(input_table_frame, width=5), tk.Entry(input_table_frame, width=5)
        at.insert(0, "0"); bt.insert(0, "1"); pr.insert(0, "0")
        at.grid(row=i+1, column=1, pady=1); bt.grid(row=i+1, column=2, pady=1); pr.grid(row=i+1, column=3, pady=1)
        arrival_entries.append(at); burst_entries.append(bt); priority_entries.append(pr)

def draw_gantt(gantt):
    for widget in gantt_frame.winfo_children(): widget.destroy()
    # Dynamic width based on time, capped for readability
    total_time = gantt[-1][1] + gantt[-1][2]
    fig_width = max(8, total_time * 0.5)
    fig, ax = plt.subplots(figsize=(min(fig_width, 15), 2), dpi=100)
    colors = plt.cm.get_cmap('Set3', 10)
    
    gantt = [g for g in gantt if g[2] > 0]
    for pid, start, duration in gantt:
        ax.barh(0, duration, left=start, color=colors(pid % 10), edgecolor='black')
        ax.text(start + duration/2, 0, f"P{pid}", ha='center', va='center', fontweight='bold', fontsize=8)
    
    ax.set_yticks([]); ax.set_xlabel("Time Units")
    fig.tight_layout()
    canvas = FigureCanvasTkAgg(fig, gantt_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)

def run_simulation():
    try:
        procs = []
        for i in range(num_procs.get()):
            procs.append(Process(i+1, int(arrival_entries[i].get()), int(burst_entries[i].get()), int(priority_entries[i].get())))
        
        algo = algo_var.get()
        if algo == "FCFS": result, gantt = fcfs(procs)
        elif algo == "SJF (Non-Preemptive)": result, gantt = sjf_np(procs)
        elif algo == "SJF (Preemptive)": result, gantt = sjf_preemptive(procs)
        elif algo == "Priority (Non-Preemptive)": result, gantt = priority_np(procs)
        elif algo == "Priority (Preemptive)": result, gantt = priority_preemptive(procs)
        else: result, gantt = round_robin(procs, int(quantum_entry.get()))

        for row in result_table.get_children(): result_table.delete(row)
        avg_wt = avg_tat = 0
        for p in sorted(result, key=lambda x: x.pid):
            result_table.insert("", "end", values=(f"P{p.pid}", p.at, p.bt, p.pr, p.ct, p.tat, p.wt))
            avg_wt += p.wt; avg_tat += p.tat
        
        avg_label.config(text=f"Average WT: {avg_wt/len(result):.2f} | Average TAT: {avg_tat/len(result):.2f}", fg="#2c3e50")
        draw_gantt(gantt)
        auto_compare()
        
    except Exception as e:
        messagebox.showerror("Input Error", "Please ensure all fields are valid integers.")

def auto_compare():
    algorithms = ["FCFS", "SJF (Non-Preemptive)", "SJF (Preemptive)", "Priority (Non-Preemptive)", "Priority (Preemptive)", "Round Robin"]
    results = []
    base_procs = [Process(i+1, int(arrival_entries[i].get()), int(burst_entries[i].get()), int(priority_entries[i].get())) for i in range(num_procs.get())]
    
    for algo in algorithms:
        p_copy = copy.deepcopy(base_procs)
        if algo == "FCFS": res, _ = fcfs(p_copy)
        elif algo == "SJF (Non-Preemptive)": res, _ = sjf_np(p_copy)
        elif algo == "SJF (Preemptive)": res, _ = sjf_preemptive(p_copy)
        elif algo == "Priority (Non-Preemptive)": res, _ = priority_np(p_copy)
        elif algo == "Priority (Preemptive)": res, _ = priority_preemptive(p_copy)
        else: res, _ = round_robin(p_copy, int(quantum_entry.get()))
        results.append((algo, sum(p.wt for p in res)/len(res), sum(p.tat for p in res)/len(res)))

    min_wt = min(r[1] for r in results)
    for row in comparison_table.get_children(): comparison_table.delete(row)
    for algo, wt, tat in results:
        tag = "best" if wt == min_wt else ""
        comparison_table.insert("", "end", values=(algo, f"{wt:.2f}", f"{tat:.2f}"), tags=(tag,))

# ---------------- GUI LAYOUT ----------------

root = tk.Tk()
root.title("CPU Scheduling Simulator")
root.geometry("1200x900")

# Scrollable Setup
main_canvas = tk.Canvas(root, bg="#f0f4f8")
scrollbar = ttk.Scrollbar(root, orient="vertical", command=main_canvas.yview)
scroll_content = tk.Frame(main_canvas, bg="#f0f4f8")

scroll_content.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
main_canvas.create_window((0, 0), window=scroll_content, anchor="nw", width=1180)
main_canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
main_canvas.pack(side="left", fill="both", expand=True)

# Styles
style = ttk.Style(); style.theme_use("clam")
style.configure("Treeview.Heading", background="#2c3e50", foreground="white", font=("Arial", 10, "bold"))
style.configure("Treeview", rowheight=25)
style.map("Treeview", background=[("selected", "#3498db")])

tk.Label(scroll_content, text="CPU SCHEDULING ALGORITHM SIMULATOR", font=("Helvetica", 18, "bold"), fg="#2c3e50", bg="#f0f4f8").pack(pady=15)

top_row = tk.Frame(scroll_content, bg="#f0f4f8")
top_row.pack(fill="both", expand=True, padx=20)

# Input Section (Fixed Left)
left_panel = tk.Frame(top_row, bg="#eef2f7", bd=2, relief="groove", padx=15, pady=15)
left_panel.pack(side="left", fill="y", padx=5)

tk.Label(left_panel, text="Configuration", font=("Arial", 11, "bold"), bg="#eef2f7").pack(pady=5)
algo_var = tk.StringVar(value="FCFS")
ttk.Combobox(left_panel, textvariable=algo_var, values=["FCFS", "SJF (Non-Preemptive)", "SJF (Preemptive)", "Priority (Non-Preemptive)", "Priority (Preemptive)", "Round Robin"], state="readonly").pack(fill="x")

tk.Label(left_panel, text="Quantum (RR):", bg="#eef2f7").pack(anchor="w")
quantum_entry = tk.Entry(left_panel); quantum_entry.insert(0, "2"); quantum_entry.pack(fill="x")

tk.Label(left_panel, text="No. of Processes:", bg="#eef2f7").pack(anchor="w", pady=(10, 0))
num_procs = tk.IntVar(value=3)
tk.Entry(left_panel, textvariable=num_procs).pack(fill="x")

tk.Button(left_panel, text="CREATE FIELDS", bg="#3498db", fg="white", command=create_fields).pack(fill="x", pady=10)

# Scrollable Input Grid
input_canvas = tk.Canvas(left_panel, height=300, bg="#eef2f7", highlightthickness=0)
input_scroll = ttk.Scrollbar(left_panel, orient="vertical", command=input_canvas.yview)
input_table_frame = tk.Frame(input_canvas, bg="#eef2f7")
input_table_frame.bind("<Configure>", lambda e: input_canvas.configure(scrollregion=input_canvas.bbox("all")))
input_canvas.create_window((0, 0), window=input_table_frame, anchor="nw")
input_canvas.configure(yscrollcommand=input_scroll.set)

input_canvas.pack(side="left", fill="both", expand=True)
input_scroll.pack(side="right", fill="y")

tk.Button(left_panel, text="RUN SIMULATION", bg="#27ae60", fg="white", font=("Arial", 10, "bold"), height=2, command=run_simulation).pack(fill="x", side="bottom", pady=10)

# Right Results Section
right_panel = tk.Frame(top_row, bg="#f0f4f8")
right_panel.pack(side="right", fill="both", expand=True, padx=10)

# Calculation Table (Increased height for more processes)
tk.Label(right_panel, text="Calculation Table", font=("Arial", 12, "bold"), bg="#f0f4f8").pack(anchor="w")
cols = ("PID", "AT", "BT", "Priority", "CT", "TAT", "WT")
result_table = ttk.Treeview(right_panel, columns=cols, show="headings", height=12)
for col in cols:
    result_table.heading(col, text=col)
    result_table.column(col, width=70, anchor="center")
result_table.pack(fill="x")

avg_label = tk.Label(right_panel, text="", font=("Arial", 10, "bold"), bg="#f0f4f8")
avg_label.pack(pady=5)

# Comparison Table
tk.Label(right_panel, text="Algorithm Comparison", font=("Arial", 12, "bold"), bg="#f0f4f8").pack(anchor="w", pady=(15, 0))
comp_cols = ("Algorithm", "Avg WT", "Avg TAT")
comparison_table = ttk.Treeview(right_panel, columns=comp_cols, show="headings", height=6)
for col in comp_cols:
    comparison_table.heading(col, text=col)
    comparison_table.column(col, width=150, anchor="center")
comparison_table.tag_configure("best", background="#d4edda")
comparison_table.pack(fill="x")

# Bottom Gantt Section
gantt_container = tk.Frame(scroll_content, bg="#f0f4f8")
gantt_container.pack(fill="x", pady=20)
tk.Label(gantt_container, text="Visual Timeline (Gantt Chart)", font=("Arial", 12, "bold"), bg="#f0f4f8").pack()
gantt_frame = tk.Frame(gantt_container, bg="white", bd=1, relief="sunken")
gantt_frame.pack(pady=5, padx=20)

arrival_entries, burst_entries, priority_entries = [], [], []
create_fields()
root.mainloop()
