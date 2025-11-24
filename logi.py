import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

class EditorTexto:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor de texto")
        self.archivo_actual = None

        # Área de texto con scroll
        self.texto = tk.Text(root, wrap="word", undo=True)
        self.texto.pack(fill="both", expand=True, side="left")
        scroll = ttk.Scrollbar(root, command=self.texto.yview)
        scroll.pack(fill="y", side="right")
        self.texto.config(yscrollcommand=scroll.set)

        # Menú superior
        menubar = tk.Menu(root)
        root.config(menu=menubar)

        archivo_menu = tk.Menu(menubar, tearoff=0)
        archivo_menu.add_command(label="Nuevo", accelerator="Ctrl+N", command=self.nuevo_archivo)
        archivo_menu.add_command(label="Abrir...", accelerator="Ctrl+O", command=self.abrir_archivo)
        archivo_menu.add_command(label="Guardar", accelerator="Ctrl+S", command=self.guardar)
        archivo_menu.add_command(label="Guardar como...", command=self.guardar_como)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Salir", command=self.salir)

        editar_menu = tk.Menu(menubar, tearoff=0)
        editar_menu.add_command(label="Deshacer", accelerator="Ctrl+Z", command=lambda: self.texto.event_generate("<<Undo>>"))
        editar_menu.add_command(label="Rehacer", accelerator="Ctrl+Y", command=lambda: self.texto.event_generate("<<Redo>>"))
        editar_menu.add_separator()
        editar_menu.add_command(label="Cortar", accelerator="Ctrl+X", command=lambda: self.texto.event_generate("<<Cut>>"))
        editar_menu.add_command(label="Copiar", accelerator="Ctrl+C", command=lambda: self.texto.event_generate("<<Copy>>"))
        editar_menu.add_command(label="Pegar", accelerator="Ctrl+V", command=lambda: self.texto.event_generate("<<Paste>>"))
        editar_menu.add_separator()
        editar_menu.add_command(label="Seleccionar todo", accelerator="Ctrl+A", command=self.seleccionar_todo)

        ver_menu = tk.Menu(menubar, tearoff=0)
        self.wrap_var = tk.BooleanVar(value=True)
        ver_menu.add_checkbutton(label="Ajuste de línea", onvalue=True, offvalue=False,
                                 variable=self.wrap_var, command=self.toggle_wrap)

        ayuda_menu = tk.Menu(menubar, tearoff=0)
        ayuda_menu.add_command(label="Acerca de", command=self.acerca_de)

        menubar.add_cascade(label="Archivo", menu=archivo_menu)
        menubar.add_cascade(label="Editar", menu=editar_menu)
        menubar.add_cascade(label="Ver", menu=ver_menu)
        menubar.add_cascade(label="Ayuda", menu=ayuda_menu)

        # Barra de estado
        self.status = tk.StringVar(value="Listo")
        status_bar = ttk.Label(root, textvariable=self.status, anchor="w")
        status_bar.pack(fill="x", side="bottom")

        # Atajos de teclado
        root.bind("<Control-n>", lambda e: self.nuevo_archivo())
        root.bind("<Control-o>", lambda e: self.abrir_archivo())
        root.bind("<Control-s>", lambda e: self.guardar())
        root.bind("<Control-a>", lambda e: self.seleccionar_todo())

        # Actualizar título al modificar
        self.texto.bind("<<Modified>>", self.on_modified)

    # ----- Funciones de archivo -----
    def nuevo_archivo(self):
        if self.confirmar_descartar_cambios():
            self.texto.delete("1.0", "end")
            self.archivo_actual = None
            self.root.title("Editor de texto - Nuevo")
            self.status.set("Nuevo archivo")

    def abrir_archivo(self):
        if not self.confirmar_descartar_cambios():
            return
        ruta = filedialog.askopenfilename(
            title="Abrir archivo",
            filetypes=[("Texto", "*.txt"), ("Todos", "*.*")]
        )
        if ruta:
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    contenido = f.read()
                self.texto.delete("1.0", "end")
                self.texto.insert("1.0", contenido)
                self.archivo_actual = ruta
                self.root.title(f"Editor de texto - {ruta}")
                self.status.set(f"Abierto: {ruta}")
                self.texto.edit_modified(False)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{e}")

    def guardar(self):
        if self.archivo_actual is None:
            return self.guardar_como()
        try:
            contenido = self.texto.get("1.0", "end-1c")
            with open(self.archivo_actual, "w", encoding="utf-8") as f:
                f.write(contenido)
            self.status.set(f"Guardado: {self.archivo_actual}")
            self.texto.edit_modified(False)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")

    def guardar_como(self):
        ruta = filedialog.asksaveasfilename(
            title="Guardar como",
            defaultextension=".txt",
            filetypes=[("Texto", "*.txt"), ("Todos", "*.*")]
        )
        if ruta:
            try:
                contenido = self.texto.get("1.0", "end-1c")
                with open(ruta, "w", encoding="utf-8") as f:
                    f.write(contenido)
                self.archivo_actual = ruta
                self.root.title(f"Editor de texto - {ruta}")
                self.status.set(f"Guardado: {ruta}")
                self.texto.edit_modified(False)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")

    def salir(self):
        if self.confirmar_descartar_cambios():
            self.root.quit()

    # ----- Utilidades -----
    def seleccionar_todo(self):
        self.texto.tag_add("sel", "1.0", "end")

    def toggle_wrap(self):
        self.texto.config(wrap="word" if self.wrap_var.get() else "none")

    def on_modified(self, event=None):
        if self.texto.edit_modified():
            self.status.set("Modificado")
            self.texto.edit_modified(False)

    def confirmar_descartar_cambios(self):
        # Detecta cambios no guardados
        actual = self.texto.get("1.0", "end-1c")
        try:
            guardado = ""
            if self.archivo_actual:
                with open(self.archivo_actual, "r", encoding="utf-8") as f:
                    guardado = f.read()
            if actual != guardado:
                resp = messagebox.askyesnocancel("Cambios sin guardar",
                    "Tienes cambios sin guardar. ¿Deseas guardar antes de continuar?")
                if resp is None:  # Cancelar
                    return False
                if resp:          # Sí, guardar
                    self.guardar()
        except Exception:
            pass
        return True

    def acerca_de(self):
        messagebox.showinfo("Acerca de", "Editor de texto simple\nTkinter + Python\nGuarda en la ruta que elijas.")

def main():
    root = tk.Tk()
    root.geometry("800x600")
    EditorTexto(root)
    root.mainloop()

if __name__ == "__main__":
    main()


