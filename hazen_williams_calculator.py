

import math
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText

class HazenWilliamsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hazen-Williams Formula Solver")
        self.root.geometry("750x600")

        # Set up the main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="Hazen-Williams Formula Solver",
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10, sticky=tk.W)

        # Unit system selection
        unit_frame = ttk.LabelFrame(main_frame, text="Unit System", padding="10")
        unit_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W+tk.E, pady=10)

        self.unit_var = tk.IntVar(value=1)
        us_radio = ttk.Radiobutton(unit_frame, text="U.S. Customary (feet, inches, cfs)",
                                  variable=self.unit_var, value=1, command=self.update_units)
        si_radio = ttk.Radiobutton(unit_frame, text="SI (meters, millimeters, m³/s)",
                                  variable=self.unit_var, value=2, command=self.update_units)

        us_radio.grid(row=0, column=0, sticky=tk.W, padx=10)
        si_radio.grid(row=0, column=1, sticky=tk.W, padx=10)

        # What to solve for
        solve_frame = ttk.LabelFrame(main_frame, text="Solve For", padding="10")
        solve_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W+tk.E, pady=10)

        self.solve_var = tk.IntVar(value=1)
        velocity_radio = ttk.Radiobutton(solve_frame, text="Velocity (V)",
                                       variable=self.solve_var, value=1, command=self.update_inputs)
        flow_radio = ttk.Radiobutton(solve_frame, text="Flow Rate (Q)",
                                    variable=self.solve_var, value=2, command=self.update_inputs)
        head_radio = ttk.Radiobutton(solve_frame, text="Head Loss (hf)",
                                    variable=self.solve_var, value=3, command=self.update_inputs)
        diameter_radio = ttk.Radiobutton(solve_frame, text="Pipe Diameter (D)",
                                       variable=self.solve_var, value=4, command=self.update_inputs)

        velocity_radio.grid(row=0, column=0, sticky=tk.W, padx=10)
        flow_radio.grid(row=0, column=1, sticky=tk.W, padx=10)
        head_radio.grid(row=1, column=0, sticky=tk.W, padx=10)
        diameter_radio.grid(row=1, column=1, sticky=tk.W, padx=10)

        # Input frame
        self.input_frame = ttk.LabelFrame(main_frame, text="Input Parameters", padding="10")
        self.input_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W+tk.E, pady=10)

        # Common input: C value
        ttk.Label(self.input_frame, text="Hazen-Williams Coefficient (C):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.c_var = tk.StringVar(value="120")
        ttk.Entry(self.input_frame, textvariable=self.c_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        # Other inputs will be added dynamically
        self.velocity_var = tk.StringVar()
        self.flow_var = tk.StringVar()
        self.head_var = tk.StringVar()
        self.diameter_var = tk.StringVar()
        self.vq_var = tk.StringVar(value="V")

        # Create radio buttons for velocity/flow choice (hidden initially)
        self.vq_frame = ttk.Frame(self.input_frame)
        self.vq_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        v_radio = ttk.Radiobutton(self.vq_frame, text="Use Velocity", variable=self.vq_var, value="V", command=self.update_vq_choice)
        q_radio = ttk.Radiobutton(self.vq_frame, text="Use Flow Rate", variable=self.vq_var, value="Q", command=self.update_vq_choice)
        v_radio.grid(row=0, column=0, padx=5)
        q_radio.grid(row=0, column=1, padx=5)

        # Solve button
        solve_button = ttk.Button(main_frame, text="Solve", command=self.solve)
        solve_button.grid(row=4, column=0, pady=10)

        # Clear button
        clear_button = ttk.Button(main_frame, text="Clear", command=self.clear)
        clear_button.grid(row=4, column=1, pady=10)

        # Results area
        result_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        result_frame.grid(row=5, column=0, columnspan=3, sticky=tk.W+tk.E+tk.N+tk.S, pady=10)
        result_frame.grid_columnconfigure(0, weight=1)
        result_frame.grid_rowconfigure(0, weight=1)

        self.result_text = ScrolledText(result_frame, height=10, width=70, wrap=tk.WORD)
        self.result_text.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)

        # Set up the initial state
        self.update_units()
        self.update_inputs()

    def update_units(self):
        # Update unit labels based on selection
        if self.unit_var.get() == 1:  # U.S. Customary
            self.unit_v = "ft/s"
            self.unit_d = "inches"
            self.unit_q = "cfs"
            self.unit_hf = "ft/1000ft"
            self.d_convert = 12.0  # convert ft to in
            self.k = 1.318  # for fps units
        else:  # SI
            self.unit_v = "m/s"
            self.unit_d = "mm"
            self.unit_q = "m³/s"
            self.unit_hf = "m/100m"
            self.d_convert = 1000.0  # convert m to mm
            self.k = 0.849  # for m/s units

        # Refresh input labels
        self.update_inputs()

    def update_vq_choice(self):
        # Update which input is shown based on V/Q choice
        solve_for = self.solve_var.get()

        # Show/hide velocity or flow rate entry based on selection
        for widget in self.input_frame.grid_slaves():
            if widget.grid_info()['row'] == 4:
                widget.grid_forget()

        if self.vq_var.get() == "V":
            ttk.Label(self.input_frame, text=f"Velocity ({self.unit_v}):").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
            ttk.Entry(self.input_frame, textvariable=self.velocity_var, width=10).grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        else:
            ttk.Label(self.input_frame, text=f"Flow Rate ({self.unit_q}):").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
            ttk.Entry(self.input_frame, textvariable=self.flow_var, width=10).grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)

    def update_inputs(self):
        # Clear existing input widgets (except C value)
        for widget in self.input_frame.grid_slaves():
            if widget.grid_info()['row'] > 0 and widget != self.vq_frame:
                widget.grid_forget()

        # Hide V/Q choice frame initially
        self.vq_frame.grid_forget()

        solve_for = self.solve_var.get()

        if solve_for == 1:  # Solve for velocity
            # Need diameter and head loss
            ttk.Label(self.input_frame, text=f"Pipe Diameter ({self.unit_d}):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
            ttk.Entry(self.input_frame, textvariable=self.diameter_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

            ttk.Label(self.input_frame, text=f"Head Loss ({self.unit_hf}):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
            ttk.Entry(self.input_frame, textvariable=self.head_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        elif solve_for == 2:  # Solve for flow rate
            # Need diameter and head loss
            ttk.Label(self.input_frame, text=f"Pipe Diameter ({self.unit_d}):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
            ttk.Entry(self.input_frame, textvariable=self.diameter_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

            ttk.Label(self.input_frame, text=f"Head Loss ({self.unit_hf}):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
            ttk.Entry(self.input_frame, textvariable=self.head_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        elif solve_for == 3:  # Solve for head loss
            # Need diameter and either velocity or flow rate
            ttk.Label(self.input_frame, text=f"Pipe Diameter ({self.unit_d}):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
            ttk.Entry(self.input_frame, textvariable=self.diameter_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

            # Show V/Q choice
            self.vq_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
            self.update_vq_choice()

        elif solve_for == 4:  # Solve for diameter
            # Need head loss and either velocity or flow rate
            ttk.Label(self.input_frame, text=f"Head Loss ({self.unit_hf}):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
            ttk.Entry(self.input_frame, textvariable=self.head_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

            # Show V/Q choice
            self.vq_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
            self.update_vq_choice()

    def solve(self):
        try:
            # Get unit system parameters
            unit_choice = self.unit_var.get()
            solve_for = self.solve_var.get()

            # Get C value
            try:
                C = float(self.c_var.get())
                if C <= 0:
                    raise ValueError("C must be positive")
            except ValueError:
                messagebox.showerror("Input Error", "Please enter a valid positive number for C")
                return

            # Clear results
            self.result_text.delete(1.0, tk.END)

            # Solve based on what we're looking for
            if solve_for == 1:  # Solve for velocity
                try:
                    D = float(self.diameter_var.get()) / self.d_convert  # Convert to ft or m
                    hf = float(self.head_var.get())

                    if D <= 0 or hf <= 0:
                        raise ValueError("Values must be positive")

                except ValueError:
                    messagebox.showerror("Input Error", "Please enter valid positive numbers")
                    return

                # Convert head loss to slope
                if unit_choice == 1:
                    S = hf / 1000  # ft/ft
                else:
                    S = hf / 100   # m/m

                R = D / 4
                V = self.k * C * R**0.63 * S**0.54

                # Calculate flow rate
                A = math.pi * (D**2) / 4  # Area in ft² or m²
                Q = V * A

                # Display results
                self.result_text.insert(tk.END, f"Velocity (V) = {V:.4f} {self.unit_v}\n")
                self.result_text.insert(tk.END, f"Flow rate (Q) = {Q:.6f} {self.unit_q}\n")

            elif solve_for == 2:  # Solve for flow rate
                try:
                    D = float(self.diameter_var.get()) / self.d_convert  # Convert to ft or m
                    hf = float(self.head_var.get())

                    if D <= 0 or hf <= 0:
                        raise ValueError("Values must be positive")

                except ValueError:
                    messagebox.showerror("Input Error", "Please enter valid positive numbers")
                    return

                if unit_choice == 1:
                    S = hf / 1000  # ft/ft
                else:
                    S = hf / 100   # m/m

                R = D / 4
                V = self.k * C * R**0.63 * S**0.54
                A = math.pi * (D**2) / 4
                Q = V * A

                self.result_text.insert(tk.END, f"Flow rate (Q) = {Q:.6f} {self.unit_q}\n")
                self.result_text.insert(tk.END, f"Velocity (V) = {V:.4f} {self.unit_v}\n")

            elif solve_for == 3:  # Solve for head loss
                try:
                    D = float(self.diameter_var.get()) / self.d_convert  # Convert to ft or m

                    if D <= 0:
                        raise ValueError("Diameter must be positive")

                except ValueError:
                    messagebox.showerror("Input Error", "Please enter a valid positive number for diameter")
                    return

                # Get either velocity or flow rate
                vq_choice = self.vq_var.get()

                if vq_choice == 'V':
                    try:
                        V = float(self.velocity_var.get())
                        if V <= 0:
                            raise ValueError("Velocity must be positive")
                    except ValueError:
                        messagebox.showerror("Input Error", "Please enter a valid positive number for velocity")
                        return

                    A = math.pi * (D**2) / 4
                    Q = V * A
                else:
                    try:
                        Q = float(self.flow_var.get())
                        if Q <= 0:
                            raise ValueError("Flow rate must be positive")
                    except ValueError:
                        messagebox.showerror("Input Error", "Please enter a valid positive number for flow rate")
                        return

                    A = math.pi * (D**2) / 4
                    V = Q / A

                R = D / 4
                # Manual calculation for solving S
                S = (V / (self.k * C * R**0.63))**(1/0.54)

                if unit_choice == 1:
                    hf = S * 1000  # Convert to ft/1000ft
                else:
                    hf = S * 100   # Convert to m/100m

                self.result_text.insert(tk.END, f"Head loss per length (hf) = {hf:.4f} {self.unit_hf}\n")
                if vq_choice == 'Q':
                    self.result_text.insert(tk.END, f"Velocity (V) = {V:.4f} {self.unit_v}\n")
                else:
                    self.result_text.insert(tk.END, f"Flow rate (Q) = {Q:.6f} {self.unit_q}\n")

            elif solve_for == 4:  # Solve for diameter
                try:
                    hf = float(self.head_var.get())

                    if hf <= 0:
                        raise ValueError("Head loss must be positive")

                except ValueError:
                    messagebox.showerror("Input Error", "Please enter a valid positive number for head loss")
                    return

                # Get either velocity or flow rate
                vq_choice = self.vq_var.get()

                if unit_choice == 1:
                    S = hf / 1000  # ft/ft
                else:
                    S = hf / 100   # m/m

                if vq_choice == 'V':
                    try:
                        V = float(self.velocity_var.get())
                        if V <= 0:
                            raise ValueError("Velocity must be positive")
                    except ValueError:
                        messagebox.showerror("Input Error", "Please enter a valid positive number for velocity")
                        return

                    # Using trial and error rather than scipy.optimize
                    # Start with a small diameter and increase until we match the velocity
                    D = 0.01  # Initial guess (in ft or m)
                    step = 0.01
                    max_iterations = 1000
                    iterations = 0

                    while iterations < max_iterations:
                        R = D / 4
                        V_calc = self.k * C * R**0.63 * S**0.54

                        if abs(V_calc - V) < 0.0001:
                            break

                        if V_calc < V:
                            D += step
                        else:
                            D -= step
                            step /= 2
                            D += step

                        iterations += 1

                    A = math.pi * (D**2) / 4
                    Q = V * A

                else:  # Using flow rate (Q)
                    try:
                        Q = float(self.flow_var.get())
                        if Q <= 0:
                            raise ValueError("Flow rate must be positive")
                    except ValueError:
                        messagebox.showerror("Input Error", "Please enter a valid positive number for flow rate")
                        return

                    # For Q, we can use a similar approach
                    D = 0.01  # Initial guess (in ft or m)
                    step = 0.01
                    max_iterations = 1000
                    iterations = 0

                    while iterations < max_iterations:
                        R = D / 4
                        V_calc = self.k * C * R**0.63 * S**0.54
                        A = math.pi * (D**2) / 4
                        Q_calc = V_calc * A

                        if abs(Q_calc - Q) < 0.0001:
                            break

                        if Q_calc < Q:
                            D += step
                        else:
                            D -= step
                            step /= 2
                            D += step

                        iterations += 1

                    A = math.pi * (D**2) / 4
                    V = Q / A

                # Convert back to inches or mm for display
                D_display = D * self.d_convert

                self.result_text.insert(tk.END, f"Pipe diameter (D) = {D_display:.4f} {self.unit_d}\n")
                if vq_choice == 'V':
                    self.result_text.insert(tk.END, f"Flow rate (Q) = {Q:.6f} {self.unit_q}\n")
                else:
                    self.result_text.insert(tk.END, f"Velocity (V) = {V:.4f} {self.unit_v}\n")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def clear(self):
        # Reset input fields
        self.c_var.set("120")
        self.velocity_var.set("")
        self.flow_var.set("")
        self.head_var.set("")
        self.diameter_var.set("")

        # Clear results
        self.result_text.delete(1.0, tk.END)

def main():
    root = tk.Tk()
    app = HazenWilliamsGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main();
