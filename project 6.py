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

# ---------------- Algorithms ----------------

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

def sjf_preemptive(processes):
    time = 0
    completed = []
    gantt = []
    remaining = {p.pid: p.bt for p in processes}
    while len(completed) < len(processes):
        ready = [p for p in processes if p.at <= time and remaining[p.pid] > 0]
        if not ready:
            time +=1
            continue
        ready.sort(key=lambda x: remaining[x.pid])
        p = ready[0]
        gantt.append((p.pid, time, 1))
        remaining[p.pid] -=1
        time +=1
        if remaining[p.pid]==0:
            p.ct=time
            p.tat=p.ct - p.at
            p.wt=p.tat - p.bt
            completed.append(p)
    return completed, gantt

def priority_np(processes):
    time = 0
    completed=[]
    gantt=[]
    while processes:
        ready=[p for p in processes if p.at<=time]
        if not ready:
            time+=1
            continue
        ready.sort(key=lambda x:x.pr)
        p=ready[0]
        processes.remove(p)
        gantt.append((p.pid,time,p.bt))
        time+=p.bt
        p.ct=time
        p.tat=p.ct-p.at
        p.wt=p.tat-p.bt
        completed.append(p)
    return completed,gantt

def priority_preemptive(processes):
    time=0
    completed=[]
    gantt=[]
    remaining={p.pid:p.bt for p in processes}
    while len(completed)<len(processes):
        ready=[p for p in processes if p.at<=time and remaining[p.pid]>0]
        if not ready:
            time+=1
            continue
        ready.sort(key=lambda x:x.pr)
        p=ready[0]
        gantt.append((p.pid,time,1))
        remaining[p.pid]-=1
        time+=1
        if remaining[p.pid]==0:
            p.ct=time
            p.tat=p.ct-p.at
            p.wt=p.tat-p.bt
            completed.append(p)
    return completed,gantt

def round_robin(processes,q):
    time=0
    queue=deque()
    gantt=[]
    remaining={p.pid:p.bt for p in processes}
    processes.sort(key=lambda x:x.at)
    i=0
    completed=[]
    while queue or i<len(processes):
        while i<len(processes) and processes[i].at<=time:
            queue.append(processes[i])
            i+=1
        if not queue:
            time+=1
            continue
        p=queue.popleft()
        exec_time=min(q,remaining[p.pid])
        gantt.append((p.pid,time,exec_time))
        time+=exec_time
        remaining[p.pid]-=exec_time
        while i<len(processes) and processes[i].at<=time:
            queue.append(processes[i])
            i+=1
        if remaining[p.pid]>0:
            queue.append(p)
        else:
            p.ct=time
            p.tat=p.ct-p.at
            p.wt=p.tat-p.bt
            completed.append(p)
    return completed,gantt

# ---------------- GUI FUNCTIONS ----------------

def create_fields():
    for widget in input_frame.winfo_children():
        widget.destroy()
    arrival_entries.clear()
    burst_entries.clear()
    priority_entries.clear()

    headers=["PID","Arrival","Burst","Priority"]
    for col,text in enumerate(headers):
        tk.Label(input_frame,text=text,bg="#eef2f7",font=("Arial",10,"bold")).grid(row=0,column=col)

    for i in range(num_procs.get()):
        tk.Label(input_frame,text=f"P{i+1}",bg="#eef2f7").grid(row=i+1,column=0)
        at=tk.Entry(input_frame,width=6)
        bt=tk.Entry(input_frame,width=6)
        pr=tk.Entry(input_frame,width=6)
        at.grid(row=i+1,column=1)
        bt.grid(row=i+1,column=2)
        pr.grid(row=i+1,column=3)
        arrival_entries.append(at)
        burst_entries.append(bt)
        priority_entries.append(pr)

def draw_gantt(gantt):
    for widget in gantt_frame.winfo_children():
        widget.destroy()
    fig,ax=plt.subplots(figsize=(7,2))
    for pid,start,duration in gantt:
        ax.barh(0,duration,left=start)
        ax.text(start+duration/2,0,f"P{pid}",ha='center',va='center',color='white')
    ax.set_yticks([])
    ax.set_xlabel("Time")
    ax.set_title("Gantt Chart")
    canvas=FigureCanvasTkAgg(fig,gantt_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

def run_simulation():
    processes=[]
    for i in range(num_procs.get()):
        processes.append(Process(i+1,
                                 int(arrival_entries[i].get()),
                                 int(burst_entries[i].get()),
                                 int(priority_entries[i].get())))
    algo=algo_var.get()
    if algo=="FCFS":
        result,gantt=fcfs(processes)
    elif algo=="SJF (Non-Preemptive)":
        result,gantt=sjf_np(processes)
    elif algo=="SJF (Preemptive)":
        result,gantt=sjf_preemptive(processes)
    elif algo=="Priority (Non-Preemptive)":
        result,gantt=priority_np(processes)
    elif algo=="Priority (Preemptive)":
        result,gantt=priority_preemptive(processes)
    else:
        result,gantt=round_robin(processes,int(quantum_entry.get()))

    # Clear result table
    for row in result_table.get_children():
        result_table.delete(row)
    avg_wt=avg_tat=0
    for p in result:
        result_table.insert("", "end", values=(f"P{p.pid}",p.at,p.bt,p.pr,p.ct,p.tat,p.wt))
        avg_wt+=p.wt
        avg_tat+=p.tat
    avg_wt/=len(result)
    avg_tat/=len(result)
    avg_label.config(text=f"Avg WT: {avg_wt:.2f}   Avg TAT: {avg_tat:.2f}")

    draw_gantt(gantt)
    auto_compare()

def auto_compare():
    algorithms = ["FCFS",
                  "SJF (Non-Preemptive)",
                  "SJF (Preemptive)",
                  "Priority (Non-Preemptive)",
                  "Priority (Preemptive)",
                  "Round Robin"]
    results=[]
    base_processes=[]
    for i in range(num_procs.get()):
        base_processes.append(Process(i+1,int(arrival_entries[i].get()),int(burst_entries[i].get()),int(priority_entries[i].get())))
    for algo in algorithms:
        processes=copy.deepcopy(base_processes)
        if algo=="FCFS":
            result,_=fcfs(processes)
        elif algo=="SJF (Non-Preemptive)":
            result,_=sjf_np(processes)
        elif algo=="SJF (Preemptive)":
            result,_=sjf_preemptive(processes)
        elif algo=="Priority (Non-Preemptive)":
            result,_=priority_np(processes)
        elif algo=="Priority (Preemptive)":
            result,_=priority_preemptive(processes)
        else:
            result,_=round_robin(processes,int(quantum_entry.get()))
        avg_wt=sum(p.wt for p in result)/len(result)
        avg_tat=sum(p.tat for p in result)/len(result)
        results.append((algo,avg_wt,avg_tat))
    min_wt=min(r[1] for r in results)
    for row in comparison_table.get_children():
        comparison_table.delete(row)
    comparison_table.config(height=len(results))
    for algo,wt,tat in results:
        if wt==min_wt:
            comparison_table.insert("", "end", values=(algo,f"{wt:.2f}",f"{tat:.2f}"),tags=("best",))
        else:
            comparison_table.insert("", "end", values=(algo,f"{wt:.2f}",f"{tat:.2f}"))

# ---------------- GUI LAYOUT ----------------

root=tk.Tk()
root.title("CPU Scheduling Simulator - Mini Project")
root.geometry("1200x750")
root.configure(bg="#e8eef5")

style=ttk.Style()
style.theme_use("clam")
style.configure("Treeview",rowheight=28,
                background="#f5f7fa",
                fieldbackground="#f5f7fa")
style.map("Treeview",
          background=[("selected","#ff9800")],
          foreground=[("selected","white")])

# Heading
tk.Label(root,text="CPU Scheduling Algorithm Simulator",
         font=("Arial",20,"bold"),
         fg="#1e3d59",
         bg="#e8eef5").pack(pady=10)

main_frame=tk.Frame(root,bg="#e8eef5")
main_frame.pack(fill="both",expand=True)

# LEFT PANEL
left_panel=tk.Frame(main_frame,bg="#eef2f7",padx=10,pady=10)
left_panel.pack(side="left",fill="y")

tk.Label(left_panel,text="Process Setup",bg="#eef2f7",font=("Arial",14,"bold")).pack(pady=5)
num_procs=tk.IntVar(value=4)
algo_var=tk.StringVar(value="FCFS")
tk.Label(left_panel,text="Processes",bg="#eef2f7").pack()
tk.Entry(left_panel,textvariable=num_procs,width=6).pack()
tk.Button(left_panel,text="Create Fields",bg="#4a90e2",fg="white",font=("Arial",10,"bold"),
          command=create_fields).pack(pady=5)
tk.Label(left_panel,text="Algorithm",bg="#eef2f7").pack(pady=3)
ttk.Combobox(left_panel,textvariable=algo_var,
             values=["FCFS","SJF (Non-Preemptive)","SJF (Preemptive)","Priority (Non-Preemptive)","Priority (Preemptive)","Round Robin"],
             state="readonly").pack()
tk.Label(left_panel,text="Quantum (RR)",bg="#eef2f7").pack()
quantum_entry=tk.Entry(left_panel,width=6)
quantum_entry.insert(0,"2")
quantum_entry.pack()
tk.Button(left_panel,text="Run Simulation",bg="#ff9800",fg="white",font=("Arial",11,"bold"),
          padx=10,pady=5,command=run_simulation).pack(pady=10)

# RIGHT PANEL
right_panel=tk.Frame(main_frame,bg="#e8eef5")
right_panel.pack(side="right",fill="both",expand=True)

# Input fields for processes
input_frame=tk.Frame(left_panel,bg="#eef2f7")
input_frame.pack(pady=5)

arrival_entries=[]
burst_entries=[]
priority_entries=[]
create_fields()

# Result Table
columns=("PID","AT","BT","Priority","CT","TAT","WT")
result_table=ttk.Treeview(right_panel,columns=columns,show="headings",height=8)
for col in columns:
    result_table.heading(col,text=col)
    result_table.column(col,width=90)
scroll_y=ttk.Scrollbar(right_panel,orient="vertical",command=result_table.yview)
result_table.configure(yscroll=scroll_y.set)
scroll_y.pack(side="right",fill="y")
result_table.pack(side="left",fill="both",expand=True,pady=10)

# Comparison Table
tk.Label(right_panel,text="Algorithm Comparison",font=("Arial",13,"bold"),fg="#1e3d59",bg="#e8eef5").pack(pady=5)
comp_columns=("Algorithm","Avg WT","Avg TAT")
comparison_table=ttk.Treeview(right_panel,columns=comp_columns,show="headings",height=6)
for col in comp_columns:
    comparison_table.heading(col,text=col)
    comparison_table.column(col,width=180)
comparison_table.tag_configure("best",background="#c8f7c5")
comparison_table.pack(pady=5)

# Gantt chart frame
gantt_frame=tk.Frame(root,bg="#e8eef5")
gantt_frame.pack(fill="x",pady=10)

avg_label=tk.Label(root,font=("Arial",11,"bold"),bg="#e8eef5")
avg_label.pack(pady=5)

root.mainloop()
