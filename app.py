import time
import customtkinter as ctk
from tkinter import messagebox

from db_setup import init_db
from vault_manager import add_vault_entry, get_all_vault_labels, get_encrypted_blob
# Make sure your utils folder exists with these original files
from utils.generator import generate_passphrase, optimize_passphrase
from utils.ml_engine import predict, LABEL_MAP
from utils.security import entropy_bits, crack_time_label, encrypt_passphrase, decrypt_passphrase

class PassCraftApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("PassCraft - Secure Password Manager")
        self.geometry("900x650")
        
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Initialize SQLite database
        self.Session = init_db()
        self.db_session = self.Session()
        
        self.build_sidebar()
        self.build_generator_frame()
        self.build_vault_frame()
        
        self.show_generator()

    def build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)
        
        self.logo = ctk.CTkLabel(self.sidebar, text="PassCraft", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo.grid(row=0, column=0, padx=20, pady=(20, 30))
        
        self.btn_gen = ctk.CTkButton(self.sidebar, text="Generator", command=self.show_generator)
        self.btn_gen.grid(row=1, column=0, padx=20, pady=10)
        
        self.btn_vault = ctk.CTkButton(self.sidebar, text="My Vault", command=self.show_vault)
        self.btn_vault.grid(row=2, column=0, padx=20, pady=10)
        
        self.theme_switch = ctk.CTkSwitch(self.sidebar, text="Dark Mode", command=self.toggle_theme)
        self.theme_switch.grid(row=4, column=0, padx=20, pady=20, sticky="s")
        if ctk.get_appearance_mode() == "Dark":
            self.theme_switch.select()

    def toggle_theme(self):
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")

    def build_generator_frame(self):
        self.gen_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.gen_frame.grid_columnconfigure(0, weight=1)
        
        self.header = ctk.CTkLabel(self.gen_frame, text="Create a Memorable Password", font=ctk.CTkFont(size=20, weight="bold"))
        self.header.grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        self.location_entry = ctk.CTkEntry(self.gen_frame, width=500, placeholder_text="Memorable Places (e.g., Kyoto, Brooklyn, Yosemite)")
        self.location_entry.grid(row=1, column=0, sticky="w", pady=10)
        
        self.hobby_entry = ctk.CTkEntry(self.gen_frame, width=500, placeholder_text="Hobbies or Interests (e.g., Astronomy, Chess, Photography)")
        self.hobby_entry.grid(row=2, column=0, sticky="w", pady=10)
        
        self.media_entry = ctk.CTkEntry(self.gen_frame, width=500, placeholder_text="Favorite Books/Movies (e.g., Dune, Interstellar, Matrix)")
        self.media_entry.grid(row=3, column=0, sticky="w", pady=10)
        
        self.year_entry = ctk.CTkEntry(self.gen_frame, width=200, placeholder_text="Memorable Year (e.g., 2007)")
        self.year_entry.insert(0, "2007")
        self.year_entry.grid(row=4, column=0, sticky="w", pady=10)
        
        self.memory_style = ctk.CTkOptionMenu(self.gen_frame, values=["Phonetic", "Spatial", "Visual Absurdity"])
        self.memory_style.grid(row=5, column=0, sticky="w", pady=10)
        
        self.action_btn = ctk.CTkButton(self.gen_frame, text="Auto-Strengthen & Generate", command=self.generate_password, fg_color="#2db862", hover_color="#23924d")
        self.action_btn.grid(row=6, column=0, sticky="w", pady=20)
        
        self.result_box = ctk.CTkEntry(self.gen_frame, font=ctk.CTkFont(size=18, weight="bold"), justify="center")
        self.result_box.insert(0, "...")
        self.result_box.configure(state="disabled")
        self.result_box.grid(row=7, column=0, sticky="ew", pady=(10, 0))
        
        self.strength_label = ctk.CTkLabel(self.gen_frame, text="Strength: N/A | Time to Crack: N/A", text_color="gray")
        self.strength_label.grid(row=8, column=0, sticky="w", pady=5)
        
        self.save_frame = ctk.CTkFrame(self.gen_frame, fg_color="transparent")
        self.save_frame.grid(row=9, column=0, sticky="ew", pady=20)
        
        self.service_entry = ctk.CTkEntry(self.save_frame, placeholder_text="Service Label (e.g., GitHub)")
        self.service_entry.grid(row=0, column=0, padx=(0, 10))
        
        self.pin_entry = ctk.CTkEntry(self.save_frame, placeholder_text="Master PIN", show="*")
        self.pin_entry.grid(row=0, column=1, padx=(0, 10))
        
        self.save_btn = ctk.CTkButton(self.save_frame, text="Save to Vault", command=self.save_to_vault)
        self.save_btn.grid(row=0, column=2)

    def build_vault_frame(self):
        self.vault_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.vault_frame.grid_columnconfigure(0, weight=1)
        self.vault_frame.grid_rowconfigure(1, weight=1)
        
        self.v_header = ctk.CTkLabel(self.vault_frame, text="My Secure Vault", font=ctk.CTkFont(size=20, weight="bold"))
        self.v_header.grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        self.scroll_frame = ctk.CTkScrollableFrame(self.vault_frame)
        self.scroll_frame.grid(row=1, column=0, sticky="nsew")
        
        self.decrypt_frame = ctk.CTkFrame(self.vault_frame, fg_color="transparent")
        self.decrypt_frame.grid(row=2, column=0, sticky="ew", pady=20)
        
        self.dec_pin_entry = ctk.CTkEntry(self.decrypt_frame, placeholder_text="Master PIN", show="*")
        self.dec_pin_entry.grid(row=0, column=0, padx=(0, 10))
        
        self.decrypt_btn = ctk.CTkButton(self.decrypt_frame, text="Unlock Selected", command=self.unlock_password)
        self.decrypt_btn.grid(row=0, column=1)

    def show_generator(self):
        self.vault_frame.grid_forget()
        self.gen_frame.grid(row=0, column=1, padx=40, pady=40, sticky="nsew")

    def show_vault(self):
        self.gen_frame.grid_forget()
        self.vault_frame.grid(row=0, column=1, padx=40, pady=40, sticky="nsew")
        self.refresh_vault_list()

    def generate_password(self):
        locations = [x.strip() for x in self.location_entry.get().split(",") if x.strip()]
        hobbies = [x.strip() for x in self.hobby_entry.get().split(",") if x.strip()]
        media = [x.strip() for x in self.media_entry.get().split(",") if x.strip()]
        
        artists_list = media 
        aesthetics_list = locations + hobbies 
        year_val = self.year_entry.get().strip()
        profile_val = self.memory_style.get()
        
        if not artists_list and not aesthetics_list:
            messagebox.showerror("Input Error", "Please enter at least one location, hobby, or media type.")
            return
            
        self.action_btn.configure(text="Generating...", state="disabled")
        self.update() 
        
        try:
            raw = generate_passphrase(
                artists=artists_list, aesthetics=aesthetics_list,
                year=year_val, profile=profile_val, seed=int(time.time())
            )
            
            optimized, final_score, _ = optimize_passphrase(raw, predict_fn=predict, max_iterations=30)
            bits = entropy_bits(optimized)
            crack = crack_time_label(bits)
            score_label = LABEL_MAP.get(final_score, "Strong")
            
            self.result_box.configure(state="normal")
            self.result_box.delete(0, 'end')
            self.result_box.insert(0, optimized)
            self.result_box.configure(state="disabled")
            
            self.strength_label.configure(text=f"Strength: {score_label.upper()} | Time to Crack: {crack}")
            
            self.current_passphrase = optimized
            self.current_score = final_score
            self.current_bits = bits
            
        except Exception as e:
            messagebox.showerror("Generation Error", str(e))
        finally:
            self.action_btn.configure(text="Auto-Strengthen & Generate", state="normal")

    def save_to_vault(self):
        service_label = self.service_entry.get().strip()
        pin = self.pin_entry.get()
        
        if not hasattr(self, 'current_passphrase') or not self.current_passphrase:
            messagebox.showerror("Error", "Generate a password first.")
            return
            
        if not service_label or not pin:
            messagebox.showerror("Error", "Service label and Master PIN are required.")
            return
            
        try:
            encrypted_blob = encrypt_passphrase(self.current_passphrase, pin)
            add_vault_entry(self.db_session, service_label, encrypted_blob, self.current_score, self.current_bits)
            
            messagebox.showinfo("Success", f"Password for '{service_label}' securely saved!")
            self.service_entry.delete(0, 'end')
            self.pin_entry.delete(0, 'end')
            
        except Exception as e:
            messagebox.showerror("Encryption Error", str(e))

    def refresh_vault_list(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        try:
            entries = get_all_vault_labels(self.db_session)
            
            if not entries:
                lbl = ctk.CTkLabel(self.scroll_frame, text="Your vault is empty.", text_color="gray")
                lbl.pack(pady=20)
                self.vault_selection = None
                return
                
            self.vault_selection = ctk.StringVar(value=str(entries[0]['id']))
            
            for entry in entries:
                rb = ctk.CTkRadioButton(
                    self.scroll_frame, text=entry['label'], 
                    variable=self.vault_selection, value=str(entry['id'])
                )
                rb.pack(anchor="w", pady=10, padx=10)
                
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def unlock_password(self):
        if not hasattr(self, 'vault_selection') or not self.vault_selection:
            messagebox.showerror("Error", "No password selected or vault is empty.")
            return
            
        entry_id = self.vault_selection.get()
        pin = self.dec_pin_entry.get()
        
        if not pin:
            messagebox.showerror("Error", "Master PIN is required to unlock.")
            return
            
        try:
            encrypted_blob = get_encrypted_blob(self.db_session, entry_id)
            if not encrypted_blob:
                messagebox.showerror("Error", "Entry not found in database.")
                return
                
            decrypted_pass = decrypt_passphrase(encrypted_blob, pin)
            
            if decrypted_pass is None:
                messagebox.showerror("Error", "Incorrect Master PIN or corrupted data.")
                return
                
            messagebox.showinfo("Unlocked Successfully", f"Your Password:\n\n{decrypted_pass}\n\n(Highlight to copy. Keep this safe!)")
            self.dec_pin_entry.delete(0, 'end')
            
        except Exception as e:
            messagebox.showerror("Decryption Error", str(e))

if __name__ == "__main__":
    app = PassCraftApp()
    app.mainloop()
