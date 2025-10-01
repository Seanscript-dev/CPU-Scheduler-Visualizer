import tkinter as tk
from tkinter import ttk
import threading
import time
import subprocess
import sys
import os

class LoadingPage:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduling Visualizer - Loading")
        
        # Make it fullscreen like your main app
        self.root.state('zoomed')
        
        # Colors matching your main application
        self.bg_color = '#1E1E1E'
        self.panel_bg = '#2D2D2D'
        self.fg_color = '#FFFFFF'
        self.button_bg = '#0078D4'
        self.accent_green = '#28A745'
        self.accent_blue = '#17A2B8'
        
        self.root.configure(bg=self.bg_color)
        self.setup_ui()
        
        # Start the loading animation
        self.start_loading_animation()
        
        # Bind escape key
        self.root.bind('<Escape>', lambda e: self.root.quit())

    def setup_ui(self):
        """Setup the loading page UI"""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=self.panel_bg, relief=tk.RAISED, bd=2)
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        title_label = tk.Label(
            header_frame,
            text="🖥️ CPU Scheduling Visualizer",
            font=('Arial', 28, 'bold'),
            bg=self.panel_bg,
            fg=self.fg_color,
            pady=20
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="by Group 3: Operating System",
            font=('Arial', 12),
            bg=self.panel_bg,
            fg='#E0E0E0'
        )
        subtitle_label.pack(pady=(0, 10))
        
        # Content area
        content_frame = tk.Frame(main_frame, bg=self.bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Loading animation
        left_frame = tk.Frame(content_frame, bg=self.bg_color)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        # CPU Animation
        self.animation_frame = tk.Frame(left_frame, bg=self.panel_bg, relief=tk.RAISED, bd=2)
        self.animation_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # CPU Loader
        self.cpu_canvas = tk.Canvas(
            self.animation_frame,
            bg=self.panel_bg,
            highlightthickness=0,
            height=200
        )
        self.cpu_canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Loading text
        self.loading_text = tk.Label(
            left_frame,
            text="Initializing System Components...",
            font=('Arial', 14, 'bold'),
            bg=self.bg_color,
            fg=self.fg_color
        )
        self.loading_text.pack(pady=10)
        
        # Progress bar
        self.progress_frame = tk.Frame(left_frame, bg=self.bg_color)
        self.progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            orient=tk.HORIZONTAL,
            length=400,
            mode='determinate'
        )
        self.progress_bar.pack(pady=5)
        
        self.progress_label = tk.Label(
            self.progress_frame,
            text="0%",
            font=('Arial', 11),
            bg=self.bg_color,
            fg=self.fg_color
        )
        self.progress_label.pack()
        
        # Right side - Information
        right_frame = tk.Frame(content_frame, bg=self.bg_color)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Team info
        team_frame = tk.LabelFrame(
            right_frame,
            text="👥 Project Team",
            font=('Arial', 14, 'bold'),
            bg=self.panel_bg,
            fg=self.fg_color,
            relief=tk.RAISED,
            bd=2
        )
        team_frame.pack(fill=tk.X, pady=(0, 20))
        
        team_members = [
            "SeanScript Development",
            "Group 3 Members",
            "Operating Systems Course"
        ]
        
        for member in team_members:
            member_label = tk.Label(
                team_frame,
                text=f"• {member}",
                font=('Arial', 11),
                bg=self.panel_bg,
                fg='#E0E0E0',
                anchor='w'
            )
            member_label.pack(fill=tk.X, padx=10, pady=5)
        
        # Features info
        features_frame = tk.LabelFrame(
            right_frame,
            text="🚀 Supported Algorithms",
            font=('Arial', 14, 'bold'),
            bg=self.panel_bg,
            fg=self.fg_color,
            relief=tk.RAISED,
            bd=2
        )
        features_frame.pack(fill=tk.BOTH, expand=True)
        
        algorithms = [
            ("📊 FCFS", "First Come First Serve"),
            ("⚡ SJF", "Shortest Job First"),
            ("🔄 Round Robin", "Time Quantum Based"),
            ("🎯 Priority", "Priority Based Scheduling")
        ]
        
        for algo, desc in algorithms:
            algo_frame = tk.Frame(features_frame, bg=self.panel_bg)
            algo_frame.pack(fill=tk.X, padx=10, pady=8)
            
            algo_label = tk.Label(
                algo_frame,
                text=algo,
                font=('Arial', 12, 'bold'),
                bg=self.panel_bg,
                fg=self.fg_color,
                anchor='w'
            )
            algo_label.pack(side=tk.LEFT)
            
            desc_label = tk.Label(
                algo_frame,
                text=desc,
                font=('Arial', 10),
                bg=self.panel_bg,
                fg='#B0B0B0',
                anchor='w'
            )
            desc_label.pack(side=tk.RIGHT)
        
        # Launch button (initially disabled)
        self.launch_btn = tk.Button(
            main_frame,
            text="Launching Visualizer...",
            font=('Arial', 16, 'bold'),
            bg='#6C757D',
            fg='white',
            relief=tk.FLAT,
            cursor='watch',
            state=tk.DISABLED,
            pady=15
        )
        self.launch_btn.pack(fill=tk.X, pady=20)

    def start_loading_animation(self):
        """Start the loading animation and progress"""
        # Start CPU animation
        self.animate_cpu()
        
        # Start progress simulation in a separate thread
        threading.Thread(target=self.simulate_loading, daemon=True).start()

    def animate_cpu(self):
        """Animate the CPU loader"""
        self.cpu_canvas.delete("all")
        
        width = self.cpu_canvas.winfo_width()
        height = self.cpu_canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            self.root.after(50, self.animate_cpu)
            return
        
        center_x = width // 2
        center_y = height // 2
        
        # Draw CPU chip
        chip_size = min(width, height) // 3
        self.cpu_canvas.create_rectangle(
            center_x - chip_size, center_y - chip_size,
            center_x + chip_size, center_y + chip_size,
            fill='#2D2D2D',
            outline='#0078D4',
            width=3
        )
        
        # Draw CPU core with pulsing effect
        core_size = chip_size // 2
        pulse = (time.time() * 2) % 1
        core_color = f'#{int(0x28 + pulse * 0xD7):02x}{int(0xA7 + pulse * 0x58):02x}{int(0x45 + pulse * 0xBA):02x}'
        
        self.cpu_canvas.create_rectangle(
            center_x - core_size, center_y - core_size,
            center_x + core_size, center_y + core_size,
            fill=core_color,
            outline='#FFFFFF',
            width=2
        )
        
        # Draw pins
        pin_length = chip_size // 8
        for i in range(8):
            angle = (i / 8) * 360
            rad = math.radians(angle)
            pin_x = center_x + (chip_size + 5) * math.cos(rad)
            pin_y = center_y + (chip_size + 5) * math.sin(rad)
            
            self.cpu_canvas.create_rectangle(
                pin_x - 2, pin_y - 2,
                pin_x + 2, pin_y + pin_length,
                fill='#28A745',
                outline=''
            )
        
        self.root.after(100, self.animate_cpu)

    def simulate_loading(self):
        """Simulate loading progress"""
        loading_steps = [
            (10, "Loading scheduling algorithms..."),
            (25, "Initializing process visualizer..."),
            (45, "Setting up Gantt chart components..."),
            (65, "Preparing performance metrics..."),
            (85, "Finalizing user interface..."),
            (100, "Ready to launch!")
        ]
        
        for progress, message in loading_steps:
            self.update_progress(progress, message)
            time.sleep(0.8)  # Simulate work being done
        
        # Enable launch button
        self.root.after(0, self.enable_launch)

    def update_progress(self, value, message):
        """Update progress bar and text"""
        def update():
            self.progress_bar['value'] = value
            self.progress_label.config(text=f"{value}%")
            self.loading_text.config(text=message)
        
        self.root.after(0, update)

    def enable_launch(self):
        """Enable the launch button"""
        self.launch_btn.config(
            text="🚀 LAUNCH VISUALIZER",
            bg=self.accent_green,
            cursor='hand2',
            state=tk.NORMAL,
            command=self.launch_main_app
        )
        
        # Add hover effect
        def on_enter(e):
            self.launch_btn.config(bg='#218838')
        
        def on_leave(e):
            self.launch_btn.config(bg=self.accent_green)
        
        self.launch_btn.bind("<Enter>", on_enter)
        self.launch_btn.bind("<Leave>", on_leave)

    def launch_main_app(self):
        """Launch the main CPU scheduler visualizer"""
        self.launch_btn.config(
            text="⏳ Launching...",
            bg='#FFC107',
            state=tk.DISABLED
        )
        
        # Close loading page and launch main app
        self.root.after(1000, self.execute_launch)

    def execute_launch(self):
        """Execute the main application launch"""
        try:
            # Close the loading window
            self.root.destroy()
            
            # Import main app class here to avoid circular import issues
            from cpu_scheduler_visualizer import SchedulerVisualizerApp
            
            # Create and launch the main application directly
            main_root = tk.Tk()
            main_app = SchedulerVisualizerApp(main_root)  # Your main app class
            main_root.mainloop()
            
        except Exception as e:
            # Show error and keep loading window open
            error_window = tk.Toplevel(self.root)
            error_window.title("Launch Error")
            error_window.geometry("400x200")
            error_window.configure(bg=self.bg_color)
            
            tk.Label(
                error_window,
                text="🚨 Launch Error",
                font=('Arial', 16, 'bold'),
                bg=self.bg_color,
                fg='#DC3545'
            ).pack(pady=20)
            
            tk.Label(
                error_window,
                text=f"Could not launch main application:\n{str(e)}",
                font=('Arial', 11),
                bg=self.bg_color,
                fg=self.fg_color,
                justify=tk.CENTER
            ).pack(pady=10)
            
            tk.Button(
                error_window,
                text="Close",
                command=error_window.destroy,
                font=('Arial', 12, 'bold'),
                bg=self.button_bg,
                fg='white',
                relief=tk.FLAT,
                pady=10
            ).pack(pady=20)

# Required import for math functions
import math

def main():
    """Main function to run the loading page"""
    root = tk.Tk()
    app = LoadingPage(root)
    root.mainloop()

if __name__ == "__main__":
    main()