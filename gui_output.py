# Use Tkinter for python 2, tkinter for python 3
import Tkinter as tk
import tkFileDialog
import datetime
import global_variables
import output, volume_time
import ttkcalendar
import calendar
import tkMessageBox

class GUI(tk.Frame):
    def __init__(self, master):

        self.tempNumExistPhase = 0
        self.GUIphases = []

        tk.Frame.__init__(self,master,width = 540, height = 450)

        self.master.title ("RPM analysis")
        self.pack_propagate(0)
        self.pack()

        # Basic information panel

        self.rpm = tk.LabelFrame(self,text= 'Visualize Consumption', width = 540, height = 55)
        self.rpm.pack(padx = 5,pady = 5,side = tk.TOP)
        self.rpm.propagate()
        self.rpm.grid_propagate(0)
        
        self.rpm_input = tk.LabelFrame(self.rpm,text= 'Data Input',width = 240, height = 55)
        self.rpm_input.pack(padx = 5,pady = 5,side = tk.LEFT)
        self.rpm_input.propagate()
        self.rpm_input.grid_propagate(0)
        
        #file selection buttons

        self.generate_label("Select RPM File(s):",self.rpm_input,1,1)
        self.load_RPM_button = tk.Button(self.rpm_input, text = "...", bd = 2,command = self.get_dir)
        self.load_RPM_button.grid(row = 1, column = 2, sticky= 'W')

        self.tank_type_var = tk.StringVar(self.rpm_input)
        self.tank_type = tk.OptionMenu(self.rpm_input, self.tank_type_var, "std", "hyb")
        self.tank_type_var.set("std")
        self.tank_type.grid(row = 1, column = 3, sticky= 'W', padx = 15)
        

        self.graph_output = tk.LabelFrame(self.rpm,text= 'Graph Output',width = 250, height = 55)
        self.graph_output.pack(padx = 5,pady = 5,side = tk.RIGHT)
        self.graph_output.propagate()
        self.graph_output.grid_propagate(0)


        self.PhaseB = tk.Button(self.graph_output, text = "Time Series Graph",bd =2,
                                command= lambda: volume_time.create_volume_time_graph(self.tank_type_var.get(), global_variables.file_path1, global_variables.file_path2))

        self.PhaseB.grid(row = 1,column = 1,sticky= 'W')

        self.output = tk.LabelFrame(self,text= 'Calculate Output',width = 530, height = 350)
        self.output.pack(padx = 5,pady = 5,side = tk.BOTTOM)
        self.output.propagate()
        self.output.grid_propagate(0)

        #Generates the frams for the calendars
        
        self.date_select = tk.LabelFrame(self.output,text= 'Date Selection',width = 520, height = 270)
        self.date_select.grid(padx = 5,pady = 5,row = 1, column = 1)
        self.date_select.propagate()
        self.date_select.grid_propagate(0)

        self.date_from = tk.LabelFrame(self.date_select, text= 'Date From',width = 250, height = 230)
        self.date_from.grid(padx = 5,pady = 5,row = 1, column = 1)
        self.date_from.propagate()
        self.date_from.grid_propagate(0)
        
        self.date_to = tk.LabelFrame(self.date_select, text= 'Date To',width = 250, height = 230)
        self.date_to.grid(padx = 5,pady = 5,row = 1, column = 2)
        self.date_to.propagate()
        self.date_to.grid_propagate(0)
        
        #Generates the calendars in the frames, along with the date labels

        self.ttkcal_from = ttkcalendar.Calendar2(self.date_from, firstweekday=calendar.SUNDAY)
        self.ttkcal_from.grid(row = 1, column = 1, sticky= 'W')

        self.l1 = tk.Label(self.date_from, text="Selected Date From")
        self.l1.grid(padx = 5,pady = 5,row = 2, column = 1)
        self.date_from.propagate()
        self.date_from.grid_propagate(0)
        self.ttkcal_from.set_selection_callback(self.update_label1)
        
        self.ttkcal_to = ttkcalendar.Calendar2(self.date_to, firstweekday=calendar.SUNDAY)
        self.ttkcal_to.grid(row = 1, column = 1, sticky= 'W')
        
        self.l2 = tk.Label(self.date_to, text="Selected Date To")
        self.l2.grid(padx = 5,pady = 5,row = 2, column = 1)
        self.date_to.propagate()
        self.date_to.grid_propagate(0)
        self.ttkcal_to.set_selection_callback(self.update_label2)

        self.calculate_output = tk.LabelFrame(self.output,width = 520, height = 35)
        self.calculate_output.grid(padx = 5,pady = 5,row = 2, column = 1)
        self.calculate_output.propagate()
        self.calculate_output.grid_propagate(0)

        try:
            self.output_button = tk.Button(self.calculate_output, text = "Calculate Output",bd =2,
                                    command= lambda: output.calculate_consumption(global_variables.date_from, global_variables.date_to, self.tank_type_var.get(), global_variables.file_path1, global_variables.file_path2))
        except ValueError:
            tkMessageBox.showinfo("DateWarning","Please select date from and date to first")

            # self.tk.tkMessageBox.showinfo("FileWarning","Please select a file first")
            # return  %H:%M:%S

        self.output_button.grid(padx = 3,pady = 3, row = 1, columnspan=2)
        

    def update_label1(self, x):
        self.l1['text'] = x
        global_variables.date_from = self.l1['text']

    def update_label2(self, x):
        self.l2['text'] = x
        global_variables.date_to = self.l2['text']

    def clicked(event):
        print cal.selection
        
    def generate_label(self, label_str, panel, row, column):
        self.label = tk.StringVar()
        self.label_create = tk.Label(panel,textvariable = self.label)
        self.label.set(label_str)
        self.label_create.grid (row = row,column = column,padx = 5,pady = 6,sticky= 'W')

    def get_dir(self):
        self.dir = tkFileDialog.askopenfilenames(parent=self.rpm_input, initialdir="C://My Documents//Output Test",title='Please Select .CSV Files')
        if len(self.dir) == 1:
            global_variables.file_warning = False
            global_variables.file_path1 = self.dir[0]
        elif len(self.dir) == 2:
            global_variables.file_warning = False
            global_variables.file_path1 = self.dir[0]
            global_variables.file_path2 = self.dir[1]
        else:
            tkMessageBox.showinfo("FileWarning","Please select 1 or 2 files")


def main(): 
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()

