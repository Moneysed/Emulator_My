import tkinter as tk
from tkinter import filedialog, messagebox
from processor import Emulator
from assembler import Assembler


class AssemblerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Emulator")

        self.processor = Emulator()  # Инициализация эмулятора
        self.assembler = Assembler()  # Инициализация ассемблера

        # Frame для кнопок сверху
        button_frame = tk.Frame(self.root)
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=20)

        # Кнопки для запуска, загрузки и сохранения программы
        self.run_button = tk.Button(button_frame, text="Запустить", command=self.run)
        self.run_button.pack(side=tk.LEFT)
        self.next_button = tk.Button(button_frame, text="Следующий шаг", command=self.next_step)
        self.next_button.pack(side=tk.LEFT)
        self.load_button = tk.Button(button_frame, text="Загрузить из файла", command=self.load_from_file)
        self.load_button.pack(side=tk.LEFT)
        self.save_button = tk.Button(button_frame, text="Сохранить в файл", command=self.save_to_file)
        self.save_button.pack(side=tk.LEFT)

        # Frame для строки ввода и кнопки "Загрузить в память"
        input_frame = tk.Frame(self.root)
        input_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)

        # Поле для ввода данных
        self.memory_input = tk.Entry(input_frame, width=50)
        self.memory_input.pack(side=tk.LEFT, padx=5)

        # Кнопка для загрузки в память
        self.load_memory_button = tk.Button(input_frame, text="Загрузить в память", command=self.update_memory)
        self.load_memory_button.pack(side=tk.LEFT, padx=5)

        # Используем Frame для текстовой области и дополнительных элементов
        content_frame = tk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Настройка строк и столбцов для равномерного распределения
        content_frame.rowconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=1)
        content_frame.columnconfigure(0, weight=3)  # Широкая колонка для текста
        content_frame.columnconfigure(1, weight=1)
        content_frame.columnconfigure(2, weight=1)

        # Поле для ввода ассемблерного кода
        self.text_area = tk.Text(content_frame, height=20, width=60)
        self.text_area.grid(row=0, column=0, rowspan=2, padx=5, pady=5, sticky="nsew")  # Растяжение по всему пространству

        # Область для отображения регистров
        self.reg_frame = tk.LabelFrame(content_frame, text="Регистры", highlightthickness=0, bd=0)
        self.reg_frame.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

        # Область для отображения памяти
        self.mem_frame = tk.LabelFrame(content_frame, text="Память", highlightthickness=0, bd=0)
        self.mem_frame.grid(row=0, column=2, rowspan=2, padx=5, pady=5, sticky='nsew')

        # Отображение регистров
        self.reg_labels = []
        for i in range(16):  # Для всех 16 регистров
            label = tk.Label(self.reg_frame, text=f"R{i}: 0")
            label.pack(anchor='w', pady=1)  # Минимальный отступ между строками
            self.reg_labels.append(label)

        # Отображение первых 16 ячеек памяти
        self.mem_labels = []
        for i in range(8):
            label = tk.Label(self.mem_frame, text=f"Mem[{i}]: 0")
            label.pack(anchor='w', pady=1)  # Минимальный отступ между строками
            self.mem_labels.append(label)
        for i in range(8):
            label = tk.Label(self.mem_frame, text=f"Mem[{512}]: 0")
            label.pack(anchor='w', pady=1)  # Минимальный отступ между строками
            self.mem_labels.append(label)

        self.update_register_gui()
        self.run_flag = False

    def update_register_gui(self):
        for i in range(16):
            self.reg_labels[i].config(text=f"R{i}: {self.processor.registers[i]}")
        for i in range(8):
            self.mem_labels[i].config(text=f"Mem[{i}]: {self.processor.memory[i]}")
        for i in range(8):
            self.mem_labels[i+8].config(text=f"Mem[{511+i}]: {self.processor.memory[511+i]}")

    def run(self):
        code = self.text_area.get("1.0", tk.END).strip()
        if code:
            try:
                # Ассемблирование программы
                program = self.assembler.assemble(code)
                self.processor.load_program(program)  # Загрузка программы в эмулятор
                self.run_flag = True
                self.processor.step()
                self.update_register_gui()
                self.highlight_line(0)
            except UserWarning as e:
                messagebox.showinfo("Информация", str(e))
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        else:
            messagebox.showwarning("Внимание", "Поле ввода команд пустое!")

    def next_step(self):
        if self.run_flag:
            try:
                self.highlight_line(self.processor.PC - self.processor.offset)
                self.processor.step()
                self.update_register_gui()
            except UserWarning as e:
                messagebox.showinfo("Информация", str(e))
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        else:
            messagebox.showwarning("Внимание", "Программа не запущена!")

    def update_memory(self):
        input_data = self.memory_input.get().strip()
        try:
            # Преобразование строки в список чисел
            values = list(map(int, input_data.split(',')))
            for i in range(self.processor.offset):
                self.processor.memory[i] = values[i] if i < len(values) else 0
            self.update_register_gui()
            print(f"Память обновлена: {values}")
        except ValueError:
            print("Ошибка: некорректный формат ввода. Используйте целые числа, разделённые запятыми.")

    def load_from_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".asm", filetypes=[("Assembly files", "*.asm"), ("Text files", "*.txt")])
        if file_path:
            try:
                with open(file_path, "r") as file:
                    lines = file.readlines()  # Читаем файл построчно
                    if lines:  # Проверяем, что файл не пуст
                        # Первая строка — массив
                        array_line = lines[0].strip()  # Убираем лишние пробелы и переносы
                        try:
                            # Преобразуем первую строку в массив чисел
                            array = list(map(int, array_line.strip("[]").split(',')))
                            for i in range(self.processor.offset):
                                self.processor.memory[i] = array[i] if i < len(array) else 0
                            self.update_register_gui()
                            print(f"Массив загружен в память: {array}")
                        except Exception as e:
                            messagebox.showerror("Ошибка", f"Ошибка при обработке массива: {str(e)}")

                        # Остальной текст — ассемблерный код
                        assembler_code = "".join(lines[1:])
                        self.text_area.delete("1.0", tk.END)
                        self.text_area.insert(tk.END, assembler_code)
                    else:
                        messagebox.showinfo("Информация", "Файл пустой.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при загрузке файла: {str(e)}")

    def save_to_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".asm", filetypes=[("Assembly files", "*.asm"), ("Text files", "*.txt")])
        if file_path:
            try:
                code = self.text_area.get("1.0", tk.END)
                with open(file_path, "w") as file:
                    file.write(code)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении файла: {str(e)}")

    def highlight_line(self, line_no):
        self.text_area.tag_remove("highlight", "1.0", "end")  # Снять старую подсветку
        start = f"{line_no + 1}.0"
        end = f"{line_no + 1}.end"
        self.text_area.tag_add("highlight", start, end)
        self.text_area.tag_config("highlight", background="gray")


if __name__ == "__main__":
    root = tk.Tk()
    app = AssemblerGUI(root)
    root.mainloop()
