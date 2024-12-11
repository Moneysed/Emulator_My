class Assembler:
    def __init__(self):
        # Таблица операций и их коды
        self.opcode_table = {
            "NOP": 0b0000,
            "LW": 0b0001,
            "SW": 0b0010,
            "ADD": 0b0011,
            "ADDI": 0b0100,
            "SUB": 0b0101,
            "SUBI": 0b0110,
            "CMP": 0b0111,
            "JMP": 0b1000,
            "JG": 0b1001,
            "JL": 0b1010,
            "MOV": 0b1100,
            "HALT": 0b1111,
        }
        self.labels = {}  # Таблица меток
        self.machine_code = []  # Список машинных кодов

    def parse_operand(self, operand, is_immediate=False):
        operand = operand.split(';', 1)[0].strip()
        operand = operand.strip(',')
        if operand.startswith("R") and not is_immediate:  # Регистр
            return int(operand[1:]) & 0b1111
        elif operand.isdigit() or (operand[0] == '-' and operand[1:].isdigit()):  # Непосредственное значение
            if is_immediate:
                return int(operand) & 0b1111
            else:
                raise ValueError(f"Ожидался регистр, но получено непосредственное значение: {operand}")
        else:  # Метка
            return operand

    def assemble(self, assembly_code):
        self.labels.clear()
        self.machine_code.clear()

        # Первый проход: сбор меток
        instructions = []
        pc = 0
        for line_no, line in enumerate(assembly_code.splitlines()):
            # Удаляем комментарии и пробелы
            line = line.split(';', 1)[0].strip()
            if not line:  # Пропуск пустых строк
                continue
            if line.endswith(":"):  # Метка
                label = line[:-1].strip()
                if label in self.labels:
                    raise ValueError(f"Метка '{label}' объявлена более одного раза.")
                self.labels[label] = pc
                instructions.append((pc, "NOP", line_no))  # Добавляем фиктивную инструкцию
                pc += 1
            else:
                instructions.append((pc, line, line_no))
                pc += 1

        # Второй проход: генерация инструкций
        for pc, line, line_no in instructions:
            parts = line.split()
            command = parts[0]
            operands = parts[1:] if len(parts) > 1 else []

            if command not in self.opcode_table:
                raise ValueError(f"Неизвестная команда '{command}' на строке {line_no + 1}.")

            opcode = self.opcode_table[command] << 12

            # Обработка операндов для каждой команды
            if command in ["ADDI", "SUBI", "CMPI"]:  # Регистр, регистр, непосредственное значение
                if len(operands) != 3:
                    raise ValueError(
                        f"Команда '{command}' ожидает 3 операнда, но получено {len(operands)} (строка {line_no + 1}).")
                operand_values = [
                    self.parse_operand(operands[0]),  # Регистр-назначение
                    self.parse_operand(operands[1]),  # Регистр-источник
                    self.parse_operand(operands[2], is_immediate=True),  # Непосредственное значение
                ]
            elif command == "CMP":  # 3 регистра
                if len(operands) != 3:
                    raise ValueError(
                        f"Команда '{command}' ожидает 3 операнда (регистра), но получено {len(operands)} (строка {line_no + 1}).")
                operand_values = [self.parse_operand(op) for op in operands]
            elif command in ["MOV"]:  # 2 регистра
                if len(operands) != 2:
                    raise ValueError(
                        f"Команда '{command}' ожидает 2 операнда, но получено {len(operands)} (строка {line_no + 1}).")
                operand_values = [
                    self.parse_operand(operands[0]),  # Регистр-назначение
                    self.parse_operand(operands[1]),  # Регистр-источник
                    0
                ]
            elif command in ["LW", "SW"]:  # Регистр и адрес
                if len(operands) != 2:
                    raise ValueError(
                        f"Команда '{command}' ожидает 2 операнда, но получено {len(operands)} (строка {line_no + 1}).")
                operand_values = [self.parse_operand(operands[0]), self.parse_operand(operands[1]), 0]
            elif command == "JMP":  # Безусловный переход, только метка
                if len(operands) != 1:
                    raise ValueError(
                        f"Команда '{command}' ожидает 1 операнд (метку), но получено {len(operands)} (строка {line_no + 1}).")
                label = operands[0].strip(", ")
                if label not in self.labels:
                    raise ValueError(f"Метка '{label}' не найдена (строка {line_no + 1}).")
                address = self.labels[label]
                operand_values = [address, 0, 0]
            elif command in ["JG", "JL"]:  # Условные переходы: метка и регистр
                if len(operands) != 2:
                    raise ValueError(
                        f"Команда '{command}' ожидает 2 операнда (метку и регистр), но получено {len(operands)} (строка {line_no + 1}).")
                label = operands[0].strip(", ")
                if label not in self.labels:
                    raise ValueError(f"Метка '{label}' не найдена (строка {line_no + 1}).")
                address = self.labels[label]
                reg = self.parse_operand(operands[1])
                operand_values = [address, reg, 0]
            elif command in ["HALT", "NOP"]:  # Нет операндов
                if operands:
                    raise ValueError(f"Команда '{command}' не принимает операнды (строка {line_no + 1}).")
                operand_values = [0, 0, 0]
            else:  # Любая неизвестная команда
                raise ValueError(f"Неизвестная команда '{command}' на строке {line_no + 1}.")

            # Формирование машинного слова
            machine_word = (
                    opcode |
                    (operand_values[0] << 8) |  # Первый операнд
                    (operand_values[1] << 4) |  # Второй операнд
                    operand_values[2]  # Третий операнд
            )
            self.machine_code.append(machine_word)

        return self.machine_code

