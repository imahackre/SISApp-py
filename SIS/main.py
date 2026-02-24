import customtkinter as ctk
from tkinter import ttk, messagebox, Listbox, Toplevel, BooleanVar
import data_handler as dh

active_dropdowns = []

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class SearchableCombobox(ctk.CTkFrame):
    """a custom searchable combobox widget with dropdown functionality.
    
    provides a text entry field with searchable dropdown list that filters
    options based on user input.
    """
    def __init__(self, parent, placeholder_text="Select...", width=200, height=30, dropdown_height=150, **kwargs):
        super().__init__(parent, fg_color="transparent")
        
        self.width = width
        self.height = height
        self.dropdown_height = dropdown_height
        self.placeholder_text = placeholder_text
        self.selected_value = ""
        self.items = []
        self.filtered_items = []
        self.dropdown_window = None
        self.listbox = None
        
        # Create the entry field
        self.entry = ctk.CTkEntry(self, width=width, height=height, placeholder_text=placeholder_text)
        self.entry.pack()
        self.entry.bind("<KeyRelease>", self.on_key_release)
        self.entry.bind("<FocusIn>", self.on_focus_in)
        self.entry.bind("<Return>", self.on_enter)
        self.entry.bind("<Down>", self.on_arrow_down)
        
    def set_items(self, items):
        self.items = items
        self.filtered_items = items
        
    def get(self):
        return self.selected_value if self.selected_value else self.entry.get()
        
    def set(self, value):
        self.selected_value = value
        self.entry.delete(0, "end")
        if value:
            self.entry.insert(0, value)
        
    def on_key_release(self, event):
        search_text = self.entry.get().lower()
        self.filtered_items = [item for item in self.items if search_text in item.lower()]
        if self.dropdown_window and self.dropdown_window.winfo_exists():
            self.update_listbox()
        else:
            self.show_dropdown()
            
    def on_focus_in(self, event):
        if not self.dropdown_window or not self.dropdown_window.winfo_exists():
            self.show_dropdown()
            
    def on_enter(self, event):
        if self.filtered_items:
            self.set(self.filtered_items[0])
            self.hide_dropdown()
            # clear focus by calling parent's reset method
            if hasattr(self.master, 'reset_focus_state'):
                self.master.reset_focus_state()
            else:
                self.master.focus_set()
            self.after(10, self.hide_dropdown)
            
    def on_arrow_down(self, event):
        if not self.dropdown_window or not self.dropdown_window.winfo_exists():
            self.show_dropdown()
        elif self.listbox and self.listbox.size() > 0:
            self.listbox.selection_set(0)
            self.listbox.focus_set()
            
    def show_dropdown(self):
        if self.dropdown_window and self.dropdown_window.winfo_exists():
            return
            
        self.dropdown_window = Toplevel(self)
        self.dropdown_window.overrideredirect(True)
        self.dropdown_window.configure(bg="#1a1a1a")

        active_dropdowns.append(self)
        self._in_active_dropdowns = True
        
        # position of dropdown
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.height
        self.dropdown_window.geometry(f"{self.width}x{self.dropdown_height}+{x}+{y}")
        
        # listbox with scrollbar
        list_frame = ctk.CTkFrame(self.dropdown_window, fg_color="#1a1a1a")
        list_frame.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        
        self.listbox = Listbox(list_frame, yscrollcommand=scrollbar.set, 
                              bg="#2b2b2b", fg="white", selectbackground="#2a942a",
                              activestyle="none", highlightthickness=0, borderwidth=0,
                              font=("Roboto", 10))
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        self.listbox.bind("<ButtonRelease-1>", self.on_listbox_select)
        self.listbox.bind("<Motion>", self.on_listbox_motion)
        self.listbox.bind("<Leave>", self.on_listbox_leave)
        
        self.update_listbox()
        self.dropdown_window.bind("<Escape>", lambda e: self.hide_dropdown())
        self.dropdown_window.focus_set()
        
    def hide_dropdown(self):
        if self.dropdown_window and self.dropdown_window.winfo_exists():
            if self in active_dropdowns:
                active_dropdowns.remove(self)
            self.dropdown_window.destroy()
            self.dropdown_window = None
            self.listbox = None
                
    def update_listbox(self):
        if not self.listbox:
            return
            
        self.listbox.delete(0, "end")
        for item in self.filtered_items:
            self.listbox.insert("end", item)
            
    def on_listbox_select(self, event):
        if self.listbox.curselection():
            selected = self.listbox.get(self.listbox.curselection())
            self.set(selected)
            self.hide_dropdown()

            if hasattr(self.master, 'reset_focus_state'):
                self.master.reset_focus_state()
            else:
                self.master.focus_set()
            self.after(10, self.hide_dropdown)
            
    def on_listbox_motion(self, event):
        index = self.listbox.nearest(event.y)
        if index >= 0:
            self.listbox.selection_clear(0, "end")
            self.listbox.selection_set(index)
            self.listbox.activate(index)
            
    def on_listbox_leave(self, event):
        self.listbox.selection_clear(0, "end")
        

class SISApp(ctk.CTk):
    """Student Information System Application.
    
    A comprehensive GUI application for managing student, program, and college data.
    Features tabbed interface with CRUDL operations for each entity type.
    """
    def __init__(self):
        """Initialize the SIS application with main window and tabs."""
        super().__init__()
        self.title("Student Information System")
        self.geometry("1200x750")

        self.setup_treeview_style()

        self.tabview = ctk.CTkTabview(self, command=self.on_tab_change)
        self.tabview.pack(expand=True, fill="both", padx=20, pady=20)

        self.student_tab = self.tabview.add("  Students  ")
        self.program_tab = self.tabview.add("  Programs  ")
        self.college_tab = self.tabview.add("  Colleges  ")
        
        # record count labels for each tab
        self.student_count_label = None
        self.program_count_label = None
        self.college_count_label = None

        self.filtered_student_count = None
        self.filtered_program_count = None

        self.setup_college_ui()
        self.setup_program_ui()
        self.setup_student_ui()
        
        # dropdown behavior
        self.bind_all("<Button-1>", self.on_global_click)
        self.last_focused_entry = None
        
    def reset_focus_state(self):
        # clear focus from all widgets by setting focus to main window
        self.focus_set()
        self.last_focused_entry = None
        
    def on_global_click(self, event):
        widget = event.widget
        current = widget
        while current and hasattr(current, 'master'):
            if isinstance(current, ctk.CTkOptionMenu):
                return
            current = current.master
        
        for dropdown in active_dropdowns[:]:
            if dropdown.dropdown_window and dropdown.dropdown_window.winfo_exists():
                current = widget
                is_dropdown_click = False
                while current and hasattr(current, 'master'):
                    if current == dropdown.dropdown_window or current == dropdown.entry:
                        is_dropdown_click = True
                        break
                    current = current.master
                
                if not is_dropdown_click:
                    dropdown.hide_dropdown()

    def setup_treeview_style(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#2b2b2b", 
                        foreground="white", 
                        fieldbackground="#2b2b2b", 
                        rowheight=30,
                        borderwidth=0)
        style.map('Treeview', background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading", 
                        background="#333333", 
                        foreground="white", 
                        relief="flat",
                        font=("Roboto", 10, "bold"))
        style.map("Treeview.Heading", 
                  background=[("active", "#4a4a4a")],
                  foreground=[("active", "white")])

    def update_all_record_counts(self):
        # update college count
        if self.college_count_label:
            college_count = len(dh.college_db.load_data())
            self.college_count_label.configure(text=f"Total Records: {college_count}")
        
        # update program count
        if self.program_count_label:
            if hasattr(self, 'filtered_program_count') and self.filtered_program_count is not None:
                total_program_count = len(dh.program_db.load_data())
                self.program_count_label.configure(text=f"Showing: {self.filtered_program_count} / {total_program_count} records")
            else:
                program_count = len(dh.program_db.load_data())
                self.program_count_label.configure(text=f"Total Records: {program_count}")
        
        # update student count
        if self.student_count_label:
            if hasattr(self, 'filtered_student_count') and self.filtered_student_count is not None:
                total_student_count = len(dh.student_db.load_data())
                self.student_count_label.configure(text=f"Showing: {self.filtered_student_count} / {total_student_count} records")
            else:
                student_count = len(dh.student_db.load_data())
                self.student_count_label.configure(text=f"Total Records: {student_count}")

    # COLLEGES SECTION

    def create_button_frame(self, parent, add_cmd, update_cmd, delete_cmd, clear_cmd):
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="Add", width=90, fg_color="#2a942a", command=add_cmd).grid(row=0, column=0, padx=2, pady=2)
        ctk.CTkButton(btn_frame, text="Update", width=90, command=update_cmd).grid(row=0, column=1, padx=2, pady=2)
        ctk.CTkButton(btn_frame, text="Delete", width=90, fg_color="#942a2a", hover_color="#701e1e", command=delete_cmd).grid(row=1, column=0, padx=2, pady=2)
        ctk.CTkButton(btn_frame, text="Clear", width=90, fg_color="gray", command=clear_cmd).grid(row=1, column=1, padx=2, pady=2)
        
        return btn_frame

    def setup_college_ui(self):
        # left input form
        self.coll_form = ctk.CTkFrame(self.college_tab)
        self.coll_form.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(self.coll_form, text="College Information", font=("Roboto", 16, "bold")).pack(pady=10)

        self.entry_college_code = ctk.CTkEntry(self.coll_form, placeholder_text="College Code", width=200)
        self.entry_college_code.pack(pady=5, padx=10)

        self.entry_college_name = ctk.CTkEntry(self.coll_form, placeholder_text="College Name", width=200)
        self.entry_college_name.pack(pady=5, padx=10)

        self.create_button_frame(self.coll_form, self.add_college, self.update_college, 
                                self.delete_college, self.clear_college_fields)

        # right table
        table_frame = ctk.CTkFrame(self.college_tab)
        table_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_rowconfigure(1, weight=0)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_columnconfigure(1, weight=0)

        # record count label for colleges
        self.college_count_label = ctk.CTkLabel(table_frame, text="Total Records: 0", 
                                                font=("Roboto", 12, "bold"), text_color="#2a942a")
        self.college_count_label.grid(row=1, column=1, sticky="e", padx=5, pady=5)

        self.college_tree = ttk.Treeview(table_frame, columns=("Code", "Name"), show="headings")
        self.college_tree.heading("Code", text="College Code")
        self.college_tree.heading("Name", text="College Name")
        self.college_tree.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.college_tree.bind("<<TreeviewSelect>>", self.on_college_select)
        
        self.refresh_college_table()
        self.update_all_record_counts()

    def add_college(self):
        try:
            code = self.entry_college_code.get().strip().upper()
            name = self.entry_college_name.get().strip()
            if not code or not name:
                messagebox.showerror("Error", "All fields are required!")
                return
            
            if not code.isalnum():
                messagebox.showerror("Error", "College code must be alphanumeric!")
                return
            
            data = dh.college_db.load_data()
            if any(c['code'] == code for c in data):
                messagebox.showerror("Error", "College Code already exists!")
                return
            
            data.insert(0, {'code': code, 'name': name})
            dh.college_db.save_data(data)
            self.refresh_college_table()
            self.update_college_dropdown()
            self.update_all_record_counts()
            messagebox.showinfo("College Added", "College added successfully!")
            self.clear_college_fields()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add college: {str(e)}")

    def update_college(self):
        code = self.entry_college_code.get().strip()
        name = self.entry_college_name.get().strip()
        if not code or not name:
            messagebox.showerror("Error", "All fields are required!")
            return
        
        data = dh.college_db.load_data()
        changed = False
        for c in data:
            if c['code'] == code:
                if c['name'] != name:
                    c['name'] = name
                    changed = True
                break
        
        if changed:
            dh.college_db.save_data(data)
            self.refresh_college_table()
            self.update_college_dropdown()
            self.update_all_record_counts()
            messagebox.showinfo("College Updated", "College updated successfully!")
        self.clear_college_fields()

    def delete_college(self):
        code = self.entry_college_code.get().strip()
        if not code:
            return
        
        # check if college is being used by programs (might change this to allow for deletion even if)
        programs = dh.program_db.load_data()
        if any(p['college_code'] == code for p in programs):
            messagebox.showerror("Error", "Cannot delete. College has programs!")
            return
            
        if messagebox.askyesno("Confirm", f"Delete college {code}?"):
            data = dh.college_db.load_data()
            new_data = [c for c in data if c['code'] != code]
            dh.college_db.save_data(new_data)
            self.refresh_college_table()
            self.update_college_dropdown()
            self.update_all_record_counts()
            messagebox.showinfo("College Deleted", "College deleted successfully!")
            self.clear_college_fields()

    def clear_college_fields(self):
        self.entry_college_code.configure(state="normal")
        self.entry_college_code.delete(0, 'end')
        self.entry_college_name.delete(0, 'end')

    def on_college_select(self, event):
        selected = self.college_tree.selection()
        if not selected:
            return
        val = self.college_tree.item(selected[0])['values']
        self.clear_college_fields()
        self.entry_college_code.delete(0, 'end')
        self.entry_college_code.insert(0, val[0])
        self.entry_college_code.configure(state="disabled")
        self.entry_college_name.delete(0, 'end')
        self.entry_college_name.insert(0, val[1])

    def refresh_college_table(self):
        for item in self.college_tree.get_children():
            self.college_tree.delete(item)
        for college in dh.college_db.load_data():
            self.college_tree.insert("", "end", values=(college['code'], college['name']))

    # PROGRAMS SECTION

    def setup_program_ui(self):
        self.prog_form = ctk.CTkFrame(self.program_tab)

        # left side form
        self.prog_form.pack(side="left", fill="y", padx=10, pady=10)
        ctk.CTkLabel(self.prog_form, text="Program Information", font=("Roboto", 16, "bold")).pack(pady=10)

        self.entry_prog_code = ctk.CTkEntry(self.prog_form, placeholder_text="Program Code", width=200)
        self.entry_prog_code.pack(pady=5)
        self.entry_prog_name = ctk.CTkEntry(self.prog_form, placeholder_text="Program Name", width=200)
        self.entry_prog_name.pack(pady=5)

        self.combo_prog_college = ctk.CTkOptionMenu(self.prog_form, width=200, values=["Select College"], command=lambda value: self.reset_focus_state())
        self.combo_prog_college.pack(pady=5)

        self.create_button_frame(self.prog_form, self.add_program, self.update_program,
                                self.delete_program, self.clear_program_fields)

        table_frame = ctk.CTkFrame(self.program_tab)

        # right side table
        table_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        table_frame.grid_rowconfigure(0, weight=0)
        table_frame.grid_rowconfigure(1, weight=1)
        table_frame.grid_rowconfigure(2, weight=0)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # search and filter
        sortFilter_frame = ctk.CTkFrame(table_frame)
        sortFilter_frame.grid(row=0, column=0, sticky="nsew")

        search_filter_frame = ctk.CTkFrame(sortFilter_frame, fg_color="transparent")
        search_filter_frame.pack()

        self.entry_prog_search = ctk.CTkEntry(search_filter_frame, placeholder_text="Search programs...", width=450)
        self.entry_prog_search.pack(side="left", padx=10, pady=10)
        self.entry_prog_search.bind("<KeyRelease>", self.search_program)

        filter_button = ctk.CTkButton(search_filter_frame, text="Filter", command=self.open_filter_window_prog, width=50)
        filter_button.pack(side="right", padx=10, pady=10)
        
        # program list
        tree_container = ctk.CTkFrame(table_frame)
        tree_container.grid(row=1, column=0, sticky="nsew")
        
        self.program_tree = ttk.Treeview(tree_container, columns=("Program Code", "Program Name", "College Code"), show="headings")
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.program_tree.yview)
        self.program_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.program_tree.pack(side="left", fill="both", expand=True)
        
        # record count label for programs
        self.program_count_label = ctk.CTkLabel(table_frame, text="Total Records: 0", 
                                               font=("Roboto", 12, "bold"), text_color="#2a942a")
        self.program_count_label.grid(row=2, column=0, sticky="e", padx=5, pady=5)

        for col in ("Program Code", "Program Name", "College Code"):
            self.program_tree.heading(col, text=col + " ↕", command=lambda c=col: self.sort_program_table(c, False))
            self.program_tree.column(col, width=100)
        
        self.program_tree.bind("<<TreeviewSelect>>", self.on_program_select)
        self.refresh_program_table()
        self.update_college_dropdown()
        self.update_all_record_counts()

    def add_program(self):
        try:
            code, name, coll = self.entry_prog_code.get().strip().upper(), self.entry_prog_name.get().strip(), self.combo_prog_college.get()
            if not all([code, name, coll]) or coll == "Select College":
                messagebox.showerror("Error", "All fields required!")
                return
            
            if not code.isalnum():
                messagebox.showerror("Error", "Program code must be alphanumeric!")
                return
                
            data = dh.program_db.load_data()
            if any(p['code'] == code for p in data):
                messagebox.showerror("Error", "Program Code exists!")
                return
            data.insert(0, {'code': code, 'name': name, 'college_code': coll})
            dh.program_db.save_data(data)
            self.refresh_program_table()
            self.update_program_dropdown()
            self.update_all_record_counts()
            messagebox.showinfo("Program Added", "Program added successfully!")
            self.clear_program_fields()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add program: {str(e)}")

    def update_program(self):
        code = self.entry_prog_code.get().strip()
        name = self.entry_prog_name.get().strip()
        coll = self.combo_prog_college.get()
        
        if not all([code, name, coll]) or coll == "Select College":
            messagebox.showerror("Error", "All fields required!")
            return
            
        data = dh.program_db.load_data()
        changed = False
        for p in data:
            if p['code'] == code:
                if p['name'] != name or p['college_code'] != coll:
                    p['name'], p['college_code'] = name, coll
                    changed = True
                break
        
        if changed:
            dh.program_db.save_data(data)
            self.refresh_program_table()
            self.update_program_dropdown()
            self.update_all_record_counts()
            messagebox.showinfo("Program Updated", "Program updated successfully!")
        self.clear_program_fields()

    def delete_program(self):
        code = self.entry_prog_code.get().strip()
        if not code:
            return
            
        students = dh.student_db.load_data()
        if any(s['program_code'] == code for s in students):
            messagebox.showerror("Error", "Cannot delete. Students enrolled!")
            return
            
        if messagebox.askyesno("Confirm", f"Delete program {code}?"):
            data = dh.program_db.load_data()
            new_data = [p for p in data if p['code'] != code]
            dh.program_db.save_data(new_data)
            self.refresh_program_table()
            self.update_program_dropdown()
            self.update_all_record_counts()
            messagebox.showinfo("Program Deleted", "Program deleted successfully!")
            self.clear_program_fields()

    def clear_program_fields(self):
        self.entry_prog_code.configure(state="normal")
        self.entry_prog_code.delete(0, 'end')
        self.entry_prog_name.delete(0, 'end')
        self.combo_prog_college.set('Select College')

    def on_program_select(self, event):
        selected = self.program_tree.selection()
        if not selected:
            return
        val = self.program_tree.item(selected[0])['values']
        self.clear_program_fields()
        self.entry_prog_code.delete(0, 'end')
        self.entry_prog_code.insert(0, val[0])
        self.entry_prog_code.configure(state="disabled")
        self.entry_prog_name.delete(0, 'end')
        self.entry_prog_name.insert(0, val[1])
        self.combo_prog_college.set(val[2])

    def update_college_dropdown(self):
        codes = [c['code'] for c in dh.college_db.load_data()]
        self.combo_prog_college.configure(values=codes if codes else ["No Colleges"])

    def refresh_program_table(self):
        for item in self.program_tree.get_children():
            self.program_tree.delete(item)
        for p in dh.program_db.load_data():
            self.program_tree.insert("", "end", values=(p['code'], p['name'], p['college_code']))

    def search_program(self, event):
        query = self.entry_prog_search.get().lower()
        for item in self.program_tree.get_children():
            self.program_tree.delete(item)
        
        search_results = []
        for p in dh.program_db.load_data():
            if any(query in str(v).lower() for v in p.values()):
                self.program_tree.insert("", "end", values=(p['code'], p['name'], p['college_code']))
                search_results.append(p)
        
        if query:
            self.filtered_program_count = len(search_results)
        else:
            self.filtered_program_count = None
        
        self.update_all_record_counts()

    def sort_program_table(self, col, reverse):
        col_mapping = {
            "Program Code": "code",
            "Program Name": "name",
            "College Code": "college_code"
        }

        db_field = col_mapping.get(col, col.lower().replace(" ", "_"))
        for header_col in ("Program Code", "Program Name", "College Code"):
            self.program_tree.heading(header_col, text=header_col + " ↕")

        arrow = " ▼" if reverse else " ▲"
        self.program_tree.heading(col, text=col + arrow)

        # check if in a filtered state
        if hasattr(self, 'filtered_program_count') and self.filtered_program_count is not None:
            current_items = []
            for item in self.program_tree.get_children():
                values = self.program_tree.item(item)['values']
                # create a dict with the same structure as database records
                current_items.append({
                    'code': values[0],
                    'name': values[1], 
                    'college_code': values[2]
                })
            
            # sort the current items
            current_items.sort(key=lambda x: str(x[db_field]), reverse=reverse)
            
            for item in self.program_tree.get_children():
                self.program_tree.delete(item)
            for p in current_items:
                self.program_tree.insert("", "end", values=list(p.values()))
        else:
            # sort all data when not filtered
            data = dh.program_db.load_data()
            data.sort(key=lambda x: str(x[db_field]), reverse=reverse)
            for item in self.program_tree.get_children():
                self.program_tree.delete(item)
            for p in data:
                self.program_tree.insert("", "end", values=list(p.values()))
        
        self.program_tree.heading(col, command=lambda: self.sort_program_table(col, not reverse))
    
    def open_filter_window_prog(self):
        filter_window = Toplevel(self.master)
        filter_window.title("Filter Programs")
        filter_window.geometry("350x350")
        filter_window.configure(bg='#2b2b2b')
        filter_window.resizable(False, False)
        
        if not hasattr(self, 'prog_filter_vars'):
            self.prog_filter_vars = {}
        
        main_frame = ctk.CTkFrame(filter_window)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # college filter
        college_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        college_frame.pack(fill="both")
        ctk.CTkLabel(college_frame, text="College:", font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        colleges = dh.college_db.load_data()
        for college in colleges:
            college_code = college['code']
            var_name = f'prog_college_{college_code}'
            if var_name not in self.prog_filter_vars:
                self.prog_filter_vars[var_name] = BooleanVar(value=False)
            ctk.CTkCheckBox(college_frame, text=college_code, variable=self.prog_filter_vars[var_name]).pack(pady=3)

        button_frame = ctk.CTkFrame(filter_window)
        button_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkButton(button_frame, text="Apply Filters", command=lambda: self.apply_prog_filters(filter_window), width=100).pack(side="left", padx=8)
        ctk.CTkButton(button_frame, text="Clear All", command=self.clear_prog_filters, width=100).pack(side="left", padx=8)
        ctk.CTkButton(button_frame, text="Cancel", command=filter_window.destroy, width=100).pack(side="left", padx=8)

    def apply_prog_filters(self, filter_window=None):
        for item in self.program_tree.get_children():
            self.program_tree.delete(item)
    
        programs = dh.program_db.load_data()
        filtered_programs = []
        
        active_college_filters = []
        colleges = dh.college_db.load_data()
        for college in colleges:
            college_code = college['code']
            if self.prog_filter_vars[f'prog_college_{college_code}'].get():
                active_college_filters.append(college_code)
        
        if active_college_filters:
            for program in programs:
                if program['college_code'] in active_college_filters:
                    filtered_programs.append(program)
        else:
            filtered_programs = programs
        
        for program in filtered_programs:
            self.program_tree.insert("", "end", values=(program['code'], program['name'], program['college_code']))

        self.filtered_program_count = len(filtered_programs)
        self.update_all_record_counts()
        
        if filter_window:
            filter_window.destroy()
            
    def clear_prog_filters(self):
        if hasattr(self, 'prog_filter_vars'):
            for var in self.prog_filter_vars.values():
                var.set(False)
        
        self.filtered_program_count = None
        self.refresh_program_table()
        self.update_all_record_counts()

    # STUDENTS SECTION

    def setup_student_ui(self):
        self.stud_form = ctk.CTkFrame(self.student_tab)

        # left side form
        self.stud_form.pack(side="left", fill="y", padx=10, pady=10)
        ctk.CTkLabel(self.stud_form, text="Student Information", font=("Roboto", 16, "bold")).pack(pady=10)
        
        self.entry_stud_id = ctk.CTkEntry(self.stud_form, placeholder_text="ID: YYYY-NNNN", width=200)
        self.entry_stud_id.pack(pady=2)
        self.entry_stud_fname = ctk.CTkEntry(self.stud_form, placeholder_text="First Name", width=200)
        self.entry_stud_fname.pack(pady=2)
        self.entry_stud_lname = ctk.CTkEntry(self.stud_form, placeholder_text="Last Name", width=200)
        self.entry_stud_lname.pack(pady=2)

        self.combo_stud_prog = SearchableCombobox(self.stud_form, placeholder_text="Select Program", width=200)
        self.combo_stud_prog.pack(pady=5)

        self.combo_stud_year = ctk.CTkOptionMenu(self.stud_form, width=200, values=["Select Year", "1", "2", "3", "4"], command=lambda value: self.reset_focus_state())
        self.combo_stud_year.pack(pady=5)
        self.combo_stud_year.set("Select Year")

        self.combo_stud_gender = ctk.CTkOptionMenu(self.stud_form, width=200, values=["Select Gender", "Male", "Female"], command=lambda value: self.reset_focus_state())
        self.combo_stud_gender.pack(pady=5)
        self.combo_stud_gender.set("Select Gender")

        self.create_button_frame(self.stud_form, self.add_student, self.update_student,
                                self.delete_student, self.clear_student_fields)

        # right table & search
        right_frame = ctk.CTkFrame(self.student_tab)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        right_frame.grid_rowconfigure(0, weight=0)
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_rowconfigure(2, weight=0)
        right_frame.grid_columnconfigure(0, weight=1)

        # search and filter
        sortFilter_frame = ctk.CTkFrame(right_frame)
        sortFilter_frame.grid(row=0, column=0, sticky="nsew")

        search_filter_frame = ctk.CTkFrame(sortFilter_frame, fg_color="transparent")
        search_filter_frame.pack()

        self.entry_search = ctk.CTkEntry(search_filter_frame, placeholder_text="Search students...", width=450)
        self.entry_search.pack(side="left", padx=10, pady=10)
        self.entry_search.bind("<KeyRelease>", self.search_student)
        
        filter_button = ctk.CTkButton(search_filter_frame, text="Filter", command=self.open_filter_window_stud, width=50)
        filter_button.pack(side="right", padx=10, pady=10)

        # student list
        tree_container = ctk.CTkFrame(right_frame)
        tree_container.grid(row=1, column=0, sticky="nsew")

        self.student_tree = ttk.Treeview(tree_container, columns=("ID", "First Name", "Last Name", "Program", "Year", "Gender"), show="headings")
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.student_tree.yview)
        self.student_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.student_tree.pack(side="left", fill="both", expand=True)

        # record count label for students
        self.student_count_label = ctk.CTkLabel(right_frame, text="Total Records: 0", 
                                               font=("Roboto", 12, "bold"), text_color="#2a942a")
        self.student_count_label.grid(row=2, column=0, sticky="e", padx=5, pady=5)
        
        for col in ("ID", "First Name", "Last Name", "Program", "Year", "Gender"):
            self.student_tree.heading(col, text=col + " ↕", command=lambda c=col: self.sort_student_table(c, False))
            self.student_tree.column(col, width=100)

        self.student_tree.bind("<<TreeviewSelect>>", self.on_student_select)
        self.refresh_student_table()
        self.update_program_dropdown()
        self.update_all_record_counts() 

    def add_student(self):
        try:
            sid = self.entry_stud_id.get().strip()
            fn = self.entry_stud_fname.get().strip()
            ln = self.entry_stud_lname.get().strip()
            pr = self.combo_stud_prog.get()
            yr = self.combo_stud_year.get()
            gn = self.combo_stud_gender.get()
            
            if not all([sid, fn, ln, pr, yr, gn]) or pr == "Select Program" or yr == "Select Year" or gn == "Select Gender":
                messagebox.showerror("Error", "All fields required!")
                return
                
            if not dh.validate_student_id(sid):
                messagebox.showerror("Error", "Format: YYYY-NNNN")
                return
                
            # check if the typed program exists
            programs = dh.program_db.load_data()
            program_codes = [p['code'] for p in programs]
            if pr not in program_codes:
                messagebox.showerror("Error", f"Program '{pr}' does not exist! Please select from the dropdown.")
                return
                
            data = dh.student_db.load_data()
            if any(s['id'] == sid for s in data):
                messagebox.showerror("Error", "ID exists!")
                return
            data.insert(0, {'id': sid, 'firstname': fn, 'lastname': ln, 'program_code': pr, 'year': yr, 'gender': gn})
            dh.student_db.save_data(data)
            self.refresh_student_table()
            self.update_all_record_counts()
            messagebox.showinfo("Student Added", "Student added successfully!")
            self.clear_student_fields()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add student: {str(e)}")

    def update_student(self):
        sid = self.entry_stud_id.get().strip()
        fn = self.entry_stud_fname.get().strip()
        ln = self.entry_stud_lname.get().strip()
        pr = self.combo_stud_prog.get()
        yr = self.combo_stud_year.get()
        gn = self.combo_stud_gender.get()
        
        if not all([sid, fn, ln, pr, yr, gn]) or pr == "Select Program" or yr == "Select Year" or gn == "Select Gender":
            messagebox.showerror("Error", "All fields required!")
            return
            
        data = dh.student_db.load_data()
        changed = False
        for s in data:
            if s['id'] == sid:
                if (s['firstname'] != fn or s['lastname'] != ln or 
                    s['program_code'] != pr or s['year'] != yr or s['gender'] != gn):
                    s.update({'firstname': fn, 'lastname': ln, 'program_code': pr, 'year': yr, 'gender': gn})
                    changed = True
                break
        
        if changed:
            dh.student_db.save_data(data)
            self.refresh_student_table() 
            self.update_all_record_counts()
            messagebox.showinfo("Student Updated", "Student updated successfully!")
        self.clear_student_fields()

    def delete_student(self):
        sid = self.entry_stud_id.get().strip()
        if not sid:
            return
            
        if messagebox.askyesno("Confirm", f"Delete student {sid}?"):
            data = [s for s in dh.student_db.load_data() if s['id'] != sid]
            dh.student_db.save_data(data)
            self.refresh_student_table()
            self.update_all_record_counts()
            messagebox.showinfo("Student Deleted", "Student deleted successfully!")
            self.clear_student_fields()

    def clear_student_fields(self):
        self.entry_stud_id.configure(state="normal")
        self.entry_stud_id.delete(0, 'end')
        self.entry_stud_fname.delete(0, 'end')
        self.entry_stud_lname.delete(0, 'end')
        self.combo_stud_prog.set('') 
        self.combo_stud_prog.selected_value = ''
        self.combo_stud_year.set('Select Year')
        self.combo_stud_gender.set('Select Gender')

    def on_student_select(self, event):
        selected = self.student_tree.selection()
        if not selected:
            return
        val = self.student_tree.item(selected[0])['values']
        self.clear_student_fields()
        self.entry_stud_id.insert(0, val[0])
        self.entry_stud_id.configure(state="disabled")
        self.entry_stud_fname.insert(0, val[1])
        self.entry_stud_lname.insert(0, val[2])
        self.combo_stud_prog.set(val[3])
        self.combo_stud_year.set(str(val[4]))
        self.combo_stud_gender.set(val[5])

    def update_program_dropdown(self):
        programs = dh.program_db.load_data()
        codes = [p['code'] for p in programs]
        self.combo_stud_prog.set_items(codes if codes else ["No Programs"])

    def refresh_student_table(self):
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        for s in dh.student_db.load_data():
            self.student_tree.insert("", "end", values=list(s.values()))

    def search_student(self, event):
        query = self.entry_search.get().lower()
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        
        search_results = []
        for s in dh.student_db.load_data():
            if any(query in str(v).lower() for v in s.values()):
                self.student_tree.insert("", "end", values=list(s.values()))
                search_results.append(s)
        
        # update filtered count for search results
        if query:
            self.filtered_student_count = len(search_results)
        else:
            self.filtered_student_count = None
        
        self.update_all_record_counts()

    def sort_student_table(self, col, reverse):
        # map column headers to database field names
        col_mapping = {
            "ID": "id",
            "First Name": "firstname", 
            "Last Name": "lastname",
            "Program": "program_code",
            "Year": "year",
            "Gender": "gender"
        }

        db_field = col_mapping.get(col, col.lower().replace(" ", "_"))
        
        # reset all headers to subtle indicators
        for header_col in ("ID", "First Name", "Last Name", "Program", "Year", "Gender"):
            self.student_tree.heading(header_col, text=header_col + " ↕")
        
        # add prominent arrow to current column to show active sort direction
        arrow = " ▼" if reverse else " ▲"
        self.student_tree.heading(col, text=col + arrow)
        
        if hasattr(self, 'filtered_student_count') and self.filtered_student_count is not None:
            current_items = []
            for item in self.student_tree.get_children():
                values = self.student_tree.item(item)['values']
                current_items.append({
                    'id': values[0],
                    'firstname': values[1],
                    'lastname': values[2],
                    'program_code': values[3],
                    'year': values[4],
                    'gender': values[5]
                })
            
            current_items.sort(key=lambda x: str(x[db_field]), reverse=reverse)
            
            for item in self.student_tree.get_children():
                self.student_tree.delete(item)
            for s in current_items:
                self.student_tree.insert("", "end", values=list(s.values()))
        else:
            data = dh.student_db.load_data()
            data.sort(key=lambda x: str(x[db_field]), reverse=reverse)
            for item in self.student_tree.get_children():
                self.student_tree.delete(item)
            for s in data:
                self.student_tree.insert("", "end", values=list(s.values()))
        
        self.student_tree.heading(col, command=lambda: self.sort_student_table(col, not reverse))

    def open_filter_window_stud(self):
        filter_window = Toplevel(self.master)
        filter_window.title("Filter Students")
        filter_window.geometry("380x350")
        filter_window.configure(bg='#2b2b2b')
        filter_window.resizable(False, False)
        
        if not hasattr(self, 'filter_vars'):
            self.filter_vars = {}
        
        main_frame = ctk.CTkFrame(filter_window)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        left_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="both", padx=10, pady=10)

        ltop_frame = ctk.CTkFrame(left_frame)
        ltop_frame.pack(fill="x", expand=True)

        # gender filter
        gender_frame = ctk.CTkFrame(ltop_frame, fg_color="transparent")
        gender_frame.pack(side="left", fill="both")
        ctk.CTkLabel(gender_frame, text="Gender:", font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        if 'male' not in self.filter_vars:
            self.filter_vars['male'] = BooleanVar(value=False)
        if 'female' not in self.filter_vars:
            self.filter_vars['female'] = BooleanVar(value=False)
            
        ctk.CTkCheckBox(gender_frame, text="Male", variable=self.filter_vars['male']).pack(pady=3)
        ctk.CTkCheckBox(gender_frame, text="Female", variable=self.filter_vars['female']).pack(pady=3)
        
        lbot_frame = ctk.CTkFrame(left_frame)
        lbot_frame.pack(fill="x", expand=True)

        # year level filter
        year_frame = ctk.CTkFrame(lbot_frame, fg_color="transparent")
        year_frame.pack(fill="both")
        ctk.CTkLabel(year_frame, text="Year Level:", font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        year1_frame = ctk.CTkFrame(year_frame)
        year1_frame.pack(side="left", fill="both", expand=True)

        for year in ["1st", "2nd"]:
            var_name = f'year_{year}'
            if var_name not in self.filter_vars:
                self.filter_vars[var_name] = BooleanVar(value=False)
            ctk.CTkCheckBox(year1_frame, text=year, variable=self.filter_vars[var_name]).pack(pady=1)

        year2_frame = ctk.CTkFrame(year_frame)
        year2_frame.pack(side="right", fill="both", expand=True)
        for year in ["3rd", "4th"]:
            var_name = f'year_{year}'
            if var_name not in self.filter_vars:
                self.filter_vars[var_name] = BooleanVar(value=False)
            ctk.CTkCheckBox(year2_frame, text=year, variable=self.filter_vars[var_name]).pack(pady=1)
        
        right_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # college filter
        college_frame = ctk.CTkFrame(right_frame)
        college_frame.pack(fill="both")
        ctk.CTkLabel(college_frame, text="College:", font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        colleges = dh.college_db.load_data()
        for i, college in enumerate(colleges):
            college_code = college['code']
            var_name = f'college_{college_code}'
            if var_name not in self.filter_vars:
                self.filter_vars[var_name] = BooleanVar(value=False)
            ctk.CTkCheckBox(college_frame, text=college_code, variable=self.filter_vars[var_name]).pack(pady=3)
        
        # buttons frame
        button_frame = ctk.CTkFrame(filter_window)
        button_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkButton(button_frame, text="Apply Filters", command=lambda: self.apply_filters(filter_window), width=100).pack(side="left", padx=8)
        ctk.CTkButton(button_frame, text="Clear All", command=self.clear_all_filters, width=100).pack(side="left", padx=8)
        ctk.CTkButton(button_frame, text="Cancel", command=filter_window.destroy, width=100).pack(side="left", padx=8)

    def apply_filters(self, filter_window=None):
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)

        students = dh.student_db.load_data()
        filtered_students = []
        
        # pre-load programs for college lookup
        programs = dh.program_db.load_data()
        program_college_map = {prog['code']: prog['college_code'] for prog in programs}
        
        for student in students:
            # gender filter
            gender_match = True
            if self.filter_vars['male'].get() or self.filter_vars['female'].get():
                # only check if at least one gender filter is active
                gender_match = False
                if self.filter_vars['male'].get() and student['gender'].lower() == 'male':
                    gender_match = True
                if self.filter_vars['female'].get() and student['gender'].lower() == 'female':
                    gender_match = True
            
            # year level filter
            year_match = True
            active_year_filters = [year for year in ['1st', '2nd', '3rd', '4th'] 
                                 if self.filter_vars[f'year_{year}'].get()]
            if active_year_filters:
                year_match = False
                year_mapping = {'1st': '1', '2nd': '2', '3rd': '3', '4th': '4'}
                for year_filter in active_year_filters:
                    if student['year'] == year_mapping[year_filter]:
                        year_match = True
                        break
            
            # college filter
            college_match = True
            active_college_filters = []
            colleges = dh.college_db.load_data()
            for college in colleges:
                college_code = college['code']
                if self.filter_vars[f'college_{college_code}'].get():
                    active_college_filters.append(college_code)
            
            if active_college_filters:
                college_match = False
                student_college = program_college_map.get(student['program_code'])
                if student_college and student_college in active_college_filters:
                    college_match = True
            
            # if all active filters match, add to filtered list
            if gender_match and year_match and college_match:
                filtered_students.append(student)
        
        # if no filters are active, show all students
        any_filter_active = any(var.get() for var in self.filter_vars.values())
        if not any_filter_active:
            filtered_students = students
        
        # populate table with filtered results
        for student in filtered_students:
            self.student_tree.insert("", "end", values=list(student.values()))
        self.filtered_student_count = len(filtered_students)
        self.update_all_record_counts()

        # close filter window if provided
        if filter_window:
            filter_window.destroy()

    def clear_all_filters(self):
        if hasattr(self, 'filter_vars'):
            for var in self.filter_vars.values():
                var.set(False)
        
        self.filtered_student_count = None
        self.refresh_student_table()
        self.update_all_record_counts()

    def on_tab_change(self):
        tab = self.tabview.get().strip()
        if tab == "Students":
            progs = [p['code'] for p in dh.program_db.load_data()]
            self.combo_stud_prog.set_items(progs if progs else ["No Programs"])
        elif tab == "Programs":
            self.update_college_dropdown()

if __name__ == "__main__":
    app = SISApp()
    app.mainloop()
