import tkinter as tk
from tkinter import ttk
import pyperclip
import pyautogui
import time
import threading
import random

# Disable pyautogui fail-safe (move mouse to corner to abort) – optional safety
pyautogui.FAILSAFE = True
# Small pause between pyautogui actions
pyautogui.PAUSE = 0.05

class CopyBoxApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CopyBox")
        
        # Make window always on top
        self.root.attributes('-topmost', True)
        
        # Remove window decorations for cleaner look
        self.root.overrideredirect(True)
        
        # We will adjust geometry dynamically
        self.current_x = 100
        self.current_y = 100
        self.base_width = 600
        self.min_width = 450
        self.root.geometry(f"{self.base_width}x110+{self.current_x}+{self.current_y}")
        
        # Make window background transparent for rounded corners effect
        self.root.configure(bg='#F0F0F0')
        
        # Distinct color palette for pins
        self.pin_colors = [
            '#FF3333',  # Red
            '#3388FF',  # Blue
            '#33CC33',  # Green
            '#FF9900',  # Orange
            '#AA33FF',  # Purple
            '#FF33AA',  # Pink
            '#00CCCC',  # Teal
            '#FFCC00',  # Yellow
            '#FF6633',  # Coral
            '#3399CC',  # Sky Blue
            '#CC6699',  # Rose
            '#66CC33',  # Lime
        ]
        self.color_index = 0
        
        # Create main rounded container
        self.main_frame = tk.Frame(
            root, 
            bg='white', 
            relief='solid', 
            borderwidth=1,
            highlightbackground='#D0D0D0',
            highlightthickness=1
        )
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Add rounded corners effect using padding
        self.rounded_frame = tk.Frame(
            self.main_frame, 
            bg='white',
            relief='flat'
        )
        self.rounded_frame.pack(fill='both', expand=True, padx=4, pady=4)
        
        # Header for dragging and buttons
        self.header_frame = tk.Frame(self.rounded_frame, bg='white')
        self.header_frame.pack(fill='x', padx=8, pady=(4, 0))
        
        # Drag handle / Title
        self.drag_label = tk.Label(
            self.header_frame, 
            text="≡ Drag me to move", 
            bg='white', 
            fg='#808080', 
            cursor='fleur', 
            font=('Arial', 9, 'bold')
        )
        self.drag_label.pack(side='left')
        
        # Bind dragging to header and label
        self.drag_label.bind('<Button-1>', self.start_move)
        self.drag_label.bind('<B1-Motion>', self.on_move)
        self.header_frame.bind('<Button-1>', self.start_move)
        self.header_frame.bind('<B1-Motion>', self.on_move)
        
        # Close Button
        self.close_btn = tk.Label(
            self.header_frame, 
            text="✕", 
            bg='white', 
            fg='#FF5555', 
            font=('Arial', 11, 'bold'), 
            cursor='hand2'
        )
        self.close_btn.pack(side='right', padx=(10, 0))
        self.close_btn.bind('<Button-1>', lambda e: self.root.destroy())
        self.close_btn.bind('<Enter>', lambda e: self.close_btn.config(fg='#FF0000'))
        self.close_btn.bind('<Leave>', lambda e: self.close_btn.config(fg='#FF5555'))
        
        # Add Button
        self.add_btn = tk.Label(
            self.header_frame, 
            text="＋ Add Box", 
            bg='white', 
            fg='#4CAF50', 
            font=('Arial', 10, 'bold'), 
            cursor='hand2'
        )
        self.add_btn.pack(side='right')
        self.add_btn.bind('<Button-1>', lambda e: self.add_box())
        self.add_btn.bind('<Enter>', lambda e: self.add_btn.config(fg='#45a049'))
        self.add_btn.bind('<Leave>', lambda e: self.add_btn.config(fg='#4CAF50'))

        # Container for copy boxes
        self.boxes_container = tk.Frame(self.rounded_frame, bg='white')
        self.boxes_container.pack(fill='both', expand=True, padx=8, pady=(8, 4))
        
        # Resize handle at bottom-right
        self.resize_frame = tk.Frame(self.rounded_frame, bg='white')
        self.resize_frame.pack(fill='x', side='bottom')
        
        self.resize_handle = tk.Label(
            self.resize_frame,
            text="⟋",
            bg='white',
            fg='#C0C0C0',
            font=('Arial', 10),
            cursor='size_nw_se'
        )
        self.resize_handle.pack(side='right', padx=(0, 2), pady=(0, 2))
        self.resize_handle.bind('<Button-1>', self.start_resize)
        self.resize_handle.bind('<B1-Motion>', self.on_resize)
        self.resize_handle.bind('<Enter>', lambda e: self.resize_handle.config(fg='#808080'))
        self.resize_handle.bind('<Leave>', lambda e: self.resize_handle.config(fg='#C0C0C0'))
        
        self.boxes = []  # list of (box_frame, pin_data) tuples
        self.add_box()
        
    def add_box(self):
        # Create search container for the row
        box_frame = tk.Frame(self.boxes_container, bg='white')
        box_frame.pack(fill='x', pady=(0, 8))
        
        # Assign a unique color to this box
        box_color = self.pin_colors[self.color_index % len(self.pin_colors)]
        self.color_index += 1
        
        # --- Per-box pin data ---
        pin_data = {
            'pinned': False,
            'target_x': None,
            'target_y': None,
            'pin_label': None,
            'entry': None,
            'coord_label': None,
            'color': box_color,
        }
        
        # Color indicator bar on the left
        color_bar = tk.Frame(box_frame, width=4, bg=box_color)
        color_bar.pack(side='left', fill='y', padx=(2, 0))
        
        # Pushpin icon (clickable to enter targeting mode)
        pushpin_label = tk.Label(
            box_frame, 
            text="📌", 
            bg='white', 
            fg=box_color,
            font=('Arial', 12),
            cursor='hand2'
        )
        pushpin_label.pack(side='left', padx=(5, 8))
        pin_data['pin_label'] = pushpin_label
        
        # Bind pin click to start targeting
        pushpin_label.bind('<Button-1>', lambda e, pd=pin_data: self.start_targeting(pd))
        
        # Separator line
        separator1 = tk.Frame(box_frame, width=1, bg='#E0E0E0')
        separator1.pack(side='left', fill='y', padx=(0, 8))
        
        # Search entry
        search_entry = tk.Entry(
            box_frame,
            bg='white',
            fg='#333333',
            relief='flat',
            font=('Arial', 11),
            width=15,
            bd=0,
            highlightthickness=0,
            insertbackground='#333333'
        )
        search_entry.pack(side='left', fill='x', expand=True, padx=5)
        search_entry.insert(0, "text here...")
        search_entry.config(fg='#999999')
        pin_data['entry'] = search_entry
        
        # Placeholder behavior
        def on_focus_in(event, entry=search_entry):
            if entry.get() == "text here...":
                entry.delete(0, 'end')
                entry.config(fg='#333333')
        
        def on_focus_out(event, entry=search_entry):
            if not entry.get():
                entry.insert(0, "text here...")
                entry.config(fg='#999999')
                
        search_entry.bind('<FocusIn>', on_focus_in)
        search_entry.bind('<FocusOut>', on_focus_out)
        
        # Separator line
        separator2 = tk.Frame(box_frame, width=1, bg='#E0E0E0')
        separator2.pack(side='left', fill='y', padx=(8, 0))
        
        # Clear button
        def clear_text(event, entry=search_entry):
            entry.delete(0, 'end')
            entry.focus()
            
        x_button = tk.Label(
            box_frame,
            text="✕",
            bg='white',
            fg='#808080',
            font=('Arial', 11),
            cursor='hand2',
            padx=5
        )
        x_button.pack(side='left', padx=(5, 5))
        x_button.bind('<Button-1>', clear_text)
        
        # --- Buttons container (to keep paste and copy together on the right) ---
        buttons_frame = tk.Frame(box_frame, bg='white')
        buttons_frame.pack(side='right', padx=(3, 0))
        
        # --- Paste button ---
        paste_button_frame = tk.Frame(
            buttons_frame,
            bg='#2196F3',
            relief='flat',
            padx=8,
            pady=4
        )
        paste_button_frame.pack(side='left', padx=(0, 3))
        
        paste_button = tk.Label(
            paste_button_frame,
            text="paste",
            bg='#2196F3',
            fg='white',
            font=('Arial', 9, 'bold'),
            cursor='hand2'
        )
        paste_button.pack()
        
        # --- Copy button ---
        copy_button_frame = tk.Frame(
            buttons_frame,
            bg='#4CAF50',
            relief='flat',
            padx=8,
            pady=4
        )
        copy_button_frame.pack(side='left')
        
        copy_button = tk.Label(
            copy_button_frame,
            text="copy",
            bg='#4CAF50',
            fg='white',
            font=('Arial', 9, 'bold'),
            cursor='hand2'
        )
        copy_button.pack()
        
        def copy_text(event, entry=search_entry, btn=copy_button, frm=copy_button_frame):
            text = entry.get()
            if text and text != "text here...":
                pyperclip.copy(text)
                btn.config(text='copied!')
                frm.config(bg='#2196F3')
                btn.config(bg='#2196F3')
                self.root.after(1000, lambda: reset_copy_btn(btn, frm))
                
        def reset_copy_btn(btn, frm):
            try:
                btn.config(text='copy')
                frm.config(bg='#4CAF50')
                btn.config(bg='#4CAF50')
            except tk.TclError:
                pass
                
        copy_button.bind('<Button-1>', copy_text)
        
        def paste_text(event, entry=search_entry, pd=pin_data, btn=paste_button, frm=paste_button_frame):
            text = entry.get()
            if text and text != "text here..." and pd['pinned'] and pd['target_x'] is not None:
                # Visual feedback
                btn.config(text='pasting...')
                frm.config(bg='#FF9800')
                btn.config(bg='#FF9800')
                self.root.update()
                
                # Run paste in a thread so the UI doesn't freeze
                def do_paste():
                    tx, ty = pd['target_x'], pd['target_y']
                    
                    # Hide the floating pin and CopyBox so the click lands on the real app
                    float_win = pd.get('float_win')
                    if float_win and float_win.winfo_exists():
                        self.root.after(0, float_win.withdraw)
                    self.root.after(0, self.root.withdraw)
                    time.sleep(0.3)  # wait for windows to hide
                    
                    # Click at the pinned location to focus it
                    pyautogui.click(tx, ty)
                    time.sleep(0.15)
                    
                    # Paste the text using clipboard
                    pyperclip.copy(text)
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(0.15)
                    
                    # Show CopyBox and floating pin again
                    self.root.after(0, self.root.deiconify)
                    if float_win and float_win.winfo_exists():
                        self.root.after(50, float_win.deiconify)
                    
                    # Reset button in main thread
                    self.root.after(500, lambda: reset_paste_btn(btn, frm))
                    
                threading.Thread(target=do_paste, daemon=True).start()
            elif not pd['pinned']:
                # Flash the pin to indicate user needs to set a target first
                pin_lbl = pd['pin_label']
                pin_lbl.config(fg='#FF0000')
                self.root.after(300, lambda: pin_lbl.config(fg='#FF0000'))
                self.root.after(600, lambda: pin_lbl.config(fg='#808080'))
                self.root.after(900, lambda: pin_lbl.config(fg='#FF0000'))
                self.root.after(1200, lambda: pin_lbl.config(fg='#808080'))
        
        def reset_paste_btn(btn, frm):
            try:
                btn.config(text='paste')
                frm.config(bg='#2196F3')
                btn.config(bg='#2196F3')
            except tk.TclError:
                pass
                
        paste_button.bind('<Button-1>', paste_text)
        
        # --- Small coordinate label under the pin (shows where it's pinned) ---
        coord_label = tk.Label(
            box_frame,
            text="",
            bg='white',
            fg='#AAAAAA',
            font=('Arial', 7)
        )
        # Don't pack yet – will show after pin is set
        pin_data['coord_label'] = coord_label
        
        # Remove box button (only if more than 1 box)
        if len(self.boxes) > 0:
            del_button = tk.Label(
                box_frame,
                text="−",
                bg='white',
                fg='#FF5555',
                font=('Arial', 14, 'bold'),
                cursor='hand2'
            )
            del_button.pack(side='right', padx=(0, 5))
            def del_box(event, b_frame=box_frame, pd=pin_data):
                # Destroy floating pin if it exists
                if pd.get('float_win'):
                    try:
                        pd['float_win'].destroy()
                    except:
                        pass
                b_frame.destroy()
                self.boxes = [(bf, p) for bf, p in self.boxes if bf != b_frame]
                self.update_geometry()
            del_button.bind('<Button-1>', del_box)
            
        self.boxes.append((box_frame, pin_data))
        self.update_geometry()
    
    # =============================================
    #  FLOATING DRAGGABLE PIN
    # =============================================
    def start_targeting(self, pin_data):
        """Toggle floating pin: create a draggable pin window or remove existing one."""
        # If this pin already has a floating window, destroy it (toggle off)
        if pin_data.get('float_win') and pin_data['float_win'].winfo_exists():
            pin_data['float_win'].destroy()
            pin_data['float_win'] = None
            pin_data['pinned'] = False
            pin_data['target_x'] = None
            pin_data['target_y'] = None
            pin_data['pin_label'].config(fg=pin_data['color'])
            # Hide coordinate label
            pin_data['coord_label'].pack_forget()
            return
        
        # Get this box's color
        color = pin_data['color']
        # Darken color for outline
        def darken(hex_color):
            r = max(0, int(hex_color[1:3], 16) - 40)
            g = max(0, int(hex_color[3:5], 16) - 40)
            b = max(0, int(hex_color[5:7], 16) - 40)
            return f'#{r:02x}{g:02x}{b:02x}'
        dark_color = darken(color)
        
        # Turn pin to its color
        pin_data['pin_label'].config(fg=color)
        
        # Create a small floating pin window
        float_win = tk.Toplevel(self.root)
        float_win.overrideredirect(True)
        float_win.attributes('-topmost', True)
        float_win.attributes('-alpha', 0.9)
        float_win.configure(bg='')
        
        # Make the window transparent (Windows)
        float_win.wm_attributes('-transparentcolor', '#F0F0F0')
        
        # Window size: pin on top, pointer line, red dot at bottom
        win_w = 50
        win_h = 70
        
        # Position it near the center of the screen initially
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        init_x = screen_w // 2 - win_w // 2
        init_y = screen_h // 2 - win_h // 2
        float_win.geometry(f"{win_w}x{win_h}+{init_x}+{init_y}")
        
        # Use a Canvas to draw the pin + pointer line + target dot
        canvas = tk.Canvas(
            float_win,
            width=win_w,
            height=win_h,
            bg='#F0F0F0',
            highlightthickness=0,
            cursor='fleur'
        )
        canvas.pack(fill='both', expand=True)
        
        # Draw the pin emoji at the top-center
        canvas.create_text(win_w // 2, 15, text="📌", font=('Arial', 16), fill=color)
        
        # Draw a thin colored line from pin down to the target dot
        canvas.create_line(win_w // 2, 28, win_w // 2, win_h - 8, fill=color, width=2, dash=(3, 2))
        
        # Draw the target dot (●) at the bottom-center — THIS is the exact paste point
        canvas.create_oval(
            win_w // 2 - 6, win_h - 12,
            win_w // 2 + 6, win_h,
            fill=color, outline=dark_color, width=2
        )
        
        # Draw a tiny crosshair at the exact center of the dot
        dot_cx = win_w // 2
        dot_cy = win_h - 6
        canvas.create_line(dot_cx - 4, dot_cy, dot_cx + 4, dot_cy, fill='white', width=1)
        canvas.create_line(dot_cx, dot_cy - 4, dot_cx, dot_cy + 4, fill='white', width=1)
        
        # Draw the box number label
        box_num = self.color_index
        canvas.create_text(win_w // 2, 38, text=f"#{box_num}", font=('Arial', 8, 'bold'), fill=color)
        
        # Store reference
        pin_data['float_win'] = float_win
        
        # The target point is the BOTTOM-CENTER of the window (where the red dot is)
        pin_data['pinned'] = True
        pin_data['target_x'] = init_x + win_w // 2
        pin_data['target_y'] = init_y + win_h - 5  # center of the red dot
        
        # Show coordinates
        coord_lbl = pin_data['coord_label']
        coord_lbl.config(text=f"({pin_data['target_x']},{pin_data['target_y']})", fg=color)
        try:
            coord_lbl.pack(side='left', before=pin_data['entry'])
        except tk.TclError:
            pass
        
        # --- Drag logic for the floating pin ---
        drag_data = {'x': 0, 'y': 0}
        
        def on_press(event):
            drag_data['x'] = event.x_root - float_win.winfo_x()
            drag_data['y'] = event.y_root - float_win.winfo_y()
        
        def on_drag(event):
            new_x = event.x_root - drag_data['x']
            new_y = event.y_root - drag_data['y']
            float_win.geometry(f"+{new_x}+{new_y}")
            # Target = bottom-center of window (the red dot)
            pin_data['target_x'] = new_x + win_w // 2
            pin_data['target_y'] = new_y + win_h - 5
            coord_lbl.config(text=f"({pin_data['target_x']},{pin_data['target_y']})")
        
        canvas.bind('<Button-1>', on_press)
        canvas.bind('<B1-Motion>', on_drag)
        
        # Right-click to close the floating pin
        def on_right_click(event):
            float_win.destroy()
            pin_data['float_win'] = None
            pin_data['pinned'] = False
            pin_data['target_x'] = None
            pin_data['target_y'] = None
            pin_data['pin_label'].config(fg=color)
            pin_data['coord_label'].pack_forget()
        
        canvas.bind('<Button-3>', on_right_click)
        
    def update_geometry(self):
        num_boxes = len(self.boxes)
        needed_height = 80 + (num_boxes * 42)
        # Cap at 80% of screen height
        max_height = int(self.root.winfo_screenheight() * 0.8)
        if needed_height > max_height:
            needed_height = max_height
        self.root.geometry(f"{self.base_width}x{needed_height}")
        
    def start_move(self, event):
        self.start_x = event.x_root - self.root.winfo_x()
        self.start_y = event.y_root - self.root.winfo_y()
    
    def on_move(self, event):
        x = event.x_root - self.start_x
        y = event.y_root - self.start_y
        self.root.geometry(f"+{x}+{y}")
    
    def start_resize(self, event):
        self.resize_start_x = event.x_root
        self.resize_start_w = self.root.winfo_width()
    
    def on_resize(self, event):
        dx = event.x_root - self.resize_start_x
        new_width = max(self.min_width, self.resize_start_w + dx)
        self.base_width = new_width
        self.update_geometry()

if __name__ == "__main__":
    root = tk.Tk()
    app = CopyBoxApp(root)
    root.mainloop()
