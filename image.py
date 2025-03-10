import tkinter as tk
from tkinter import messagebox, ttk
import math
import threading
import time

class ElectronConfigurationApp:
    def __init__(self, master):
        self.master = master
        master.title("Electron Configuration")
        master.geometry("600x800")

        # Variables
        self.electron_count = tk.IntVar(value=1)
        self.confirmed_electron_count = 1
        self.electron_names = [''] * 28  # Initialize with empty strings
        self.is_electron_count_confirmed = False
        self.is_names_confirmed = False
        
        # Rotation tracking
        self.rotation_angles = [0] * 28  # Track rotation for up to 28 electrons
        self.stop_rotation = False
        self.electron_ids = []  # Store canvas IDs for electrons
        self.name_labels = []   # Store name labels

        # Create UI Components
        self.create_widgets()

    def create_widgets(self):
        # Main frame with scrollbar
        main_frame = tk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Canvas for scrolling
        self.canvas_frame = tk.Canvas(main_frame, yscrollcommand=scrollbar.set)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure scrollbar
        scrollbar.config(command=self.canvas_frame.yview)

        # Inner frame to hold content
        self.inner_frame = tk.Frame(self.canvas_frame)
        self.canvas_frame.create_window((0,0), window=self.inner_frame, anchor='nw')

        # Electron Count Input
        tk.Label(self.inner_frame, text="Number of Electrons:").pack(pady=(10,0))
        
        # Frame for electron count input
        count_frame = tk.Frame(self.inner_frame)
        count_frame.pack(pady=10)
        
        # Electron count entry
        self.electron_count_entry = tk.Entry(count_frame, textvariable=self.electron_count, width=10)
        self.electron_count_entry.pack(side=tk.LEFT, padx=5)
        
        # Confirm button
        confirm_count_btn = tk.Button(count_frame, text="Confirm", command=self.confirm_electron_count)
        confirm_count_btn.pack(side=tk.LEFT)

        # Canvas for atom visualization
        self.canvas = tk.Canvas(self.inner_frame, width=400, height=400, bg='white')
        self.canvas.pack(pady=20)

        # Frame for electron name inputs
        self.names_frame = tk.Frame(self.inner_frame)
        self.names_frame.pack(pady=10)

        # Confirmed names display
        self.names_display = tk.Text(self.inner_frame, height=10, width=50)
        self.names_display.pack(pady=10)

        # Update scrollregion
        self.inner_frame.update_idletasks()
        self.canvas_frame.config(scrollregion=self.canvas_frame.bbox("all"))
        
        # Bind configure event to update scrollregion when window resizes
        self.canvas_frame.bind('<Configure>', self.on_frame_configure)

    def on_frame_configure(self, event=None):
        # Update the scrollregion to encompass the inner frame
        self.canvas_frame.configure(scrollregion=self.canvas_frame.bbox("all"))

    def confirm_electron_count(self):
        try:
            count = self.electron_count.get()
            if 1 <= count <= 28:
                # Stop previous rotation thread if exists
                self.stop_rotation = True
                time.sleep(0.1)  # Give time for thread to stop
                
                self.confirmed_electron_count = count
                self.is_electron_count_confirmed = True
                self.is_names_confirmed = False
                
                # Reset rotation angles
                self.rotation_angles = [0] * 28
                
                # Clear previous name inputs
                for widget in self.names_frame.winfo_children():
                    widget.destroy()
                
                # Create name input fields
                self.electron_names = [''] * count
                self.create_name_inputs()
                
                # Draw atom with electrons
                self.draw_atom()
                
                # Start rotation thread
                self.stop_rotation = False
                rotation_thread = threading.Thread(target=self.rotate_electrons)
                rotation_thread.daemon = True
                rotation_thread.start()
                
                # Update scrollregion
                self.inner_frame.update_idletasks()
                self.canvas_frame.config(scrollregion=self.canvas_frame.bbox("all"))
            else:
                messagebox.showerror("Invalid Input", "Electron count must be between 1 and 28")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number")

    def create_name_inputs(self):
        # Create input fields for electron names
        for i in range(self.confirmed_electron_count):
            frame = tk.Frame(self.names_frame)
            frame.pack(pady=5)
            
            tk.Label(frame, text=f"Electron {i+1}:").pack(side=tk.LEFT, padx=(0,5))
            
            entry = tk.Entry(frame, width=20)
            entry.pack(side=tk.LEFT, padx=5)
            
            # Set initial value if available
            if i < len(self.electron_names) and self.electron_names[i]:
                entry.insert(0, self.electron_names[i])

        # Confirm names button
        confirm_names_btn = tk.Button(self.names_frame, text="Confirm Names", 
                                      command=self.confirm_electron_names)
        confirm_names_btn.pack(pady=10)

    def confirm_electron_names(self):
        # Collect names from entry fields
        entries = []
        for child in self.names_frame.winfo_children():
            if isinstance(child, tk.Frame):
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, tk.Entry):
                        entries.append(grandchild)
        
        # Get names from entries
        names = [entry.get().strip() for entry in entries]
        
        # Validate all names are filled
        if all(names) and len(names) == self.confirmed_electron_count:
            self.electron_names = names
            self.is_names_confirmed = True
            
            # Display confirmed names
            self.names_display.delete(1.0, tk.END)
            for i, name in enumerate(names):
                self.names_display.insert(tk.END, f"Electron {i+1}: {name}\n")
            
            # Update electron labels on visualization
            self.update_electron_labels()
        else:
            messagebox.showerror("Invalid Names", "Please fill in names for all electrons")

    def draw_atom(self):
        # Clear previous drawing
        self.canvas.delete("all")
        self.electron_ids = []
        self.name_labels = []
        
        # Atom center
        center_x, center_y = 200, 200
        nucleus_radius = 20
        
        # Draw nucleus
        self.canvas.create_oval(
            center_x - nucleus_radius, 
            center_y - nucleus_radius, 
            center_x + nucleus_radius, 
            center_y + nucleus_radius, 
            fill='red'
        )

        # Electron shell configurations
        shells = [
            {'radius': 80, 'max_electrons': 2},
            {'radius': 120, 'max_electrons': 8},
            {'radius': 160, 'max_electrons': 18}
        ]

        # Track total electrons drawn
        electrons_drawn = 0

        # Draw electron shells and electrons
        for shell_index, shell in enumerate(shells):
            # Draw shell circle
            self.canvas.create_oval(
                center_x - shell['radius'], 
                center_y - shell['radius'], 
                center_x + shell['radius'], 
                center_y + shell['radius'], 
                outline='gray'
            )

            # Calculate and draw electrons
            electrons_in_shell = min(self.confirmed_electron_count - electrons_drawn, shell['max_electrons'])
            
            for i in range(electrons_in_shell):
                # Break if all electrons are drawn
                if electrons_drawn >= self.confirmed_electron_count:
                    break

                angle = (2 * math.pi * i) / max(1, electrons_in_shell)  # Avoid division by zero
                electron_x = center_x + shell['radius'] * math.cos(angle)
                electron_y = center_y + shell['radius'] * math.sin(angle)
                
                # Create electron
                electron_id = self.canvas.create_oval(
                    electron_x - 10, electron_y - 10, 
                    electron_x + 10, electron_y + 10, 
                    fill='blue', tags=f'electron_{electrons_drawn}'
                )
                self.electron_ids.append(electron_id)
                
                # Create label for electron
                label_id = self.canvas.create_text(
                    electron_x, electron_y, 
                    text=str(electrons_drawn + 1),  # Default label is electron number
                    fill='white',
                    tags=f'label_{electrons_drawn}'
                )
                self.name_labels.append(label_id)
                
                # Increment electrons drawn
                electrons_drawn += 1
        
        # Update electron labels if names are confirmed
        if self.is_names_confirmed:
            self.update_electron_labels()

    def update_electron_labels(self):
        # Update electron labels with confirmed names
        if self.is_names_confirmed:
            for i in range(min(len(self.name_labels), len(self.electron_names))):
                # Get current coordinates of the electron
                coords = self.canvas.coords(f'electron_{i}')
                if coords:
                    electron_x = (coords[0] + coords[2]) / 2
                    electron_y = (coords[1] + coords[3]) / 2
                    
                    # Update label position and text
                    self.canvas.coords(self.name_labels[i], electron_x, electron_y)
                    self.canvas.itemconfig(self.name_labels[i], text=self.electron_names[i])

    def rotate_electrons(self):
        # Rotation thread
        center_x, center_y = 200, 200
        shells = [
            {'radius': 80, 'max_electrons': 2, 'speed': 0.05},
            {'radius': 120, 'max_electrons': 8, 'speed': 0.03},
            {'radius': 160, 'max_electrons': 18, 'speed': 0.02}
        ]

        try:
            while not self.stop_rotation:
                # Track total electrons drawn
                electrons_drawn = 0

                for shell_index, shell in enumerate(shells):
                    electrons_in_shell = min(self.confirmed_electron_count - electrons_drawn, shell['max_electrons'])
                    
                    for i in range(electrons_in_shell):
                        # Break if all electrons are drawn
                        if electrons_drawn >= self.confirmed_electron_count:
                            break

                        # Update rotation angle with different speeds per shell
                        self.rotation_angles[electrons_drawn] += shell['speed']
                        angle = (2 * math.pi * i) / max(1, electrons_in_shell) + self.rotation_angles[electrons_drawn]

                        electron_x = center_x + shell['radius'] * math.cos(angle)
                        electron_y = center_y + shell['radius'] * math.sin(angle)
                        
                        # Update electron position
                        try:
                            self.canvas.coords(
                                f'electron_{electrons_drawn}', 
                                electron_x - 10, electron_y - 10, 
                                electron_x + 10, electron_y + 10
                            )
                            
                            # Also update the label position
                            if electrons_drawn < len(self.name_labels):
                                self.canvas.coords(self.name_labels[electrons_drawn], electron_x, electron_y)
                        except tk.TclError:
                            # Stop if canvas is destroyed
                            return

                        # Increment electrons drawn
                        electrons_drawn += 1

                # Small delay to control rotation speed
                time.sleep(0.05)
                
                # Refresh canvas
                try:
                    self.canvas.update()
                except tk.TclError:
                    # Window was closed
                    return
        except Exception as e:
            print(f"Error in rotation thread: {e}")
            return

def main():
    root = tk.Tk()
    app = ElectronConfigurationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()