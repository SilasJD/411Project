
instructions_file = 'data.txt'

class FunctionalUnit:

    def __init__(self, name, instructions, ex_time, Fi, Fj, Fk):
        self.name = name                    # name of functional unit (primarily for debugging)
        self.instructions = instructions    # list of instructions the FU can handle
        self.instruction = None             # string with instruction currently in FU
        self.busy = False                   # bool that describes if FU is busy (initially False)
        self.ex_time = ex_time              # int that determines FU's default execute time
        self.time_left = ex_time            # counter that determines time left in execute
        self.Fi = Fi                        # stores instructions destination
        self.Fj = Fj                        # stores instructions register a
        self.Fk = Fk                        # stores instructions register b
        self.Read = True                    # determines if the FU needs to be read (initially true)
        self.Ex = True                      # determines if the FU needs to be executed (initially true)
        self.Write = True                      # determines if the FU needs to be executed (initially true)
        self.inst_counter = 0               # defines the order of the instructions


    # sets FU if in the issue stage
    # becomes busy, sets execute time, sets registers, sets count stage
    def issue(self, inst, count):

        self.busy = True                    
        self.time_left = self.ex_time
        self.instruction = inst.inst
        self.Fi = inst.location
        self.Fj = inst.reg_a
        self.Fk = inst.reg_b
        self.inst_counter = count 


    # subtracts 1 every time FU executes
    def execute(self):

        self.time_left -= 1


class instruction: 

    def __init__(self, inst, location, reg_a, reg_b):
        self.inst = inst            # stores the instruction type
        self.location = location    # stores the destination of instruction
        self.reg_a = reg_a          # determines register a
        self.reg_b = reg_b          # determines register b
        self.issue = 0              # shows clock cycle for issue
        self.read_op = 0            # shows clock cycle for read
        self.execute = 0            # shows clock cycle for exe
        self.write = 0              # shows clock cycle for write

        
class Scoreboard:

    def __init__(self):
        
        self.FU = []                # stores all of systems FU's
        self.instructions = []      # stores all incoming instructions
        self.registers = {}         # stores FP registers and values
        self.int_registers = {}     # stores integer registers and values
        self.memory = {}            # stores memory values
        self.curr_registers = {}    # stores currently used registers
        self.inst_counter = 0       # stores count of instructions issued
        self.clk = 1                # clock
        
    # determines whether the scoreboard is done running
    def done(self):

        no_inst = True
        no_FU = True

        if(self.inst_counter < len(self.instructions)):
            no_inst = False
        if no_inst == True:
            for fu in self.FU:
                if fu.busy == True:
                    no_FU = False
                    break
        
        return no_inst and no_FU

    # parses incoming instructions
    def parse_instructions(self, inst_file):
        with open(inst_file) as fp:
            line = fp.readline()
            while line:
                nc_line = line.replace(',','')

                # splits line into array
                inst_arr = nc_line.split()
                # if array is 3 then its LD SD, else arithmetic inst
                if(len(inst_arr) == 3):
                    off_loc = inst_arr[2].split('(')
                    loc = off_loc[1].replace(')', '')
                    off = off_loc[0]

                    # handles store and load instructions
                    if inst_arr[0] == "L.D":
                        ii = instruction(inst_arr[0], inst_arr[1], loc, off)
                    else:
                        ii = instruction(inst_arr[0], loc, inst_arr[1], off)

                    self.instructions.append(ii)
                    line = fp.readline()
                elif(len(inst_arr) == 4):
                    ai = instruction(inst_arr[0], inst_arr[1], inst_arr[2], inst_arr[3])
                    self.instructions.append(ai)
                    line = fp.readline()

                else:
                    raise SyntaxError('Invalid Input instruction')
                    
    # initialize the FU's for the system
    def init_fu(self):
        
        add_fu = FunctionalUnit('Add', ['ADD', 'ADD.D', 'ADDI', 'SUB.D', 'SUB'], 2, None, None, None)
        mul_fu = FunctionalUnit('Multiply', ['MUL.D'], 10, None, None, None)
        div_fu = FunctionalUnit('Divide', ['DIV.D'], 40, None, None, None)
        int_fu = FunctionalUnit('Integer', ['L.D', 'S.D'], 1, None, None, None)

        self.FU.append(add_fu)
        self.FU.append(mul_fu)
        self.FU.append(div_fu)
        self.FU.append(int_fu)

    # initialize the registers for the system
    def init_registers(self):

        self.registers = {'F0': 0, 'F1': 0, 'F2': 0, 'F3': 0, 'F4': 0, 'F5': 0, 'F6': 0, 'F7': 0,
                          'F8': 0, 'F9': 0, 'F10': 0,'F11': 0, 'F12': 0, 'F13': 0, 'F14': 0, 'F15': 0,
                          'F16': 0, 'F17': 0, 'F18': 0, 'F19': 0, 'F20': 0, 'F21': 0, 'F22': 0, 'F23': 0,
                          'F24': 0, 'F25': 0, 'F26': 0, 'F27': 0, 'F28': 0, 'F29': 0, 'F30': 0, 'F31': 0
                        }

        self.int_registers = {'$0': 0, '$1': 0, '$2': 0, '$3': 0, '$4': 0, '$5': 0, '$6': 0, '$7': 0,
                          '$8': 0, '$9': 0, '$10': 0,'$11': 0, '$12': 0, '$13': 0, '$14': 0, '$15': 0,
                          '$16': 0, '$17': 0, '$18': 0, '$19': 0, '$20': 0, '$21': 0, '$22': 0, '$23': 0,
                          '$24': 0, '$25': 0, '$26': 0, '$27': 0, '$28': 0, '$29': 0, '$30': 0, '$31': 0
                        }

        self.memory =   {"0": 45, "1": 12, "2": 0, "3": 0, "4": 10, "5": 135, "6": 254, "7": 127,
                         "8": 18, "9": 4, "10": 55, "11": 8, "12": 2, "13": 98, "14": 13, "15": 5,
                         "16": 233, "17": 158, "18": 167
                        }


    # checks if instruction can be issued
    def can_issue(self, curr_inst):

        for curr_fu in self.FU:
            # RAR: if current instructions location is not already being written to 
            if curr_inst.location == curr_fu.Fi and curr_inst.inst not in curr_fu.instructions:
                return False 
        
        return True

    # issues an instruction to an FU
    def issue(self, inst, fu):
       
        fu.issue(inst, self.inst_counter)
        self.instructions[self.inst_counter].issue = self.clk
 
    # determines whether an instruction can be read
    def can_read(self, fu):
        
        print("checking if ", fu.name, "can read")
        
        #if currently used registers is empty
        if not bool(self.curr_registers):
            print(fu.name, "ok to read with registers ", fu.Fj, fu.Fk)
            return True
        
        # if instruction has been already read
        elif fu.Read == False:
            print('Instruction already read')
            return False
        else:  
            for reg_fu in self.curr_registers:
                # RAW: if a register in the instruction is currently being Written to 
                if (fu.Fj == reg_fu.Fi or fu.Fk == reg_fu.Fi) and fu.inst_counter > reg_fu.inst_counter:
                    print("cannot read, register being used")
                    return False 
            for reg_fu in self.FU:
                if reg_fu not in self.curr_registers.values() and reg_fu.busy == True and (fu.Fj == reg_fu.Fi or fu.Fk == reg_fu.Fi):
                    return False
        
        return True

    # Simulates read for FU
    def read(self, fu):
        
        self.curr_registers[fu] = fu
        fu.Read = False
        self.instructions[fu.inst_counter].read_op = self.clk

    # checks if FU can execute, if read has already happened
    def can_execute(self, fu):
        
        return not fu.Read

    # checks if FU can write
    def can_write(self, fu):
        
        # if already executed...
        if not fu.Ex:
            for reg_fu in self.FU:

                if fu.Fi == reg_fu.Fi and reg_fu.name != fu.name:
                    return True
                # WAR: if location is being read in other FU and FU is not already read and instruction occurred before current instruction
                if (fu.Fi == reg_fu.Fj or fu.Fi == reg_fu.Fk) and reg_fu not in self.curr_registers.values() and reg_fu.name != fu.name and reg_fu.inst_counter < fu.inst_counter:
                    print("cannot write, register being used")
                    return False 

        return not fu.Ex

    # simulates write within the FU
    def write(self, fu):
       
        fu.Write = False
        self.instructions[fu.inst_counter].write = self.clk

    def finish_func(self, fu):
        del self.curr_registers[fu]
        fu.busy = False
        fu.Read = True
        fu.Ex = True
        fu.Write = True
        fu.Fi = None
        fu.Fj = None
        fu.Fk = None
        fu.instruction = None

    # simulates execute within the FU
    def execute(self, fu):
        
        # if execute is not complete then continue cycling
        if fu.Ex == True:
            fu.execute()
            print("Execute time left: ", fu.time_left)

        # else simulate  instruction in registers
        if fu.time_left == 0:
            print('Execution Complete')
            self.execute_instruction(fu)
            fu.Ex = False
            fu.time_left = fu.ex_time
            self.instructions[fu.inst_counter].execute = self.clk 

    # does the arithmetic required by the instruction
    def execute_instruction(self, fu):

        # Handles Load/Store
        if fu.name == "Integer":
            if fu.instruction == "L.D":
                print("Loading memory ", fu.Fj, fu.Fk, " into location ", fu.Fi)
                mem_loc = int(fu.Fj)
                mem_offset = int(fu.Fk)
                mem_load = str(mem_loc + mem_offset)
                self.registers[fu.Fi] = self.memory[mem_load]
           
            else:
                print("Storing data from register ", fu.Fj, "into location ", fu.Fi, fu.Fk)
                mem_loc = int(fu.Fi)
                mem_offset = int(fu.Fk)
                mem_store = str(mem_loc + mem_offset) 
                self.memory[mem_store] = self.registers[fu.Fj]

        # Handles Multiplication
        elif fu.name == "Multiply":
            print("Storing result of multiplying ", fu.Fj, " and ", fu.Fk, " into ", fu.Fi)
            self.registers[fu.Fi] = self.registers[fu.Fj] * self.registers[fu.Fk]
      
        # Handles Division
        elif fu.name == "Divide": 
            print("Storing result of dividing ", fu.Fj, " and ", fu.Fk, " into ", fu.Fi)
            try:
                self.registers[fu.Fi] = self.registers[fu.Fj] / self.registers[fu.Fk]
            except Exception:
                return
        
        # Handles Addition/Subtraction
        else:
            if fu.instruction == "ADD.D":
                print("Storing result of adding ", fu.Fj, " to ", fu.Fk, " into ", fu.Fi)
                self.registers[fu.Fi] = self.registers[fu.Fj] + self.registers[fu.Fk]
            elif fu.instruction == "ADDI":
                print("Stroring immidiate addition result of adding ", fu.Fj, " to ", fu.Fk, " into ", fu.Fi)
                self.int_registers[fu.Fi] = self.int_registers[fu.Fj] + int(fu.Fk)
            elif fu.instruction == "ADD":
                print("Storing result of adding ", fu.Fj, " to ", fu.Fk, " into ", fu.Fi)
                self.int_registers[fu.Fi] = self.int_registers[fu.Fj] + self.int_registers[fu.Fk]
            elif fu.instruction == "SUB.D":
                print("Storing result of subtracting ", fu.Fj, " from ", fu.Fk, " into ", fu.Fi)
                self.registers[fu.Fi] = self.registers[fu.Fj] - self.registers[fu.Fk]
            elif fu.instruction == "SUB":
                print("Storing result of subtracting ", fu.Fj, " from ", fu.Fk, " into ", fu.Fi)
                self.int_registers[fu.Fi] = self.int_registers[fu.Fj] - self.int_registers[fu.Fk]

    # starts and runs the scoreboard
    def start(self):
        
        RAN_ALL_INSTRUCTIONS = False
        while not self.done():

            print('\n\n\nCLOCK CYCLE: ', self.clk)

            # sets current instruction if all instructions have not been completed
            if(self.inst_counter < len(self.instructions)):     
                curr_inst = self.instructions[self.inst_counter]
            else:
                RAN_ALL_INSTRUCTIONS = True

            # Goes through every Functional Unit each clock cycle
            for fu in self.FU:

                #checks if issue is allowed
                if curr_inst.inst in fu.instructions and not fu.busy and not RAN_ALL_INSTRUCTIONS:

                    can_issue = self.can_issue(curr_inst)
                    if can_issue:
                        print(curr_inst.inst, 'is being entered into FU', fu.name)

                        self.issue(curr_inst, fu)
                        self.inst_counter += 1

                        print("count: ", self.inst_counter)

                elif fu.busy:
                    can_read = self.can_read(fu)
                    can_execute = self.can_execute(fu)
                    can_write = self.can_write(fu)
                    
                    # reads if appropriate
                    if can_read:
                        print(fu.name, "allowed to read")
                        self.read(fu)

                    # executes if appropriate                   
                    elif can_execute and not can_write:
                        self.execute(fu)

                    # writes if appropriate
                    elif can_write:
                        self.write(fu)

            # updates registers after so that no other units have incorrect values
            for fu in self.FU:
                if fu.Write == False:
                    self.finish_func(fu)
            self.clk += 1






if __name__ == '__main__':
    
    instructions = []

    sb = Scoreboard()

    sb.parse_instructions(instructions_file)

    sb.init_fu()
    sb.init_registers()

    sb.start()

    print("\n\nINSTRUCTION  | Fi   |  Fj  |  Fk  | ISSUE  | READ OPEPRAND  | EXECUTE  | WRITE BACK")
    print("--------------------------------------------------------------------------------------")
    for instruction in sb.instructions:
        print("    {:<5}    |  {:<3} |  {:<3} |  {:<3} |   {:<3}  |       {:<3}      |    {:<3}   |    {:<3}   ".format(instruction.inst, instruction.location, instruction.reg_a, instruction.reg_b, instruction.issue, instruction.read_op, instruction.execute, instruction.write))
    
    print('\n\nRegister Values\n')
    print("MEMORY | VALUE")
    print("----------------")
    for loc in sb.memory:
        print("   {:<3}  |  {:<3}".format(loc, sb.memory[loc]))

    print("\n\nFP REGISTER | VALUE")
    print("----------------------")
    for loc in sb.registers:
        print("     {:<3}    |  {:<3}".format(loc, sb.registers[loc]))
    
    print("\n\nINT REGISTER | VALUE")
    print("----------------------")
    for loc in sb.int_registers:
        print("     {:<3}    |  {:<3}".format(loc, sb.int_registers[loc]))
