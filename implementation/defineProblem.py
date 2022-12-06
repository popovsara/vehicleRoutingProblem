import tkinter
from tkinter import Toplevel
import haversine as hs
import customtkinter
from tkintermapview import TkinterMapView
import vehicles


class City:
    def __init__(self, city, requirement, location):
        self.city = city
        self.requirement = requirement
        self.location = location


customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

all_routes = []
distances = {}


class App(customtkinter.CTk):
    APP_NAME = "Vehicle routing problem"
    WIDTH = 1200
    HEIGHT = 700

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title(App.APP_NAME)
        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        self.minsize(App.WIDTH, App.HEIGHT)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Command-q>", self.on_closing)
        self.bind("<Command-w>", self.on_closing)
        self.createcommand('tk::mac::Quit', self.on_closing)

        self.marker_list = []

        # ============ create two CTkFrames ============

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self, corner_radius=0)
        self.frame_left.grid(row=0, column=0, rowspan=1, columnspan=1, padx=0, pady=0, sticky="nsew")

        self.frame_right = customtkinter.CTkFrame(master=self, corner_radius=0)
        self.frame_right.grid(row=1, column=1, rowspan=1, columnspan=1, pady=0, padx=0, sticky="nsew")

        # ============ frame_left ============

        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Set Marker",
                                                command=self.set_marker_event,
                                                width=120, height=30,
                                                border_width=0,
                                                corner_radius=8)
        self.button_1.grid(pady=(20, 0), padx=(20, 20), row=0, column=0)

        self.button_2 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Set Depot",
                                                command=lambda: self.set_marker_event(True),
                                                width=120, height=30,
                                                border_width=0,
                                                corner_radius=8)
        self.button_2.grid(pady=(20, 0), padx=(20, 20), row=1, column=0)

        self.button_3 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Clear Markers",
                                                command=self.clear_marker_event,
                                                width=120, height=30,
                                                border_width=0,
                                                corner_radius=8)
        self.button_3.grid(pady=(20, 0), padx=(20, 20), row=2, column=0)

        self.button_4 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Find optimal path",
                                                command=self.set_params,
                                                width=120, height=30,
                                                border_width=0,
                                                corner_radius=8)
        self.button_4.grid(pady=(20, 0), padx=(20, 20), row=3, column=0)

        # ============ frame_right ============

        self.map_widget = TkinterMapView(corner_radius=11)
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.map_widget.grid(row=0, rowspan=1, column=1, columnspan=3, sticky="nswe", padx=(20, 20), pady=(20, 0))
        self.map_widget.set_address("Belgrade")

        self.entry = customtkinter.CTkEntry(master=self.frame_right,
                                            placeholder_text="type address",
                                            width=140,
                                            height=30,
                                            corner_radius=8)
        self.entry.grid(row=1, column=0, sticky="we", padx=(20, 0), pady=20)
        self.entry.entry.bind("<Return>", self.search_event)

        self.button_5 = customtkinter.CTkButton(master=self.frame_right,
                                                height=30,
                                                text="Search",
                                                command=self.search_event,
                                                border_width=0,
                                                corner_radius=8)
        self.button_5.grid(row=1, column=1, sticky="w", padx=(20, 0), pady=20)

        self.slider_1 = customtkinter.CTkSlider(master=self.frame_right,
                                                width=200,
                                                height=16,
                                                from_=0, to=19,
                                                border_width=5,
                                                command=self.slider_event)
        self.slider_1.grid(row=1, column=2, sticky="e", padx=20, pady=20)
        self.slider_1.set(self.map_widget.zoom)

    def search_event(self, event=None):
        self.map_widget.set_address(self.entry.get())
        self.slider_1.set(self.map_widget.zoom)

    def slider_event(self, value):
        self.map_widget.set_zoom(value)

    def set_marker_event(self, isDepot=False):
        current_position = self.map_widget.get_position()
        self.marker_list.append(self.map_widget.set_marker(current_position[0], current_position[1]))
        if not isDepot:
            self.enter_requirement()
        else:
            self.set_route(0, True)

    def clear_marker_event(self):
        for marker in self.marker_list:
            marker.delete()

    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()

    def enter_requirement(self):
        global pop
        pop = Toplevel()
        pop.config(bg='black')
        my_frame = customtkinter.CTkFrame(pop, bg='black', width=300, height=250)
        my_frame.pack(pady=5)
        my_frame.grid(column=2, row=2)

        def slider_event_size(value):
            label_size = customtkinter.CTkLabel(master=my_frame, text=int(requirement.get()))
            label_size.grid(column=0, row=1)

        requirement = customtkinter.CTkSlider(master=my_frame,
                                              from_=0,
                                              to=1000,
                                              cursor='dot',
                                              command=slider_event_size)
        requirement.grid(column=0, row=2)

        label_size_txt = customtkinter.CTkLabel(master=my_frame,
                                                text='Enter wanted amount in this city')
        label_size_txt.grid(column=0, row=0)

        label_size = customtkinter.CTkLabel(master=my_frame, text=int(requirement.get()))
        label_size.grid(column=0, row=1)

        yes = customtkinter.CTkButton(master=my_frame,
                                      text='Commit',
                                      command=lambda: self.set_route(requirement.get(), False),
                                      height=30,
                                      border_width=0,
                                      corner_radius=8)
        yes.grid(pady=(20, 0), padx=(20, 20), row=4, column=0)

    def set_route(self, requirement, isDepot):
        if isDepot:
            location = City('DEPOT', 0, self.marker_list[-1].position)
        else:
            pop.destroy()
            location = City('LOC' + str(len(all_routes)), int(requirement), self.marker_list[-1].position)
        all_routes.append(location)

    def set_params(self):
        global params
        params = Toplevel()
        params.geometry()
        params.config(bg='black')
        my_frame = customtkinter.CTkFrame(params, bg='black', width=350, height=325)
        my_frame.pack(pady=5)
        my_frame.grid(columnspan=15, rowspan=15)

        # size of init population
        def slider_event_size(value):
            label_size = customtkinter.CTkLabel(master=my_frame, text=int(size_of_init_pop.get()))
            label_size.grid(column=0, row=4)

        size_of_init_pop = customtkinter.CTkSlider(master=my_frame, from_=(len(self.marker_list) -1)*10,
                                                   to=1000, cursor='dot',
                                                   command=slider_event_size)
        size_of_init_pop.grid(column=0, row=5)

        label_size_txt = customtkinter.CTkLabel(master=my_frame, text='Size of init population')
        label_size_txt.grid(column=0, row=3)

        label_size = customtkinter.CTkLabel(master=my_frame, text=int(size_of_init_pop.get()))
        label_size.grid(column=0, row=4)

        # number of generations
        def slider_event_num(value):
            num_generations_val = customtkinter.CTkLabel(master=my_frame, text=int(number_of_generations.get()))
            num_generations_val.grid(column=0, row=7)

        number_of_generations = customtkinter.CTkSlider(master=my_frame, from_=0, to=1000, cursor='dot',
                                                        command=slider_event_num)
        number_of_generations.grid(column=0, row=8)

        number_of_generations_txt = customtkinter.CTkLabel(master=my_frame, text='Number of generations')
        number_of_generations_txt.grid(column=0, row=6)

        num_generations_val = customtkinter.CTkLabel(master=my_frame, text=int(number_of_generations.get()))
        num_generations_val.grid(column=0, row=7)

        # crossover method
        crossover_method = customtkinter.CTkLabel(master=my_frame, text='Crossover method')
        crossover_method.grid(column=0, row=9)
        selection_method_oc = customtkinter.CTkRadioButton(master=my_frame,
                                                           text='Order crossover',
                                                           width=20,
                                                           height=20,
                                                           value=1)

        selection_method_pmc = customtkinter.CTkRadioButton(master=my_frame,
                                                            text='Partially mapped crossover',
                                                            width=20,
                                                            height=20,
                                                            value=2)

        selection_method_oc.grid(pady=(20, 0), padx=(20, 20), column=0, row=10)
        selection_method_pmc.grid(pady=(20, 0), padx=(20, 10), column=0, row=11)

        confirm = customtkinter.CTkButton(master=my_frame,
                                          text='Submit',
                                          command=lambda: self.ga(int(number_of_generations.get()),
                                                                  int(size_of_init_pop.get()),
                                                                  selection_method_oc.check_state,
                                                                  selection_method_pmc.check_state),
                                          height=30,
                                          border_width=0,
                                          corner_radius=8)
        confirm.grid(pady=(10, 0), padx=(10, 10), row=12, column=0)

    def ga(self, number_of_generations, size_of_init_pop, oc, pmc):
        for route1 in all_routes:
            distances[route1.city] = {}
            for route2 in all_routes:
                distances[route1.city].update({route2.city: hs.haversine(route1.location, route2.location)})

        import vrp, plot
        vrp.distances = distances
        vrp.all_routes = all_routes
        initial_population = vrp.create_init_population(size_of_init_pop, all_routes, vehicles.all_vehicles)
        if oc is True:
            best_solutions_ox = vrp.evolution(number_of_generations, 100, 'ox', initial_population)
            optimum_ox = min(best_solutions_ox, key = lambda t: t[1][1])
            plot.plot_fitness_values(best_solutions_ox, 'Order crossover')
            plot.plot_routes(optimum_ox[1][0], 'Order crossover routes')
            plots('Order crossover', optimum_ox[1][0])
        if pmc is True:
            best_solutions_pmx = vrp.evolution(number_of_generations, 100, 'pmx', initial_population)
            optimum_pmx = min(best_solutions_pmx, key = lambda t: t[1][1])
            plot.plot_fitness_values(best_solutions_pmx, 'Partially mapped crossover')
            plot.plot_routes(optimum_pmx[1][0], 'Partially mapped crossover routes')
            plots1('Partially mapped crossover', optimum_pmx[1][0])


def plots(title, solution):
    global pop
    pop = Toplevel()
    pop.geometry()
    my_frame = customtkinter.CTkFrame(pop, bg='black', width=1500, height=150)
    my_frame.pack(pady=5)

    global plot, plot1
    plot = tkinter.PhotoImage(file='../plots/' + title + '.png')
    plot_photo = tkinter.Label(my_frame, image=plot)
    plot_photo.grid(row=0, column=1)

    plot1 = tkinter.PhotoImage(file='../plots/' + title + ' routes' + '.png')
    plot_photo1 = tkinter.Label(my_frame, image=plot1)
    plot_photo1.grid(row=0, column=0)

    text = ''
    for veh in solution:
        if len(veh.routes) > 0:
            text += '\nVehicle: ' + str(veh.vehicle_number) + ' ,capacity: ' + str(veh.capacity) + '\n Routes: \n'
            for j in range(0, len(veh.routes)):
                text += veh.routes[j].city + ' requirement ' + str(veh.routes[j].requirement)
                if j != len(veh.routes) - 1:
                    text += ' -> '
    label_size_txt = customtkinter.CTkLabel(master=my_frame, text=text)
    label_size_txt.grid(column=0, row=1)


def plots1(title, solution):
    global pop1
    pop1 = Toplevel()
    pop1.geometry()
    my_frame1 = customtkinter.CTkFrame(pop1, bg='black', width=1500, height=150)
    my_frame1.pack(pady=5)

    global plot2, plot3
    plot2 = tkinter.PhotoImage(file='../plots/' + title + '.png')
    plot_photo2 = tkinter.Label(my_frame1, image=plot2)
    plot_photo2.grid(row=0, column=1)

    plot3 = tkinter.PhotoImage(file='../plots/' + title + ' routes' + '.png')
    plot_photo3 = tkinter.Label(my_frame1, image=plot3)
    plot_photo3.grid(row=0, column=0)

    text = ''
    for veh in solution:
        if len(veh.routes) > 0:
            text += '\nVehicle: ' + str(veh.vehicle_number) + ' ,capacity: ' + str(veh.capacity) + '\n Routes: \n'
            for j in range(0, len(veh.routes)):
                text += veh.routes[j].city + ' requirement ' + str(veh.routes[j].requirement)
                if j != len(veh.routes) - 1:
                    text += ' -> '
    label_size_txt = customtkinter.CTkLabel(master=my_frame1, text=text)
    label_size_txt.grid(row=1, column=0)


if __name__ == "__main__":
    app = App()
    app.start()
