import os
import json
import smtplib
import speech_recognition as sr
import pyttsx3
from email.message import EmailMessage
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import threading

# Initialize recognizer and text-to-speech engine
listener = sr.Recognizer()
engine = pyttsx3.init()

# Text-to-speech function
def talk(text):
    engine.say(text)
    engine.runAndWait()

# Function to log messages in the GUI
def log(message):
    log_text.configure(state='normal')
    log_text.insert(tk.END, message + "\n")
    log_text.configure(state='disabled')
    log_text.yview(tk.END)

# Load contacts from file
def load_contacts():
    if os.path.exists('contacts.json'):
        with open('contacts.json', 'r') as file:
            return json.load(file)
    return {}

# Save contacts to file
def save_contacts():
    with open('contacts.json', 'w') as file:
        json.dump(email_list, file)

# Optimized speech recognition function
def get_info():
    try:
        with sr.Microphone() as source:
            listener.adjust_for_ambient_noise(source, duration=1.0)
            log('Listening...')
            talk('Listening...')
            voice = listener.listen(source, timeout=5)
            info = listener.recognize_google(voice, show_all=False)
            log(f"Recognized: {info}")
            return info.lower()
    except sr.WaitTimeoutError:
        log("Listening timed out.")
        return None
    except sr.UnknownValueError:
        log("Could not understand audio.")
        return None
    except Exception as e:
        log("Error: " + str(e))
        return None

# Function to send an email
def send_email(receiver, subject, message):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('jeeva7712.k@gmail.com', 'dsuu swum uhkj simc')  # Update with your email and password
        email = EmailMessage()
        email['From'] = 'jeeva7712.k@gmail.com'  # Update with your email
        email['To'] = receiver
        email['Subject'] = subject
        email.set_content(message)
        server.send_message(email)
        server.quit()
        log("Email sent successfully.")
        talk('Your email has been sent.')
    except Exception as e:
        log("Failed to send email: " + str(e))
        talk("Sorry, I couldn't send the email. Please check your connection and try again.")

# Load predefined list of email contacts
email_list = load_contacts()

# Function to update the email list in the GUI
def update_email_list(tree):
    for item in tree.get_children():
        tree.delete(item)
    for name, email in email_list.items():
        tree.insert('', 'end', values=(name, email))

# Function to update the email list in the GUI after adding/removing contacts
def add_contact(tree, name_entry, email_entry):
    name = name_entry.get()
    email = email_entry.get()

    if not name or not email:
        messagebox.showerror("Error", "Both name and email must be filled.")
        return

    if name in email_list:
        messagebox.showerror("Error", "Contact already exists.")
        return

    email_list[name] = email
    save_contacts()  # Save the updated contacts
    update_email_list(tree)
    log(f"Added contact: {name} <{email}>")
    name_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)

# Function to remove selected contact
def remove_contact(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "No contact selected.")
        return

    name = tree.item(selected_item)['values'][0]
    confirm = messagebox.askyesno("Confirm", f"Are you sure you want to remove {name}?")
    if confirm:
        del email_list[name]
        save_contacts()  # Save the updated contacts
        update_email_list(tree)
        log(f"Removed contact: {name}")

# Main function to gather email information and send the email
def get_email_info():
    talk('To whom do you want to send the email?')
    name = get_info()

    if name is None:
        return

    receiver = email_list.get(name)
    if receiver is None:
        log(f"I don't have an email address for {name}. Please try again.")
        talk(f"I don't have an email address for {name}. Please try again.")
        return

    talk('What is the subject of your email?')
    subject = get_info()

    if subject is None:
        return

    talk('Tell me the text in your email.')
    message = get_info()

    if message is None:
        return

    talk('Can I send the mail?')
    confirmation = get_info()
    if confirmation in ["yes", "send", "go ahead", "yes send"]:
        send_email(receiver, subject, message)
    else:
        log("Email not sent.")

# Function to handle sending email in a separate thread
def send_email_thread():
    threading.Thread(target=get_email_info, daemon=True).start()

# Setup GUI
def setup_gui():
    global log_text

    root = tk.Tk()
    root.title("Voice Email Sender")
    root.geometry("600x400")
    root.configure(bg="#D3D3D3")  # Light grey background color for the main window

    # Title at the top center with black text
    title_label = tk.Label(root, text="VOICE MAIL AUTOMATION", font=("Times New Roman", 20, "bold"), fg="black", bg="#D3D3D3")
    title_label.pack(fill=tk.X, pady=(0, 0))

    # Create top frame for toggle button
    top_frame = tk.Frame(root, bg="#D3D3D3")
    top_frame.pack(fill=tk.X, padx=20, pady=(10, 0))

    # Toggle button for email contacts
    toggle_button = tk.Button(top_frame, text="Contacts", command=lambda: toggle_drawer(drawer_frame),
                               bg="#3498DB", fg="white", relief=tk.RAISED, bd=5, font=("Times New Roman", 12))
    toggle_button.pack(side=tk.RIGHT)

    # Center frame
    center_frame = tk.Frame(root, bg="#D3D3D3")
    center_frame.pack(expand=True, padx=20, pady=10)

    mic_label = tk.Label(center_frame, text="      🎙️", font=("Times New Roman", 40), bg="#D3D3D3")
    mic_label.pack(pady=10)

    start_button = tk.Button(center_frame, text="Start", font=("Times New Roman", 16), command=send_email_thread, bg="#27AE60", fg="white", relief=tk.RAISED, bd=5)
    start_button.pack(pady=10)

    # Log frame
    log_frame = tk.Frame(root, bg="#D3D3D3")
    log_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

    log_text = tk.Text(log_frame, height=10, bg="#F0F0F0", font=("Times New Roman", 10), state='disabled')
    log_text.pack(expand=True, fill=tk.BOTH)

    # Drawer for email contacts
    drawer_frame = tk.Frame(root, bg="#3498DB", width=200)
    drawer_frame.pack(side=tk.RIGHT, fill=tk.Y)

    label = tk.Label(drawer_frame, text="Email Contacts", font=("Times New Roman", 12), bg="#D3D3D3", fg="black")
    label.pack(pady=5)

    columns = ('Name', 'Email')
    tree = ttk.Treeview(drawer_frame, columns=columns, show='headings', height=10)
    tree.heading('Name', text='Name', anchor=tk.CENTER)
    tree.heading('Email', text='Email', anchor=tk.CENTER)
    tree.column('Name', anchor=tk.CENTER, width=60)
    tree.column('Email', anchor=tk.CENTER, width=60)
    tree.pack(fill=tk.BOTH, expand=True)

    update_email_list(tree)

    # Entry fields for adding contacts
    contact_frame = tk.Frame(drawer_frame, bg="#AED6F1")
    contact_frame.pack(pady=5)

    name_entry = tk.Entry(contact_frame, width=12, font=("Times New Roman", 12))
    name_entry.grid(row=0, column=0, padx=5, pady=5)
    name_entry.insert(0, "Name")

    email_entry = tk.Entry(contact_frame, width=12, font=("Times New Roman", 12))
    email_entry.grid(row=0, column=1, padx=5, pady=5)
    email_entry.insert(0, "Email")

    add_button = tk.Button(drawer_frame, text="Add Contact", command=lambda: add_contact(tree, name_entry, email_entry), bg="#F7DC6F", font=("Times New Roman", 12))
    add_button.pack(pady=2)

    remove_button = tk.Button(drawer_frame, text="Remove Contact", command=lambda: remove_contact(tree), bg="#E74C3C", fg="white", font=("Times New Roman", 12))
    remove_button.pack(pady=0)

    root.mainloop()

# Toggle the visibility of the drawer
def toggle_drawer(drawer_frame):
    if drawer_frame.winfo_ismapped():
        drawer_frame.pack_forget()
    else:
        drawer_frame.pack(side=tk.RIGHT, fill=tk.Y)

# Start the GUI application
setup_gui()