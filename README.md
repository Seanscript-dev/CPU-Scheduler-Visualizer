# CPU-Scheduler-Visualizer
A sophisticated desktop application that visually demonstrates various CPU scheduling algorithms used in operating systems. Built with Python and Tkinter, it provides an interactive educational tool for understanding process scheduling concepts.
CPU Scheduling Algorithms Visualizer - Complete Description
🎯 Project Overview
A sophisticated desktop application that visually demonstrates various CPU scheduling algorithms used in operating systems. Built with Python and Tkinter, it provides an interactive educational tool for understanding process scheduling concepts.

🏗️ Architecture & Components
1. Loading Page (LoadingPage Class)
Purpose: Professional splash screen that loads before the main application

Key Features:

Animated CPU Visualization: Real-time pulsing CPU core animation with rotating pins

Progress Simulation: Simulated loading steps with progress bar

Team Information: Displays project team and supported algorithms

Smooth Transition: Seamlessly launches the main application after loading

Technical Implementation:

Uses threading for non-blocking loading animation

Mathematical calculations for smooth CPU animation effects

Dynamic color schemes matching the main application

2. Process Management (Process Class)
Purpose: Represents individual processes in the scheduling system

Attributes:

pid: Process identifier (P1, P2, etc.)

arrival_time: Time when process arrives in ready queue

burst_time: CPU time required for completion

priority: Process priority level (for priority scheduling)

remaining_time: Tracks remaining execution time (for preemptive algorithms)

Timing metrics: start_time, finish_time, turnaround_time, waiting_time

color: Unique color for visual identification

3. Scheduling Algorithms (SchedulingAlgorithm Class)
Purpose: Implements all CPU scheduling algorithms with both logic and visualization data

Supported Algorithms:

FCFS (First-Come-First-Serve)
Type: Non-preemptive

Logic: Processes executed in order of arrival

Use Case: Simple batch systems

SJF (Shortest Job First)
Non-preemptive: Selects shortest job from ready queue

Preemptive (SRTF): Always executes process with shortest remaining time

Use Case: Optimal for minimizing waiting time

Round Robin
Type: Preemptive

Logic: Cyclic execution with fixed time quantum

Features: Configurable time quantum

Use Case: Time-sharing systems

Priority Scheduling
Non-preemptive: Executes highest priority process to completion

Preemptive: Can interrupt lower priority processes

Logic: Lower number = higher priority

Use Case: Real-time systems

4. Main Application (SchedulerVisualizerApp Class)
Purpose: Comprehensive GUI for algorithm visualization and analysis

🎨 User Interface Components
Left Panel - Process Input
Dynamic Input Fields: Automatically generates input fields based on process count

Algorithm-Aware Inputs: Shows/hides priority inputs based on selected algorithm

Quick Actions:

Random Data Generation

Clear All Inputs

Export Results

Algorithm Explanations

Center Panel - Gantt Chart Visualization
Real-time Animation: Step-by-step execution visualization

Configurable Speed: Adjustable animation timing

Color-coded Processes: Each process has unique color

Time Scale: Automatic scaling for different simulation durations

Right Panel - Results Table
Comprehensive Metrics: Displays all process timing information

Sortable Columns: PID, Arrival Time, Burst Time, Priority, Finish Time, Turnaround Time, Waiting Time

Export Functionality: Save results to CSV format

Bottom Panel - Analytics
Performance Metrics:

Average Turnaround Time

Average Waiting Time

Throughput (processes/time unit)

Comparative Charts: Bar charts for waiting times and turnaround times

Restart Controls: Quick simulation reset

🔧 Technical Features
Input Validation
Data Type Checking: Ensures numeric inputs

Range Validation: Non-negative times, positive burst times

Error Handling: User-friendly error messages

Animation System
Smooth Transitions: Configurable animation speed (10-500ms)

Non-blocking Execution: Uses after() method for smooth UI

Visual Feedback: Real-time status updates

Data Persistence
CSV Export: Comprehensive results with timestamps

Chart Generation: Matplotlib integration for data visualization

Session Management: Easy simulation restart

Visual Design
Dark Theme: Professional dark color scheme

Responsive Layout: Adapts to different screen sizes

Consistent Styling: Unified color palette and typography

Interactive Elements: Hover effects and visual feedback

🚀 Key Algorithms Implementation
Algorithm Selection Logic
python
if algorithm == "FCFS":
    result_processes, timeline = SchedulingAlgorithm.fcfs(processes)
elif algorithm == "SJF (Non-preemptive)":
    result_processes, timeline = SchedulingAlgorithm.sjf_non_preemptive(processes)
# ... etc.
Timeline Generation
Each algorithm returns:

result_processes: List of processes with calculated timing metrics

timeline: List of execution blocks for Gantt chart visualization

Metrics Calculation
Turnaround Time: Finish Time - Arrival Time

Waiting Time: Turnaround Time - Burst Time

Throughput: Total Processes / Total Simulation Time

📊 Educational Value
Learning Objectives
Understand Algorithm Behavior: Visual comparison of different scheduling approaches

Analyze Performance: Quantitative metrics for algorithm evaluation

Process Timing Concepts: Grasp turnaround time, waiting time, and throughput

Preemptive vs Non-preemptive: Visual distinction between scheduling types

Use Cases
Computer Science Education: Operating systems courses

Algorithm Analysis: Performance comparison studies

Professional Training: System administrator education

Research Tool: Algorithm behavior analysis

🔄 Workflow
Configuration: Select algorithm and set process parameters

Input: Define process arrival times, burst times, and priorities

Simulation: Run algorithm with animated visualization

Analysis: Review performance metrics and charts

Export: Save results for further analysis

💻 Technical Stack
GUI Framework: Tkinter

Visualization: Matplotlib for charts, Canvas for Gantt chart

Data Handling: CSV for export/import

Architecture: Object-oriented design with separation of concerns

🌟 Unique Features
Professional Loading Screen: Enhanced user experience

Comprehensive Algorithm Coverage: 6 different scheduling strategies

Real-time Animation: Visual execution flow

Educational Explanations: Step-by-step algorithm walkthroughs

Export Capabilities: Data persistence and sharing

Responsive Design: Adapts to user preferences and screen sizes

This application serves as both an educational tool for understanding CPU scheduling concepts and a practical demonstration of Python GUI development with complex algorithm implementations.
