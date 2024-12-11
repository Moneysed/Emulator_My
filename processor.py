class Emulator:
    def __init__(self, memory_size=1024):
        self.registers = [0] * 16  # 16 регистров
        self.PC = 0  # Программный счетчик
        self.offset = 512  # Смещение программы в памяти
        self.memory = [0] * memory_size  # Память процессора

    def load_program(self, program):
        # Загружает программу в память начиная с заданного смещения
        for i, code in enumerate(program):
            self.memory[self.offset + i] = code
        self.PC = self.offset

    def run(self):
        # Запускает выполнение программы
        try:
            self.step()
        except StopIteration:
            print("Программа завершена.")

    def step(self):
        if self.PC >= len(self.memory):
            print("Программный счетчик вышел за пределы памяти")
            return

        instruction = self.memory[self.PC]
        if instruction == 0:
            print(f"{self.PC}: Пустая команда (NOP)")
            self.PC += 1
            return

        print(f"\nТекущая команда: {self.PC}: {instruction:04X}")
        self.exec(instruction)

    def exec(self, instruction):
        opcode = (instruction >> 12) & 0b1111  # Опкод
        dest = (instruction >> 8) & 0b1111  # Первый операнд
        op1 = (instruction >> 4) & 0b1111  # Второй операнд
        op2 = instruction & 0b1111  # Третий операнд

        match opcode:
            case 0x1:  # LW (Load Word)
                self.registers[dest] = self.memory[self.registers[op1]]
                print(f"LW: R{dest} <- MEM[R{op1}] = {self.registers[dest]}")
            case 0x2:  # SW (Store Word)
                self.memory[self.registers[op1]] = self.registers[dest]
                print(f"SW: MEM[R{op1}] <- R{dest} = {self.memory[self.registers[op1]]}")
            case 0x3:  # ADD
                self.registers[dest] = (self.registers[op1] + self.registers[op2]) & 0xFFFF
                print(f"ADD: R{dest} <- R{op1} + R{op2} = {self.registers[dest]}")
            case 0x4:  # ADDI (Add Immediate)
                self.registers[dest] = (self.registers[op1] + op2) & 0xFFFF
                print(f"ADDI: R{dest} <- R{op1} + {op2} = {self.registers[dest]}")
            case 0x5:  # SUB
                self.registers[dest] = (self.registers[op1] - self.registers[op2]) & 0xFFFF
                print(f"SUB: R{dest} <- R{op1} - R{op2} = {self.registers[dest]}")
            case 0x6:  # SUBI (Subtract Immediate)
                self.registers[dest] = (self.registers[op1] - op2) & 0xFFFF
                print(f"SUBI: R{dest} <- R{op1} - {op2} = {self.registers[dest]}")
            case 0x7:  # CMP
                self.registers[dest] = 1 if self.registers[op1] < self.registers[op2] else 0
                print(f"CMP: R{dest} <- (R{op1} < R{op2}) = {self.registers[dest]}")
            case 0x8:  # JMP
                self.PC = dest + self.offset
                print(f"JMP: переход на {self.PC}")
                return
            case 0x9:  # JG (Jump if Greater)
                if self.registers[op1] > 0:
                    self.PC = dest + self.offset
                    print(f"JG: переход на {self.PC}, CMP: {self.registers[op1]}")
                    return
            case 0xA:  # JL (Jump if Less)
                if self.registers[op1] == 0:
                    self.PC = dest + self.offset
                    print(f"JL: переход на {self.PC}, CMP: {self.registers[op1]}")
                    return
            case 0xC:  # MOV
                self.registers[dest] = self.registers[op1]
                print(f"MOV: R{dest} <- R{op1} = {self.registers[dest]}")
            case 0xF:  # HALT
                print("HALT: остановка программы")
                raise StopIteration("Программа завершена")
            case _:  # Неизвестная команда
                raise ValueError(f"Неизвестная команда: {opcode}")

        self.PC += 1