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

def sjf_np(processes):
    time = 0
    completed = []
    gantt = []
    while processes:
        ready = [p for p in processes if p.at <= time]
        if not ready:
            time +=1
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

def sjf_p(processes):
    time = 0
    gantt = []
    completed = []
    remaining = {p.pid: p.bt for p in processes}
    while len(completed) < len(processes):
        ready = [p for p in processes if p.at <= time and remaining[p.pid] > 0]
        if not ready:
            time +=1
            continue
        ready.sort(key=lambda x: remaining[x.pid])
        p = ready[0]
        gantt.append((p.pid, time, 1))
        remaining[p.pid] -= 1
        time +=1
        if remaining[p.pid]==0:
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
            time +=1
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

def priority_p(processes):
    time = 0
    gantt = []
    completed = []
    remaining = {p.pid: p.bt for p in processes}
    while len(completed) < len(processes):
        ready = [p for p in processes if p.at <= time and remaining[p.pid]>0]
        if not ready:
            time +=1
            continue
        ready.sort(key=lambda x: x.pr)
        p = ready[0]
        gantt.append((p.pid, time,1))
        remaining[p.pid] -=1
        time +=1
        if remaining[p.pid]==0:
            p.ct = time
            p.tat = p.ct - p.at
            p.wt = p.tat - p.bt
            completed.append(p)
    return completed, gantt

def round_robin(processes, q):
    time = 0
    queue = deque()
    gantt = []
    remaining = {p.pid: p.bt for p in processes}
    processes.sort(key=lambda x:x.at)
    i = 0
    completed = []
    while queue or i < len(processes):
        while i < len(processes) and processes[i].at <= time:
            queue.append(processes[i])
            i+=1
        if not queue:
            time+=1
            continue
        p = queue.popleft()
        exec_time = min(q, remaining[p.pid])
        gantt.append((p.pid, time, exec_time))
        time += exec_time
        remaining[p.pid]-=exec_time
        while i < len(processes) and processes[i].at <= time:
            queue.append(processes[i])
            i+=1
        if remaining[p.pid]>0:
            queue.append(p)
        else:
            p.ct=time
            p.tat=p.ct-p.at
            p.wt=p.tat-p.bt
            completed.append(p)
    return completed, gantt

# ---------------- Gantt Chart ----------------
def draw_gantt(gantt):
    for widget in gantt_frame.winfo_children():
        widget.destroy()
    fig, ax = plt.subplots(figsize=(8,2))
    for pid, start, duration in gantt:
        ax.barh(0, duration, left=start)
        ax.text(start + duration/2, 0, f"P{pid}", ha='center', va='center', color='white')
    ax.set_title("Gantt Chart")
    ax.set_xlabel("Time")
    ax.set_yticks([])
    ax.set_ylim(-1,1)
    canvas = FigureCanvasTkAgg(fig, gantt_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

# ---------------- Run Simulation ----------------
def run_simulation():
    processes = []
    for i in range(num_procs.get()):
        pr = int(priority_entries[i].get()) if priority_var.get() else 0
        processes.append(Process(i+1, int(arrival_entries[i].get()), int(burst_entries[i].get()), pr))
    
    algo = algo_var.get()
    q = int(quantum_entry.get())
    
    if algo=="FCFS":
        result, gantt = fcfs(copy.deepcopy(processes))
    elif algo=="SJF NP":
        result, gantt = sjf_np(copy.deepcopy(processes))
    elif algo=="SJF P":
        result, gantt = sjf_p(copy.deepcopy(processes))
    elif algo=="Priority NP":
        result, gantt = priority_np(copy.deepcopy(processes))
    elif algo=="Priority P":
        result, gantt = priority_p(copy.deepcopy(processes))
    elif algo=="RR":
        result, gantt = round_robin(copy.deepcopy(processes), q)
    
    for row in table.get_children():
        table.delete(row)
    
    total_wt=total_tat=0
    for idx,p in enumerate(result):
        tag = "evenrow" if idx%2==0 else "oddrow"
        table.insert("", "end", values=(p.pid, p.at, p.bt, p.pr, p.ct, p.tat, p.wt), tags=(tag,))
        total_wt += p.wt
        total_tat += p.tat
    
    table.tag_configure("evenrow", background="#e3f2fd")
    table.tag_configure("oddrow", background="#ffffff")
    
    avg_wt = total_wt/len(result)
    avg_tat = total_tat/len(result)
    
    total_bt = sum(p.bt for p in result)
    total_time = max(p.ct for p in result)
    cpu_util = (total_bt/total_time)*100
    throughput = len(result)/total_time
    
    avg_label.config(text=f"Avg WT: {avg_wt:.2f}   Avg TAT: {avg_tat:.2f}   CPU: {cpu_util:.2f}%   Throughput: {throughput:.2f}")
    
    draw_gantt(gantt)
    auto_compare(processes)

# ---------------- Auto Comparison ----------------
def auto_compare(base_processes):
    algos = ["FCFS", "SJF NP", "SJF P", "Priority NP", "Priority P", "RR"]
    comp_table.delete(*comp_table.get_children())
    results=[]
    for algo in algos:
        processes = copy.deepcopy(base_processes)
        q = int(quantum_entry.get())
        if algo=="FCFS":
            res,_=fcfs(processes)
        elif algo=="SJF NP":
            res,_=sjf_np(processes)
        elif algo=="SJF P":
            res,_=sjf_p(processes)
        elif algo=="Priority NP":
            res,_=priority_np(processes)
        elif algo=="Priority P":
            res,_=priority_p(processes)
        else:
            res,_=round_robin(processes,q)
        avg_wt = sum(p.wt for p in res)/len(res)
        avg_tat = sum(p.tat for p in res)/len(res)
        results.append((algo, avg_wt, avg_tat))
    min_wt = min(results, key=lambda x:x[1])[1]
    for r in results:
        tag="best" if r[1]==min_wt else ""
        comp_table.insert("", "end", values=(r[0], f"{r[1]:.2f}", f"{r[2]:.2f}"), tags=(tag,))
    comp_table.tag_configure("best", background="#c8f7c5")

# ---------------- Create Fields ----------------
def create_fields():
    for w in input_frame.winfo_children():
        w.destroy()
    arrival_entries.clear()
    burst_entries.clear()
    priority_entries.clear()
    
    tk.Label(input_frame, text="PID").grid(row=0, column=0)
    tk.Label(input_frame, text="Arrival").grid(row=0, column=1)
    tk.Label(input_frame, text="Burst").grid(row=0, column=2)
    tk.Label(input_frame, text="Priority").grid(row=0, column=3)
    
    for i in range(num_procs.get()):
        tk.Label(input_frame, text=f"P{i+1}").grid(row=i+1, column=0)
        at = tk.Entry(input_frame, width=6)
        bt = tk.Entry(input_frame, width=6)
        pr = tk.Entry(input_frame, width=6)
        at.grid(row=i+1, column=1)
        bt.grid(row=i+1, column=2)
        pr.grid(row=i+1, column=3)
        arrival_entries.append(at)
        burst_entries.append(bt)
        priority_entries.append(pr)

# ---------------- GUI ----------------
root = tk.Tk()
root.title("CPU Scheduling Simulator - Mini Project")
root.geometry("1200x750")

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview.Heading", background="#1e3d59", foreground="white", font=("Arial",11,"bold"))
style.configure("Treeview", rowheight=28, background="#f5f7fa", fieldbackground="#f5f7fa")
style.map("Treeview", background=[("selected","#ff9800")], foreground=[("selected","white")])

tk.Label(root, text="CPU Scheduling Algorithm Simulator", font=("Arial",20,"bold"), fg="#1e3d59").pack(pady=15)

main_frame=tk.Frame(root)
main_frame.pack(fill="both", expand=True)

# Left Panel
left_panel=tk.Frame(main_frame)
left_panel.pack(side="left", fill="y", padx=15)

num_procs=tk.IntVar(value=4)
algo_var=tk.StringVar(value="FCFS")
priority_var=tk.BooleanVar(value=True)

tk.Label(left_panel, text="Number of Processes").pack(pady=5)
tk.Entry(left_panel, textvariable=num_procs, width=8).pack()
tk.Button(left_panel, text="Create Fields", width=20, height=2, command=create_fields).pack(pady=10)
tk.Label(left_panel, text="Algorithm").pack(pady=5)
ttk.Combobox(left_panel, textvariable=algo_var, values=["FCFS","SJF NP","SJF P","Priority NP","Priority P","RR"], state="readonly", width=18).pack()
tk.Label(left_panel, text="Quantum (RR)").pack(pady=5)
quantum_entry=tk.Entry(left_panel, width=8)
quantum_entry.insert(0,"2")
quantum_entry.pack()
tk.Button(left_panel, text="Run Simulation", width=20, height=2, bg="#4caf50", fg="white", command=run_simulation).pack(pady=15)

input_frame=tk.Frame(left_panel)
input_frame.pack(pady=10)
arrival_entries=[]
burst_entries=[]
priority_entries=[]
create_fields()

# Right Panel
right_panel=tk.Frame(main_frame)
right_panel.pack(side="right", fill="both", expand=True)

columns=("PID","AT","BT","Priority","CT","TAT","WT")
table_frame=tk.Frame(right_panel)
table_frame.pack(pady=10)
scroll_y=tk.Scrollbar(table_frame)
scroll_y.pack(side="right", fill="y")
table=ttk.Treeview(table_frame, columns=columns, show="headings", yscrollcommand=scroll_y.set, height=10)
scroll_y.config(command=table.yview)
for col in columns:
    table.heading(col, text=col)
    table.column(col, width=90)
table.pack()

avg_label=tk.Label(right_panel,font=("Arial",12,"bold"), fg="#1e3d59")
avg_label.pack(pady=5)

# Comparison Table
comp_columns=("Algorithm","Avg WT","Avg TAT")
comp_table=tk.Treeview(right_panel, columns=comp_columns, show="headings", height=6)
for col in comp_columns:
    comp_table.heading(col, text=col)
    comp_table.column(col,width=120)
comp_table.tag_configure("best", background="#c8f7c5")
comp_table.pack(pady=10)

# Gantt Frame
gantt_frame=tk.Frame(root)
gantt_frame.pack(pady=20)

root.mainloop()
