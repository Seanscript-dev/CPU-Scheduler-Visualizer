import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import random
import csv
from datetime import datetime
import copy

class Process:
    """Process class to store process information"""
    def __init__(self, pid, arrival_time, burst_time, priority=0):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority
        self.start_time = -1
        self.finish_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0
        self.response_time = 0
        self.color = self.generate_color()
    
    def generate_color(self):
        """Generate a unique color for the process"""
        colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
            '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52B788',
            '#E63946', '#F4A261', '#2A9D8F', '#264653', '#E76F51'
        ]
        return colors[int(self.pid[1:]) % len(colors)]

class SchedulingAlgorithm:
    """Base class for scheduling algorithms"""
    
    @staticmethod
    def fcfs(processes):
        """First Come First Serve"""
        processes = sorted(processes, key=lambda x: x.arrival_time)
        timeline = []
        current_time = 0
        
        for process in processes:
            if current_time < process.arrival_time:
                current_time = process.arrival_time
            
            process.start_time = current_time
            process.finish_time = current_time + process.burst_time
            process.turnaround_time = process.finish_time - process.arrival_time
            process.waiting_time = process.turnaround_time - process.burst_time
            
            timeline.append({
                'pid': process.pid,
                'start': current_time,
                'end': process.finish_time,
                'color': process.color
            })
            
            current_time = process.finish_time
        
        return processes, timeline
    
    @staticmethod
    def sjf_non_preemptive(processes):
        """Shortest Job First - Non-preemptive"""
        timeline = []
        current_time = 0
        completed = []
        ready_queue = []
        remaining_processes = copy.deepcopy(processes)
        
        while len(completed) < len(processes):
            # Add arrived processes to ready queue
            arrived = [p for p in remaining_processes if p.arrival_time <= current_time]
            ready_queue.extend(arrived)
            for p in arrived:
                remaining_processes.remove(p)
            
            if not ready_queue:
                if remaining_processes:
                    current_time = min(p.arrival_time for p in remaining_processes)
                continue
            
            # Select process with shortest burst time
            process = min(ready_queue, key=lambda x: x.burst_time)
            ready_queue.remove(process)
            
            process.start_time = current_time
            process.finish_time = current_time + process.burst_time
            process.turnaround_time = process.finish_time - process.arrival_time
            process.waiting_time = process.turnaround_time - process.burst_time
            
            timeline.append({
                'pid': process.pid,
                'start': current_time,
                'end': process.finish_time,
                'color': process.color
            })
            
            current_time = process.finish_time
            completed.append(process)
        
        return completed, timeline
    
    @staticmethod
    def sjf_preemptive(processes):
        """Shortest Job First - Preemptive (SRTF)"""
        timeline = []
        current_time = 0
        completed = []
        remaining_processes = copy.deepcopy(processes)
        
        for p in remaining_processes:
            p.remaining_time = p.burst_time
        
        while len(completed) < len(processes):
            # Get available processes
            available = [p for p in remaining_processes if p.arrival_time <= current_time and p.remaining_time > 0]
            
            if not available:
                current_time += 1
                continue
            
            # Select process with shortest remaining time
            process = min(available, key=lambda x: x.remaining_time)
            
            if process.start_time == -1:
                process.start_time = current_time
            
            # Execute for 1 time unit
            timeline.append({
                'pid': process.pid,
                'start': current_time,
                'end': current_time + 1,
                'color': process.color
            })
            
            process.remaining_time -= 1
            current_time += 1
            
            if process.remaining_time == 0:
                process.finish_time = current_time
                process.turnaround_time = process.finish_time - process.arrival_time
                process.waiting_time = process.turnaround_time - process.burst_time
                completed.append(process)
        
        return completed, timeline
    
    @staticmethod
    def round_robin(processes, time_quantum):
        """Round Robin with time quantum"""
        timeline = []
        current_time = 0
        ready_queue = []
        
        # Create working copies and keep reference to originals
        working_processes = copy.deepcopy(processes)
        process_map = {wp.pid: wp for wp in working_processes}
        original_map = {p.pid: p for p in processes}
        
        for p in working_processes:
            p.remaining_time = p.burst_time
            p.start_time = -1
        
        # Sort by arrival time
        working_processes.sort(key=lambda x: x.arrival_time)
        remaining_processes = working_processes.copy()
        
        while remaining_processes or ready_queue:
            # Add arrived processes to ready queue
            while remaining_processes and remaining_processes[0].arrival_time <= current_time:
                ready_queue.append(remaining_processes.pop(0))
            
            if not ready_queue:
                if remaining_processes:
                    current_time = remaining_processes[0].arrival_time
                continue
            
            process = ready_queue.pop(0)
            
            if process.start_time == -1:
                process.start_time = current_time
            
            # Execute for time quantum or remaining time
            exec_time = min(time_quantum, process.remaining_time)
            
            timeline.append({
                'pid': process.pid,
                'start': current_time,
                'end': current_time + exec_time,
                'color': process.color
            })
            
            process.remaining_time -= exec_time
            current_time += exec_time
            
            # Add newly arrived processes
            while remaining_processes and remaining_processes[0].arrival_time <= current_time:
                ready_queue.append(remaining_processes.pop(0))
            
            if process.remaining_time > 0:
                ready_queue.append(process)
            else:
                process.finish_time = current_time
                process.turnaround_time = process.finish_time - process.arrival_time
                process.waiting_time = process.turnaround_time - process.burst_time
                
                # Update the original process with results
                original_process = original_map[process.pid]
                original_process.start_time = process.start_time
                original_process.finish_time = process.finish_time
                original_process.turnaround_time = process.turnaround_time
                original_process.waiting_time = process.waiting_time
        
        return processes, timeline
    
    @staticmethod
    def priority_non_preemptive(processes):
        """Priority Scheduling - Non-preemptive"""
        timeline = []
        current_time = 0
        completed = []
        ready_queue = []
        remaining_processes = copy.deepcopy(processes)
        
        while len(completed) < len(processes):
            # Add arrived processes to ready queue
            arrived = [p for p in remaining_processes if p.arrival_time <= current_time]
            ready_queue.extend(arrived)
            for p in arrived:
                remaining_processes.remove(p)
            
            if not ready_queue:
                if remaining_processes:
                    current_time = min(p.arrival_time for p in remaining_processes)
                continue
            
            # Select process with highest priority (lower number = higher priority)
            process = min(ready_queue, key=lambda x: (x.priority, x.arrival_time))
            ready_queue.remove(process)
            
            process.start_time = current_time
            process.finish_time = current_time + process.burst_time
            process.turnaround_time = process.finish_time - process.arrival_time
            process.waiting_time = process.turnaround_time - process.burst_time
            
            timeline.append({
                'pid': process.pid,
                'start': current_time,
                'end': process.finish_time,
                'color': process.color
            })
            
            current_time = process.finish_time
            completed.append(process)
        
        return completed, timeline
    
    @staticmethod
    def priority_preemptive(processes):
        """Priority Scheduling - Preemptive"""
        timeline = []
        current_time = 0
        completed = []
        remaining_processes = copy.deepcopy(processes)
        
        for p in remaining_processes:
            p.remaining_time = p.burst_time
        
        while len(completed) < len(processes):
            # Get available processes
            available = [p for p in remaining_processes if p.arrival_time <= current_time and p.remaining_time > 0]
            
            if not available:
                current_time += 1
                continue
            
            # Select process with highest priority
            process = min(available, key=lambda x: (x.priority, x.arrival_time))
            
            if process.start_time == -1:
                process.start_time = current_time
            
            # Execute for 1 time unit
            timeline.append({
                'pid': process.pid,
                'start': current_time,
                'end': current_time + 1,
                'color': process.color
            })
            
            process.remaining_time -= 1
            current_time += 1
            
            if process.remaining_time == 0:
                process.finish_time = current_time
                process.turnaround_time = process.finish_time - process.arrival_time
                process.waiting_time = process.turnaround_time - process.burst_time
                completed.append(process)
        
        return completed, timeline

class SchedulerVisualizerApp:
    """Main application class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduling Algorithms Visualizer - SeanScript Development")
        
        # Make fullscreen
        self.root.state('zoomed')  # Windows
        # self.root.attributes('-zoomed', True)  # Linux
        
        # Variables
        self.processes = []
        self.timeline = []
        self.current_algorithm = tk.StringVar(value="FCFS")
        self.time_quantum = tk.IntVar(value=2)
        self.num_processes = tk.IntVar(value=4)
        self.dark_mode = tk.BooleanVar(value=True)  # Dark mode enabled by default
        self.animation_speed = tk.IntVar(value=100)
        self.animation_running = False
        
        # Colors
        self.set_dark_colors()
        
        # Setup UI
        self.setup_ui()
        
        # Bind escape key to exit fullscreen
        self.root.bind('<Escape>', lambda e: self.root.state('normal'))
        self.root.bind('<F11>', lambda e: self.root.state('zoomed'))

    def set_dark_colors(self):
        """Set all colors to dark mode (default and only mode)"""
        self.bg_color = '#1E1E1E'
        self.fg_color = '#FFFFFF'
        self.panel_bg = '#2D2D2D'
        self.input_bg = '#3C3C3C'
        self.button_bg = '#0078D4'
        self.table_bg = '#252525'

    def update_colors(self):
        """Update color scheme (only dark mode now)"""
        self.set_dark_colors()
    
    def setup_ui(self):
        """Setup the user interface"""
        self.root.configure(bg=self.bg_color)
        
        # Top bar
        self.create_top_bar()
        
        # Main content area
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel - Input
        self.create_left_panel(main_frame)
        
        # Center panel - Gantt Chart
        self.create_center_panel(main_frame)
        
        # Right panel - Results
        self.create_right_panel(main_frame)
        
        # Bottom panel - Charts and Summary
        self.create_bottom_panel()
    
    def create_top_bar(self):
        """Create top navigation bar with gradient effect"""
        top_bar = tk.Frame(self.root, bg=self.panel_bg, height=70)
        top_bar.pack(fill=tk.X, side=tk.TOP)

        # Remove gradient_canvas and use a simple frame for header
        header_frame = tk.Frame(top_bar, bg=self.panel_bg)
        header_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_frame = tk.Frame(header_frame, bg=self.panel_bg)
        title_frame.pack(side=tk.LEFT, padx=20, pady=10)

        title_label = tk.Label(
            title_frame,
            text="🖥️ CPU Scheduling Visualizer",
            font=('Arial', 22, 'bold'),
            bg=self.panel_bg,
            fg='white'
        )
        title_label.pack(side=tk.LEFT)

        subtitle = tk.Label(
            title_frame,
            text="by SeanScript Development",
            font=('Arial', 11),
            bg=self.panel_bg,
            fg='#E0E0E0'
        )
        subtitle.pack(side=tk.LEFT, padx=10)

        # Controls frame
        controls_frame = tk.Frame(header_frame, bg=self.panel_bg)
        controls_frame.pack(side=tk.RIGHT, padx=20, pady=10)

        # Algorithm selector
        tk.Label(
            controls_frame,
            text="Algorithm:",
            font=('Arial', 11),
            bg=self.panel_bg,
            fg='white'
        ).pack(side=tk.LEFT, padx=5)

        algorithms = [
            "FCFS",
            "SJF (Non-preemptive)",
            "SJF (Preemptive)",
            "Round Robin",
            "Priority (Non-preemptive)",
            "Priority (Preemptive)"
        ]

        algo_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.current_algorithm,
            values=algorithms,
            state='readonly',
            width=25,
            font=('Arial', 10)
        )
        algo_combo.pack(side=tk.LEFT, padx=5)
        # Update process inputs and quantum visibility when algorithm changes
        algo_combo.bind("<<ComboboxSelected>>", lambda e: [self.update_process_inputs(), self.update_quantum_visibility()])

        # Run button with hover effect
        self.run_btn = tk.Button(
            controls_frame,
            text="▶ RUN",
            command=self.run_simulation,
            font=('Arial', 12, 'bold'),
            bg='#28A745',
            fg='white',
            padx=25,
            pady=8,
            relief=tk.FLAT,
            cursor='hand2',
            bd=0
        )
        self.run_btn.pack(side=tk.LEFT, padx=10)
        self.run_btn.bind("<Enter>", lambda e: self.run_btn.config(bg='#218838'))
        self.run_btn.bind("<Leave>", lambda e: self.run_btn.config(bg='#28A745'))
    
    def create_left_panel(self, parent):
        """Create left input panel"""
        left_panel = tk.Frame(parent, bg=self.panel_bg, relief=tk.RAISED, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)
        left_panel.config(width=350)
        left_panel.pack_propagate(False)
        
        # Header
        header = tk.Label(
            left_panel,
            text="📝 Process Input",
            font=('Arial', 16, 'bold'),
            bg=self.panel_bg,
            fg=self.fg_color
        )
        header.pack(pady=10)
        
        # Number of processes
        num_frame = tk.Frame(left_panel, bg=self.panel_bg)
        num_frame.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(
            num_frame,
            text="Number of Processes:",
            font=('Arial', 11),
            bg=self.panel_bg,
            fg=self.fg_color
        ).pack(side=tk.LEFT)
        
        tk.Spinbox(
            num_frame,
            from_=1,
            to=99,
            textvariable=self.num_processes,
            font=('Arial', 11),
            width=5,
            command=self.update_process_inputs
        ).pack(side=tk.RIGHT)
        
        # Time quantum (for Round Robin) - only show for Round Robin
        self.quantum_frame = tk.Frame(left_panel, bg=self.panel_bg)
        self.quantum_frame.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(
            self.quantum_frame,
            text="Time Quantum (RR):",
            font=('Arial', 11),
            bg=self.panel_bg,
            fg=self.fg_color
        ).pack(side=tk.LEFT)
        tk.Spinbox(
            self.quantum_frame,
            from_=1,
            to=99,
            textvariable=self.time_quantum,
            font=('Arial', 11),
            width=5
        ).pack(side=tk.RIGHT)
        
        # Buttons with hover effects
        self.btn_frame = tk.Frame(left_panel, bg=self.panel_bg)
        self.btn_frame.pack(fill=tk.X, padx=15, pady=10)

        # Configure grid for 2x2 layout
        self.btn_frame.grid_columnconfigure(0, weight=1)
        self.btn_frame.grid_columnconfigure(1, weight=1)
        self.btn_frame.grid_rowconfigure(0, weight=1)
        self.btn_frame.grid_rowconfigure(1, weight=1)

        self.generate_btn = tk.Button(
            self.btn_frame,
            text="Export to CSV",
            command=self.export_results,
            font=('Arial', 10, 'bold'),
            bg=self.button_bg,
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            pady=8
        )
        self.generate_btn.grid(row=0, column=0, padx=2, pady=2, sticky='ew')

        self.random_btn = tk.Button(
            self.btn_frame,
            text="Generate Data",
            command=self.random_fill,
            font=('Arial', 10, 'bold'),
            bg='#FFC107',
            fg='black',
            relief=tk.FLAT,
            cursor='hand2',
            pady=8
        )
        self.random_btn.grid(row=0, column=1, padx=2, pady=2, sticky='ew')

        self.clear_btn = tk.Button(
            self.btn_frame,
            text="Clear Data",
            command=self.clear_inputs,
            font=('Arial', 10, 'bold'),
            bg='#DC3545',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            pady=8
        )
        self.clear_btn.grid(row=1, column=0, padx=2, pady=2, sticky='ew')

        self.process_btn = tk.Button(
            self.btn_frame,
            text="Process",
            command=self.show_process,
            font=('Arial', 10, 'bold'),
            bg='#28A745',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            pady=8
        )
        self.process_btn.grid(row=1, column=1, padx=2, pady=2, sticky='ew')

        # Add hover effects
        self.generate_btn.bind("<Enter>", lambda e: self.generate_btn.config(bg='#005a9e'))
        self.generate_btn.bind("<Leave>", lambda e: self.generate_btn.config(bg=self.button_bg))

        self.random_btn.bind("<Enter>", lambda e: self.random_btn.config(bg='#e0a800'))
        self.random_btn.bind("<Leave>", lambda e: self.random_btn.config(bg='#FFC107'))

        self.clear_btn.bind("<Enter>", lambda e: self.clear_btn.config(bg='#c82333'))
        self.clear_btn.bind("<Leave>", lambda e: self.clear_btn.config(bg='#DC3545'))

        self.process_btn.bind("<Enter>", lambda e: self.process_btn.config(bg='#218838'))
        self.process_btn.bind("<Leave>", lambda e: self.process_btn.config(bg='#28A745'))
        
        # Scrollable process input area
        input_canvas = tk.Canvas(left_panel, bg=self.panel_bg, highlightthickness=0)
        scrollbar = tk.Scrollbar(left_panel, orient="vertical", command=input_canvas.yview)
        self.process_input_frame = tk.Frame(input_canvas, bg=self.panel_bg)
        
        self.process_input_frame.bind(
            "<Configure>",
            lambda e: input_canvas.configure(scrollregion=input_canvas.bbox("all"))
        )
        
        input_canvas.create_window((0, 0), window=self.process_input_frame, anchor="nw")
        input_canvas.configure(yscrollcommand=scrollbar.set)
        
        input_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind mouse wheel
        input_canvas.bind_all("<MouseWheel>", lambda e: input_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # Initial process inputs
        self.update_process_inputs()
        self.update_quantum_visibility()

    def update_quantum_visibility(self):
        """Show/hide time quantum input based on algorithm"""
        if self.current_algorithm.get() == "Round Robin":
            self.quantum_frame.pack(fill=tk.X, padx=15, pady=5, before=self.btn_frame)
        else:
            self.quantum_frame.pack_forget()

    def create_center_panel(self, parent):
        """Create center Gantt chart panel"""
        center_panel = tk.Frame(parent, bg=self.panel_bg, relief=tk.RAISED, bd=2)
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Header
        header = tk.Label(
            center_panel,
            text="📊 Gantt Chart Visualization",
            font=('Arial', 16, 'bold'),
            bg=self.panel_bg,
            fg=self.fg_color
        )
        header.pack(pady=10)
        
        # Animation speed control
        speed_frame = tk.Frame(center_panel, bg=self.panel_bg)
        speed_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(
            speed_frame,
            text="Animation Speed:",
            font=('Arial', 10),
            bg=self.panel_bg,
            fg=self.fg_color
        ).pack(side=tk.LEFT)
        
        tk.Scale(
            speed_frame,
            from_=10,
            to=500,
            orient=tk.HORIZONTAL,
            variable=self.animation_speed,
            bg=self.panel_bg,
            fg=self.fg_color,
            highlightthickness=0
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10)
        
        tk.Label(
            speed_frame,
            text="ms",
            font=('Arial', 10),
            bg=self.panel_bg,
            fg=self.fg_color
        ).pack(side=tk.RIGHT)
        
        # Gantt chart canvas
        self.gantt_canvas = tk.Canvas(
            center_panel,
            bg='#30394c',
            height=200,
            relief=tk.SUNKEN,
            bd=2
        )
        self.gantt_canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Status label
        self.status_label = tk.Label(
            center_panel,
            text="Ready to simulate. Configure processes and click RUN.",
            font=('Arial', 11),
            bg=self.panel_bg,
            fg='#0078D4'
        )
        self.status_label.pack(pady=10)
    
    def create_right_panel(self, parent):
        """Create right results panel"""
        right_panel = tk.Frame(parent, bg=self.panel_bg, relief=tk.RAISED, bd=2)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)
        right_panel.config(width=450)
        right_panel.pack_propagate(False)
        
        # Header
        header = tk.Label(
            right_panel,
            text="📈 Results Table",
            font=('Arial', 16, 'bold'),
            bg=self.panel_bg,
            fg=self.fg_color
        )
        header.pack(pady=10)
        
        # Table frame
        table_frame = tk.Frame(right_panel, bg=self.panel_bg)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Configure grid weights for proper expansion
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Scrollbars
        vsb = tk.Scrollbar(table_frame, orient="vertical")
        hsb = tk.Scrollbar(table_frame, orient="horizontal")
        
        # Treeview with clean white background and black text
        style = ttk.Style()
        style.configure("Results.Treeview", 
                       background='white',
                       foreground='black',
                       fieldbackground='white',
                       rowheight=28,
                       font=('Arial', 10))
        style.configure("Results.Treeview.Heading",
                       background='#f8f9fa',
                       foreground='black',
                       relief='flat',
                       font=('Arial', 10, 'bold'))
        style.map("Results.Treeview.Heading",
                 background=[('active', '#e9ecef')])
        
        columns = ('PID', 'AT', 'BT', 'Priority', 'FT', 'TAT', 'WT')
        self.results_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            height=18,
            style="Results.Treeview"
        )
        
        # Configure scrollbars
        vsb.config(command=self.results_tree.yview)
        hsb.config(command=self.results_tree.xview)
        
        # Column headings
        headings = {
            'PID': 'Process ID',
            'AT': 'Arrival Time',
            'BT': 'Burst Time',
            'Priority': 'Priority',
            'FT': 'Finish Time',
            'TAT': 'Turnaround',
            'WT': 'Waiting'
        }
        
        # Configure column widths for better visibility
        column_widths = {
            'PID': 80,
            'AT': 85,
            'BT': 75,
            'Priority': 65,
            'FT': 85,
            'TAT': 85,
            'WT': 75
        }
        
        for col in columns:
            self.results_tree.heading(col, text=headings[col])
            self.results_tree.column(col, width=column_widths[col], anchor='center')
        
        # Pack table and scrollbars using grid for better control
        self.results_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        # Export button with hover effect
        self.export_btn = tk.Button(
            right_panel,
            text="📥 Export to CSV",
            command=self.export_results,
            font=('Arial', 11, 'bold'),
            bg='#17A2B8',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            pady=10
        )
        self.export_btn.pack(fill=tk.X, padx=10, pady=10)
        
        # Add hover effect
        self.export_btn.bind("<Enter>", lambda e: self.export_btn.config(bg='#138496'))
        self.export_btn.bind("<Leave>", lambda e: self.export_btn.config(bg='#17A2B8'))
    
    def create_bottom_panel(self):
        """Create bottom summary and charts panel"""
        bottom_panel = tk.Frame(self.root, bg=self.panel_bg, relief=tk.RAISED, bd=2)
        bottom_panel.pack(side=tk.BOTTOM, fill=tk.BOTH, padx=10, pady=5)
        bottom_panel.config(height=300)
        
        # Summary frame
        summary_frame = tk.Frame(bottom_panel, bg=self.panel_bg)
        summary_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=20, pady=10, expand=False)
        summary_frame.config(width=300)
        summary_frame.pack_propagate(False)
        
        tk.Label(
            summary_frame,
            text="📊 Performance Metrics",
            font=('Arial', 14, 'bold'),
            bg=self.panel_bg,
            fg=self.fg_color
        ).pack(pady=10)
        
        # Performance metrics with larger font and better spacing
        metrics_frame = tk.Frame(summary_frame, bg=self.panel_bg)
        metrics_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.avg_tat_label = tk.Label(
            metrics_frame,
            text="Average Turnaround Time: --",
            font=('Arial', 12, 'bold'),
            bg=self.panel_bg,
            fg='#FFFFFF',
            anchor='w'
        )
        self.avg_tat_label.pack(fill=tk.X, pady=4, padx=10)
        
        self.avg_wt_label = tk.Label(
            metrics_frame,
            text="Average Waiting Time: --",
            font=('Arial', 12, 'bold'),
            bg=self.panel_bg,
            fg='#FFFFFF',
            anchor='w'
        )
        self.avg_wt_label.pack(fill=tk.X, pady=0, padx=10)
        
        self.throughput_label = tk.Label(
            metrics_frame,
            text="Throughput: --",
            font=('Arial', 12, 'bold'),
            bg=self.panel_bg,
            fg='#FFFFFF',
            anchor='w'
        )
        self.throughput_label.pack(fill=tk.X, pady=0, padx=10)
        
        # Larger Restart button with hover effect
        self.restart_btn = tk.Button(
            summary_frame,
            text="🔄 RESTART SIMULATION",
            command=self.restart_simulation,
            font=('Arial', 13, 'bold'),
            bg='#6C757D',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            pady=10,
            height=2  # Increase this value for more vertical height (number of text lines)
        )
        self.restart_btn.pack(fill=tk.X, pady=20, padx=10)
        
        # Add hover effect
        self.restart_btn.bind("<Enter>", lambda e: self.restart_btn.config(bg='#5a6268'))
        self.restart_btn.bind("<Leave>", lambda e: self.restart_btn.config(bg='#6C757D'))
        
        # Charts frame
        charts_frame = tk.Frame(bottom_panel, bg=self.panel_bg)
        charts_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Matplotlib figure for charts
        self.fig = Figure(figsize=(12, 3), dpi=80, facecolor=self.panel_bg)
        self.chart_canvas = FigureCanvasTkAgg(self.fig, charts_frame)
        self.chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def update_process_inputs(self):
        """Generate input fields for processes"""
        # Clear existing inputs
        for widget in self.process_input_frame.winfo_children():
            widget.destroy()
        
        n = self.num_processes.get()
        self.process_entries = []
        show_priority = "Priority" in self.current_algorithm.get()

        # Set background color for process input frame and its parent canvas
        bg_color = self.panel_bg
        parent_canvas = self.process_input_frame.master
        parent_canvas.config(bg=bg_color, highlightthickness=0)
        self.process_input_frame.config(bg=bg_color)

        for i in range(n):
            process_frame = tk.LabelFrame(
                self.process_input_frame,
                text=f"Process P{i+1}",
                font=('Arial', 11, 'bold'),
                bg=bg_color,
                fg='white',
                relief=tk.GROOVE,
                bd=2
            )
            process_frame.pack(fill=tk.X, padx=10, pady=8)
            entries = {}

            # Arrival Time
            at_frame = tk.Frame(process_frame, bg=bg_color)
            at_frame.pack(fill=tk.X, padx=10, pady=3)
            tk.Label(
                at_frame,
                text="Arrival Time:",
                font=('Arial', 10),
                bg=bg_color,
                fg='white'
            ).pack(side=tk.LEFT)
            at_entry = tk.Entry(at_frame, font=('Arial', 10), width=8, bg='#3C3C3C', fg='white', insertbackground='white')
            at_entry.pack(side=tk.RIGHT)
            entries['at'] = at_entry

            # Burst Time
            bt_frame = tk.Frame(process_frame, bg=bg_color)
            bt_frame.pack(fill=tk.X, padx=10, pady=3)
            tk.Label(
                bt_frame,
                text="Burst Time:",
                font=('Arial', 10),
                bg=bg_color,
                fg='white'
            ).pack(side=tk.LEFT)
            bt_entry = tk.Entry(bt_frame, font=('Arial', 10), width=8, bg='#3C3C3C', fg='white', insertbackground='white')
            bt_entry.pack(side=tk.RIGHT)
            entries['bt'] = bt_entry

            # Priority (only for Priority Scheduling)
            if show_priority:
                priority_frame = tk.Frame(process_frame, bg=bg_color)
                priority_frame.pack(fill=tk.X, padx=10, pady=3)
                tk.Label(
                    priority_frame,
                    text="Priority:",
                    font=('Arial', 10),
                    bg=bg_color,
                    fg='white'
                ).pack(side=tk.LEFT)
                priority_entry = tk.Entry(priority_frame, font=('Arial', 10), width=8, bg='#3C3C3C', fg='white', insertbackground='white')
                priority_entry.pack(side=tk.RIGHT)
                entries['priority'] = priority_entry
            self.process_entries.append(entries)
    
    def random_fill(self):
        """Fill inputs with random values"""
        show_priority = "Priority" in self.current_algorithm.get()
        for i, entries in enumerate(self.process_entries):
            entries['at'].delete(0, tk.END)
            entries['at'].insert(0, str(random.randint(0, 10)))
            
            entries['bt'].delete(0, tk.END)
            entries['bt'].insert(0, str(random.randint(1, 10)))
            
            if show_priority and 'priority' in entries:
                entries['priority'].delete(0, tk.END)
                entries['priority'].insert(0, str(random.randint(1, 5)))
    
    def clear_inputs(self):
        """Clear all input fields"""
        for entries in self.process_entries:
            entries['at'].delete(0, tk.END)
            entries['bt'].delete(0, tk.END)
            if 'priority' in entries:
                entries['priority'].delete(0, tk.END)
    
    def toggle_dark_mode(self):
        """No-op: dark mode is always enabled"""
        pass

    def validate_inputs(self):
        """Validate all process inputs"""
        try:
            processes = []
            show_priority = "Priority" in self.current_algorithm.get()
            for i, entries in enumerate(self.process_entries):
                at = int(entries['at'].get())
                bt = int(entries['bt'].get())
                if show_priority and 'priority' in entries:
                    priority = int(entries['priority'].get()) if entries['priority'].get() else 0
                else:
                    priority = 0
                
                if at < 0 or bt <= 0:
                    raise ValueError(f"Process P{i+1}: Times must be non-negative and burst time > 0")
                
                process = Process(f"P{i+1}", at, bt, priority)
                processes.append(process)
            
            return True, processes
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return False, None
        except Exception as e:
            messagebox.showerror("Input Error", "Please fill all fields with valid numbers")
            return False, None
    
    def run_simulation(self):
        """Run the scheduling simulation"""
        if self.animation_running:
            messagebox.showwarning("Running", "Animation is already running!")
            return
        
        # Validate inputs
        valid, processes = self.validate_inputs()
        if not valid:
            return

        self.processes = processes
        algorithm = self.current_algorithm.get()
        
        # Run scheduling algorithm
        try:
            if algorithm == "FCFS":
                result_processes, timeline = SchedulingAlgorithm.fcfs(copy.deepcopy(self.processes))
            elif algorithm == "SJF (Non-preemptive)":
                result_processes, timeline = SchedulingAlgorithm.sjf_non_preemptive(copy.deepcopy(self.processes))
            elif algorithm == "SJF (Preemptive)":
                result_processes, timeline = SchedulingAlgorithm.sjf_preemptive(copy.deepcopy(self.processes))
            elif algorithm == "Round Robin":
                result_processes, timeline = SchedulingAlgorithm.round_robin(
                    copy.deepcopy(self.processes),
                    self.time_quantum.get()
                )
            elif algorithm == "Priority (Non-preemptive)":
                result_processes, timeline = SchedulingAlgorithm.priority_non_preemptive(copy.deepcopy(self.processes))
            elif algorithm == "Priority (Preemptive)":
                result_processes, timeline = SchedulingAlgorithm.priority_preemptive(copy.deepcopy(self.processes))
            else:
                messagebox.showerror("Error", "Unknown algorithm selected")
                return
            
            # Update processes with results
            for original_p in self.processes:
                for result_p in result_processes:
                    if original_p.pid == result_p.pid:
                        original_p.finish_time = result_p.finish_time
                        original_p.turnaround_time = result_p.turnaround_time
                        original_p.waiting_time = result_p.waiting_time
                        break
            
            self.timeline = timeline
            
            # Update results table
            self.update_results_table()
            
            # Update summary
            self.update_summary()
            
            # Animate Gantt chart
            self.animate_gantt_chart()
            
            # Draw charts
            self.draw_charts()
            
            self.status_label.config(text=f"✓ Simulation completed using {algorithm}", fg='#28A745')
            
        except Exception as e:
            messagebox.showerror("Simulation Error", f"An error occurred: {str(e)}")
            self.status_label.config(text=f"✗ Simulation failed", fg='#DC3545')
    
    def update_results_table(self):
        """Update the results table with process data"""
        # Clear existing data
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        show_priority = "Priority" in self.current_algorithm.get()
        # Insert new data
        for process in self.processes:
            self.results_tree.insert('', tk.END, values=(
                process.pid,
                process.arrival_time,
                process.burst_time,
                process.priority if show_priority else "--",
                process.finish_time,
                process.turnaround_time,
                process.waiting_time
            ))
    
    def update_summary(self):
        """Update summary statistics"""
        if not self.processes:
            return
        
        avg_tat = sum(p.turnaround_time for p in self.processes) / len(self.processes)
        avg_wt = sum(p.waiting_time for p in self.processes) / len(self.processes)
        
        # Calculate throughput
        if self.timeline:
            total_time = max(t['end'] for t in self.timeline)
            throughput = len(self.processes) / total_time if total_time > 0 else 0
        else:
            throughput = 0
        
        self.avg_tat_label.config(text=f"Average Turnaround Time: {avg_tat:.2f}")
        self.avg_wt_label.config(text=f"Average Waiting Time: {avg_wt:.2f}")
        self.throughput_label.config(text=f"Throughput: {throughput:.3f} processes/unit")
    
    def animate_gantt_chart(self):
        """Animate the Gantt chart"""
        if not self.timeline:
            return
        
        self.animation_running = True
        self.gantt_canvas.config(bg='#30394c')
        self.gantt_canvas.delete("all")
        
        # Calculate dimensions
        canvas_width = self.gantt_canvas.winfo_width()
        canvas_height = self.gantt_canvas.winfo_height()
        
        if canvas_width <= 1:  # Canvas not yet rendered
            canvas_width = 800
            canvas_height = 200
        
        margin = 50
        chart_width = canvas_width - 2 * margin
        chart_height = canvas_height - 2 * margin
        
        # Get max time
        max_time = max(t['end'] for t in self.timeline)
        time_scale = chart_width / max_time if max_time > 0 else 1
        
        # Draw axes
        self.gantt_canvas.create_line(
            margin, canvas_height - margin,
            canvas_width - margin, canvas_height - margin,
            width=2, fill='white'
        )
        
        # Draw time labels
        for i in range(0, max_time + 1, max(1, max_time // 10)):
            x = margin + i * time_scale
            self.gantt_canvas.create_line(
                x, canvas_height - margin,
                x, canvas_height - margin + 10,
                width=2, fill='white'
            )
            self.gantt_canvas.create_text(
                x, canvas_height - margin + 20,
                text=str(i), font=('Arial', 9),
                fill='white'
            )
        
        # Animate timeline
        self.current_animation_index = 0
        self.animate_next_block()
    
    def animate_next_block(self):
        """Animate next block in timeline"""
        if self.current_animation_index >= len(self.timeline):
            self.animation_running = False
            return
        
        block = self.timeline[self.current_animation_index]
        
        canvas_width = self.gantt_canvas.winfo_width()
        canvas_height = self.gantt_canvas.winfo_height()
        
        if canvas_width <= 1:
            canvas_width = 800
            canvas_height = 200
        
        margin = 50
        chart_width = canvas_width - 2 * margin
        chart_height = canvas_height - 2 * margin
        
        max_time = max(t['end'] for t in self.timeline)
        time_scale = chart_width / max_time if max_time > 0 else 1
        
        # Calculate block position
        x1 = margin + block['start'] * time_scale
        x2 = margin + block['end'] * time_scale
        y1 = margin + chart_height * 0.2
        y2 = margin + chart_height * 0.8
        
        # Draw block
        rect_id = self.gantt_canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=block['color'],
            outline='black',
            width=2
        )
        
        # Add process label
        label_color = 'white'
        text_id = self.gantt_canvas.create_text(
            (x1 + x2) / 2, (y1 + y2) / 2,
            text=block['pid'],
            font=('Arial', 12, 'bold'),
            fill=label_color
        )
        
        # Add time labels
        self.gantt_canvas.create_text(
            x1, y1 - 10,
            text=str(block['start']),
            font=('Arial', 9),
            fill='white'
        )
        
        if self.current_animation_index == len(self.timeline) - 1 or \
           self.timeline[self.current_animation_index + 1]['start'] != block['end']:
            self.gantt_canvas.create_text(
                x2, y1 - 10,
                text=str(block['end']),
                font=('Arial', 9),
                fill='white'
            )
        
        self.current_animation_index += 1
        
        # Schedule next animation
        self.root.after(self.animation_speed.get(), self.animate_next_block)
    
    def draw_charts(self):
        """Draw waiting time and turnaround time charts"""
        if not self.processes:
            return
        
        self.fig.clear()
        
        # Create subplots
        ax1 = self.fig.add_subplot(121)
        ax2 = self.fig.add_subplot(122)
        
        # Set dark background for charts
        self.fig.patch.set_facecolor(self.panel_bg)
        ax1.set_facecolor('#2D2D2D')
        ax2.set_facecolor('#2D2D2D')
        
        # Extract data
        pids = [p.pid for p in self.processes]
        waiting_times = [p.waiting_time for p in self.processes]
        turnaround_times = [p.turnaround_time for p in self.processes]
        colors = [p.color for p in self.processes]
        
        # Waiting Time Chart
        bars1 = ax1.bar(pids, waiting_times, color=colors, edgecolor='white', linewidth=1.5)
        ax1.set_xlabel('Process ID', fontsize=10, fontweight='bold', color='white')
        ax1.set_ylabel('Waiting Time', fontsize=10, fontweight='bold', color='white')
        ax1.set_title('Waiting Time per Process', fontsize=12, fontweight='bold', color='white')
        ax1.grid(axis='y', alpha=0.3, color='white')
        ax1.tick_params(axis='both', colors='white')
        
        # Add value labels on bars
        for i, (pid, wt) in enumerate(zip(pids, waiting_times)):
            ax1.text(i, wt + 0.1, str(wt), ha='center', va='bottom', fontsize=9, fontweight='bold', color='white')
        
        # Turnaround Time Chart
        bars2 = ax2.bar(pids, turnaround_times, color=colors, edgecolor='white', linewidth=1.5)
        ax2.set_xlabel('Process ID', fontsize=10, fontweight='bold', color='white')
        ax2.set_ylabel('Turnaround Time', fontsize=10, fontweight='bold', color='white')
        ax2.set_title('Turnaround Time per Process', fontsize=12, fontweight='bold', color='white')
        ax2.grid(axis='y', alpha=0.3, color='white')
        ax2.tick_params(axis='both', colors='white')
        
        # Add value labels on bars
        for i, (pid, tat) in enumerate(zip(pids, turnaround_times)):
            ax2.text(i, tat + 0.1, str(tat), ha='center', va='bottom', fontsize=9, fontweight='bold', color='white')
        
        self.fig.tight_layout()
        self.chart_canvas.draw()
    
    def export_results(self):
        """Export results to CSV file"""
        if not self.processes:
            messagebox.showwarning("No Data", "No results to export. Run a simulation first.")
            return
        
        # Ask for save location
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"scheduling_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                show_priority = "Priority" in self.current_algorithm.get()
                writer.writerow([
                    'Process ID', 'Arrival Time', 'Burst Time', 'Priority' if show_priority else '',
                    'Finish Time', 'Turnaround Time', 'Waiting Time'
                ] if show_priority else [
                    'Process ID', 'Arrival Time', 'Burst Time',
                    'Finish Time', 'Turnaround Time', 'Waiting Time'
                ])
                
                # Write process data
                for process in self.processes:
                    if show_priority:
                        writer.writerow([
                            process.pid,
                            process.arrival_time,
                            process.burst_time,
                            process.priority,
                            process.finish_time,
                            process.turnaround_time,
                            process.waiting_time
                        ])
                    else:
                        writer.writerow([
                            process.pid,
                            process.arrival_time,
                            process.burst_time,
                            process.finish_time,
                            process.turnaround_time,
                            process.waiting_time
                        ])
                
                # Write summary
                writer.writerow([])
                writer.writerow(['Summary Statistics'])
                avg_tat = sum(p.turnaround_time for p in self.processes) / len(self.processes)
                avg_wt = sum(p.waiting_time for p in self.processes) / len(self.processes)
                writer.writerow(['Average Turnaround Time', f'{avg_tat:.2f}'])
                writer.writerow(['Average Waiting Time', f'{avg_wt:.2f}'])
                writer.writerow(['Algorithm', self.current_algorithm.get()])
                writer.writerow(['Export Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            
            messagebox.showinfo("Export Successful", f"Results exported to:\n{filename}")
        
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export results:\n{str(e)}")

    def show_process(self):
        """Show step-by-step explanation of the scheduling process"""
        if not self.processes or not self.timeline:
            messagebox.showwarning("No Data", "Run a simulation first to see process.")
            return

        # Create explanation window
        explanation_window = tk.Toplevel(self.root)
        explanation_window.title("Scheduling Process Explanation")
        explanation_window.geometry("600x400")
        explanation_window.configure(bg=self.bg_color)

        # Title
        title_label = tk.Label(
            explanation_window,
            text="Step-by-Step Scheduling Explanation",
            font=('Arial', 16, 'bold'),
            bg=self.bg_color,
            fg=self.fg_color
        )
        title_label.pack(pady=10)

        # Text area with scrollbar
        text_frame = tk.Frame(explanation_window, bg=self.bg_color)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=('Arial', 11),
            bg='#2D2D2D',
            fg='white',
            padx=10,
            pady=10
        )
        scrollbar = tk.Scrollbar(text_frame, command=text_widget.yview)
        text_widget.config(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Generate explanation
        explanation = self.generate_explanation()
        text_widget.insert(tk.END, explanation)
        text_widget.config(state=tk.DISABLED)

        # Close button
        close_btn = tk.Button(
            explanation_window,
            text="Close",
            command=explanation_window.destroy,
            font=('Arial', 12, 'bold'),
            bg=self.button_bg,
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            pady=8
        )
        close_btn.pack(pady=10)

    def generate_explanation(self):
        """Generate the step-by-step explanation text"""
        explanation = f"Scheduling Algorithm: {self.current_algorithm.get()}\n\n"

        # Get all arrival events
        arrivals = []
        for process in self.processes:
            arrivals.append({
                'time': process.arrival_time,
                'type': 'arrival',
                'pid': process.pid
            })

        # Get all execution events from timeline
        executions = []
        for block in self.timeline:
            executions.append({
                'time': block['start'],
                'type': 'start',
                'pid': block['pid']
            })
            executions.append({
                'time': block['end'],
                'type': 'end',
                'pid': block['pid']
            })

        # Combine and sort all events
        all_events = arrivals + executions
        all_events.sort(key=lambda x: (x['time'], 0 if x['type'] == 'arrival' else 1 if x['type'] == 'start' else 2))

        # Generate explanation text
        current_time = 0
        for event in all_events:
            if event['time'] > current_time:
                explanation += f"\n"
            explanation += f"Time {event['time']}: "

            if event['type'] == 'arrival':
                explanation += f"Process {event['pid']} arrived\n"
            elif event['type'] == 'start':
                explanation += f"Process {event['pid']} started executing\n"
            elif event['type'] == 'end':
                explanation += f"Process {event['pid']} finished executing\n"

            current_time = event['time']

        # Add final statistics
        explanation += f"\nFinal Results:\n"
        for process in self.processes:
            explanation += f"Process {process.pid}: Arrival={process.arrival_time}, Burst={process.burst_time}, "
            explanation += f"Start={process.start_time}, Finish={process.finish_time}, "
            explanation += f"Turnaround={process.turnaround_time}, Waiting={process.waiting_time}\n"

        return explanation

    def restart_simulation(self):
        """Restart the simulation"""
        # Clear Gantt chart
        self.gantt_canvas.delete("all")
        
        # Clear results table
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Clear charts
        self.fig.clear()
        self.chart_canvas.draw()
        
        # Reset summary
        self.avg_tat_label.config(text="Average Turnaround Time: --")
        self.avg_wt_label.config(text="Average Waiting Time: --")
        self.throughput_label.config(text="Throughput: --")
        
        # Reset status
        self.status_label.config(
            text="Ready to simulate. Configure processes and click RUN.",
            fg='#0078D4'
        )
        
        # Clear inputs
        self.clear_inputs()
        
        # Reset variables
        self.processes = []
        self.timeline = []
        self.animation_running = False

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = SchedulerVisualizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
