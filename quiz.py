import json
import random
import platform
from tkinter import *
from tkinter.messagebox import *
from tkinter.ttk import Progressbar
from tkinter import ttk
import os

# Sound configuration
if platform.system() == "Windows":
    import winsound
else:
    winsound = None

SOUND_CORRECT = "correct.wav"
SOUND_WRONG = "wrong.wav"
SOUND_CLICK = "click.wav"
SOUND_START = "start.wav"

if not os.path.exists(SOUND_CORRECT) and winsound:
    winsound.Beep(1000, 200)

DARK_THEME = {
    "bg": "#2d2d2d",
    "fg": "#ffffff",
    "card_bg": "#3d3d3d",
    "card_fg": "#ffffff",
    "button_bg": "#4CAF50",
    "button_fg": "#ffffff",
    "button_active": "#45a049",
    "button_hover": "#3e8e41",
    "radio_bg": "#3d3d3d",
    "radio_select": "#4d4d4d",
    "correct_color": "#4CAF50",
    "wrong_color": "#f44336",
    "timer_warning": "#ff9800",
    "timer_danger": "#f44336",
    "highlight_bg": "#4d4d4d",
    "progress_bg": "#3d3d3d",
    "progress_fg": "#4CAF50"
}

LIGHT_THEME = {
    "bg": "#f5f5f5",
    "fg": "#333333",
    "card_bg": "#ffffff",
    "card_fg": "#333333",
    "button_bg": "#4CAF50",
    "button_fg": "#ffffff",
    "button_active": "#45a049",
    "button_hover": "#3e8e41",
    "radio_bg": "#ffffff",
    "radio_select": "#f0f0f0",
    "correct_color": "#4CAF50",
    "wrong_color": "#f44336",
    "timer_warning": "#ff9800",
    "timer_danger": "#f44336",
    "highlight_bg": "#e3f2fd",
    "progress_bg": "#f0f0f0",
    "progress_fg": "#4CAF50"
}

win = Tk()
win.title("Gym Quiz Game")
win.geometry("900x700")
win.minsize(800, 600)
win.configure(bg=DARK_THEME["bg"])

try:
    with open("quiz.json", "r") as file:
        questions = json.load(file)
except Exception as e:
    showerror("Error", f"Failed to load quiz data: {e}")
    win.destroy()

current_question = 0
score = 0
user_answers = []
total_questions = 0
time_left = 30
timer_id = None
filtered_questions = []
current_theme = DARK_THEME

header_frame = Frame(win, bg=current_theme["bg"])
header_frame.pack(fill=X, padx=20, pady=10)

main_frame = Frame(win, bg=current_theme["bg"])
main_frame.pack(expand=True, fill=BOTH, padx=20, pady=10)

footer_frame = Frame(win, bg=current_theme["bg"])
footer_frame.pack(fill=X, padx=20, pady=10)

title_label = Label(header_frame, text="Gym Quiz Challenge", 
                   font=("Arial", 24, "bold"), bg=current_theme["bg"], fg=current_theme["fg"])
title_label.pack(side=LEFT)

def toggle_theme():
    global current_theme
    if current_theme == DARK_THEME:
        current_theme = LIGHT_THEME
        theme_btn.config(text="🌙 Dark Mode")
    else:
        current_theme = DARK_THEME
        theme_btn.config(text="☀️ Light Mode")
    apply_theme()

theme_btn = Button(header_frame, text="☀️ Light Mode", command=toggle_theme,
                  font=("Arial", 10), bg=current_theme["button_bg"], fg=current_theme["button_fg"],
                  borderwidth=0, padx=10)
theme_btn.pack(side=RIGHT)

timer_label = Label(header_frame, text="", font=("Arial", 14), 
                   bg=current_theme["bg"], fg=current_theme["fg"])
timer_label.pack(side=RIGHT, padx=20)

question_card = Frame(main_frame, bg=current_theme["card_bg"], padx=20, pady=15,
                     highlightbackground="#555", highlightthickness=1)
question_label = Label(question_card, text="", font=("Arial", 16), 
                      bg=current_theme["card_bg"], fg=current_theme["card_fg"], wraplength=700)
question_label.pack()

options_card = Frame(main_frame, bg=current_theme["card_bg"], padx=20, pady=15,
                    highlightbackground="#555", highlightthickness=1)
options_frame = Frame(options_card, bg=current_theme["card_bg"])
options_frame.pack()

selected_option = IntVar(value=-1)
radio_buttons = []
for i in range(4):
    rb = Radiobutton(options_frame, text="", variable=selected_option, value=i, 
                    bg=current_theme["radio_bg"], font=("Arial", 14), 
                    fg=current_theme["card_fg"], selectcolor=current_theme["radio_select"],
                    activebackground=current_theme["radio_bg"],
                    activeforeground=current_theme["card_fg"])
    rb.pack(anchor='w', pady=8, ipadx=10)
    radio_buttons.append(rb)

style = ttk.Style()
style.configure("custom.Horizontal.TProgressbar",
               background=current_theme["progress_fg"],
               troughcolor=current_theme["progress_bg"])

progress = Progressbar(main_frame, orient=HORIZONTAL, length=700, mode='determinate',
                      style="custom.Horizontal.TProgressbar")

button_frame = Frame(footer_frame, bg=current_theme["bg"])
button_frame.pack()

start_button = Button(button_frame, text="Start Quiz", command=lambda: [play_sound(SOUND_START), start_quiz()], 
                     font=("Arial", 14, "bold"), bg=current_theme["button_bg"], fg=current_theme["button_fg"], 
                     padx=30, pady=10, bd=0, highlightthickness=0)

next_button = Button(button_frame, text="Next Question", command=lambda: [play_sound(SOUND_CLICK), next_question()], 
                    font=("Arial", 14, "bold"), bg="#2196F3", fg="white", 
                    padx=30, pady=10, bd=0, highlightthickness=0)

category_card = Frame(main_frame, bg=current_theme["card_bg"], padx=20, pady=15,
                     highlightbackground="#555", highlightthickness=1)
Label(category_card, text="Select Categories:", font=("Arial", 14, "bold"),
      bg=current_theme["card_bg"], fg=current_theme["card_fg"]).pack(anchor='w')

category_vars = {}
categories = list(set(q.get("category", "General") for q in questions))
category_buttons_frame = Frame(category_card, bg=current_theme["card_bg"])
category_buttons_frame.pack(fill=X, pady=10)
for cat in categories:
    category_vars[cat] = BooleanVar(value=True)
    Checkbutton(category_buttons_frame, text=cat, variable=category_vars[cat], 
               bg=current_theme["card_bg"], font=("Arial", 12),
               fg=current_theme["card_fg"], selectcolor=current_theme["radio_select"]).pack(anchor='w', padx=10)

difficulty_card = Frame(main_frame, bg=current_theme["card_bg"], padx=20, pady=15,
                      highlightbackground="#555", highlightthickness=1)
Label(difficulty_card, text="Select Difficulty:", font=("Arial", 14, "bold"),
      bg=current_theme["card_bg"], fg=current_theme["card_fg"]).pack(anchor='w')

difficulty_var = StringVar(value="All")
difficulty_frame = Frame(difficulty_card, bg=current_theme["card_bg"])
difficulty_frame.pack(fill=X, pady=10)
difficulty_options = ["All", "Easy", "Medium", "Hard"]
for diff in difficulty_options:
    Radiobutton(difficulty_frame, text=diff, variable=difficulty_var, value=diff, 
               bg=current_theme["card_bg"], font=("Arial", 12),
               fg=current_theme["card_fg"], selectcolor=current_theme["radio_select"]).pack(side=LEFT, padx=15)

count_card = Frame(main_frame, bg=current_theme["card_bg"], padx=20, pady=15,
                 highlightbackground="#555", highlightthickness=1)
Label(count_card, text="Number of questions (5-20):", 
      font=("Arial", 14, "bold"), bg=current_theme["card_bg"], fg=current_theme["card_fg"]).pack(anchor='w')

count_frame = Frame(count_card, bg=current_theme["card_bg"])
count_frame.pack(fill=X, pady=10)
question_count = Spinbox(count_frame, from_=5, to=20, width=3, font=("Arial", 14))
question_count.pack(side=LEFT, padx=10)

def apply_theme():
    """Apply the current theme to all widgets"""
    win.config(bg=current_theme["bg"])
    header_frame.config(bg=current_theme["bg"])
    main_frame.config(bg=current_theme["bg"])
    footer_frame.config(bg=current_theme["bg"])
    
    for widget in [title_label, timer_label]:
        widget.config(bg=current_theme["bg"], fg=current_theme["fg"])
    
    for card in [question_card, options_card, category_card, difficulty_card, count_card]:
        card.config(bg=current_theme["card_bg"], highlightbackground=current_theme["fg"])
    
    question_label.config(bg=current_theme["card_bg"], fg=current_theme["card_fg"])
    options_frame.config(bg=current_theme["card_bg"])
    
    for rb in radio_buttons:
        rb.config(bg=current_theme["radio_bg"], fg=current_theme["card_fg"],
                selectcolor=current_theme["radio_select"])
    
    style.configure("custom.Horizontal.TProgressbar",
                  background=current_theme["progress_fg"],
                  troughcolor=current_theme["progress_bg"])
    
    for btn in [start_button, next_button, theme_btn]:
        btn.config(bg=current_theme["button_bg"], fg=current_theme["button_fg"])
    
    for widget in category_card.winfo_children() + difficulty_card.winfo_children() + count_card.winfo_children():
        if isinstance(widget, (Label, Checkbutton, Radiobutton)):
            widget.config(bg=current_theme["card_bg"], fg=current_theme["card_fg"])

def show_welcome():
    """Show the welcome screen with configuration options"""
    clear_main_frame()
    
    welcome_card = Frame(main_frame, bg=current_theme["card_bg"], padx=20, pady=20,
                        highlightbackground="#555", highlightthickness=1)
    welcome_card.pack(fill=BOTH, expand=True, pady=20)
    
    welcome_text = """Welcome to the Gym Quiz Challenge!

Test your knowledge of:
- Workout techniques
- Nutrition facts
- Exercise physiology
- Gym equipment

Select your preferences below and click 'Start Quiz' to begin!"""
    Label(welcome_card, text=welcome_text, font=("Arial", 16), 
          bg=current_theme["card_bg"], fg=current_theme["card_fg"], justify=LEFT).pack(pady=20)
    
    category_card.pack(fill=X, pady=10)
    difficulty_card.pack(fill=X, pady=10)
    count_card.pack(fill=X, pady=10)
    
    start_button.pack(pady=20)

def clear_main_frame():
    """Clear all widgets from the main frame"""
    for widget in main_frame.winfo_children():
        widget.pack_forget()

def play_sound(sound_file):
    """Play a sound effect if available"""
    try:
        if winsound:
            winsound.PlaySound(sound_file, winsound.SND_FILENAME)
    except Exception as e:
        print(f"Error playing sound: {e}")

def shake_window():
    """Create a small shaking effect for the window"""
    x = win.winfo_x()
    y = win.winfo_y()
    for _ in range(3):
        win.geometry(f"+{x+5}+{y}")
        win.update()
        win.after(50)
        win.geometry(f"+{x-5}+{y}")
        win.update()
        win.after(50)
    win.geometry(f"+{x}+{y}")

def update_timer():
    """Update the countdown timer"""
    global time_left, timer_id
    
    if timer_id is None:  # Safety check
        return
    
    time_left -= 1
    timer_label.config(text=f"Time left: {time_left}s")
    
    if time_left <= 10:
        timer_label.config(fg=current_theme["timer_danger"])
    elif time_left <= 20:
        timer_label.config(fg=current_theme["timer_warning"])
    
    if time_left > 0:
        timer_id = win.after(1000, update_timer)
    else:
        play_sound(SOUND_WRONG)
        next_question()

def load_question():
    """Load the current question into the UI"""
    global current_question, timer_id
    
    if timer_id is not None:
        win.after_cancel(timer_id)
        timer_id = None
    
    time_left = 30
    timer_label.config(text=f"Time left: {time_left}s", fg=current_theme["fg"])
    timer_id = win.after(1000, update_timer)
    
    question_data = filtered_questions[current_question]
    question_label.config(text=f"Question {current_question + 1}: {question_data['question']}")
    
    for i, option in enumerate(question_data["options"]):
        radio_buttons[i].config(text=option, state=NORMAL, bg=current_theme["radio_bg"])
    
    selected_option.set(-1)  
    
    progress['value'] = (current_question + 1) / total_questions * 100
    win.update_idletasks()

def highlight_options():
    """Briefly highlight the options to draw attention"""
    for rb in radio_buttons:
        rb.config(bg=current_theme["highlight_bg"])
    win.after(500, lambda: [rb.config(bg=current_theme["radio_bg"]) for rb in radio_buttons])

def next_question():
    """Handle moving to the next question or showing results"""
    global current_question, score
    
    if selected_option.get() == -1:
        play_sound(SOUND_WRONG)
        showwarning("No Selection", "Please select an answer before proceeding.")
        highlight_options()
        shake_window()
        return
    
    # Record answer
    user_answer = selected_option.get()
    user_answers.append(user_answer)
    
    # Play appropriate sound
    if user_answer == filtered_questions[current_question]["correct_answer"]:
        play_sound(SOUND_CORRECT)
        score += 1
    else:
        play_sound(SOUND_WRONG)
    
    # Move to next question or show results
    if current_question < total_questions - 1:
        current_question += 1
        load_question()
    else:
        show_result()

def reset_quiz_state():
    """Reset all quiz variables to initial state"""
    global current_question, score, user_answers, time_left, timer_id, filtered_questions
    
    current_question = 0
    score = 0
    user_answers = []
    time_left = 30
    if timer_id is not None:
        win.after_cancel(timer_id)
        timer_id = None
    filtered_questions = []
    selected_option.set(-1)
    timer_label.config(text="", fg=current_theme["fg"])

def start_quiz():
    """Start the quiz with selected parameters"""
    global total_questions, filtered_questions
    
    reset_quiz_state()
    
    # Validate question count
    try:
        total_questions = int(question_count.get())
        if not 5 <= total_questions <= 20:
            showerror("Error", "Please choose between 5 and 20 questions.")
            return
    except ValueError:
        showerror("Error", "Please enter a valid number.")
        return
    
    # Get selected categories
    selected_categories = [cat for cat, var in category_vars.items() if var.get()]
    if not selected_categories:
        showerror("Error", "Please select at least one category")
        return
    
    # Get selected difficulty
    selected_difficulty = difficulty_var.get()
    
    # Filter questions
    filtered_questions = [
        q for q in questions 
        if q.get("category", "General") in selected_categories and 
        (selected_difficulty == "All" or q.get("difficulty", "Medium") == selected_difficulty)
    ]
    
    if len(filtered_questions) < total_questions:
        showerror("Error", 
                 f"Not enough questions available with current filters ({len(filtered_questions)} available, {total_questions} requested)")
        return
    
    random.shuffle(filtered_questions)
    filtered_questions = filtered_questions[:total_questions]
    
    clear_main_frame()
    question_card.pack(fill=X, pady=10)
    options_card.pack(fill=X, pady=10)
    progress.pack(pady=20)
    next_button.pack(pady=20)
    
    load_question()

def show_result():
    """Show the quiz results"""
    global timer_id
    
    if timer_id is not None:
        win.after_cancel(timer_id)
        timer_id = None
    
    percentage = (score / total_questions) * 100
    
    if percentage < 40:
        rating = "Newbie"
        rating_color = current_theme["wrong_color"]
    elif percentage < 60:
        rating = "Beginner"
        rating_color = "#FFC107"
    elif percentage < 80:
        rating = "Intermediate"
        rating_color = "#2196F3"
    elif percentage < 90:
        rating = "Advanced"
        rating_color = "#4CAF50"
    else:
        rating = "Elite"
        rating_color = "#9C27B0"
    
    result_window = Toplevel(win)
    result_window.title("Quiz Results")
    result_window.geometry("700x600")
    result_window.minsize(600, 500)
    result_window.configure(bg=current_theme["bg"])
    
    header_frame_result = Frame(result_window, bg=current_theme["bg"])
    header_frame_result.pack(fill=X, padx=20, pady=10)
    
    Label(header_frame_result, text="Quiz Results", font=("Arial", 24, "bold"), 
          bg=current_theme["bg"], fg=current_theme["fg"]).pack()
    
    score_card = Frame(result_window, bg=current_theme["card_bg"], padx=20, pady=15,
                     highlightbackground="#555", highlightthickness=1)
    score_card.pack(fill=X, padx=20, pady=10)
    
    score_text = f"Your score: {score}/{total_questions} ({percentage:.1f}%)"
    Label(score_card, text=score_text, font=("Arial", 18), 
          bg=current_theme["card_bg"], fg=current_theme["card_fg"]).pack(pady=5)
    
    Label(score_card, text=f"Rating: {rating}", font=("Arial", 18), 
          fg=rating_color, bg=current_theme["card_bg"]).pack(pady=5)
    
    details_card = Frame(result_window, bg=current_theme["card_bg"], padx=20, pady=15,
                       highlightbackground="#555", highlightthickness=1)
    details_card.pack(fill=BOTH, expand=True, padx=20, pady=10)
    
    Label(details_card, text="Detailed Results:", font=("Arial", 16, "bold"),
          bg=current_theme["card_bg"], fg=current_theme["card_fg"]).pack(anchor='w')
    
    canvas_result = Canvas(details_card, bg=current_theme["card_bg"], highlightthickness=0)
    scrollbar = Scrollbar(details_card, orient=VERTICAL, command=canvas_result.yview)
    scrollable_frame = Frame(canvas_result, bg=current_theme["card_bg"])
    
    scrollable_frame.bind("<Configure>", lambda e: canvas_result.configure(scrollregion=canvas_result.bbox("all")))
    
    canvas_result.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas_result.configure(yscrollcommand=scrollbar.set)
    
    
    for i, answer in enumerate(user_answers):
        result_frame = Frame(scrollable_frame, bg=current_theme["card_bg"])
        result_frame.pack(fill=X, padx=10, pady=5)
        
        is_correct = answer == filtered_questions[i]["correct_answer"]
        color = current_theme["correct_color"] if is_correct else current_theme["wrong_color"]
        symbol = "✓" if is_correct else "✗"
        
        Label(result_frame, text=f"Q{i+1}: {symbol}", font=("Arial", 14), 
              fg=color, width=5, bg=current_theme["card_bg"]).pack(side=LEFT)
        
        question_text = Frame(result_frame, bg=current_theme["card_bg"])
        question_text.pack(side=LEFT, expand=True, fill=X, padx=10)
        
        Label(question_text, text=filtered_questions[i]["question"], font=("Arial", 12), 
              wraplength=500, justify=LEFT, bg=current_theme["card_bg"], fg=current_theme["card_fg"]).pack(anchor='w')
        

        if not is_correct:
            correct_answer = filtered_questions[i]["options"][filtered_questions[i]["correct_answer"]]
            Label(question_text, text=f"Correct answer: {correct_answer}", font=("Arial", 12, "italic"), 
                  fg=current_theme["correct_color"], bg=current_theme["card_bg"]).pack(anchor='w')
    
    canvas_result.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.pack(side=RIGHT, fill=Y)
    

    button_frame_result = Frame(result_window, bg=current_theme["bg"])
    button_frame_result.pack(fill=X, padx=20, pady=20)
    
    Button(button_frame_result, text="Play Again", command=lambda: [result_window.destroy(), start_quiz()], 
           font=("Arial", 14), bg="#4CAF50", fg="white", padx=20, pady=10).pack(side=LEFT, expand=True)
    
    Button(button_frame_result, text="New Quiz", command=lambda: [result_window.destroy(), show_welcome()], 
           font=("Arial", 14), bg="#2196F3", fg="white", padx=20, pady=10).pack(side=LEFT, expand=True, padx=20)
    
    Button(button_frame_result, text="Quit", command=win.quit, 
           font=("Arial", 14), bg="#f44336", fg="white", padx=20, pady=10).pack(side=LEFT, expand=True)


def on_enter(e):
    e.widget['background'] = e.widget.hover_color if hasattr(e.widget, 'hover_color') else current_theme["button_hover"]

def on_leave(e):
    e.widget['background'] = e.widget.default_color if hasattr(e.widget, 'default_color') else current_theme["button_bg"]


for btn in [start_button, next_button, theme_btn]:
    btn.default_color = btn.cget("background")
    btn.hover_color = current_theme["button_hover"]
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)


apply_theme()
show_welcome()
win.mainloop()