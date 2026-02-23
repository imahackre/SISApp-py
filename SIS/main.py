import customtkinter as ctk
from tkinter import ttk, messagebox, Listbox, Toplevel
import data_handler as dh

active_dropdowns = []

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class SearchableCombobox(ctk.CTkFrame):
    """A custom searchable combobox widget with dropdown functionality.
    
    Provides a text entry field with searchable dropdown list that filters
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
            # Clear focus by calling parent's reset method
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
        
        # Add to global tracking
        active_dropdowns.append(self)
        self._in_active_dropdowns = True
        
        # Position the dropdown
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.height
        self.dropdown_window.geometry(f"{self.width}x{self.dropdown_height}+{x}+{y}")
        
        # Create listbox with scrollbar
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
        
        # Bind events
        self.listbox.bind("<ButtonRelease-1>", self.on_listbox_select)
        self.listbox.bind("<Motion>", self.on_listbox_motion)
        self.listbox.bind("<Leave>", self.on_listbox_leave)
        
        self.update_listbox()
        
        # Bind escape key to close dropdown
        self.dropdown_window.bind("<Escape>", lambda e: self.hide_dropdown())
        
        # Make the dropdown window grab focus
        self.dropdown_window.focus_set()
        
    def hide_dropdown(self):
        if self.dropdown_window and self.dropdown_window.winfo_exists():
            # Remove from global tracking
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
            # Clear focus by calling parent's reset method
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

        # Tab Control using CTK Tabview
        self.tabview = ctk.CTkTabview(self, command=self.on_tab_change)
        self.tabview.pack(expand=True, fill="both", padx=20, pady=20)

        # Main Frames (Tabs)
        self.student_tab = self.tabview.add("  Students  ")
        self.program_tab = self.tabview.add("  Programs  ")
        self.college_tab = self.tabview.add("  Colleges  ")

        # Init UI for each tab
        self.setup_college_ui()
        self.setup_program_ui()
        self.setup_student_ui()
        
        """Dropdown behavior"""
        self.bind_all("<Button-1>", self.on_global_click)
        self.last_focused_entry = None
        
    def reset_focus_state(self):
        """Reset UI to initial state with no focused widgets."""
        # Clear focus from all widgets by setting focus to main window
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


    # COLLEGES SECTION

    def create_button_frame(self, parent, add_cmd, update_cmd, delete_cmd, clear_cmd):
        """Create a standardized button frame with CRUD operations.
        
        Args:
            parent: Parent widget to contain the button frame
            add_cmd: Command for Add button
            update_cmd: Command for Update button  
            delete_cmd: Command for Delete button
            clear_cmd: Command for Clear button
            
        Returns:
            The created button frame widget
        """
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="Add", width=90, fg_color="#2a942a", command=add_cmd).grid(row=0, column=0, padx=2, pady=2)
        ctk.CTkButton(btn_frame, text="Update", width=90, command=update_cmd).grid(row=0, column=1, padx=2, pady=2)
        ctk.CTkButton(btn_frame, text="Delete", width=90, fg_color="#942a2a", hover_color="#701e1e", command=delete_cmd).grid(row=1, column=0, padx=2, pady=2)
        ctk.CTkButton(btn_frame, text="Clear", width=90, fg_color="gray", command=clear_cmd).grid(row=1, column=1, padx=2, pady=2)
        
        return btn_frame

    def setup_college_ui(self):
        """Create and layout the college management interface."""
        # Left input form
        self.coll_form = ctk.CTkFrame(self.college_tab)
        self.coll_form.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(self.coll_form, text="College Information", font=("Roboto", 16, "bold")).pack(pady=10)

        self.entry_college_code = ctk.CTkEntry(self.coll_form, placeholder_text="College Code", width=200)
        self.entry_college_code.pack(pady=5, padx=10)

        self.entry_college_name = ctk.CTkEntry(self.coll_form, placeholder_text="College Name", width=200)
        self.entry_college_name.pack(pady=5, padx=10)

        self.create_button_frame(self.coll_form, self.add_college, self.update_college, 
                                self.delete_college, self.clear_college_fields)

        # Right table
        table_frame = ctk.CTkFrame(self.college_tab)
        table_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.college_tree = ttk.Treeview(table_frame, columns=("Code", "Name"), show="headings")
        self.college_tree.heading("Code", text="College Code")
        self.college_tree.heading("Name", text="College Name")
        self.college_tree.pack(fill="both", expand=True)
        self.college_tree.bind("<<TreeviewSelect>>", self.on_college_select)
        
        self.refresh_college_table()

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
            
            data.append({'code': code, 'name': name})
            dh.college_db.save_data(data)
            self.refresh_college_table()
            self.update_college_dropdown()
            messagebox.showinfo("College Added", "College added successfully!")
            self.clear_college_fields()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add college: {str(e)}")

    def refresh_college_table(self):
        for item in self.college_tree.get_children():
            self.college_tree.delete(item)
        for college in dh.college_db.load_data():
            self.college_tree.insert("", "end", values=(college['code'], college['name']))

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
            messagebox.showinfo("College Updated", "College updated successfully!")
        self.clear_college_fields()

    def delete_college(self):
        code = self.entry_college_code.get().strip()
        if not code:
            return
        
        # Check if college is being used by programs (might change this to allow for deletion even if)
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
            messagebox.showinfo("College Deleted", "College deleted successfully!")
            self.clear_college_fields()

    def clear_college_fields(self):
        self.entry_college_code.configure(state="normal")
        self.entry_college_code.delete(0, 'end')
        self.entry_college_name.delete(0, 'end')


    # PROGRAMS SECTION

    def setup_program_ui(self):
        self.prog_form = ctk.CTkFrame(self.program_tab)

        # Left side form
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

        # Right side table
        table_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        tree_container = ctk.CTkFrame(table_frame)
        tree_container.pack(fill="both", expand=True)

        self.program_tree = ttk.Treeview(tree_container, columns=("Code", "Name", "College"), show="headings")
        self.program_tree.heading("Code", text="Program Code")
        self.program_tree.heading("Name", text="Program Name")
        self.program_tree.heading("College", text="College Code")
        
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.program_tree.yview)
        self.program_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.program_tree.pack(fill="both", expand=True)
        self.program_tree.bind("<<TreeviewSelect>>", self.on_program_select)
        self.refresh_program_table()
        self.update_college_dropdown()

    def update_college_dropdown(self):
        codes = [c['code'] for c in dh.college_db.load_data()]
        self.combo_prog_college.configure(values=codes if codes else ["No Colleges"])

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
            data.append({'code': code, 'name': name, 'college_code': coll})
            dh.program_db.save_data(data)
            self.refresh_program_table()
            self.update_program_dropdown()
            messagebox.showinfo("Program Added", "Program added successfully!")
            self.clear_program_fields()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add program: {str(e)}")

    def refresh_program_table(self):
        for item in self.program_tree.get_children():
            self.program_tree.delete(item)
        for p in dh.program_db.load_data():
            self.program_tree.insert("", "end", values=(p['code'], p['name'], p['college_code']))

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
            messagebox.showinfo("Program Deleted", "Program deleted successfully!")
            self.clear_program_fields()

    def clear_program_fields(self):
        self.entry_prog_code.configure(state="normal")
        self.entry_prog_code.delete(0, 'end')
        self.entry_prog_name.delete(0, 'end')
        self.combo_prog_college.set('Select College')


    # STUDENTS SECTION

    def setup_student_ui(self):
        self.stud_form = ctk.CTkFrame(self.student_tab)

        # Left side form
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

        # Right table & search
        right_frame = ctk.CTkFrame(self.student_tab)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.entry_search = ctk.CTkEntry(right_frame, placeholder_text="Search students...", width=300)
        self.entry_search.pack(pady=10)
        self.entry_search.bind("<KeyRelease>", self.search_student)

        tree_container = ctk.CTkFrame(right_frame)
        tree_container.pack(fill="both", expand=True)

        self.student_tree = ttk.Treeview(tree_container, columns=("ID", "First Name", "Last Name", "Program", "Year", "Gender"), show="headings")
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.student_tree.yview)
        self.student_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.student_tree.pack(side="left", fill="both", expand=True)

        for col in ("ID", "First Name", "Last Name", "Program", "Year", "Gender"):
            self.student_tree.heading(col, text=col + " ↕", command=lambda c=col: self.sort_student_table(c, False))
            self.student_tree.column(col, width=100)

        self.student_tree.bind("<<TreeviewSelect>>", self.on_student_select)
        self.refresh_student_table()
        self.update_program_dropdown() 

    def update_program_dropdown(self):
        programs = dh.program_db.load_data()
        codes = [p['code'] for p in programs]
        self.combo_stud_prog.set_items(codes if codes else ["No Programs"])

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
                
            # Check if the typed program exists
            programs = dh.program_db.load_data()
            program_codes = [p['code'] for p in programs]
            if pr not in program_codes:
                messagebox.showerror("Error", f"Program '{pr}' does not exist! Please select from the dropdown.")
                return
                
            data = dh.student_db.load_data()
            if any(s['id'] == sid for s in data):
                messagebox.showerror("Error", "ID exists!")
                return
            data.append({'id': sid, 'firstname': fn, 'lastname': ln, 'program_code': pr, 'year': yr, 'gender': gn})
            dh.student_db.save_data(data)
            self.refresh_student_table()
            messagebox.showinfo("Student Added", "Student added successfully!")
            self.clear_student_fields()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add student: {str(e)}")

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

    def search_student(self, event):
        query = self.entry_search.get().lower()
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        for s in dh.student_db.load_data():
            if any(query in str(v).lower() for v in s.values()):
                self.student_tree.insert("", "end", values=list(s.values()))

    def refresh_student_table(self):
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        for s in dh.student_db.load_data():
            self.student_tree.insert("", "end", values=list(s.values()))

    def sort_student_table(self, col, reverse):
        # Map column headers to database field names
        col_mapping = {
            "ID": "id",
            "First Name": "firstname", 
            "Last Name": "lastname",
            "Program": "program_code",
            "Year": "year",
            "Gender": "gender"
        }
        
        # Get the correct database field name
        db_field = col_mapping.get(col, col.lower().replace(" ", "_"))
        
        # Reset all headers to subtle indicators
        for header_col in ("ID", "First Name", "Last Name", "Program", "Year", "Gender"):
            self.student_tree.heading(header_col, text=header_col + " ↕")
        
        # Add prominent arrow to current column to show active sort direction
        arrow = " ▼" if reverse else " ▲"
        self.student_tree.heading(col, text=col + arrow)
        
        data = dh.student_db.load_data()
        data.sort(key=lambda x: str(x[db_field]), reverse=reverse)
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        for s in data:
            self.student_tree.insert("", "end", values=list(s.values()))
        self.student_tree.heading(col, command=lambda: self.sort_student_table(col, not reverse))

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