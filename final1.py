import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# ---------------- Helper to create input fields ----------------
def create_fields():
    # Clear previous entries if any
    for widget in input_frame.winfo_children():
        widget.destroy()
    arrival_entries.clear()
    burst_entries.clear()
    priority_entries.clear()

    n = num_procs.get()
    if n <= 0:
        messagebox.showerror("Error", "Number of processes must be > 0")
        return

    # Table headers
    tk.Label(input_frame, text="PID", width=6, bg="#eef2f7").grid(row=0, column=0)
    tk.Label(input_frame, text="Arrival Time", width=12, bg="#eef2f7").grid(row=0, column=1)
    tk.Label(input_frame, text="Burst Time", width=12, bg="#eef2f7").grid(row=0, column=2)
    tk.Label(input_frame, text="Priority", width=12, bg="#eef2f7").grid(row=0, column=3)

    for i in range(n):
        tk.Label(input_frame, text=f"P{i+1}", width=6, bg="#eef2f7").grid(row=i+1, column=0)
        at = tk.Entry(input_frame, width=12)
        bt = tk.Entry(input_frame, width=12)
        pr = tk.Entry(input_frame, width=12)
        at.grid(row=i+1, column=1)
        bt.grid(row=i+1, column=2)
        pr.grid(row=i+1, column=3)
        arrival_entries.append(at)
        burst_entries.append(bt)
        priority_entries.append(pr)

# ---------------- Placeholder simulation function ----------------
def run_simulation():
    try:
        n = num_procs.get()
        v = []  # Placeholder list to hold process results
        for i in range(n):
            at = int(arrival_entries[i].get())
            bt = int(burst_entries[i].get())
            pr = int(priority_entries[i].get() or 0)  # default 0 if empty
            pid = f"P{i+1}"
            # Placeholder CT, TAT, WT (just using dummy values)
            ct = at + bt
            tat = ct - at
            wt = tat - bt
            v.append({"PID": pid, "AT": at, "BT": bt, "Priority": pr, "CT": ct, "TAT": tat, "WT": wt})

        # Clear previous table
        for row in result_table.get_children():
            result_table.delete(row)

        # Populate result_table
        for i, process in enumerate(v):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            result_table.insert("", "end", values=(process['PID'], process['AT'], process['BT'],
                                                   process['Priority'], process['CT'],
                                                   process['TAT'], process['WT']), tags=(tag,))

        # Update average label (dummy avg for now)
        avg_wt = sum(p["WT"] for p in v) / n
        avg_tat = sum(p["TAT"] for p in v) / n
        avg_label.config(text=f"Average WT: {avg_wt:.2f}   Average TAT: {avg_tat:.2f}")

        # Clear Gantt chart
        for widget in gantt_frame.winfo_children():
            widget.destroy()
        tk.Label(gantt_frame, text="Gantt Chart placeholder", bg="#e8eef5").pack()

    except ValueError:
        messagebox.showerror("Error", "Please enter valid integers for AT, BT, and Priority.")

# ---------------- GUI LAYOUT ----------------
root = tk.Tk()
root.title("CPU Scheduling Simulator")
root.geometry("1200x750")
root.configure(bg="#e8eef5")

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", rowheight=25, background="#cce5ff", fieldbackground="#cce5ff")
style.map("Treeview", background=[("selected", "#ff9800")], foreground=[("selected", "white")])

# Heading
tk.Label(root, text="CPU Scheduling Algorithm Simulator",
         font=("Arial", 20, "bold"),
         fg="#1e3d59", bg="#e8eef5").pack(pady=10)

main_frame = tk.Frame(root, bg="#e8eef5")
main_frame.pack(fill="both", expand=True)

# LEFT PANEL
left_panel = tk.Frame(main_frame, bg="#eef2f7", padx=10, pady=10)
left_panel.pack(side="left", fill="y")

tk.Label(left_panel, text="Select Algorithm", bg="#eef2f7", font=("Arial", 12, "bold")).pack(pady=3)
algo_var = tk.StringVar(value="FCFS")
ttk.Combobox(left_panel, textvariable=algo_var,
             values=["FCFS", "SJF (Non-Preemptive)", "SJF (Preemptive)",
                     "Priority (Non-Preemptive)", "Priority (Preemptive)", "Round Robin"],
             state="readonly").pack(pady=3)

tk.Label(left_panel, text="Number of Processes", bg="#eef2f7").pack(pady=3)
num_procs = tk.IntVar(value=4)
tk.Entry(left_panel, textvariable=num_procs, width=6).pack(pady=3)

input_frame = tk.Frame(left_panel, bg="#eef2f7")
input_frame.pack(pady=5)

arrival_entries = []
burst_entries = []
priority_entries = []
create_fields()

tk.Button(left_panel, text="Run Simulation", bg="#ff4500", fg="white",
          font=("Arial", 11, "bold"), command=run_simulation).pack(pady=5)

# RIGHT PANEL
right_panel = tk.Frame(main_frame, bg="#e8eef5")
right_panel.pack(side="right", fill="both", expand=True)

columns = ("PID", "AT", "BT", "Priority", "CT", "TAT", "WT")
result_table = ttk.Treeview(right_panel, columns=columns, show="headings", height=6)
for idx, col in enumerate(columns):
    result_table.heading(col, text=col)
    result_table.column(col, width=90)
result_table.tag_configure("evenrow", background="#cce5ff")
result_table.tag_configure("oddrow", background="#ffffff")
scroll_y = ttk.Scrollbar(right_panel, orient="vertical", command=result_table.yview)
result_table.configure(yscroll=scroll_y.set)
scroll_y.pack(side="right", fill="y")
result_table.pack(side="top", fill="x", padx=10, pady=5)

# Comparison Table
tk.Label(right_panel, text="Algorithm Comparison", font=("Arial", 13, "bold"),
         fg="#1e3d59", bg="#e8eef5").pack(pady=2)
comp_columns = ("Algorithm", "Avg WT", "Avg TAT")
comparison_table = ttk.Treeview(right_panel, columns=comp_columns, show="headings", height=5)
for col in comp_columns:
    comparison_table.heading(col, text=col)
    comparison_table.column(col, width=150)
comparison_table.tag_configure("evenrow", background="#cce5ff")
comparison_table.tag_configure("oddrow", background="#ffffff")
comparison_table.tag_configure("best", background="#c8f7c5")
comparison_table.pack(side="top", fill="x", padx=10, pady=5)

avg_label = tk.Label(right_panel, font=("Arial", 11, "bold"), bg="#e8eef5")
avg_label.pack(pady=5)

# Gantt chart frame
gantt_frame = tk.Frame(root, bg="#e8eef5")
gantt_frame.pack(pady=10)

root.mainloop()
