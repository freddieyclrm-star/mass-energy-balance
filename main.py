class Stream:
    def __init__(self, name, flowrate, temp, composition, molarweight):
        self.name = name
        self.flowrate = flowrate #thatll be in mol/s
        self.temp = temp #in celsius
        self.composition = composition #dictionary {"A": 0.67, "B": 0.23}
        self.molarweight = molarweight #dictionary {"A":18, "B":44}

    def __str__(self):
        self.name = self.name.capitalize()
        return f"{self.name}: {self.flowrate} mol/s at {self.temp}°C, comp:{self.composition}"

    def average_mw(self):
        x = self.composition.keys()
        avgmw = 0
        for i in x:
            y = self.composition[i] * self.molarweight[i]
            avgmw += y
        return avgmw

    def mass_flowrate(self):
        avg = self.average_mw()
        return avg * self.flowrate

class Mixer:
    def __init__(self, inflows):
        self.inflows = inflows

    def mix(self):
        total_flow = 0
        components = {}
        new_dict = {}
        for i in self.inflows:
            total_flow += i.flowrate
            for component, fraction in i.composition.items():
                molar_flow = fraction * i.flowrate
                if component not in components:
                    components.update({component: molar_flow})
                else:
                    orig = components[component]
                    new = molar_flow + orig
                    components.update({component: new})
        total_f = 0
        for c, f in components.items():
            total_f += f
        for c, f in components.items():
            new_f = f/total_f
            new_dict.update({c: new_f})
        return Stream (
            name = "Mixed Stream",
            flowrate = total_flow,
            temp = self.inflows[0].temp,
            composition = new_dict,
            molarweight = self.inflows[0].molarweight
            )


class Heater:
    def __init__(self, inflow_stream, shc, out_temp = None, energy = None):
        self.inflow_stream = inflow_stream
        self.shc = shc
        self.out_temp = out_temp
        self.energy = energy

    @classmethod
    def get(cls):
        choice = input("1. Q \n2. T_out \n What variable for input: ").lower().strip()
        if choice == "1" or choice == "q":
            energy = float(input("Energy: "))
            choice = "q"
            return energy, choice
        elif choice == "2" or choice == "t_out":
            out_temp = float(input("Out stream temperature: "))
            choice = "tout"
            return out_temp, choice
        else:
            raise ValueError("Invalid choice")

    def heat(self):
        m = self.inflow_stream.mass_flowrate()
        t_in = self.inflow_stream.temp
        if self.out_temp is None:
            #have energy case find out temp
            temp_change = self.energy / m / self.shc
            self.out_temp = temp_change + t_in
        elif self.energy is None:
            #have out temp case find energy
            temp_change = self.out_temp - t_in
            self.energy = m * self.shc * temp_change

        else:
            raise ValueError("Error")

        return Stream (
            name = "Out Stream",
            flowrate = self.inflow_stream.flowrate,
            temp = self.out_temp,
            composition = self.inflow_stream.composition,
            molarweight = self.inflow_stream.molarweight
            )

class Reaction:
    def __init__(self, stoich):
        self.stoich = stoich

class Reactor:
    def __init__(self, instream, reaction, conversion):
        self.instream = instream
        self.reaction = reaction
        self.conversion = conversion

    def react(self):
        react_comp = {}
        x = self.instream.composition.keys()
        f= self.instream.flowrate
        for i in x:
            ff = f * self.instream.composition[i]
            react_comp.update({i: ff})
        stoich = self.reaction.stoich.items()
        for i, j in stoich:
            if j < 0:
                reactant = i
                break
        mole_consumption = self.conversion * react_comp[reactant]
        eor = mole_consumption / abs(self.reaction.stoich[reactant])
        outmoles = {}
        for i, j in stoich:
            x = react_comp[i] + j * eor
            outmoles.update({i: x})
        totalmoles = sum(outmoles.values())
        newcomp = {}
        for i, j in outmoles.items():
            x = j / totalmoles
            newcomp.update({i: x})

        return Stream(
            name = "Out Stream Reactor",
            flowrate = totalmoles,
            temp = self.instream.temp,
            composition = newcomp,
            molarweight = self.instream.molarweight
            )

def non_negative_input(x):
    while True:
        try:
            value = float(input(x).strip())
            if value < 0:
                print("Enter a non-negative number")
                continue
            else:
                return value
        except ValueError:
            print("Enter a Valid Number")

def get_comp_fractions():
    while True:
        try:
            x = float(input("Enter Mole Fraction for A: ").strip())
            y = float(input("Enter Mole Fraction for B: ").strip())
            if x < 0 or y < 0:
                print("Fractions cannot be negative")
                continue
            if (x+y) != 1:
                print("Fractions must sum up to 1")
                continue
            return {"A": x, "B": y}
        except ValueError:
            print("Enter a Valid Number")

def get_conversion():
    while True:
        user_input = non_negative_input("Input Conversion (0-1): ")
        if user_input > 1:
            print("Conversion cannot be over 1")
            continue
        return user_input

def get_stream():
    name = input("Enter name of the Stream: ")
    flowrate = non_negative_input("Enter Flowrate of the Stream in mol/s: ")
    temp = non_negative_input("Enter Temperature of the Stream in °C: ")
    print("Enter Composition of the Stream")
    composition = get_comp_fractions()
    molarweight = {"A":18, "B":44}
    return Stream(name, flowrate, temp, composition, molarweight)


def main():
    print("========Stream 1========")
    stream_test1 = get_stream()
    print("========Stream 2========")
    stream_test2 = get_stream()
    #mix
    mixed = Mixer([stream_test1, stream_test2]).mix()
    #heat
    print("========Set Heater========")
    value, choice = Heater.get()
    if choice == "q":
        heated = Heater(mixed, 4, energy=value).heat()
    else:
        heated = Heater(mixed, 4, out_temp=value).heat()
    #react
    print("========Set Reactor========")
    conv = get_conversion()
    re = Reaction({"A": -1, "B": +1})
    reacted = Reactor(heated, re, conv).react()
    #summary
    print("========Results========")
    print(f'Total inlet molar flowrate: {stream_test1.flowrate + stream_test2.flowrate}')
    print(f'Total outlet molar flowrate: {reacted.flowrate}')
    print(reacted)


if __name__ == "__main__":
    main()


