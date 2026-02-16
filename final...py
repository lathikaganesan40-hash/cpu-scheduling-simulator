# ---------------- GUI LAYOUT ----------------
root=tk.Tk()
root.title("CPU Scheduling Simulator")
root.geometry("1200x750")
root.configure(bg="#e8eef5")

style=ttk.Style()
style.theme_use("clam")
style.configure("Treeview",rowheight=25,
                background="#cce5ff",  # same as create fields table
                fieldbackground="#cce5ff")
style.map("Treeview", background=[("selected","#ff9800")], foreground=[("selected","white")])

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

# Algorithm Selection
tk.Label(left_panel,text="Select Algorithm",bg="#eef2f7",font=("Arial",12,"bold")).pack(pady=3)
algo_var=tk.StringVar(value="FCFS")
ttk.Combobox(left_panel,textvariable=algo_var,
             values=["FCFS","SJF (Non-Preemptive)","SJF (Preemptive)",
                     "Priority (Non-Preemptive)","Priority (Preemptive)","Round Robin"],
             state="readonly").pack(pady=3)

# Number of Processes
tk.Label(left_panel,text="Number of Processes",bg="#eef2f7").pack(pady=3)
num_procs=tk.IntVar(value=4)
tk.Entry(left_panel,textvariable=num_procs,width=6).pack(pady=3)

# Input Fields
input_frame=tk.Frame(left_panel,bg="#eef2f7")
input_frame.pack(pady=5)

arrival_entries=[]
burst_entries=[]
priority_entries=[]
create_fields()

# RUN SIMULATION BUTTON below input table
tk.Button(left_panel,text="Run Simulation",bg="#ff4500",fg="white",font=("Arial",11,"bold"),
          command=run_simulation).pack(pady=5)

# RIGHT PANEL
right_panel=tk.Frame(main_frame,bg="#e8eef5")
right_panel.pack(side="right",fill="both",expand=True)

# Result Table
columns=("PID","AT","BT","Priority","CT","TAT","WT")
result_table=ttk.Treeview(right_panel,columns=columns,show="headings",height=6)
for idx,col in enumerate(columns):
    result_table.heading(col,text=col)
    result_table.column(col,width=90)
result_table.tag_configure("evenrow",background="#cce5ff")
result_table.tag_configure("oddrow",background="#ffffff")
scroll_y=ttk.Scrollbar(right_panel,orient="vertical",command=result_table.yview)
result_table.configure(yscroll=scroll_y.set)
scroll_y.pack(side="right",fill="y")
result_table.pack(side="top",fill="x",padx=10,pady=5)

# Comparison Table
tk.Label(right_panel,text="Algorithm Comparison",font=("Arial",13,"bold"),fg="#1e3d59",bg="#e8eef5").pack(pady=2)
comp_columns=("Algorithm","Avg WT","Avg TAT")
comparison_table=ttk.Treeview(right_panel,columns=comp_columns,show="headings",height=5)
for col in comp_columns:
    comparison_table.heading(col,text=col)
    comparison_table.column(col,width=150)
comparison_table.tag_configure("evenrow",background="#cce5ff")
comparison_table.tag_configure("oddrow",background="#ffffff")
comparison_table.tag_configure("best",background="#c8f7c5")
comparison_table.pack(side="top",fill="x",padx=10,pady=5)

# Avg Label
avg_label=tk.Label(right_panel,font=("Arial",11,"bold"),bg="#e8eef5")
avg_label.pack(pady=5)

# Gantt chart frame (bottom center)
gantt_frame=tk.Frame(root,bg="#e8eef5")
gantt_frame.pack(pady=10)
