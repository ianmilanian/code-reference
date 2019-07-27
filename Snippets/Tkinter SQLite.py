import sqlite3
import tkinter as tk

from functools import partial

def select_channels(client):
    def scrollable_frame(root):
        canvas = tk.Canvas(root)
        frame  = tk.Frame(canvas)
        scroll = tk.Scrollbar(root, command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set, scrollregion=canvas.bbox("all"))
        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
        scroll.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        canvas.create_window((0,0), window=frame, anchor=tk.NW)
        frame.bind("<Configure>", lambda event, canvas=canvas: canvas.configure(scrollregion=canvas.bbox("all")))
        return frame
    def set_state(id):
        state = vars[id].get()
        db.execute("UPDATE channels SET active=? WHERE id=?", (state,id,))
        db.commit()
    def tk_close():
        mode[0] = 0
        root.destroy()
    def historical():
        mode[0] = 1
        root.destroy()
    def clear():
        db.execute("DROP TABLE IF EXISTS history")
        db.isolation_level = None
        db.execute("VACUUM")
        db.isolation_level = ""
        db.commit()
        buttons.winfo_children()[-1]["state"] = tk.DISABLED
    
    with sqlite3.connect("data.db") as db:
        root  = tk.Tk()
        frame = scrollable_frame(root)
        vars, mode = {}, [0]
        for row in db.execute("SELECT * FROM channels").fetchall():
            id, title, state = row
            vars[id] = tk.IntVar()
            vars[id].set(state)
            title = "".join([char if ord(char) in range(65536) else "\uFFFD" for char in title]) # strip non BMP chars
            tk.Checkbutton(frame, text=title, variable=vars[id], command=partial(set_state, id)).pack(anchor=tk.W)
        
        buttons = tk.Frame(frame)
        buttons.pack(side=tk.BOTTOM, fill=tk.X, expand=tk.YES)
        kwargs  = {"side":tk.LEFT, "fill":tk.X, "expand":tk.YES, "padx":"3m", "pady":"1m"}
        history = db.execute("SELECT * FROM sqlite_master WHERE type='table' AND name='history'").fetchone()
        history = "normal" if history else "disabled"
        tk.Button(buttons, text="Historical",                   command=historical).pack(**kwargs)
        tk.Button(buttons, text="Clear History", state=history, command=clear     ).pack(**kwargs)
        root.protocol("WM_DELETE_WINDOW", tk_close)
        
        try:
            root.iconbitmap("{}/icon.ico".format(sys._MEIPASS))
        except: pass
        root.geometry("364x700")
        root.mainloop()
        channels = set([v[0] for v in db.execute("SELECT id FROM channels WHERE active=1").fetchall()])
        
    return channels
