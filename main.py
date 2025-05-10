import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
from collections import deque

class WatermarkApp:
    """AquaMark Pro - Professional Watermarking Tool by Dabeey 2025"""
   
    def __init__(self, root):
        self.root = root
        self.root.title("AquaMark Pro © Dabeey 2025")
        self.root.geometry("1100x750")
        self.root.minsize(900, 650)
        

        self.bg_color = "#0a1a2a"
        self.panel_color = "#162a3a"
        self.button_color = "#3a6ea5"
        self.button_hover = "#4a7eb5"
        self.text_color = "#e0f0ff"
        self.accent_color = "#4da8da"
        self.watermark_signature = "© Dabeey 2025"
        
        self.root.configure(bg=self.bg_color)
        
        # Variables
        self.image_path = ""
        self.original_image = None
        self.current_image = None
        self.watermark_text = self.watermark_signature
        self.watermark_text = "Your Watermark"
        self.watermark_color = "#FFFFFF"
        self.opacity = 0.7
        self.font_size = 36
        self.position = "Bottom Right"
        self.offset_x = 0
        self.offset_y = 0
        self.drag_data = {"x": 0, "y": 0, "item": None}
        
        # Undo/Redo stacks
        self.undo_stack = deque(maxlen=10)
        self.redo_stack = deque(maxlen=10)
        
        # Font settings
        self.font_family = "Arial"
        self.available_fonts = ["Arial", "Helvetica", "Times New Roman", "Courier New", "Verdana", "Georgia", "Palatino"]
        
        # Create UI
        self.create_widgets()
        self.setup_modern_ui()
        
    def create_widgets(self):
        # Main container
        self.main_container = tk.Frame(self.root, bg=self.bg_color)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left Frame - Image Preview with canvas for dragging
        self.left_frame = tk.Frame(self.main_container, bg=self.bg_color)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(self.left_frame, bg='#1d1d1d', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Right Frame - Controls
        self.right_frame = tk.Frame(self.main_container, width=350, bg=self.panel_color)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        
        # Toolbar section
        self.toolbar_frame = tk.Frame(self.right_frame, bg=self.panel_color)
        self.toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Undo/Redo buttons
        self.undo_btn = self.create_tool_button("↩ Undo", self.undo_action, self.toolbar_frame)
        self.redo_btn = self.create_tool_button("↪ Redo", self.redo_action, self.toolbar_frame)
        self.upload_btn = self.create_tool_button("📁 Upload", self.upload_image, self.toolbar_frame)
        
        # Watermark Text
        self.create_section("Watermark Text")
        self.text_entry = tk.Entry(self.right_frame, bg="#4d4d4d", fg=self.text_color, 
                                 insertbackground=self.text_color, relief=tk.FLAT)
        self.text_entry.insert(0, self.watermark_text)
        self.text_entry.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Font Settings
        self.create_section("Font Settings")
        
        # Font Family
        tk.Label(self.right_frame, text="Font Family:", bg=self.panel_color, fg=self.text_color).pack(anchor=tk.W, padx=10)
        self.font_var = tk.StringVar(value=self.font_family)
        self.font_menu = ttk.Combobox(self.right_frame, textvariable=self.font_var, 
                                    values=self.available_fonts, state="readonly")
        self.font_menu.pack(fill=tk.X, padx=10, pady=(0, 5))
        self.font_menu.bind("<<ComboboxSelected>>", self.update_preview)
        
        # Font Size
        tk.Label(self.right_frame, text="Font Size:", bg=self.panel_color, fg=self.text_color).pack(anchor=tk.W, padx=10)
        self.font_size_slider = tk.Scale(self.right_frame, from_=10, to=120, orient=tk.HORIZONTAL,
                                       bg=self.panel_color, fg=self.text_color, highlightthickness=0,
                                       activebackground=self.accent_color, command=self.update_preview)
        self.font_size_slider.set(self.font_size)
        self.font_size_slider.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Watermark Appearance
        self.create_section("Appearance")
        
        # Opacity
        tk.Label(self.right_frame, text="Opacity:", bg=self.panel_color, fg=self.text_color).pack(anchor=tk.W, padx=10)
        self.opacity_slider = tk.Scale(self.right_frame, from_=0.1, to=1.0, resolution=0.1,
                                     orient=tk.HORIZONTAL, bg=self.panel_color, fg=self.text_color,
                                     highlightthickness=0, activebackground=self.accent_color,
                                     command=self.update_preview)
        self.opacity_slider.set(self.opacity)
        self.opacity_slider.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Color Picker
        self.color_button = tk.Button(self.right_frame, text="Text Color", command=self.choose_color,
                                    bg="#4d4d4d", fg=self.text_color, relief=tk.FLAT, bd=0,
                                    activebackground=self.accent_color)
        self.color_button.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Position Controls
        self.create_section("Position")
        
        # Position Presets
        tk.Label(self.right_frame, text="Preset Positions:", bg=self.panel_color, fg=self.text_color).pack(anchor=tk.W, padx=10)
        self.position_var = tk.StringVar(value=self.position)
        positions = [
            "Top Left", "Top Center", "Top Right",
            "Center Left", "Center", "Center Right",
            "Bottom Left", "Bottom Center", "Bottom Right",
            "Custom"
        ]
        self.position_menu = ttk.Combobox(self.right_frame, textvariable=self.position_var,
                                        values=positions, state="readonly")
        self.position_menu.pack(fill=tk.X, padx=10, pady=(0, 10))
        self.position_menu.bind("<<ComboboxSelected>>", self.update_preview)
        
        # Numeric Positioning
        tk.Label(self.right_frame, text="Manual Positioning:", bg=self.panel_color, fg=self.text_color).pack(anchor=tk.W, padx=10)
        
        pos_frame = tk.Frame(self.right_frame, bg=self.panel_color)
        pos_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # X Position
        tk.Label(pos_frame, text="X:", bg=self.panel_color, fg=self.text_color).pack(side=tk.LEFT)
        self.x_pos_slider = tk.Scale(pos_frame, from_=-100, to=100, orient=tk.HORIZONTAL,
                                    bg=self.panel_color, fg=self.text_color, highlightthickness=0,
                                    activebackground=self.accent_color, command=self.update_position_from_sliders)
        self.x_pos_slider.set(0)
        self.x_pos_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Y Position
        tk.Label(pos_frame, text="Y:", bg=self.panel_color, fg=self.text_color).pack(side=tk.LEFT)
        self.y_pos_slider = tk.Scale(pos_frame, from_=-100, to=100, orient=tk.HORIZONTAL,
                                    bg=self.panel_color, fg=self.text_color, highlightthickness=0,
                                    activebackground=self.accent_color, command=self.update_position_from_sliders)
        self.y_pos_slider.set(0)
        self.y_pos_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Action Buttons
        self.create_section("Actions")
        self.apply_btn = tk.Button(self.right_frame, text="Apply Watermark", command=self.apply_watermark,
                                 bg=self.button_color, fg=self.text_color, relief=tk.FLAT, bd=0,
                                 activebackground=self.button_hover)
        self.apply_btn.pack(fill=tk.X, padx=10, pady=5)
        
        self.save_btn = tk.Button(self.right_frame, text="Save Image", command=self.save_image,
                                bg="#5a7a5a", fg=self.text_color, relief=tk.FLAT, bd=0,
                                activebackground="#6a8a6a", state=tk.DISABLED)
        self.save_btn.pack(fill=tk.X, padx=10, pady=5)
        
        # Bind events
        self.text_entry.bind("<KeyRelease>", self.update_preview)
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.end_drag)
        
    def setup_modern_ui(self):
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure combobox style
        style.configure('TCombobox', fieldbackground="#4d4d4d", background="#4d4d4d",
                      foreground=self.text_color, selectbackground=self.accent_color)
        
        # Configure scale style
        style.configure('Horizontal.TScale', background=self.panel_color, troughcolor="#4d4d4d")
        
        # Configure button styles
        self.root.option_add('*Button*highlightBackground', self.panel_color)
        self.root.option_add('*Button*highlightColor', self.panel_color)
        self.root.option_add('*Button*background', self.button_color)
        self.root.option_add('*Button*foreground', self.text_color)
        self.root.option_add('*Button*activeBackground', self.button_hover)
        
    def create_section(self, title):
        frame = tk.Frame(self.right_frame, bg=self.panel_color)
        frame.pack(fill=tk.X, pady=(10, 5))
        tk.Label(frame, text=title, bg=self.panel_color, fg=self.accent_color,
                font=('Helvetica', 10, 'bold')).pack(side=tk.LEFT, padx=10)
        
    def create_tool_button(self, text, command, parent):
        btn = tk.Button(parent, text=text, command=command, bg="#4d4d4d", fg=self.text_color,
                      relief=tk.FLAT, bd=0, padx=10, pady=5, activebackground=self.accent_color)
        btn.pack(side=tk.LEFT, padx=2)
        return btn
        
    def update_position_from_sliders(self, event=None):
        if self.position_var.get() != "Custom":
            self.position_var.set("Custom")
        
        # Convert slider values (-100 to 100) to pixel offsets
        img_width = self.original_image.width if self.original_image else 1000
        img_height = self.original_image.height if self.original_image else 1000
        
        self.offset_x = int((self.x_pos_slider.get() / 100) * (img_width / 2))
        self.offset_y = int((self.y_pos_slider.get() / 100) * (img_height / 2))
        
        self.update_preview()
        
    def upload_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.webp")]
        )
        if file_path:
            try:
                self.image_path = file_path
                self.original_image = Image.open(self.image_path)
                self.current_image = self.original_image.copy()
                self.update_preview()
                self.apply_btn.config(state=tk.NORMAL)
                self.save_btn.config(state=tk.DISABLED)
                self.clear_undo_stacks()
                
                # Reset position sliders when new image is loaded
                self.x_pos_slider.set(0)
                self.y_pos_slider.set(0)
                self.offset_x = 0
                self.offset_y = 0
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open image: {str(e)}")
                self.image_path = ""
                self.original_image = None
    
    def choose_color(self):
        color = colorchooser.askcolor(title="Choose Watermark Color", initialcolor=self.watermark_color)
        if color[1]:
            self.watermark_color = color[1]
            self.update_preview()
    
    def update_preview(self, event=None):
        if not self.image_path or not self.original_image:
            return
            
        try:
            # Get current settings
            self.watermark_text = self.text_entry.get()
            if not self.watermark_text.strip():
                return
                
            self.font_family = self.font_var.get()
            self.font_size = self.font_size_slider.get()
            self.opacity = self.opacity_slider.get()
            self.position = self.position_var.get()
            
            # Create preview
            preview = self.original_image.copy()
            watermarked = self.add_watermark(preview, preview=True)
            
            # Display the image
            self.display_image(watermarked)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update preview: {str(e)}")
    
    def add_watermark(self, image, preview=False):
        try:
            if not self.watermark_text.strip():
                return image
                
            # Create a transparent layer for the watermark
            watermark = Image.new("RGBA", image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark)
            
            # Convert color to RGB and add alpha for opacity
            rgb = Image.new("RGB", (1, 1), self.watermark_color)
            r, g, b = rgb.getpixel((0, 0))
            alpha = int(255 * self.opacity)
            
            # Load font
            try:
                font = ImageFont.truetype(self.font_family + ".ttf", self.font_size)
            except (OSError, IOError):
                try:
                    font = ImageFont.truetype("arial.ttf", self.font_size)
                except:
                    font = ImageFont.load_default()
            
            # Calculate text size
            text_bbox = draw.textbbox((0, 0), self.watermark_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            margin = 20
            positions = {
                "Top Left": (margin, margin),
                "Top Center": ((image.width - text_width) // 2, margin),
                "Top Right": (image.width - text_width - margin, margin),
                "Center Left": (margin, (image.height - text_height) // 2),
                "Center": ((image.width - text_width) // 2, 
                          (image.height - text_height) // 2),
                "Center Right": (image.width - text_width - margin,
                               (image.height - text_height) // 2),
                "Bottom Left": (margin, image.height - text_height - margin),
                "Bottom Center": ((image.width - text_width) // 2,
                                 image.height - text_height - margin),
                "Bottom Right": (image.width - text_width - margin,
                               image.height - text_height - margin),
                "Custom": (image.width // 2 + self.offset_x - text_width // 2,
                          image.height // 2 + self.offset_y - text_height // 2)
            }
            
            x, y = positions.get(self.position, (margin, margin))
            
            # Add text to watermark layer
            draw.text((x, y), self.watermark_text, font=font, fill=(r, g, b, alpha))
            
            # Composite the images
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
                
            watermarked = Image.alpha_composite(image, watermark)
            
            if not preview and image.mode != 'RGBA':
                watermarked = watermarked.convert(image.mode)
            
            return watermarked
            
        except Exception as e:
            raise e
    
    def display_image(self, image):
        try:
            self.canvas.delete("all")
            
            # Calculate available space
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                return
                
            # Calculate aspect ratio
            img_ratio = image.width / image.height
            canvas_ratio = canvas_width / canvas_height
            
            if img_ratio > canvas_ratio:
                # Image is wider than canvas
                new_width = canvas_width
                new_height = int(canvas_width / img_ratio)
            else:
                # Image is taller than canvas
                new_height = canvas_height
                new_width = int(canvas_height * img_ratio)
            
            # Calculate position to center the image
            x_pos = (canvas_width - new_width) // 2
            y_pos = (canvas_height - new_height) // 2
            
            # Resize with high-quality downsampling
            resized_image = image.resize((new_width, new_height), Image.LANCZOS)
            
            # Convert to PhotoImage
            self.photo_img = ImageTk.PhotoImage(resized_image)
            
            # Display on canvas
            self.canvas.create_image(x_pos, y_pos, anchor=tk.NW, image=self.photo_img)
            
            # Store scaling factors for drag calculations
            self.scale_x = image.width / new_width
            self.scale_y = image.height / new_height
            
        except Exception as e:
            messagebox.showerror("Display Error", f"Failed to display image: {str(e)}")
    
    def start_drag(self, event):
        if self.position_var.get() != "Custom":
            self.position_var.set("Custom")
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        
    def on_drag(self, event):
        if self.position_var.get() != "Custom":
            return
            
        delta_x = event.x - self.drag_data["x"]
        delta_y = event.y - self.drag_data["y"]
        
        self.offset_x += delta_x * self.scale_x
        self.offset_y += delta_y * self.scale_y
        
        # Update sliders to match new position
        if self.original_image:
            img_width = self.original_image.width
            img_height = self.original_image.height
            
            x_percent = int((self.offset_x / (img_width / 2)) * 100)
            y_percent = int((self.offset_y / (img_height / 2)) * 100)
            
            # Clamp values to slider range
            x_percent = max(-100, min(100, x_percent))
            y_percent = max(-100, min(100, y_percent))
            
            self.x_pos_slider.set(x_percent)
            self.y_pos_slider.set(y_percent)
        
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        
        self.update_preview()
    
    def end_drag(self, event):
        self.drag_data["x"] = 0
        self.drag_data["y"] = 0
    
    def apply_watermark(self):
        try:
            if not self.image_path or not self.original_image:
                return
                
            if not self.watermark_text.strip():
                messagebox.showwarning("Warning", "Please enter watermark text")
                return
                
            # Save current state to undo stack
            if self.current_image:
                self.push_undo(self.current_image.copy())
                
            watermarked = self.add_watermark(self.original_image.copy())
            self.current_image = watermarked
            self.display_image(watermarked)
            self.save_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply watermark: {str(e)}")
    
    def save_image(self):
        if not self.image_path or not self.current_image:
            return
            
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"), 
                ("JPEG files", "*.jpg;*.jpeg"), 
                ("WebP files", "*.webp"),
                ("All files", "*.*")
            ],
            initialfile=os.path.splitext(os.path.basename(self.image_path))[0] + "_watermarked"
        )
        
        if save_path:
            try:
                if save_path.lower().endswith(('.jpg', '.jpeg')):
                    if self.current_image.mode == 'RGBA':
                        self.current_image = self.current_image.convert("RGB")
                    self.current_image.save(save_path, quality=95)
                elif save_path.lower().endswith('.webp'):
                    self.current_image.save(save_path, quality=95)
                else:
                    self.current_image.save(save_path)
                    
                messagebox.showinfo("Success", "Image saved successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {str(e)}")
    
    def push_undo(self, image):
        self.undo_stack.append(image)
        self.redo_stack.clear()
        self.update_undo_redo_buttons()
    
    def undo_action(self):
        if self.undo_stack:
            self.redo_stack.append(self.current_image.copy())
            self.current_image = self.undo_stack.pop()
            self.display_image(self.current_image)
            self.update_undo_redo_buttons()
    
    def redo_action(self):
        if self.redo_stack:
            self.undo_stack.append(self.current_image.copy())
            self.current_image = self.redo_stack.pop()
            self.display_image(self.current_image)
            self.update_undo_redo_buttons()
    
    def clear_undo_stacks(self):
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.update_undo_redo_buttons()
    
    def update_undo_redo_buttons(self):
        self.undo_btn.config(state=tk.NORMAL if self.undo_stack else tk.DISABLED)
        self.redo_btn.config(state=tk.NORMAL if self.redo_stack else tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = WatermarkApp(root)
    root.mainloop()