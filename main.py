import tkinter as tk
from tkinter import ttk
import pyperclip
import pyautogui
import time
import threading
import random
import os
import re
from pynput import mouse, keyboard

try:
    import pytesseract
    from PIL import Image, ImageTk
    # Setting the path for Tesseract engine
    tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    if os.path.exists(tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
except ImportError:
    pytesseract = None
    from PIL import Image
    try:
        from PIL import ImageTk
    except:
        pass

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
        self.base_width = 750
        self.min_width = 650
        
        # Initialize attributes for dragging and resizing to satisfy linter
        self.start_x = 0
        self.start_y = 0
        self.start_root_x = 0
        self.start_root_y = 0
        self.resize_start_x = 0
        self.resize_start_w = 0
        
        # Logo feature attributes
        self.luffy_win = None
        self.luffy_photo = None
        self.luffy_frames = []
        self.luffy_frame_index = 0
        self.luffy_anim_id = None
        self.luffy_frame_anim_id = None
        self.luffy_vx = 2
        self.luffy_vy = 2
        
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
        self.drag_label.bind('<ButtonRelease-1>', self.on_drag_release)
        self.header_frame.bind('<Button-1>', self.start_move)
        self.header_frame.bind('<B1-Motion>', self.on_move)
        self.header_frame.bind('<ButtonRelease-1>', self.on_drag_release)
        
        self.is_collapsed = False
        
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

        # Add Mouse Button
        self.add_mouse_btn = tk.Label(
            self.header_frame, 
            text="＋ Add Mouse", 
            bg='white', 
            fg='#2196F3', 
            font=('Arial', 10, 'bold'), 
            cursor='hand2'
        )
        self.add_mouse_btn.pack(side='right', padx=(0, 10))
        self.add_mouse_btn.bind('<Button-1>', lambda e: self.add_mouse_box())
        self.add_mouse_btn.bind('<Enter>', lambda e: self.add_mouse_btn.config(fg='#1976D2'))
        self.add_mouse_btn.bind('<Leave>', lambda e: self.add_mouse_btn.config(fg='#2196F3'))

        # Add Global Button
        self.add_global_btn = tk.Label(
            self.header_frame, 
            text="＋ Global", 
            bg='white', 
            fg='#9C27B0', 
            font=('Arial', 10, 'bold'), 
            cursor='hand2'
        )
        self.add_global_btn.pack(side='right', padx=(0, 10))
        self.add_global_btn.bind('<Button-1>', lambda e: self.add_global_box())
        self.add_global_btn.bind('<Enter>', lambda e: self.add_global_btn.config(fg='#7B1FA2'))
        self.add_global_btn.bind('<Leave>', lambda e: self.add_global_btn.config(fg='#9C27B0'))

        # Add C Button
        self.add_c_btn = tk.Label(
            self.header_frame, 
            text="＋ Add C", 
            bg='white', 
            fg='#FF5722', 
            font=('Arial', 10, 'bold'), 
            cursor='hand2'
        )
        self.add_c_btn.pack(side='right', padx=(0, 10))
        self.add_c_btn.bind('<Button-1>', lambda e: self.add_c_box())
        self.add_c_btn.bind('<Enter>', lambda e: self.add_c_btn.config(fg='#D84315'))
        self.add_c_btn.bind('<Leave>', lambda e: self.add_c_btn.config(fg='#FF5722'))

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
            'scan_win': None,
            'scan_mode': 'TD',
            'is_control_mode': False,
            'control_mode': '',
            'saved_text': 'text here...',
            'mouse_listener': None,
            'kb_listener': None,
            'is_mouse_box': False,
            'is_active': True
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
        
        # --- Control button ---
        control_btn_frame = tk.Frame(
            buttons_frame,
            bg='#2196F3',
            relief='flat',
            padx=8,
            pady=4
        )
        control_btn_frame.pack(side='left', padx=(0, 3))
        
        control_btn = tk.Label(
            control_btn_frame,
            text="control",
            bg='#2196F3',
            fg='white',
            font=('Arial', 9, 'bold'),
            cursor='hand2'
        )
        control_btn.pack()

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
        
        # --- Scan button (Moved here) ---
        scan_button_frame = tk.Frame(
            buttons_frame,
            bg='#2196F3',
            relief='flat',
            padx=8,
            pady=4
        )
        scan_button_frame.pack(side='left', padx=(3, 0))
        
        scan_button = tk.Label(
            scan_button_frame,
            text="scan",
            bg='#2196F3',
            fg='white',
            font=('Arial', 9, 'bold'),
            cursor='hand2'
        )
        scan_button.pack()
        scan_button.bind('<Button-1>', lambda e, pd=pin_data: self.open_scan_box(pd))
        
        def toggle_control_normal(event, btn=control_btn, frm=control_btn_frame, entry=search_entry, pd=pin_data):
            if not pd['is_control_mode']:
                # Switching to control mode (turn orange)
                pd['is_control_mode'] = True
                pd['saved_text'] = entry.get()
                entry.delete(0, 'end')
                entry.config(fg='#333333')
                # If no control previously set, display right click as default
                if not pd['control_mode']:
                    entry.insert(0, "right click")
                else:
                    entry.insert(0, pd['control_mode'])
                
                frm.config(bg='#FF9800')
                btn.config(bg='#FF9800')
            else:
                # Switching back to normal mode (turn blue)
                pd['is_control_mode'] = False
                pd['control_mode'] = entry.get().strip()
                entry.delete(0, 'end')
                entry.insert(0, pd['saved_text'])
                if pd['saved_text'] == "text here...":
                    entry.config(fg='#999999')
                else:
                    entry.config(fg='#333333')
                
                frm.config(bg='#2196F3')
                btn.config(bg='#2196F3')

        control_btn.bind('<Button-1>', toggle_control_normal)
        
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
            text_to_paste = entry.get()
            scan_active = pd.get('scan_win') and pd['scan_win'].winfo_exists()
            pinned_active = pd['pinned'] and pd['target_x'] is not None

            if scan_active and pinned_active:
                # --- SCAN & PASTE MODE ---
                btn.config(text='scanning...')
                frm.config(bg='#FF9800')
                btn.config(bg='#FF9800')
                self.root.update()
                
                def do_scan_and_paste():
                    scan_win = pd['scan_win']
                    sx, sy = scan_win.winfo_rootx(), scan_win.winfo_rooty()
                    sw, sh = scan_win.winfo_width(), scan_win.winfo_height()
                    tx, ty = pd['target_x'], pd['target_y']
                    
                    # Hide windows for clear screenshot
                    float_win = pd.get('float_win')
                    if float_win and float_win.winfo_exists():
                        self.root.after(0, float_win.withdraw)
                    self.root.after(0, scan_win.withdraw)
                    self.root.after(0, self.root.withdraw)
                    time.sleep(0.4)
                    
                    scanned_text = ""
                    try:
                        # Take screenshot of the scan box area
                        screenshot = pyautogui.screenshot(region=(sx, sy, sw, sh))
                        
                        if pytesseract:
                            # Perform OCR
                            raw_text = pytesseract.image_to_string(screenshot)
                            
                            # Clean text based on mode
                            mode = pd.get('scan_mode', 'TD')
                            if mode == 'TD':
                                # Keep only digits
                                scanned_text = "".join(re.findall(r'\d+', raw_text))
                            else: # PIN mode
                                # convert dashes to dots then keep numbers and dots
                                temp_text = raw_text.replace('-', '.')
                                scanned_text = "".join(re.findall(r'[\d.]+', temp_text))
                        else:
                            scanned_text = "ERROR: Install pytesseract"
                            
                        # Update the entry box with what we found
                        final_text = scanned_text
                        def update_entry():
                            entry.delete(0, 'end')
                            entry.insert(0, final_text)
                            entry.config(fg='#333333')
                        self.root.after(0, update_entry)
                        
                        # Click target and paste
                        pyautogui.click(tx, ty)
                        time.sleep(0.2)
                        pyperclip.copy(final_text)
                        pyautogui.hotkey('ctrl', 'v')
                        time.sleep(0.2)
                        
                    except Exception as e:
                        print(f"OCR Error: {e}")
                    
                    # Restore windows
                    self.root.after(0, self.safe_deiconify)
                    if float_win and float_win.winfo_exists():
                        self.root.after(50, float_win.deiconify)
                    if scan_win and scan_win.winfo_exists():
                        self.root.after(50, scan_win.deiconify)
                        
                    self.root.after(500, lambda: reset_paste_btn(btn, frm))
                    
                threading.Thread(target=do_scan_and_paste, daemon=True).start()

            elif text_to_paste and text_to_paste != "text here..." and pinned_active:
                # --- NORMAL PASTE MODE ---
                # Visual feedback
                btn.config(text='pasting...')
                frm.config(bg='#FF9800')
                btn.config(bg='#FF9800')
                self.root.update()
                
                # Run paste in a thread so the UI doesn't freeze
                def do_paste():
                    tx, ty = pd['target_x'], pd['target_y']
                    
                    # Hide the floating pin and CopyBox
                    float_win = pd.get('float_win')
                    if float_win and float_win.winfo_exists():
                        self.root.after(0, float_win.withdraw)
                    self.root.after(0, self.root.withdraw)
                    time.sleep(0.3)
                    
                    pyautogui.click(tx, ty)
                    time.sleep(0.15)
                    pyperclip.copy(text_to_paste)
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(0.15)
                    
                    self.root.after(0, self.safe_deiconify)
                    if float_win and float_win.winfo_exists():
                        self.root.after(50, float_win.deiconify)
                    
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
        
        paste_button.bind('<Button-1>', paste_text)

        # Worker for auto paste logic in normal box
        def perform_auto_paste_normal(pd):
            if not pd['pinned'] or pd['target_x'] is None: return
            if pd['is_control_mode']: return # Don't paste if user is actively configuring the trigger

            def task():
                try:
                    time.sleep(0.1)
                    tx, ty = pd['target_x'], pd['target_y']
                    orig_x, orig_y = pyautogui.position()
                    
                    scan_active = pd.get('scan_win') and pd['scan_win'].winfo_exists()
                    # if a scan window exists, OCR and Paste it
                    if scan_active:
                        scan_win = pd['scan_win']
                        sx, sy = scan_win.winfo_rootx(), scan_win.winfo_rooty()
                        sw, sh = scan_win.winfo_width(), scan_win.winfo_height()
                        
                        float_win = pd.get('float_win')
                        if float_win and float_win.winfo_exists():
                            self.root.after(0, float_win.withdraw)
                        self.root.after(0, scan_win.withdraw)
                        self.root.after(0, self.root.withdraw)
                        time.sleep(0.4)
                        
                        screenshot = pyautogui.screenshot(region=(sx, sy, sw, sh))
                        scanned_text = ""
                        if pytesseract:
                            raw_text = pytesseract.image_to_string(screenshot)
                            mode = pd.get('scan_mode', 'TD')
                            if mode == 'TD':
                                scanned_text = "".join(re.findall(r'\d+', raw_text))
                            else:
                                temp_text = raw_text.replace('-', '.')
                                scanned_text = "".join(re.findall(r'[\d.]+', temp_text))
                        
                        pyautogui.click(tx, ty)
                        time.sleep(0.15)
                        if scanned_text:
                            pyperclip.copy(scanned_text)
                        pyautogui.hotkey('ctrl', 'v')
                        time.sleep(0.15)
                        
                        pyautogui.moveTo(orig_x, orig_y)
                        self.root.after(0, self.safe_deiconify)
                        if float_win and float_win.winfo_exists():
                            self.root.after(50, float_win.deiconify)
                        if scan_win and scan_win.winfo_exists():
                            self.root.after(50, scan_win.deiconify)
                    else:
                        # For mouse boxes, copy from current location first, then paste at target
                        if pd.get('is_mouse_box', False):
                            # Hide windows temporarily
                            float_win = pd.get('float_win')
                            if float_win and float_win.winfo_exists():
                                self.root.after(0, float_win.withdraw)
                            self.root.after(0, self.root.withdraw)
                            time.sleep(0.2)
                            
                            # First copy from current location (where right-click happened)
                            pyautogui.hotkey('ctrl', 'c')
                            time.sleep(0.2)
                            
                            # Then click target location and paste
                            pyautogui.click(tx, ty)
                            time.sleep(0.15)
                            pyautogui.hotkey('ctrl', 'v')
                            time.sleep(0.15)
                            
                            pyautogui.moveTo(orig_x, orig_y)
                            self.root.after(0, self.safe_deiconify)
                            if float_win and float_win.winfo_exists():
                                self.root.after(50, float_win.deiconify)
                        else:
                            # Normal box behavior - paste text from entry
                            text_to_paste = pd['entry'].get()
                            if not text_to_paste or text_to_paste == "text here...": return
                            
                            float_win = pd.get('float_win')
                            if float_win and float_win.winfo_exists():
                                self.root.after(0, float_win.withdraw)
                            self.root.after(0, self.root.withdraw)
                            time.sleep(0.1)
                            
                            pyautogui.click(tx, ty)
                            time.sleep(0.1)
                            pyperclip.copy(text_to_paste)
                            pyautogui.hotkey('ctrl', 'v')
                            time.sleep(0.1)
                            
                            pyautogui.moveTo(orig_x, orig_y)
                            self.root.after(0, self.safe_deiconify)
                            if float_win and float_win.winfo_exists():
                                self.root.after(50, float_win.deiconify)
                except Exception as e:
                    print("Error auto paste normal:", e)

            threading.Thread(target=task, daemon=True).start()

        def on_mouse_click_normal(x, y, button, pressed):
            if not pin_data['control_mode']: return
            trigger = str(pin_data.get('control_mode', '')).lower()
            if not pressed: return
            
            if trigger in ['right click', 'right']:
                if button == mouse.Button.right:
                    perform_auto_paste_normal(pin_data)
            elif trigger in ['middle click', 'middle']:
                if button == mouse.Button.middle:
                    perform_auto_paste_normal(pin_data)
            elif trigger in ['left click', 'left']:
                if button == mouse.Button.left:
                    perform_auto_paste_normal(pin_data)

        current_keys_normal = set()
        def on_key_press_normal(key):
            if not pin_data['control_mode']: return
            trigger = str(pin_data.get('control_mode', '')).lower().strip()
            if 'click' in trigger or trigger in ['right', 'left', 'middle']: return
            
            try: k_char = key.char.lower()
            except AttributeError: k_char = str(key).lower().replace('key.', '')
            current_keys_normal.add(k_char)
            
            modifiers = []
            if any('ctrl' in k for k in current_keys_normal): modifiers.append('ctrl')
            if any('shift' in k for k in current_keys_normal): modifiers.append('shift')
            if any('alt' in k for k in current_keys_normal): modifiers.append('alt')
            regular = [k for k in current_keys_normal if 'ctrl' not in k and 'shift' not in k and 'alt' not in k and 'cmd' not in k]
            current_state = modifiers + regular
            
            parts = trigger.replace('+', ' ').split()
            trigger_state = []
            for p in parts:
                if p in ['ctrl', 'control']: trigger_state.append('ctrl')
                elif p in ['shift']: trigger_state.append('shift')
                elif p in ['alt']: trigger_state.append('alt')
                else: trigger_state.append(p)
            
            if len(trigger_state) > 0 and set(trigger_state) == set(current_state):
                perform_auto_paste_normal(pin_data)

        def on_key_release_normal(key):
            try: k_char = key.char.lower()
            except AttributeError: k_char = str(key).lower().replace('key.', '')
            current_keys_normal.discard(k_char)

        def start_listeners_normal(pd):
            if pd.get('mouse_listener') is None:
                l = mouse.Listener(on_click=on_mouse_click_normal)
                l.start()
                pd['mouse_listener'] = l
            if pd.get('kb_listener') is None:
                kl = keyboard.Listener(on_press=on_key_press_normal, on_release=on_key_release_normal)
                kl.start()
                pd['kb_listener'] = kl

        def stop_listeners_normal(pd):
            if pd.get('mouse_listener'):
                pd['mouse_listener'].stop()
                pd['mouse_listener'] = None
            if pd.get('kb_listener'):
                pd['kb_listener'].stop()
                pd['kb_listener'] = None

        start_listeners_normal(pin_data)

        def reset_paste_btn(btn, frm):
            try:
                btn.config(text='paste')
                frm.config(bg='#2196F3')
                btn.config(bg='#2196F3')
            except tk.TclError:
                pass
                
        # Move paste button bind down here because we had to inject below it
        # Wait, the bind was already handled above in the replaced snippet. Let me remove it here.
        
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
        if len(self.boxes) >= 0:
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
                stop_listeners_normal(pd)
                # Destroy floating pin if it exists
                if pd.get('float_win'):
                    try:
                        pd['float_win'].destroy()
                    except:
                        pass
                # Destroy scan win if it exists
                if pd.get('scan_win'):
                    try:
                        pd['scan_win'].destroy()
                    except:
                        pass
                b_frame.destroy()
                self.boxes = [(bf, p) for bf, p in self.boxes if bf != b_frame]
                self.update_geometry()
            del_button.bind('<Button-1>', del_box)
            
        self.boxes.append((box_frame, pin_data))
        self.update_geometry()
        
    def add_mouse_box(self):
        # Create container for the row
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
            'scan_win': None,
            'scan_mode': 'TD',
            'is_mouse_box': True,
            'is_active': False,
            'control_mode': 'right click',
            'mouse_listener': None,
            'kb_listener': None
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
        
        # Search entry (Control)
        control_entry = tk.Entry(
            box_frame,
            bg='white',
            fg='#333333',
            relief='flat',
            font=('Arial', 11),
            width=15,
            bd=0,
            highlightthickness=0,
            insertbackground='#333333',
            state='disabled'
        )
        control_entry.pack(side='left', fill='x', expand=True, padx=5)
        pin_data['entry'] = control_entry
        
        # Set default string
        control_entry.config(state='normal')
        control_entry.insert(0, "right click")
        control_entry.config(state='disabled')
        
        # Separator line
        separator2 = tk.Frame(box_frame, width=1, bg='#E0E0E0')
        separator2.pack(side='left', fill='y', padx=(8, 0))
        
        # --- Buttons container ---
        buttons_frame = tk.Frame(box_frame, bg='white')
        buttons_frame.pack(side='right', padx=(3, 0))

        # 1st button: Active
        active_btn_frame = tk.Frame(
            buttons_frame,
            bg='#2196F3',
            relief='flat',
            padx=8,
            pady=4
        )
        active_btn_frame.pack(side='left', padx=(0, 3))
        
        active_btn = tk.Label(
            active_btn_frame,
            text="active",
            bg='#2196F3',
            fg='white',
            font=('Arial', 9, 'bold'),
            cursor='hand2'
        )
        active_btn.pack()
        
        # 2nd button: Control
        control_btn_frame = tk.Frame(
            buttons_frame,
            bg='#2196F3',
            relief='flat',
            padx=8,
            pady=4
        )
        control_btn_frame.pack(side='left')
        
        control_btn = tk.Label(
            control_btn_frame,
            text="control",
            bg='#2196F3',
            fg='white',
            font=('Arial', 9, 'bold'),
            cursor='hand2'
        )
        control_btn.pack()
        
        # 3rd button: Scan
        scan_btn_frame = tk.Frame(
            buttons_frame,
            bg='#2196F3',
            relief='flat',
            padx=8,
            pady=4
        )
        scan_btn_frame.pack(side='left', padx=(3, 0))
        
        scan_btn = tk.Label(
            scan_btn_frame,
            text="scan",
            bg='#2196F3',
            fg='white',
            font=('Arial', 9, 'bold'),
            cursor='hand2'
        )
        scan_btn.pack()
        scan_btn.bind('<Button-1>', lambda e, pd=pin_data: self.open_scan_box(pd))

        # Handlers
        def toggle_control(event, btn=control_btn, frm=control_btn_frame, entry=control_entry, pd=pin_data):
            if entry.cget('state') == 'disabled':
                entry.config(state='normal')
                frm.config(bg='#FF9800')
                btn.config(bg='#FF9800')
            else:
                entry.config(state='disabled')
                pd['control_mode'] = entry.get().strip().lower()
                frm.config(bg='#2196F3')
                btn.config(bg='#2196F3')

        control_btn.bind('<Button-1>', toggle_control)

        def toggle_active(event, btn=active_btn, frm=active_btn_frame, pd=pin_data):
            if not pd['is_active']:
                # Start listener
                pd['is_active'] = True
                frm.config(bg='#FF3333') # Red when active
                btn.config(bg='#FF3333')
                start_listeners(pd)
            else:
                # Stop listener
                pd['is_active'] = False
                frm.config(bg='#2196F3') # Blue when inactive
                btn.config(bg='#2196F3')
                stop_listeners(pd)

        active_btn.bind('<Button-1>', toggle_active)

        # Worker for auto paste
        def perform_auto_paste(pd):
            if not pd['is_active'] or not pd['pinned'] or pd['target_x'] is None:
                return

            def task():
                try:
                    time.sleep(0.1)
                    
                    tx, ty = pd['target_x'], pd['target_y']
                    # Store the original mouse position to go back to it
                    orig_x, orig_y = pyautogui.position()
                    
                    scan_active = pd.get('scan_win') and pd['scan_win'].winfo_exists()
                    if scan_active:
                        # OCR flow
                        scan_win = pd['scan_win']
                        sx, sy = scan_win.winfo_rootx(), scan_win.winfo_rooty()
                        sw, sh = scan_win.winfo_width(), scan_win.winfo_height()
                        
                        float_win = pd.get('float_win')
                        if float_win and float_win.winfo_exists():
                            self.root.after(0, float_win.withdraw)
                        self.root.after(0, scan_win.withdraw)
                        self.root.after(0, self.root.withdraw)
                        time.sleep(0.4)
                        
                        screenshot = pyautogui.screenshot(region=(sx, sy, sw, sh))
                        scanned_text = ""
                        if pytesseract:
                            raw_text = pytesseract.image_to_string(screenshot)
                            mode = pd.get('scan_mode', 'TD')
                            if mode == 'TD':
                                scanned_text = "".join(re.findall(r'\d+', raw_text))
                            else:
                                temp_text = raw_text.replace('-', '.')
                                scanned_text = "".join(re.findall(r'[\d.]+', temp_text))
                        
                        pyautogui.click(tx, ty)
                        time.sleep(0.15)
                        if scanned_text:
                            pyperclip.copy(scanned_text)
                        pyautogui.hotkey('ctrl', 'v')
                        time.sleep(0.15)
                        
                        # Return to original point
                        pyautogui.moveTo(orig_x, orig_y)

                        self.root.after(0, self.safe_deiconify)
                        if float_win and float_win.winfo_exists():
                            self.root.after(50, float_win.deiconify)
                        if scan_win and scan_win.winfo_exists():
                            self.root.after(50, scan_win.deiconify)
                    else:
                        # For mouse boxes, copy from current location first, then paste at target
                        float_win = pd.get('float_win')
                        if float_win and float_win.winfo_exists():
                            self.root.after(0, float_win.withdraw)
                        self.root.after(0, self.root.withdraw)
                        time.sleep(0.2)
                        
                        # First copy from current location (where right-click happened)
                        pyautogui.hotkey('ctrl', 'c')
                        time.sleep(0.2)
                        
                        # Then click target location and paste
                        pyautogui.click(tx, ty)
                        time.sleep(0.15)
                        pyautogui.hotkey('ctrl', 'v')
                        time.sleep(0.15)
                        
                        # Return to original point
                        pyautogui.moveTo(orig_x, orig_y)
                        
                        self.root.after(0, self.safe_deiconify)
                        if float_win and float_win.winfo_exists():
                            self.root.after(50, float_win.deiconify)

                except Exception as e:
                    print("Error in auto paste:", e)

            threading.Thread(target=task, daemon=True).start()

        def on_mouse_click(x, y, button, pressed):
            if not pin_data.get('is_active'): return
            trigger = str(pin_data.get('control_mode', '')).lower()
            if not pressed: return
            
            if trigger in ['right click', 'right']:
                if button == mouse.Button.right:
                    perform_auto_paste(pin_data)
            elif trigger in ['middle click', 'middle']:
                if button == mouse.Button.middle:
                    perform_auto_paste(pin_data)
            elif trigger in ['left click', 'left']:
                if button == mouse.Button.left:
                    perform_auto_paste(pin_data)

        current_keys = set()
        
        def on_key_press(key):
            if not pin_data.get('is_active'): return
            trigger = str(pin_data.get('control_mode', '')).lower().strip()
            # Ignore mouse click triggers
            if 'click' in trigger or trigger in ['right', 'left', 'middle']: return
            
            try:
                k_char = key.char.lower()
                current_keys.add(k_char)
            except AttributeError:
                k_str = str(key).lower().replace('key.', '')
                current_keys.add(k_str)
                
            modifiers = []
            if any('ctrl' in k for k in current_keys): modifiers.append('ctrl')
            if any('shift' in k for k in current_keys): modifiers.append('shift')
            if any('alt' in k for k in current_keys): modifiers.append('alt')
            
            regular = [k for k in current_keys if 'ctrl' not in k and 'shift' not in k and 'alt' not in k and 'cmd' not in k]
            current_state = modifiers + regular
            
            parts = trigger.replace('+', ' ').split()
            trigger_state = []
            for p in parts:
                if p in ['ctrl', 'control']: trigger_state.append('ctrl')
                elif p in ['shift']: trigger_state.append('shift')
                elif p in ['alt']: trigger_state.append('alt')
                else: trigger_state.append(p)
            
            if len(trigger_state) > 0 and set(trigger_state) == set(current_state):
                perform_auto_paste(pin_data)
                
        def on_key_release(key):
            try:
                k_char = key.char.lower()
                current_keys.discard(k_char)
            except AttributeError:
                k_str = str(key).lower().replace('key.', '')
                current_keys.discard(k_str)

        def start_listeners(pd):
            if pd.get('mouse_listener') is None:
                l = mouse.Listener(on_click=on_mouse_click)
                l.start()
                pd['mouse_listener'] = l
            if pd.get('kb_listener') is None:
                kl = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
                kl.start()
                pd['kb_listener'] = kl

        def stop_listeners(pd):
            if pd.get('mouse_listener'):
                pd['mouse_listener'].stop()
                pd['mouse_listener'] = None
            if pd.get('kb_listener'):
                pd['kb_listener'].stop()
                pd['kb_listener'] = None

        # --- Small coordinate label under the pin ---
        coord_label = tk.Label(
            box_frame,
            text="",
            bg='white',
            fg='#AAAAAA',
            font=('Arial', 7)
        )
        pin_data['coord_label'] = coord_label
        
        # Remove box button
        if len(self.boxes) >= 0:
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
                stop_listeners(pd)
                if pd.get('float_win'):
                    try: pd['float_win'].destroy()
                    except: pass
                if pd.get('scan_win'):
                    try: pd['scan_win'].destroy()
                    except: pass
                b_frame.destroy()
                self.boxes = [(bf, p) for bf, p in self.boxes if bf != b_frame]
                self.update_geometry()
            del_button.bind('<Button-1>', del_box)
            
        self.boxes.append((box_frame, pin_data))
        self.update_geometry()

    def add_global_box(self):
        # Create container for the row
        box_frame = tk.Frame(self.boxes_container, bg='white')
        box_frame.pack(fill='x', pady=(0, 8))
        
        # Assign a unique color to this box
        box_color = self.pin_colors[self.color_index % len(self.pin_colors)]
        self.color_index += 1
        
        # --- Per-box pin data ---
        pin_data = {
            'color': box_color,
            'is_active': False,
            'control_mode': 'right click',
            'mouse_listener': None,
            'kb_listener': None,
            'bits': []
        }
        
        # Color indicator bar on the left
        color_bar = tk.Frame(box_frame, width=4, bg=box_color)
        color_bar.pack(side='left', fill='y', padx=(2, 0))
        
        # Global Icon
        global_icon = tk.Label(
            box_frame, 
            text="🌍", 
            bg='white', 
            fg=box_color,
            font=('Arial', 12)
        )
        global_icon.pack(side='left', padx=(5, 8))
        
        # Separator line
        separator1 = tk.Frame(box_frame, width=1, bg='#E0E0E0')
        separator1.pack(side='left', fill='y', padx=(0, 8))
        
        # Search entry (Control)
        control_entry = tk.Entry(
            box_frame,
            bg='white',
            fg='#333333',
            relief='flat',
            font=('Arial', 11),
            width=15,
            bd=0,
            highlightthickness=0,
            insertbackground='#333333',
            state='disabled'
        )
        control_entry.pack(side='left', fill='x', expand=True, padx=5)
        pin_data['entry'] = control_entry
        
        # Set default string
        control_entry.config(state='normal')
        control_entry.insert(0, "right click")
        control_entry.config(state='disabled')
        
        # Separator line
        separator2 = tk.Frame(box_frame, width=1, bg='#E0E0E0')
        separator2.pack(side='left', fill='y', padx=(8, 0))
        
        # --- Buttons container ---
        buttons_frame = tk.Frame(box_frame, bg='white')
        buttons_frame.pack(side='right', padx=(3, 0))

        # 1st button: Active
        active_btn_frame = tk.Frame(buttons_frame, bg='#2196F3', relief='flat', padx=8, pady=4)
        active_btn_frame.pack(side='left', padx=(0, 3))
        active_btn = tk.Label(active_btn_frame, text="active paste", bg='#2196F3', fg='white', font=('Arial', 9, 'bold'), cursor='hand2')
        active_btn.pack()
        
        # 2nd button: Control
        control_btn_frame = tk.Frame(buttons_frame, bg='#2196F3', relief='flat', padx=8, pady=4)
        control_btn_frame.pack(side='left', padx=(0, 3))
        control_btn = tk.Label(control_btn_frame, text="control", bg='#2196F3', fg='white', font=('Arial', 9, 'bold'), cursor='hand2')
        control_btn.pack()
        
        # 3rd button: Bit +
        bit_plus_frame = tk.Frame(buttons_frame, bg='#4CAF50', relief='flat', padx=8, pady=4)
        bit_plus_frame.pack(side='left', padx=(0, 3))
        bit_plus_btn = tk.Label(bit_plus_frame, text="bit +1", bg='#4CAF50', fg='white', font=('Arial', 9, 'bold'), cursor='hand2')
        bit_plus_btn.pack()
        
        # 4th button: Bit -
        bit_minus_frame = tk.Frame(buttons_frame, bg='#FF5555', relief='flat', padx=8, pady=4)
        bit_minus_frame.pack(side='left')
        bit_minus_btn = tk.Label(bit_minus_frame, text="bit -", bg='#FF5555', fg='white', font=('Arial', 9, 'bold'), cursor='hand2')
        bit_minus_btn.pack()

        # Handlers
        def toggle_control(event, btn=control_btn, frm=control_btn_frame, entry=control_entry, pd=pin_data):
            if entry.cget('state') == 'disabled':
                entry.config(state='normal')
                frm.config(bg='#FF9800')
                btn.config(bg='#FF9800')
            else:
                entry.config(state='disabled')
                pd['control_mode'] = entry.get().strip().lower()
                frm.config(bg='#2196F3')
                btn.config(bg='#2196F3')

        control_btn.bind('<Button-1>', toggle_control)

        def toggle_active(event, btn=active_btn, frm=active_btn_frame, pd=pin_data):
            if not pd['is_active']:
                # Start listener
                pd['is_active'] = True
                frm.config(bg='#FF3333') # Red when active
                btn.config(bg='#FF3333')
                start_listeners(pd)
            else:
                # Stop listener
                pd['is_active'] = False
                frm.config(bg='#2196F3') # Blue when inactive
                btn.config(bg='#2196F3')
                stop_listeners(pd)

        active_btn.bind('<Button-1>', toggle_active)

        def perform_global_copy(pd):
            if not pd['is_active']: return
            def task():
                try:
                    # Instant copy
                    pyautogui.hotkey('ctrl', 'c')
                    time.sleep(0.01)
                    pyautogui.hotkey('ctrl', 'c') # Double tap for reliability
                    
                    # If right click was used, context menu might appear on release. 
                    # We can press Esc to close it just in case it popped up.
                    if pd.get('control_mode') in ['right click', 'right']:
                        time.sleep(0.05)
                        pyautogui.press('esc')
                except Exception as e:
                    print("Global copy error", e)
            threading.Thread(target=task, daemon=True).start()

        def on_mouse_click(x, y, button, pressed):
            if not pin_data.get('is_active'): return
            trigger = str(pin_data.get('control_mode', '')).lower()
            if not pressed: return
            if trigger in ['right click', 'right'] and button == mouse.Button.right:
                perform_global_copy(pin_data)
            elif trigger in ['middle click', 'middle'] and button == mouse.Button.middle:
                perform_global_copy(pin_data)
            elif trigger in ['left click', 'left'] and button == mouse.Button.left:
                perform_global_copy(pin_data)

        current_keys = set()
        def on_key_press(key):
            if not pin_data.get('is_active'): return
            trigger = str(pin_data.get('control_mode', '')).lower().strip()
            if 'click' in trigger or trigger in ['right', 'left', 'middle']: return
            try: k_char = key.char.lower()
            except AttributeError: k_char = str(key).lower().replace('key.', '')
            current_keys.add(k_char)
            
            modifiers = []
            if any('ctrl' in k for k in current_keys): modifiers.append('ctrl')
            if any('shift' in k for k in current_keys): modifiers.append('shift')
            if any('alt' in k for k in current_keys): modifiers.append('alt')
            regular = [k for k in current_keys if 'ctrl' not in k and 'shift' not in k and 'alt' not in k and 'cmd' not in k]
            current_state = modifiers + regular
            
            parts = trigger.replace('+', ' ').split()
            trigger_state = []
            for p in parts:
                if p in ['ctrl', 'control']: trigger_state.append('ctrl')
                elif p in ['shift']: trigger_state.append('shift')
                elif p in ['alt']: trigger_state.append('alt')
                else: trigger_state.append(p)
            
            if len(trigger_state) > 0 and set(trigger_state) == set(current_state):
                perform_global_copy(pin_data)
                
        def on_key_release(key):
            try: k_char = key.char.lower()
            except AttributeError: k_char = str(key).lower().replace('key.', '')
            current_keys.discard(k_char)

        def start_listeners(pd):
            if pd.get('mouse_listener') is None:
                l = mouse.Listener(on_click=on_mouse_click)
                l.start()
                pd['mouse_listener'] = l
            if pd.get('kb_listener') is None:
                kl = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
                kl.start()
                pd['kb_listener'] = kl

        def stop_listeners(pd):
            if pd.get('mouse_listener'):
                pd['mouse_listener'].stop()
                pd['mouse_listener'] = None
            if pd.get('kb_listener'):
                pd['kb_listener'].stop()
                pd['kb_listener'] = None

        # Bit + floating windows logic
        def add_bit(event, pd=pin_data):
            bit_index = len(pd['bits']) + 1
            float_win = tk.Toplevel(self.root)
            float_win.overrideredirect(True)
            float_win.attributes('-topmost', True)
            float_win.attributes('-alpha', 0.9)
            float_win.configure(bg='')
            float_win.wm_attributes('-transparentcolor', '#F0F0F0')
            
            win_w = 60
            win_h = 75
            screen_w = self.root.winfo_screenwidth()
            screen_h = self.root.winfo_screenheight()
            init_x = screen_w // 2 - win_w // 2 + (bit_index * 15)
            init_y = screen_h // 2 - win_h // 2
            float_win.geometry(f"{win_w}x{win_h}+{init_x}+{init_y}")
            
            canvas = tk.Canvas(float_win, width=win_w, height=win_h, bg='#F0F0F0', highlightthickness=0, cursor='fleur')
            canvas.pack(fill='both', expand=True)

            canvas.create_line(win_w // 2, 28, win_w // 2, win_h - 8, fill=box_color, width=2, dash=(3, 2))
            dark_color = '#333333'
            canvas.create_oval(win_w//2-6, win_h-12, win_w//2+6, win_h, fill=box_color, outline=dark_color, width=2)
            dot_cx, dot_cy = win_w // 2, win_h - 6
            canvas.create_line(dot_cx - 4, dot_cy, dot_cx + 4, dot_cy, fill='white', width=1)
            canvas.create_line(dot_cx, dot_cy - 4, dot_cx, dot_cy + 4, fill='white', width=1)
            
            btn = tk.Label(float_win, text=f"bit {bit_index}", bg=box_color, fg='white', font=('Arial', 8, 'bold'), cursor='hand2')
            btn.place(x=0, y=0, width=win_w, height=25)
            
            def do_paste(e):
                # Get exact bit pointer coordinates
                tx = float_win.winfo_rootx() + win_w // 2
                ty = float_win.winfo_rooty() + win_h - 5
                
                def task():
                    # Store current mouse position BEFORE any operations
                    orig_x, orig_y = pyautogui.position()
                    
                    # Hide windows for clean operation
                    for bw in pd['bits']:
                        if bw.winfo_exists():
                            bw.withdraw()
                    self.root.withdraw()
                    
                    # Wait for windows to hide completely
                    time.sleep(0.2)
                    
                    # First copy from current location with double-tap for reliability
                    pyautogui.hotkey('ctrl', 'c')
                    time.sleep(0.1)
                    pyautogui.hotkey('ctrl', 'c')  # Double tap for accuracy
                    time.sleep(0.2)
                    
                    # Click exactly at bit pointer location
                    pyautogui.click(tx, ty)
                    time.sleep(0.1)
                    
                    # Paste ONCE only
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(0.1)
                    
                    # Return cursor to EXACT original position
                    pyautogui.moveTo(orig_x, orig_y)
                    
                    # Restore windows
                    self.root.after(0, self.safe_deiconify)
                    for bw in pd['bits']:
                        if bw.winfo_exists():
                            self.root.after(50, bw.deiconify)
                            
                threading.Thread(target=task, daemon=True).start()
                        
            btn.bind('<Button-1>', do_paste)
            
            drag_data = {'x': 0, 'y': 0}
            def on_press(e):
                drag_data['x'] = e.x_root - float_win.winfo_x()
                drag_data['y'] = e.y_root - float_win.winfo_y()
            def on_drag(e):
                new_x = e.x_root - drag_data['x']
                new_y = e.y_root - drag_data['y']
                float_win.geometry(f"+{new_x}+{new_y}")
                
            canvas.bind('<Button-1>', on_press)
            canvas.bind('<B1-Motion>', on_drag)
            
            pd['bits'].append(float_win)

        bit_plus_btn.bind('<Button-1>', add_bit)

        def remove_bit(event, pd=pin_data):
            if pd['bits']:
                last_bit = pd['bits'].pop()
                if last_bit.winfo_exists():
                    last_bit.destroy()
                    
        bit_minus_btn.bind('<Button-1>', remove_bit)

        # Remove box button
        if len(self.boxes) >= 0:
            del_button = tk.Label(box_frame, text="−", bg='white', fg='#FF5555', font=('Arial', 14, 'bold'), cursor='hand2')
            del_button.pack(side='right', padx=(0, 5))
            def del_box(event, b_frame=box_frame, pd=pin_data):
                stop_listeners(pd)
                for bw in pd['bits']:
                    if bw.winfo_exists():
                        try: bw.destroy()
                        except: pass
                b_frame.destroy()
                self.boxes = [(bf, p) for bf, p in self.boxes if bf != b_frame]
                self.update_geometry()
            del_button.bind('<Button-1>', del_box)
            
        self.boxes.append((box_frame, pin_data))
        self.update_geometry()
    
    def add_c_box(self):
        # Create container for the row
        box_frame = tk.Frame(self.boxes_container, bg='white')
        box_frame.pack(fill='x', pady=(0, 8))
        
        # Assign a unique color to this box
        box_color = self.pin_colors[self.color_index % len(self.pin_colors)]
        self.color_index += 1
        
        # --- Per-box pin data ---
        pin_data = {
            'color': box_color,
            'is_active': False,
            'control_mode': 'right click',
            'mouse_listener': None,
            'kb_listener': None,
            'is_c_box': True
        }
        
        # Color indicator bar on the left
        color_bar = tk.Frame(box_frame, width=4, bg=box_color)
        color_bar.pack(side='left', fill='y', padx=(2, 0))
        
        # C Icon
        c_icon = tk.Label(
            box_frame, 
            text="C", 
            bg='white', 
            fg=box_color,
            font=('Arial', 14, 'bold')
        )
        c_icon.pack(side='left', padx=(5, 8))
        
        # Separator line
        separator1 = tk.Frame(box_frame, width=1, bg='#E0E0E0')
        separator1.pack(side='left', fill='y', padx=(0, 8))
        
        # Control entry (shows current control setting)
        control_entry = tk.Entry(
            box_frame,
            bg='white',
            fg='#333333',
            relief='flat',
            font=('Arial', 11),
            width=15,
            bd=0,
            highlightthickness=0,
            insertbackground='#333333',
            state='disabled'
        )
        control_entry.pack(side='left', fill='x', expand=True, padx=5)
        pin_data['entry'] = control_entry
        
        # Set default string
        control_entry.config(state='normal')
        control_entry.insert(0, "right click")
        control_entry.config(state='disabled')
        
        # Separator line
        separator2 = tk.Frame(box_frame, width=1, bg='#E0E0E0')
        separator2.pack(side='left', fill='y', padx=(8, 0))
        
        # --- Buttons container ---
        buttons_frame = tk.Frame(box_frame, bg='white')
        buttons_frame.pack(side='right', padx=(3, 0))

        # Active button
        active_btn_frame = tk.Frame(buttons_frame, bg='#2196F3', relief='flat', padx=8, pady=4)
        active_btn_frame.pack(side='left', padx=(0, 3))
        active_btn = tk.Label(active_btn_frame, text="active", bg='#2196F3', fg='white', font=('Arial', 9, 'bold'), cursor='hand2')
        active_btn.pack()
        
        # Control button
        control_btn_frame = tk.Frame(buttons_frame, bg='#2196F3', relief='flat', padx=8, pady=4)
        control_btn_frame.pack(side='left', padx=(0, 3))
        control_btn = tk.Label(control_btn_frame, text="control", bg='#2196F3', fg='white', font=('Arial', 9, 'bold'), cursor='hand2')
        control_btn.pack()

        # Control button handler
        def toggle_control(event, btn=control_btn, frm=control_btn_frame, entry=control_entry, pd=pin_data):
            if entry.cget('state') == 'disabled':
                # Enable editing
                entry.config(state='normal')
                entry.focus()
                btn.config(text='save')
                frm.config(bg='#FF9800')
                btn.config(bg='#FF9800')
            else:
                # Save and disable
                new_control = entry.get().strip()
                if new_control:
                    pd['control_mode'] = new_control
                entry.config(state='disabled')
                btn.config(text='control')
                frm.config(bg='#2196F3')
                btn.config(bg='#2196F3')
        
        control_btn.bind('<Button-1>', toggle_control)

        # Active button handler
        def toggle_active(event, btn=active_btn, frm=active_btn_frame, pd=pin_data):
            if not pd['is_active']:
                # Start listener
                pd['is_active'] = True
                frm.config(bg='#FF3333') # Red when active
                btn.config(bg='#FF3333')
                start_c_listeners(pd)
            else:
                # Stop listener
                pd['is_active'] = False
                frm.config(bg='#2196F3') # Blue when inactive
                btn.config(bg='#2196F3')
                stop_c_listeners(pd)

        active_btn.bind('<Button-1>', toggle_active)

        # C Box mouse click handler - trigger to click and paste at cursor location
        def on_c_mouse_click(x, y, button, pressed):
            if not pin_data.get('is_active'): return
            trigger = str(pin_data.get('control_mode', '')).lower()
            if not pressed: return
            
            # Check if the trigger matches
            trigger_matched = False
            if trigger in ['right click', 'right'] and button == mouse.Button.right:
                trigger_matched = True
            elif trigger in ['middle click', 'middle'] and button == mouse.Button.middle:
                trigger_matched = True
            elif trigger in ['left click', 'left'] and button == mouse.Button.left:
                trigger_matched = True
                
            if trigger_matched:
                perform_c_click_paste(x, y)

        def perform_c_click_paste(x, y):
            def task():
                try:
                    time.sleep(0.1)
                    # Get current cursor position (where arrow is pointing)
                    cursor_x, cursor_y = pyautogui.position()
                    
                    # Click at cursor location and paste
                    pyautogui.click(cursor_x, cursor_y)
                    time.sleep(0.1)
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(0.1)
                except Exception as e:
                    print("C box click paste error:", e)
            threading.Thread(target=task, daemon=True).start()

        # Keyboard handler for C box
        current_c_keys = set()
        def on_c_key_press(key):
            if not pin_data.get('is_active'): return
            trigger = str(pin_data.get('control_mode', '')).lower().strip()
            if 'click' in trigger or trigger in ['right', 'left', 'middle']: return
            
            try: k_char = key.char.lower()
            except AttributeError: k_char = str(key).lower().replace('key.', '')
            current_c_keys.add(k_char)
            
            modifiers = []
            if any('ctrl' in k for k in current_c_keys): modifiers.append('ctrl')
            if any('shift' in k for k in current_c_keys): modifiers.append('shift')
            if any('alt' in k for k in current_c_keys): modifiers.append('alt')
            regular = [k for k in current_c_keys if 'ctrl' not in k and 'shift' not in k and 'alt' not in k and 'cmd' not in k]
            current_state = modifiers + regular
            
            parts = trigger.replace('+', ' ').split()
            trigger_state = []
            for p in parts:
                if p in ['ctrl', 'control']: trigger_state.append('ctrl')
                elif p in ['shift']: trigger_state.append('shift')
                elif p in ['alt']: trigger_state.append('alt')
                else: trigger_state.append(p)
            
            if len(trigger_state) > 0 and set(trigger_state) == set(current_state):
                # Get current mouse position and perform click paste there
                x, y = pyautogui.position()
                perform_c_click_paste(x, y)

        def on_c_key_release(key):
            try: k_char = key.char.lower()
            except AttributeError: k_char = str(key).lower().replace('key.', '')
            current_c_keys.discard(k_char)

        def start_c_listeners(pd):
            if pd.get('mouse_listener') is None:
                l = mouse.Listener(on_click=on_c_mouse_click)
                l.start()
                pd['mouse_listener'] = l
            if pd.get('kb_listener') is None:
                kl = keyboard.Listener(on_press=on_c_key_press, on_release=on_c_key_release)
                kl.start()
                pd['kb_listener'] = kl

        def stop_c_listeners(pd):
            if pd.get('mouse_listener'):
                pd['mouse_listener'].stop()
                pd['mouse_listener'] = None
            if pd.get('kb_listener'):
                pd['kb_listener'].stop()
                pd['kb_listener'] = None

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
                # Stop listeners
                stop_c_listeners(pd)
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
        
        # Draw the target icon at the top-center
        canvas.create_text(win_w // 2, 15, text="(-_-)", font=('Arial', 12, 'bold'), fill=color)
        
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
        
    def open_scan_box(self, pin_data):
        """Create a floating transparent box that can be moved and resized."""
        # Toggle: If already exists, destroy it
        if pin_data.get('scan_win') and pin_data['scan_win'].winfo_exists():
            pin_data['scan_win'].destroy()
            pin_data['scan_win'] = None
            return

        scan_win = tk.Toplevel(self.root)
        pin_data['scan_win'] = scan_win
        scan_win.overrideredirect(True)
        scan_win.attributes('-topmost', True)
        
        # Make the box semi-transparent
        scan_win.attributes('-alpha', 0.4)
        
        # Color comes from pin_data
        box_color = pin_data['color']
        scan_win.configure(bg=box_color)
        
        # Window size: Fixed size suitable for TD/PIN lines
        win_w = 450
        win_h = 80
        
        # Position it near the center of the screen
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        init_x = (screen_w // 2) - (win_w // 2)
        init_y = (screen_h // 2) - (win_h // 2)
        scan_win.geometry(f"{win_w}x{win_h}+{init_x}+{init_y}")
        
        # Container for the scan box content
        content_frame = tk.Frame(scan_win, bg=box_color, highlightthickness=1, highlightbackground='white')
        content_frame.pack(fill='both', expand=True)
        
        # Focus Canvas to draw a white box/corners
        canvas_focus = tk.Canvas(content_frame, bg=box_color, highlightthickness=0, bd=0, cursor='fleur')
        canvas_focus.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Function to redraw indicators on resize
        def redraw_indicators(event=None):
            canvas_focus.delete("indicators")
            w = scan_win.winfo_width()
            h = scan_win.winfo_height()
            d = 20 # length of corner lines
            p = 10 # padding from edge
            
            # Top-Left
            canvas_focus.create_line(p, p, p+d, p, fill='white', width=3, tags="indicators")
            canvas_focus.create_line(p, p, p, p+d, fill='white', width=3, tags="indicators")
            # Top-Right
            canvas_focus.create_line(w-p, p, w-p-d, p, fill='white', width=3, tags="indicators")
            canvas_focus.create_line(w-p, p, w-p, p+d, fill='white', width=3, tags="indicators")
            # Bottom-Left
            canvas_focus.create_line(p, h-p, p+d, h-p, fill='white', width=3, tags="indicators")
            canvas_focus.create_line(p, h-p, p, h-p-d, fill='white', width=3, tags="indicators")
            # Bottom-Right
            canvas_focus.create_line(w-p, h-p, w-p-d, h-p, fill='white', width=3, tags="indicators")
            canvas_focus.create_line(w-p, h-p, w-p, h-p-d, fill='white', width=3, tags="indicators")
            # Dashed rectangle
            canvas_focus.create_rectangle(p+2, p+2, w-p-2, h-p-2, outline='white', width=1, dash=(4,4), tags="indicators")

        # Initial draw
        scan_win.after(10, redraw_indicators)
        # Bind resize event to redraw
        scan_win.bind("<Configure>", lambda e: redraw_indicators())

        # --- Dropdown for TD/PIN selection ---
        mode_var = tk.StringVar(scan_win, value=pin_data.get('scan_mode', 'TD'))
        
        def update_mode(*args):
            new_mode = mode_var.get()
            pin_data['scan_mode'] = new_mode
            instructions.config(text=f"SCAN AREA {new_mode}")
            
        mode_var.trace_add("write", update_mode)
        
        mode_dropdown = tk.OptionMenu(content_frame, mode_var, "TD", "PIN")
        mode_dropdown.config(
            bg=box_color, 
            fg='white', 
            activebackground=box_color, 
            activeforeground='white',
            relief='flat',
            highlightthickness=0,
            font=('Arial', 10, 'bold'),
            width=5
        )
        p = 10 # padding
        mode_dropdown.place(x=p+5, y=p+5)
        
        # Instruction label
        instructions = tk.Label(
            content_frame,
            text=f"SCAN AREA {pin_data['scan_mode']}",
            bg=box_color,
            fg='white',
            font=('Arial', 16, 'bold')
        )
        instructions.place(relx=0.5, rely=0.5, anchor='center')
        
        # --- Drag logic ---
        drag_data = {'x': 0, 'y': 0}
        
        def on_press(event):
            drag_data['x'] = event.x
            drag_data['y'] = event.y
            
        def on_drag(event):
            new_x = scan_win.winfo_x() + (event.x - drag_data['x'])
            new_y = scan_win.winfo_y() + (event.y - drag_data['y'])
            scan_win.geometry(f"+{new_x}+{new_y}")
            
        scan_win.bind('<Button-1>', on_press)
        scan_win.bind('<B1-Motion>', on_drag)
        content_frame.bind('<Button-1>', on_press)
        content_frame.bind('<B1-Motion>', on_drag)
        instructions.bind('<Button-1>', on_press)
        instructions.bind('<B1-Motion>', on_drag)
        canvas_focus.bind('<Button-1>', on_press)
        canvas_focus.bind('<B1-Motion>', on_drag)
        
        # Close on right click
        def close_scan(event):
            scan_win.destroy()
            pin_data['scan_win'] = None
            
        scan_win.bind('<Button-3>', close_scan)
        content_frame.bind('<Button-3>', close_scan)
        instructions.bind('<Button-3>', close_scan)
        canvas_focus.bind('<Button-3>', close_scan)

        # --- Resize handle (Added back) ---
        resize_handle = tk.Label(
            content_frame,
            text="⟋",
            bg=box_color,
            fg='white',
            font=('Arial', 12),
            cursor='size_nw_se'
        )
        resize_handle.place(relx=1.0, rely=1.0, anchor='se', x=-2, y=-2)
        
        def on_resize_press(event):
            drag_data['start_w'] = scan_win.winfo_width()
            drag_data['start_h'] = scan_win.winfo_height()
            drag_data['start_x_root'] = event.x_root
            drag_data['start_y_root'] = event.y_root
            
        def on_resize_drag(event):
            dw = event.x_root - drag_data['start_x_root']
            dh = event.y_root - drag_data['start_y_root']
            nw = max(150, drag_data['start_w'] + dw)
            nh = max(60, drag_data['start_h'] + dh)
            scan_win.geometry(f"{nw}x{nh}")
            
        resize_handle.bind('<Button-1>', on_resize_press)
        resize_handle.bind('<B1-Motion>', on_resize_drag)

    def update_geometry(self):
        if getattr(self, 'is_collapsed', False):
            self.root.geometry(f"160x42")
        elif self.luffy_win and self.luffy_win.winfo_exists():
            # If hidden as Luffy, don't try to resize the hidden root
            return
        else:
            num_boxes = len(self.boxes)
            needed_height = 80 + (num_boxes * 42)
            # Cap at 80% of screen height
            max_height = int(self.root.winfo_screenheight() * 0.8)
            if needed_height > max_height:
                needed_height = max_height
            self.root.geometry(f"{self.base_width}x{needed_height}")
            
    def safe_deiconify(self):
        """Restore window only if not currently hidden as Luffy logo."""
        if not self.luffy_win or not self.luffy_win.winfo_exists():
            self.root.deiconify()
            
    def toggle_collapse(self):
        if self.is_collapsed:
            self.boxes_container.pack(fill='both', expand=True, padx=8, pady=(8, 4))
            self.resize_frame.pack(fill='x', side='bottom')
            self.close_btn.pack(side='right', padx=(10, 0))
            self.add_btn.pack(side='right')
            self.add_mouse_btn.pack(side='right', padx=(0, 10))
            self.add_global_btn.pack(side='right', padx=(0, 10))
            self.is_collapsed = False
        else:
            self.boxes_container.pack_forget()
            self.resize_frame.pack_forget()
            self.close_btn.pack_forget()
            self.add_btn.pack_forget()
            self.add_mouse_btn.pack_forget()
            self.add_global_btn.pack_forget()
            self.is_collapsed = True
        self.update_geometry()
        
    def start_move(self, event):
        self.start_x = event.x_root - self.root.winfo_x()
        self.start_y = event.y_root - self.root.winfo_y()
        self.start_root_x = event.x_root
        self.start_root_y = event.y_root
        
    def on_drag_release(self, event):
        if hasattr(self, 'start_root_x'):
            dx = abs(event.x_root - self.start_root_x)
            dy = abs(event.y_root - self.start_root_y)
            if dx < 5 and dy < 5:
                self.toggle_hide_to_luffy()
    
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

    # =============================================
    #  LUFFY LOGO / HIDE FEATURE
    # =============================================
    def toggle_hide_to_luffy(self):
        """Hide main window and show floating Luffy logo."""
        self.root.withdraw()
        self.show_luffy_floating()

    def show_luffy_floating(self):
        if self.luffy_win and self.luffy_win.winfo_exists():
            return
        
        self.luffy_win = tk.Toplevel(self.root)
        self.luffy_win.overrideredirect(True)
        self.luffy_win.attributes('-topmost', True)
        
        # Transparent background setup
        trans_color = '#FFFFFF'
        self.luffy_win.wm_attributes('-transparentcolor', trans_color)
        self.luffy_win.configure(bg=trans_color)
        
        # Load Luffy GIF frames if not already loaded
        # Load Luffy GIF frames if not already loaded
        if not self.luffy_frames:
            try:
                gif_path = os.path.join(os.path.dirname(__file__), "assets", "luffy.gif")
                if os.path.exists(gif_path):
                    gif_img = Image.open(gif_path)
                    try:
                        while True:
                            # Process each frame for better transparency and size
                            frame = gif_img.copy().convert("RGBA")
                            # Put frame on a white background to respect the transparentcolor
                            bg = Image.new("RGBA", frame.size, (255, 255, 255, 255))
                            bg.paste(frame, (0, 0), frame)
                            bg = bg.resize((90, 90), Image.Resampling.LANCZOS)
                            self.luffy_frames.append(ImageTk.PhotoImage(bg))
                            gif_img.seek(gif_img.tell() + 1)
                    except EOFError:
                        pass
            except Exception as e:
                print(f"Error loading luffy gif: {e}")

        self.luffy_frame_index = 0
        if self.luffy_frames:
            self.luffy_label = tk.Label(self.luffy_win, image=self.luffy_frames[0], bg=trans_color, cursor='hand2')
        else:
            # Fallback
            self.luffy_label = tk.Label(self.luffy_win, text="🍖", font=('Arial', 24), bg=trans_color, cursor='hand2')
        
        self.luffy_label.pack()
        
        # Draggable logic for Luffy
        drag_data = {'x': 0, 'y': 0, 'moved': False}
        def on_press(e):
            drag_data['x'] = e.x
            drag_data['y'] = e.y
            drag_data['moved'] = False
        
        def on_drag(e):
            drag_data['moved'] = True
            nx = self.luffy_win.winfo_x() + (e.x - drag_data['x'])
            ny = self.luffy_win.winfo_y() + (e.y - drag_data['y'])
            self.luffy_win.geometry(f"+{nx}+{ny}")
        
        def on_release(e):
            if not drag_data['moved']:
                self.restore_from_luffy()
        
        self.luffy_label.bind('<Button-1>', on_press)
        self.luffy_label.bind('<B1-Motion>', on_drag)
        self.luffy_label.bind('<ButtonRelease-1>', on_release)

        # Start position
        curr_x = self.root.winfo_x()
        curr_y = self.root.winfo_y()
        self.luffy_win.geometry(f"90x90+{curr_x + 300}+{curr_y}")
        
        # Start only the GIF frame animation
        self.animate_luffy_gif()

    def animate_luffy_gif(self):
        """Update the GIF frame."""
        if not self.luffy_win or not self.luffy_win.winfo_exists() or not self.luffy_frames:
            return
        
        self.luffy_frame_index = (self.luffy_frame_index + 1) % len(self.luffy_frames)
        self.luffy_label.config(image=self.luffy_frames[self.luffy_frame_index])
        
        # Loop every 80ms (standard GIF speed approx)
        self.luffy_frame_anim_id = self.root.after(80, self.animate_luffy_gif)

    def start_luffy_animation(self):
        """Make Luffy wander around the screen gently."""
        if not self.luffy_win or not self.luffy_win.winfo_exists():
            return

        try:
            # Screen boundaries
            sw = self.luffy_win.winfo_screenwidth()
            sh = self.luffy_win.winfo_screenheight()
            
            # Current position
            x = self.luffy_win.winfo_x()
            y = self.luffy_win.winfo_y()
            w = 90
            h = 90
            
            # Change direction if edge hit
            if x <= 0: self.luffy_vx = abs(self.luffy_vx)
            elif x + w >= sw: self.luffy_vx = -abs(self.luffy_vx)
            
            if y <= 0: self.luffy_vy = abs(self.luffy_vy)
            elif y + h >= sh: self.luffy_vy = -abs(self.luffy_vy)
                
            # Random slight change in velocity
            if random.random() < 0.05:
                self.luffy_vx += random.uniform(-0.5, 0.5)
                self.luffy_vy += random.uniform(-0.5, 0.5)
                
            # Move
            new_x = int(x + self.luffy_vx)
            new_y = int(y + self.luffy_vy)
            
            # Respect screen bounds
            new_x = max(0, min(sw - w, new_x))
            new_y = max(0, min(sh - h, new_y))
            
            self.luffy_win.geometry(f"+{new_x}+{new_y}")
            
            self.luffy_anim_id = self.root.after(30, self.start_luffy_animation)
        except Exception:
            pass

    def restore_from_luffy(self):
        """Close Luffy logo and restore main window."""
        if self.luffy_frame_anim_id:
            self.root.after_cancel(self.luffy_frame_anim_id)
            self.luffy_frame_anim_id = None
            
        if self.luffy_win:
            self.luffy_win.destroy()
            self.luffy_win = None
        self.root.deiconify()

if __name__ == "__main__":
    root = tk.Tk()
    app = CopyBoxApp(root)
    root.mainloop()
