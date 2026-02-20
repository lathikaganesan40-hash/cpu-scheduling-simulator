import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
import copy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Process:
    def __init__(self, pid, at, bt, pr=0):
        self.pid = pid
        self.at = at
        self.bt = bt
        self.pr = pr
        self.ct, self.tat, self.wt = 0, 0, 0

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

def create_fields():
    try:
        val = num_procs_entry.get()
        n = int(val)
        if n <= 0:
            messagebox.showerror("Input Error", "Number of processes must be greater than 0.")
            return
        if n > 30: # Soft cap for UI stability
            messagebox.showwarning("Warning", "Simulating many processes may require extensive scrolling.")
    except ValueError:
        messagebox.showerror("Input Error", f"Invalid input '{num_procs_entry.get()}'. Please enter a positive integer.")
        return

    for widget in input_table_frame.winfo_children(): widget.destroy()
    arrival_entries.clear(); burst_entries.clear(); priority_entries.clear()
    
    headers = ["PID", "Arrival", "Burst", "Priority"]
    for col, text in enumerate(headers):
        tk.Label(input_table_frame, text=text, bg="#eef2f7", font=("Arial", 9, "bold")).grid(row=0, column=col, padx=5)

    for i in range(n):
        tk.Label(input_table_frame, text=f"P{i+1}", bg="#eef2f7").grid(row=i+1, column=0)
        at, bt, pr = tk.Entry(input_table_frame, width=5), tk.Entry(input_table_frame, width=5), tk.Entry(input_table_frame, width=5)
        at.insert(0, "0"); bt.insert(0, "1"); pr.insert(0, "0")
        at.grid(row=i+1, column=1, pady=1); bt.grid(row=i+1, column=2, pady=1); pr.grid(row=i+1, column=3, pady=1)
        arrival_entries.append(at); burst_entries.append(bt); priority_entries.append(pr)

def draw_gantt(gantt):
    for widget in gantt_frame.winfo_children(): widget.destroy()
    total_time = gantt[-1][1] + gantt[-1][2]
    fig_width = max(8, total_time * 0.4)
    fig, ax = plt.subplots(figsize=(min(fig_width, 14), 2), dpi=100)
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
        # Validate Quantum for Round Robin
        q_val = 1
        if algo_var.get() == "Round Robin":
            q_val = int(quantum_entry.get())
            if q_val <= 0: raise ValueError("Quantum must be positive.")

        procs = []
        for i in range(len(arrival_entries)):
            at = int(arrival_entries[i].get())
            bt = int(burst_entries[i].get())
            pr = int(priority_entries[i].get())
            if at < 0 or bt <= 0 or pr < 0:
                raise ValueError("Arrival/Priority must be >= 0 and Burst must be > 0.")
            procs.append(Process(i+1, at, bt, pr))
        
        if not procs:
            messagebox.showwarning("Warning", "Please create fields and enter process details first.")
            return

        algo = algo_var.get()
        if algo == "FCFS": result, gantt = fcfs(procs)
        elif algo == "SJF (Non-Preemptive)": result, gantt = sjf_np(procs)
        elif algo == "SJF (Preemptive)": result, gantt = sjf_preemptive(procs)
        elif algo == "Priority (Non-Preemptive)": result, gantt = priority_np(procs)
        elif algo == "Priority (Preemptive)": result, gantt = priority_preemptive(procs)
        else: result, gantt = round_robin(procs, q_val)

        for row in result_table.get_children(): result_table.delete(row)
        avg_wt = avg_tat = 0
        for p in sorted(result, key=lambda x: x.pid):
            result_table.insert("", "end", values=(f"P{p.pid}", p.at, p.bt, p.pr, p.ct, p.tat, p.wt))
            avg_wt += p.wt; avg_tat += p.tat
        
        num = len(result)
        avg_label.config(text=f"Average WT: {avg_wt/num:.2f} | Average TAT: {avg_tat/num:.2f}", fg="#2c3e50")
        draw_gantt(gantt)
        auto_compare(q_val)
        
    except ValueError as e:
        messagebox.showerror("Input Error", f"Invalid input detected: {e}\nPlease ensure all fields contain valid non-negative integers.")

def auto_compare(q):
    algorithms = ["FCFS", "SJF (Non-Preemptive)", "SJF (Preemptive)", "Priority (Non-Preemptive)", "Priority (Preemptive)", "Round Robin"]
    results = []
    base_procs = [Process(i+1, int(arrival_entries[i].get()), int(burst_entries[i].get()), int(priority_entries[i].get())) for i in range(len(arrival_entries))]
    
    for algo in algorithms:
        p_copy = copy.deepcopy(base_procs)
        if algo == "FCFS": res, _ = fcfs(p_copy)
        elif algo == "SJF (Non-Preemptive)": res, _ = sjf_np(p_copy)
        elif algo == "SJF (Preemptive)": res, _ = sjf_preemptive(p_copy)
        elif algo == "Priority (Non-Preemptive)": res, _ = priority_np(p_copy)
        elif algo == "Priority (Preemptive)": res, _ = priority_preemptive(p_copy)
        else: res, _ = round_robin(p_copy, q)
        results.append((algo, sum(p.wt for p in res)/len(res), sum(p.tat for p in res)/len(res)))

    min_wt = min(r[1] for r in results)
    for row in comparison_table.get_children(): comparison_table.delete(row)
    for algo, wt, tat in results:
        tag = "best" if wt == min_wt else ""
        comparison_table.insert("", "end", values=(algo, f"{wt:.2f}", f"{tat:.2f}"), tags=(tag,))


root = tk.Tk()
root.title("CPU Scheduling Simulator")
root.geometry("1200x900")

main_canvas = tk.Canvas(root, bg="#f0f4f8")
scrollbar = ttk.Scrollbar(root, orient="vertical", command=main_canvas.yview)
scroll_content = tk.Frame(main_canvas, bg="#f0f4f8")

scroll_content.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
main_canvas.create_window((0, 0), window=scroll_content, anchor="nw", width=1180)
main_canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
main_canvas.pack(side="left", fill="both", expand=True)

style = ttk.Style(); style.theme_use("clam")
style.configure("Treeview.Heading", background="#2c3e50", foreground="white", font=("Arial", 10, "bold"))
style.map("Treeview", background=[("selected", "#3498db")])

tk.Label(scroll_content, text="CPU SCHEDULING ALGORITHM SIMULATOR", font=("Helvetica", 18, "bold"), fg="#2c3e50", bg="#f0f4f8").pack(pady=15)

top_row = tk.Frame(scroll_content, bg="#f0f4f8")
top_row.pack(fill="both", expand=True, padx=20)


left_panel = tk.Frame(top_row, bg="#eef2f7", bd=2, relief="groove", padx=15, pady=15)
left_panel.pack(side="left", fill="y", padx=5)

tk.Label(left_panel, text="Configuration", font=("Arial", 11, "bold"), bg="#eef2f7").pack(pady=5)
algo_var = tk.StringVar(value="FCFS")
ttk.Combobox(left_panel, textvariable=algo_var, values=["FCFS", "SJF (Non-Preemptive)", "SJF (Preemptive)", "Priority (Non-Preemptive)", "Priority (Preemptive)", "Round Robin"], state="readonly").pack(fill="x")

tk.Label(left_panel, text="Quantum (RR):", bg="#eef2f7").pack(anchor="w")
quantum_entry = tk.Entry(left_panel); quantum_entry.insert(0, "2"); quantum_entry.pack(fill="x")

tk.Label(left_panel, text="No. of Processes:", bg="#eef2f7").pack(anchor="w", pady=(10, 0))
num_procs_entry = tk.Entry(left_panel)
num_procs_entry.insert(0, "3")
num_procs_entry.pack(fill="x")

tk.Button(left_panel, text="CREATE FIELDS", bg="#3498db", fg="white", font=("Arial", 9, "bold"), command=create_fields).pack(fill="x", pady=10)

input_canvas = tk.Canvas(left_panel, height=300, bg="#eef2f7", highlightthickness=0)
input_scroll = ttk.Scrollbar(left_panel, orient="vertical", command=input_canvas.yview)
input_table_frame = tk.Frame(input_canvas, bg="#eef2f7")
input_table_frame.bind("<Configure>", lambda e: input_canvas.configure(scrollregion=input_canvas.bbox("all")))
input_canvas.create_window((0, 0), window=input_table_frame, anchor="nw")
input_canvas.configure(yscrollcommand=input_scroll.set)

input_canvas.pack(side="left", fill="both", expand=True)
input_scroll.pack(side="right", fill="y")

tk.Button(left_panel, text="RUN SIMULATION", bg="#27ae60", fg="white", font=("Arial", 10, "bold"), height=2, command=run_simulation).pack(fill="x", side="bottom", pady=10)


right_panel = tk.Frame(top_row, bg="#f0f4f8")
right_panel.pack(side="right", fill="both", expand=True, padx=10)

tk.Label(right_panel, text="Calculation Table", font=("Arial", 12, "bold"), bg="#f0f4f8").pack(anchor="w")
cols = ("PID", "AT", "BT", "Priority", "CT", "TAT", "WT")
result_table = ttk.Treeview(right_panel, columns=cols, show="headings", height=12)
for col in cols:
    result_table.heading(col, text=col)
    result_table.column(col, width=70, anchor="center")
result_table.pack(fill="x")

avg_label = tk.Label(right_panel, text="", font=("Arial", 10, "bold"), bg="#f0f4f8")
avg_label.pack(pady=5)

tk.Label(right_panel, text="Algorithm Comparison", font=("Arial", 12, "bold"), bg="#f0f4f8").pack(anchor="w", pady=(15, 0))
comp_cols = ("Algorithm", "Avg WT", "Avg TAT")
comparison_table = ttk.Treeview(right_panel, columns=comp_cols, show="headings", height=6)
for col in comp_cols:
    comparison_table.heading(col, text=col)
    comparison_table.column(col, width=150, anchor="center")
comparison_table.tag_configure("best", background="#d4edda")
comparison_table.pack(fill="x")

gantt_container = tk.Frame(scroll_content, bg="#f0f4f8")
gantt_container.pack(fill="x", pady=20)
tk.Label(gantt_container, text="Visual Timeline (Gantt Chart)", font=("Arial", 12, "bold"), bg="#f0f4f8").pack()
gantt_frame = tk.Frame(gantt_container, bg="white", bd=1, relief="sunken")
gantt_frame.pack(pady=5, padx=20)

arrival_entries, burst_entries, priority_entries = [], [], []
create_fields()
root.mainloop()
