import time
import os
from collections import deque

class Process:
    def __init__(self, pid, arrival, priority, burst, parent):
        self.pid = pid
        self.arrival = arrival
        self.priority = priority
        self.burst = burst
        self.remaining_burst = burst
        self.parent = parent
        self.status = "New"
        self.waiting_time = 0
        self.turnaround_time = 0
        self.start_time = None
        self.time_in_running = 0

class ProcessManager:
    def __init__(self, scheduling_algorithm="FCFS", time_quantum=2, process_file="processes.txt"):
        self.processes = []
        self.ready_queue = deque()
        self.running_process = None
        self.clock = 0
        self.completed_processes = []
        self.context_switches = 0
        self.scheduling_algorithm = scheduling_algorithm
        self.time_quantum = time_quantum
        self.execution_order = []
        self.algorithm_locked = False
        self.load_processes(process_file)

    def load_processes(self, process_file):
        if not os.path.exists(process_file):
            print(f"Error: {process_file} not found.")
            return
        
        with open(process_file, "r") as file:
            for line in file.readlines()[1:]:
                try:
                    pid, arrival, priority, burst, parent = map(int, line.split())
                    self.processes.append(Process(pid, arrival, priority, burst, parent))
                except ValueError:
                    continue
        self.processes.sort(key=lambda p: p.arrival)

    def add_new_process(self):
        pid = len(self.processes) + 1
        arrival = self.clock
        priority = int(input("Enter priority: "))
        burst = int(input("Enter burst time: "))
        parent = int(input("Enter parent process ID (0 if none): "))
        new_process = Process(pid, arrival, priority, burst, parent)
        self.processes.append(new_process)
        print(f"New process P{pid} added with status New.")

    def schedule_processes(self):
        if self.scheduling_algorithm == "FCFS":
            self.ready_queue = deque(sorted(self.ready_queue, key=lambda p: p.arrival))
        elif self.scheduling_algorithm == "SJF":
            self.ready_queue = deque(sorted(self.ready_queue, key=lambda p: p.remaining_burst))
        elif self.scheduling_algorithm == "Priority":
            self.ready_queue = deque(sorted(self.ready_queue, key=lambda p: p.priority))

    def terminate_process(self, process):
        process.status = "Terminated"
        process.turnaround_time = self.clock - process.arrival
        self.completed_processes.append(process)
        return True

    def run_cycle(self):
        self.clock += 1
        print(f"\nCycle {self.clock}:")

        for process in self.processes:
            if process.arrival == self.clock and process.status == "New":
                process.status = "Ready"
                if len(self.ready_queue) < 5:
                    self.ready_queue.append(process)
                print(f"P{process.pid} moved to Ready state.")

        if not self.running_process and self.ready_queue:
            self.running_process = self.ready_queue.popleft()
            self.running_process.status = "Running"
            if self.running_process.start_time is None:
                self.running_process.start_time = self.clock
            self.execution_order.append((self.running_process.pid, self.clock))
            self.algorithm_locked = True

        for process in self.processes:
            print(f"P{process.pid}: {process.status}, Remaining Burst: {process.remaining_burst}")

        if self.running_process:
            self.running_process.remaining_burst -= 1
            if self.running_process.remaining_burst == 0:
                if self.terminate_process(self.running_process):
                    print(f"P{self.running_process.pid} completed execution.")
                    self.running_process = None
                    self.context_switches += 1

        self.schedule_processes()

    def run_simulation(self):
        if not self.processes:
            print("No processes loaded. Simulation aborted.")
            return
        
        while len(self.completed_processes) < len(self.processes):
            user_input = input("Add a new process? (y/n): ").strip().lower()
            if user_input == 'y':
                self.add_new_process()
            elif user_input == 'n':
                self.run_cycle()
            else:
                print("Invalid input. Continuing execution...")
            time.sleep(0.1)

        total_waiting_time = sum(p.turnaround_time - p.burst for p in self.completed_processes)
        total_turnaround_time = sum(p.turnaround_time for p in self.completed_processes)
        print("\nPerformance Metrics:")
        print(f"Average Waiting Time: {total_waiting_time / len(self.completed_processes):.2f}")
        print(f"Average Turnaround Time: {total_turnaround_time / len(self.completed_processes):.2f}")
        print(f"Total Context Switches: {self.context_switches}")
        print("Execution Order:", " -> ".join(f"P{pid} [{cycle}]" for pid, cycle in self.execution_order))

if __name__ == "__main__":
    algorithm = input("Choose scheduling algorithm (FCFS, SJF, Priority, RR): ")
    manager = ProcessManager(scheduling_algorithm=algorithm)
    manager.run_simulation()

