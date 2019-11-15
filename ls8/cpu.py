import sys

HLT = 0b00000001
PRN = 0b01000111
LDI = 0b10000010
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110
CMP = 0b10100111


class CPU:

    def __init__(self, file):
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.sp = 0xF4
        self.file = file
        self.fl = 0
        self.E = 0
        self.L = 0
        self.G = 0


    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR

    def load(self):
        address = 0

        try:

            with open(self.file) as f:
                
                for line in f:
                    line_split = line.split("#")

                    num = line_split[0].strip()

                    try:
                        val = int(num, 2)
                        self.ram[address] = val
                        address += 1
                    except ValueError:
                        continue
        
        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} Not Found")
            sys.exit(2)


    def alu(self, op, reg_a, reg_b):

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == "CMP":
            self.E = 0
            self.L = 0
            self.G = 0
            reg_a = self.reg[self.ram[self.pc + 1]]
            reg_b = self.reg[self.ram[self.pc + 2]]

            if reg_a == reg_b:
                self.E = 1
            elif reg_a < reg_b:
                self.L = 1
            elif reg_a > reg_b:
                self.G = 1

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):

        running = True

        while running:

            IR = self.ram[self.pc]
            
            if IR == LDI:
                self.reg[self.ram[self.pc + 1]] = self.ram[self.pc + 2]
                move = (IR >> 6) + 1
                self.pc += move
            
            elif IR == PRN:
                print(self.reg[self.ram[self.pc + 1]])
                move = (IR >> 6) + 1
                self.pc += move

            elif IR == MUL:
                self.alu("MUL", self.ram[self.pc + 1], self.ram[self.pc + 2])
                move = (IR >> 6) + 1
                self.pc += move

            elif IR == ADD:
                self.alu("ADD", self.ram[self.pc + 1], self.ram[self.pc + 2])
                move = (IR >> 6) + 1
                self.pc += move

            elif IR == PUSH:
                self.sp -= 1
                self.ram[self.sp] = self.reg[self.ram[self.pc + 1]]
                move = (IR >> 6) + 1
                self.pc += move

            elif IR == POP:
                self.reg[self.ram[self.pc + 1]] = self.ram[self.sp]
                self.sp += 1
                move = (IR >> 6) + 1
                self.pc += move

            elif IR == CALL:
                self.sp -= 1
                self.ram[self.sp] = self.pc + 2
                address = self.reg[self.ram[self.pc + 1]]
                self.pc = address
            elif IR == RET:
                self.pc = self.ram[self.sp]
                self.sp += 1

            elif IR == JMP:
                jump = self.reg[self.ram[self.pc + 1]]
                self.pc = jump
            
            elif IR == JEQ:
                if self.E == 1:
                    self.pc = self.reg[self.ram[self.pc + 1]]
                else:
                    move = (IR >> 6) + 1
                    self.pc += move
            
            elif IR == JNE:
                if self.E == 0:
                    self.pc = self.reg[self.ram[self.pc + 1]]
                else:
                    move = (IR >> 6) + 1
                    self.pc += move         

            
            elif IR == CMP:
                self.alu("CMP", self.ram[self.pc + 1], self.ram[self.pc + 2])
                move = (IR >> 6) + 1
                self.pc += move

                

            elif IR == HLT:
                running = False

            else:
                sys.exit(1)