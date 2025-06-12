import tkinter as tk

class Spinner(tk.Frame):
    
    def __init__(self, parent, length=100, text="", **kwargs):
        super().__init__(parent, **kwargs)
        self.length = length
        self.height = 20  
        self.text = text
        self.canvas = tk.Canvas(self, width=self.length, height=self.height, bg="white", highlightthickness=0)
        self.canvas.pack()
        self.text_id = self.canvas.create_text(self.length/2, self.height/2, text=self.text, fill="black", font=("tahoma", 10))
        self.block_width = self.length / 5   
        self.block_height = self.height
        self.block_x = -self.block_width       
        self.block = self.canvas.create_rectangle(self.block_x, 0, self.block_x + self.block_width, self.block_height, fill="green", width=0)
        self.animation_running = False

    def start(self):
        self.animation_running = True
        self.animate()
        self.pack(pady=10)

    def animate(self):
        if not self.animation_running:
            return
        
        self.block_x += 5
        if self.block_x > self.length:
            self.block_x = -self.block_width
        
        self.canvas.coords(self.block, self.block_x, 0, self.block_x + self.block_width, self.block_height)
       
        self.after(50, self.animate)

    def stop(self):
        self.animation_running = False
        self.pack_forget()

    def update_text(self, new_text):
        self.text = new_text
        self.canvas.itemconfigure(self.text_id, text=self.text)