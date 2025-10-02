import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import random
import threading
import time

# --- CHALLENGES DATA ---
# This list contains all the challenges for the game.
challenges = [
    # Level 1: Basic SELECT & Filtering
    { 'id': 0, 'locationName': 'Crash Site', 'title': 'Take Inventory (SELECT *)', 'story': "Let's see what's in the plane wreckage. Show everything from the `wreckage_manifest`.", 'query': "SELECT * FROM wreckage_manifest;", 'points': 10, 'type': 'SELECT' },
    { 'id': 1, 'locationName': 'Crash Site', 'title': 'Find Usable Items (WHERE)', 'story': "We only need items in 'Good' condition. From the wreckage, show the `description` of items where `condition` is 'Good'.", 'query': "SELECT description FROM wreckage_manifest WHERE condition = 'Good';", 'points': 10, 'type': 'SELECT' },
    { 'id': 2, 'locationName': 'Crash Site', 'title': 'Find Water (AND)', 'story': "You are thirsty. Find all resources that are 'Water' type AND are 'Potable' (safe to drink).", 'query': "SELECT * FROM resources WHERE type = 'Water' AND edibility = 'Potable';", 'points': 10, 'type': 'SELECT' },
    { 'id': 3, 'locationName': 'Beach', 'title': 'Unique Resources (DISTINCT)', 'story': "To take stock, list each unique resource `type` you've found on the island so far.", 'query': "SELECT DISTINCT type FROM resources;", 'points': 15, 'type': 'SELECT' },
    # Level 2: Sorting & Limiting
    { 'id': 4, 'locationName': 'Beach', 'title': 'Sort Wildlife (ORDER BY)', 'story': "You hear animals nearby. List all wildlife on the beach (location_id 2) and sort them by `name` alphabetically.", 'query': "SELECT name FROM wildlife WHERE location_id = 2 ORDER BY name;", 'points': 15, 'type': 'SELECT' },
    { 'id': 5, 'locationName': 'Beach', 'title': 'Find Survivors (NOT)', 'story': "Find all survivors who are NOT at the Crash Site (location_id 1).", 'query': "SELECT name FROM survivors WHERE NOT location_id = 1;", 'points': 15, 'type': 'SELECT' },
    { 'id': 6, 'locationName': 'Jungle', 'title': 'Top 3 Dangers (LIMIT)', 'story': "The jungle is dangerous. List the top 3 animals with the highest `danger_level`.", 'query': "SELECT name, danger_level FROM wildlife ORDER BY danger_level DESC LIMIT 3;", 'points': 15, 'type': 'SELECT' },
    # Level 3: Aggregation Fundamentals
    { 'id': 7, 'locationName': 'Jungle', 'title': 'Count Resources (COUNT)', 'story': "How many different kinds of resources are in the jungle (location_id 3)? Count them.", 'query': "SELECT COUNT(*) FROM resources WHERE location_id = 3;", 'points': 15, 'type': 'SELECT' },
    { 'id': 8, 'locationName': 'Jungle', 'title': 'Total Food (SUM)', 'story': "You're getting hungry. What is the total `quantity` of all 'Edible' food on the island?", 'query': "SELECT SUM(quantity) FROM resources WHERE edibility = 'Edible';", 'points': 15, 'type': 'SELECT' },
    { 'id': 9, 'locationName': 'Jungle', 'title': 'Weakest Survivor (MIN)', 'story': "We need to look out for each other. Find the `name` of the survivor with the lowest `health`.", 'query': "SELECT name FROM survivors ORDER BY health ASC LIMIT 1;", 'points': 15, 'type': 'SELECT' },
    { 'id': 10, 'locationName': 'Jungle', 'title': 'Most Dangerous Animal (MAX)', 'story': "What is the single most dangerous animal on the island? Find the maximum `danger_level`.", 'query': "SELECT MAX(danger_level) FROM wildlife;", 'points': 15, 'type': 'SELECT' },
    { 'id': 11, 'locationName': 'Jungle', 'title': 'Average Danger (AVG)', 'story': "To prepare, find the average `danger_level` of all wildlife in the jungle (location_id 3).", 'query': "SELECT AVG(danger_level) FROM wildlife WHERE location_id = 3;", 'points': 15, 'type': 'SELECT' },
    { 'id': 12, 'locationName': 'Jungle', 'title': 'Group Resources (GROUP BY)', 'story': "Let's organize our findings. Show a count of how many resources there are for each `type`.", 'query': "SELECT type, COUNT(*) FROM resources GROUP BY type;", 'points': 20, 'type': 'SELECT' },
    # Level 4: Filtering Aggregates
    { 'id': 13, 'locationName': 'Cave', 'title': 'Resource Hotspots (HAVING)', 'story': "Some areas are richer than others. Find the `location_id` for all places that have more than two kinds of resources.", 'query': "SELECT location_id FROM resources GROUP BY location_id HAVING COUNT(id) > 2;", 'points': 20, 'type': 'SELECT' },
    # Level 5: Basic Joins
    { 'id': 14, 'locationName': 'Cave', 'title': 'Survivor Locations (INNER JOIN)', 'story': "Let's find everyone. Show each survivor's `name` and the `name` of the location they are in.", 'query': "SELECT s.name, l.name as location_name FROM survivors s JOIN locations l ON s.location_id = l.id;", 'points': 25, 'type': 'SELECT' },
    { 'id': 15, 'locationName': 'Cave', 'title': 'Survivors Without Logs (LEFT JOIN & IS NULL)', 'story': "Is anyone not keeping a log? Find the names of any survivors who do not have an entry in the `survivor_log`.", 'query': "SELECT s.name FROM survivors s LEFT JOIN survivor_log sl ON s.id = sl.survivor_id WHERE sl.log_id IS NULL;", 'points': 25, 'type': 'SELECT' },
    # Level 6: Multiple Joins
    { 'id': 16, 'locationName': 'Cave', 'title': 'Full Report', 'story': "We need a full status report. Show the survivor's name, the location they are in, and their latest log entry.", 'query': "SELECT s.name, l.name AS location, sl.log_entry FROM survivors s JOIN locations l ON s.location_id = l.id LEFT JOIN survivor_log sl ON s.id = sl.survivor_id;", 'points': 30, 'type': 'SELECT' },
    # Level 7: Subqueries
    { 'id': 17, 'locationName': 'Mountain', 'title': 'Above-Average Danger (Subquery)', 'story': "To stay safe, identify all animals whose `danger_level` is higher than the island's average.", 'query': "SELECT name, danger_level FROM wildlife WHERE danger_level > (SELECT AVG(danger_level) FROM wildlife);", 'points': 35, 'type': 'SELECT' },
    # Level 8: String Functions & Filtering
    { 'id': 18, 'locationName': 'Mountain', 'title': 'Find Berries (LIKE)', 'story': "You remember seeing some berries. Find any resource whose `name` ends with the word 'Berries'.", 'query': "SELECT * FROM resources WHERE name LIKE '%Berries';", 'points': 20, 'type': 'SELECT' },
    { 'id': 19, 'locationName': 'Mountain', 'title': 'Food and Water (IN)', 'story': "You need to focus on essentials. List the names of all resources that are either 'Food' or 'Water' type.", 'query': "SELECT name FROM resources WHERE type IN ('Food', 'Water');", 'points': 20, 'type': 'SELECT' },
    { 'id': 20, 'locationName': 'Mountain', 'title': 'Clean the Manifest (TRIM)', 'story': "The item IDs in the manifest have extra spaces. Show the `description` and the `item_id` without any spaces.", 'query': "SELECT TRIM(item_id) AS cleaned_id, description FROM wreckage_manifest;", 'points': 15, 'type': 'SELECT' },
    # Level 9: Conditional Logic & Window Functions
    { 'id': 21, 'locationName': 'River Delta', 'title': 'Assess Item Conditions (CASE)', 'story': "Let's sort the salvaged items. If `condition` is 'Good', call it 'Usable'. If 'Damaged', call it 'Needs Repair'.", 'query': "SELECT description, CASE condition WHEN 'Good' THEN 'Usable' WHEN 'Damaged' THEN 'Needs Repair' END AS status FROM wreckage_manifest;", 'points': 25, 'type': 'SELECT' },
    { 'id': 22, 'locationName': 'River Delta', 'title': 'Rank Resources by Location (RANK)', 'story': "You need to organize supplies. List all resources, ranked alphabetically by `name` for each `location_id`.", 'query': "SELECT name, location_id, RANK() OVER (PARTITION BY location_id ORDER BY name) as location_rank FROM resources;", 'points': 40, 'type': 'SELECT' },
    { 'id': 23, 'locationName': 'River Delta', 'title': 'Check Previous Log (LAG)', 'story': "To understand survivor movements, show each log entry along with the entry that came before it for each survivor.", 'query': "SELECT log_entry, LAG(log_entry, 1, 'First entry') OVER (PARTITION BY survivor_id ORDER BY log_date) as previous_entry FROM survivor_log;", 'points': 40, 'type': 'SELECT' },
    # Level 10: Set Operations & Date Functions
    { 'id': 24, 'locationName': 'Abandoned Camp', 'title': 'Potential Food Sources (UNION)', 'story': "List all possible things you can eat. Combine the `name` of all 'Edible' resources with the `name` of all wildlife with a danger level less than 2.", 'query': "SELECT name FROM resources WHERE edibility = 'Edible' UNION SELECT name FROM wildlife WHERE danger_level < 2;", 'points': 30, 'type': 'SELECT' },
    { 'id': 25, 'locationName': 'Abandoned Camp', 'title': 'Logs from a Time Range (BETWEEN)', 'story': "You want to find out what happened when you first arrived. Show all log entries between October 1st and October 2nd, 2025.", 'query': "SELECT * FROM survivor_log WHERE log_date BETWEEN '2025-10-01' AND '2025-10-02';", 'points': 30, 'type': 'SELECT' },
    # Level 11: Data Modification
    { 'id': 26, 'locationName': 'Abandoned Camp', 'title': 'Add Supplies (INSERT)', 'story': "You found a stash of firewood. Add 'Firewood' to the `camp_supplies` with a quantity of 10 and a 'Good' status.", 'query': "INSERT INTO camp_supplies (item_name, quantity, status) VALUES ('Firewood', 10, 'Good');", 'points': 25, 'type': 'DML' },
    { 'id': 27, 'locationName': 'Abandoned Camp', 'title': 'Fix Supplies (UPDATE)', 'story': "The matches at the abandoned camp are damp. Update their `status` to 'Useless' in the `camp_supplies` table.", 'query': "UPDATE camp_supplies SET status = 'Useless' WHERE item_name = 'Matches';", 'points': 25, 'type': 'DML' },
    { 'id': 28, 'locationName': 'Abandoned Camp', 'title': 'Use Rope (DELETE)', 'story': "You used the rope to build a shelter. Remove 'Rope' from the `camp_supplies`.", 'query': "DELETE FROM camp_supplies WHERE item_name = 'Rope';", 'points': 25, 'type': 'DML' },
    # Level 12: Final Challenge
    { 'id': 29, 'locationName': 'Rescue Landing Site', 'title': 'Final Rescue (Complex Query)', 'story': "The rescue helicopter is close! You need a list of all survivors who are healthy (health > 90) and are at the 'Rescue Landing Site' (location_id 8).", 'query': "SELECT name FROM survivors WHERE health > 90 AND location_id = 8;", 'points': 100, 'type': 'SELECT' }
]

class SQLGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SQL Survival Island")
        self.geometry("1400x800")
        self.configure(bg="#1a202c")

        # --- Game State ---
        self.game_state = {}
        self.ai_solve_thread = None
        self.timer_thread = None

        # --- Database Setup ---
        self.db_conn = sqlite3.connect(":memory:") # Use in-memory SQLite database
        self.setup_database()

        # --- UI Setup ---
        self.create_widgets()
        self.reset_game()

    def setup_database(self):
        cursor = self.db_conn.cursor()
        # Schema
        schema = """
            CREATE TABLE survivors (id INT, name VARCHAR(255), health INT, energy INT, location_id INT);
            CREATE TABLE locations (id INT, name VARCHAR(255), icon TEXT, description VARCHAR(255), unlocks_location VARCHAR(255));
            CREATE TABLE resources (id INT, name VARCHAR(255), type VARCHAR(255), quantity INT, location_id INT, edibility VARCHAR(255));
            CREATE TABLE wildlife (id INT, name VARCHAR(255), type VARCHAR(255), danger_level INT, location_id INT);
            CREATE TABLE wreckage_manifest (item_id VARCHAR(20), description TEXT, quantity INT, condition TEXT);
            CREATE TABLE survivor_log (log_id INT, survivor_id INT, log_entry TEXT, log_date DATE);
            CREATE TABLE weather (id INT, condition TEXT, description TEXT, effect_type TEXT, modifier REAL);
            CREATE TABLE camp_supplies (item_name VARCHAR(255) PRIMARY KEY, quantity INT, status VARCHAR(50));
        """
        # Data
        data = """
            INSERT INTO survivors VALUES (1, 'Alex', 100, 100, 1), (2, 'Ben', 90, 80, 2), (3, 'Chloe', 95, 85, 3), (4, 'David', 85, 70, 2), (5, 'Frank', 80, 60, 4), (6, 'Grace', 90, 75, 4);
            INSERT INTO locations VALUES (1, 'Crash Site', '✈️', 'The smoldering wreckage of a small plane.', 'Beach'), (2, 'Beach', '🏖️', 'A sandy shore with palm trees.', 'Jungle'), (3, 'Jungle', '🌴', 'A dense, humid jungle teeming with life.', 'Cave'), (4, 'Cave', '🦇', 'A dark, mysterious cave system.', 'Mountain'), (5, 'Mountain', '⛰️', 'A high peak offering a wide view.', 'River Delta'), (6, 'River Delta', '🏞️', 'A fast-flowing river.', 'Abandoned Camp'), (7, 'Abandoned Camp', '⛺️', 'An old, deserted camp.', 'Rescue Landing Site'), (8, 'Rescue Landing Site', '🚁', 'A clear, flat area on the coast.', null);
            INSERT INTO resources VALUES (1, 'Coconut', 'Food', 10, 2, 'Edible'), (2, 'Fresh Water Spring', 'Water', 1, 3, 'Potable'), (3, 'Strange Berries', 'Food', 20, 3, 'Poisonous'), (4, 'Scrap Metal', 'Material', 5, 1, 'Inedible'), (5, 'Vine', 'Material', 15, 3, 'Inedible'), (6, 'Flint', 'Tool', 2, 4, 'Inedible'), (7, 'Ocean Water', 'Water', 999, 2, 'Salty'), (8, 'Seaweed', 'Food', 30, 2, 'Edible'), (9, 'Banana', 'Food', 25, 3, 'Edible');
            INSERT INTO wildlife VALUES (1, 'Parrot', 'Bird', 0, 3), (2, 'Boar', 'Mammal', 5, 3), (3, 'Snake', 'Reptile', 8, 3), (4, 'Crab', 'Crustacean', 1, 2), (5, 'Mountain Goat', 'Mammal', 3, 5), (6, 'Shark', 'Fish', 10, 2), (7, 'Monkey', 'Mammal', 2, 3);
            INSERT INTO wreckage_manifest VALUES (' MEDKIT-001', 'Standard First-Aid Kit', 1, 'Damaged'), (' RATION-003 ', 'Emergency Food Ration', 5, 'Good'), ('  TOOL-AXE-01', 'Small Hand Axe', 1, 'Good'), ('FABRIC-009', 'Torn Canvas Sheet', 3, 'Damaged');
            INSERT INTO survivor_log VALUES (1, 1, 'Found fresh water supply.', '2025-10-01'), (2, 2, 'Spotted a boar near the beach.', '2025-10-01'), (3, 3, 'Heard strange noises from the cave.', '2025-10-02'), (4, 1, 'Collected scrap metal from the crash.', '2025-10-02'), (5, 1, 'Feeling hopeful today.', '2025-10-03'), (6, 5, 'Lost my bearings in the cave.', '2025-10-03');
            INSERT INTO weather VALUES (1, 'Thick Fog', 'Visibility is low. It is hard to see the database schema.', 'HIDE_SCHEMA', 0), (2, 'Heavy Rain', 'The downpour makes it hard to think. You have less time.', 'TIME_PENALTY', 15), (3, 'Scorching Sun', 'The heat is draining your energy.', 'ENERGY_DRAIN', 1), (4, 'Clear Skies', 'A perfect day for survival.', 'NONE', 0);
            INSERT INTO camp_supplies VALUES ('Canned Beans', 5, 'Good'), ('Tarp', 1, 'Good'), ('Rope', 3, 'Good'), ('Matches', 1, 'Damp');
        """
        cursor.executescript(schema)
        cursor.executescript(data)
        self.db_conn.commit()

    def create_widgets(self):
        # --- Main Layout ---
        main_frame = tk.Frame(self, bg="#1a202c")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_panel = tk.Frame(main_frame, bg="#2d3748", width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)

        middle_panel = tk.Frame(main_frame, bg="#2d3748")
        middle_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right_panel = tk.Frame(main_frame, bg="#2d3748", width=350)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_panel.pack_propagate(False)

        # --- Left Panel Widgets ---
        stats_frame = tk.LabelFrame(left_panel, text="Survivor Status", fg="white", bg="#2d3748", padx=10, pady=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)

        self.health_var = tk.StringVar(value="❤️ Health: 100")
        self.energy_var = tk.StringVar(value="⚡ Energy: 100")
        self.score_var = tk.StringVar(value="🏆 Score: 0")
        self.timer_var = tk.StringVar(value="⏳ Time: 60s")
        
        tk.Label(stats_frame, textvariable=self.health_var, fg="white", bg="#4a5568").pack(fill=tk.X, pady=2)
        tk.Label(stats_frame, textvariable=self.energy_var, fg="white", bg="#4a5568").pack(fill=tk.X, pady=2)
        tk.Label(stats_frame, textvariable=self.score_var, fg="white", bg="#4a5568").pack(fill=tk.X, pady=2)
        self.timer_label = tk.Label(stats_frame, textvariable=self.timer_var, fg="#f56565", bg="#c53030")
        
        self.opponent_frame = tk.LabelFrame(left_panel, text="Opponent Status", fg="white", bg="#2d3748", padx=10, pady=10)
        self.opponent_score_var = tk.StringVar(value="🏆 Score: 0")
        self.opponent_status_var = tk.StringVar(value="Status: Waiting...")
        tk.Label(self.opponent_frame, textvariable=self.opponent_score_var, fg="white", bg="#4a5568").pack(fill=tk.X, pady=2)
        tk.Label(self.opponent_frame, textvariable=self.opponent_status_var, fg="white", bg="#4a5568").pack(fill=tk.X, pady=2)

        map_frame = tk.LabelFrame(left_panel, text="Island Map", fg="white", bg="#2d3748", padx=10, pady=10)
        map_frame.pack(fill=tk.X, padx=10, pady=10)
        self.map_label = tk.Label(map_frame, text="", fg="white", bg="#2d3748", justify=tk.LEFT, font=("Courier", 12))
        self.map_label.pack()

        # --- Middle Panel Widgets ---
        challenge_frame = tk.Frame(middle_panel, bg="#2d3748", padx=10, pady=10)
        challenge_frame.pack(fill=tk.X)
        self.challenge_title_var = tk.StringVar(value="Welcome to SQL Survival Island")
        self.challenge_story_var = tk.StringVar(value="Select a game mode to begin.")
        tk.Label(challenge_frame, textvariable=self.challenge_title_var, fg="#63b3ed", bg="#2d3748", font=("Playfair Display", 20, "bold")).pack(anchor="w")
        tk.Label(challenge_frame, textvariable=self.challenge_story_var, fg="white", bg="#2d3748", wraplength=600, justify=tk.LEFT).pack(anchor="w", pady=5)

        self.sql_editor = tk.Text(middle_panel, bg="#1a202c", fg="white", insertbackground="white", height=10, font=("Roboto Mono", 12))
        self.sql_editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        button_frame = tk.Frame(middle_panel, bg="#2d3748")
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        self.message_var = tk.StringVar()
        self.message_label = tk.Label(button_frame, textvariable=self.message_var, bg="#2d3748")
        self.message_label.pack(side=tk.LEFT)
        self.run_button = tk.Button(button_frame, text="Run Query", command=self.run_query, bg="#2b6cb0", fg="white", state=tk.DISABLED)
        self.run_button.pack(side=tk.RIGHT)
        self.hint_button = tk.Button(button_frame, text="Get Hint (-5 pts)", command=self.get_hint, bg="#4a5568", fg="white")

        # --- Right Panel Widgets ---
        tk.Label(right_panel, text="Query Result", fg="white", bg="#2d3748", font=("Playfair Display", 16)).pack(pady=10)
        
        tree_frame = tk.Frame(right_panel)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.result_tree = ttk.Treeview(tree_frame)
        
        # Scrollbars for the treeview
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.result_tree.yview)
        vsb.pack(side='right', fill='y')
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.result_tree.xview)
        hsb.pack(side='bottom', fill='x')
        self.result_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.result_tree.pack(fill=tk.BOTH, expand=True)

    def reset_game(self):
        self.game_state = {
            'mode': None,
            'difficulty': 'moderate',
            'player': {'score': 0, 'health': 100, 'energy': 100, 'unlockedLocations': ['Crash Site'], 'hintsUsed': 0},
            'opponent': {'score': 0, 'isThinking': False},
            'currentChallengeIndex': 0,
        }
        self.run_button.config(state=tk.DISABLED)
        self.show_game_mode_selection()

    def show_game_mode_selection(self):
        self.mode_window = tk.Toplevel(self)
        self.mode_window.title("Choose Your Adventure")
        self.mode_window.configure(bg="#2d3748")
        
        tk.Label(self.mode_window, text="Choose Your Adventure", fg="white", bg="#2d3748", font=("Playfair Display", 20)).pack(pady=20)
        
        tk.Button(self.mode_window, text="Single Player", command=lambda: self.select_mode('single'), bg="#4a5568", fg="white").pack(pady=5, padx=20, fill=tk.X)
        tk.Button(self.mode_window, text="vs. Computer", command=lambda: self.select_mode('cpu'), bg="#4a5568", fg="white").pack(pady=5, padx=20, fill=tk.X)
        
        self.mode_window.transient(self)
        self.mode_window.grab_set()
        self.wait_window(self.mode_window)

    def select_mode(self, mode):
        self.game_state['mode'] = mode
        self.mode_window.destroy()
        if mode in ['single', 'cpu']:
            self.show_difficulty_selection()
        else:
            self.start_game()
            
    def show_difficulty_selection(self):
        self.diff_window = tk.Toplevel(self)
        self.diff_window.title("Select Difficulty")
        self.diff_window.configure(bg="#2d3748")

        tk.Label(self.diff_window, text="Select Difficulty", fg="white", bg="#2d3748", font=("Playfair Display", 20)).pack(pady=20)
        
        tk.Button(self.diff_window, text="Easy (Hints)", command=lambda: self.select_difficulty('easy'), bg="#4a5568", fg="white").pack(pady=5, padx=20, fill=tk.X)
        tk.Button(self.diff_window, text="Moderate (No Hints)", command=lambda: self.select_difficulty('moderate'), bg="#4a5568", fg="white").pack(pady=5, padx=20, fill=tk.X)
        tk.Button(self.diff_window, text="Hard (Penalties)", command=lambda: self.select_difficulty('hard'), bg="#4a5568", fg="white").pack(pady=5, padx=20, fill=tk.X)
        tk.Button(self.diff_window, text="Genius (Timer & Penalties)", command=lambda: self.select_difficulty('genius'), bg="#4a5568", fg="white").pack(pady=5, padx=20, fill=tk.X)

        self.diff_window.transient(self)
        self.diff_window.grab_set()
        self.wait_window(self.diff_window)
        
    def select_difficulty(self, difficulty):
        self.game_state['difficulty'] = difficulty
        self.diff_window.destroy()
        self.start_game()
        
    def start_game(self):
        self.run_button.config(state=tk.NORMAL)
        if self.game_state['mode'] == 'cpu':
            self.opponent_frame.pack(fill=tk.X, padx=10, pady=10)
        else:
            self.opponent_frame.pack_forget()
        self.load_challenge(0)

    def load_challenge(self, index):
        if self.timer_thread and self.timer_thread.is_alive():
            self.game_state['stop_timer'] = True # Signal to stop
            
        if index >= len(challenges):
            self.end_game(True)
            return

        challenge = challenges[index]
        self.game_state['currentChallengeIndex'] = index
        self.challenge_title_var.set(challenge['title'])
        self.challenge_story_var.set(challenge['story'])
        
        # Reset hints used for the new challenge
        self.game_state['player']['hintsUsed'] = 0

        if self.game_state['difficulty'] == 'easy':
            self.hint_button.pack(side=tk.RIGHT, padx=5)
        else:
            self.hint_button.pack_forget()

        if self.game_state['difficulty'] == 'genius':
            self.timer_label.pack(fill=tk.X, pady=2)
            self.game_state['stop_timer'] = False
            self.timer_thread = threading.Thread(target=self.start_timer, args=(60,))
            self.timer_thread.start()
        else:
            self.timer_label.pack_forget()

        if self.game_state['mode'] == 'cpu':
            self.run_computer_ai()
        
        self.update_ui()

    def run_query(self):
        user_query = self.sql_editor.get("1.0", tk.END)
        challenge = challenges[self.game_state['currentChallengeIndex']]
        
        try:
            cursor = self.db_conn.cursor()
            cursor.execute(user_query)
            
            if challenge['type'].upper() in ['INSERT', 'UPDATE', 'DELETE']:
                self.db_conn.commit()
                self.check_answer(None, user_query)
            else:
                rows = cursor.fetchall()
                cols = [description[0] for description in cursor.description]
                self.display_results(cols, rows)
                self.check_answer(rows, user_query)

        except sqlite3.Error as e:
            self.display_error(str(e))
            self.apply_penalty()

    def get_hint(self):
        player = self.game_state['player']
        if player['score'] < 5:
            self.show_message("Not enough points for a hint!", "orange")
            return

        player['score'] -= 5
        player['hintsUsed'] += 1
        
        challenge = challenges[self.game_state['currentChallengeIndex']]
        correct_query = challenge['query']
        
        query_parts = correct_query.split(' ')
        reveal_percentage = min(0.25 * player['hintsUsed'], 1.0)
        parts_to_show_count = int(len(query_parts) * reveal_percentage)
        
        hint_text = ' '.join(query_parts[:parts_to_show_count])
        self.sql_editor.delete("1.0", tk.END)
        self.sql_editor.insert("1.0", hint_text)

        if parts_to_show_count >= len(query_parts):
            self.hint_button.config(state=tk.DISABLED)
        
        self.update_ui()
        self.show_message("Hint revealed!", "cyan")

    def check_answer(self, user_rows, user_query):
        challenge = challenges[self.game_state['currentChallengeIndex']]
        correct = False
        
        try:
            # Normalize queries for comparison, especially for DML
            normalized_user_query = ' '.join(user_query.strip().lower().split())
            normalized_correct_query = ' '.join(challenge['query'].strip().lower().split())

            if challenge['type'] == 'SELECT':
                cursor = self.db_conn.cursor()
                cursor.execute(challenge['query'])
                correct_rows = cursor.fetchall()
                correct = (user_rows == correct_rows)
            else: # DML/DDL
                correct = normalized_user_query == normalized_correct_query

            if correct:
                self.show_message("Correct!", "green")
                self.game_state['player']['score'] += challenge['points']
                self.after(1500, lambda: self.load_challenge(self.game_state['currentChallengeIndex'] + 1))
            else:
                self.show_message("Incorrect Result.", "red")
                self.apply_penalty()
        except Exception as e:
            self.show_message(f"Error checking answer: {e}", "red")


    def display_results(self, cols, rows):
        # Clear previous results
        for i in self.result_tree.get_children():
            self.result_tree.delete(i)
        
        self.result_tree["columns"] = cols
        self.result_tree["show"] = "headings"

        for col in cols:
            self.result_tree.heading(col, text=col)
            self.result_tree.column(col, width=100)

        for row in rows:
            self.result_tree.insert("", "end", values=row)
            
    def display_error(self, error_message):
        for i in self.result_tree.get_children():
            self.result_tree.delete(i)
        self.result_tree["columns"] = ("Error",)
        self.result_tree.heading("Error", text="SQL Error")
        self.result_tree.insert("", "end", values=(error_message,))
        
    def update_ui(self):
        player = self.game_state['player']
        self.health_var.set(f"❤️ Health: {player['health']}")
        self.energy_var.set(f"⚡ Energy: {player['energy']}")
        self.score_var.set(f"🏆 Score: {player['score']}")
        
        opponent = self.game_state['opponent']
        self.opponent_score_var.set(f"🏆 Score: {opponent['score']}")

        # Map Update
        map_text = []
        locations = self.db_conn.execute("SELECT name, icon FROM locations").fetchall()
        for i, loc in enumerate(locations):
            name, icon = loc
            unlocked = name in self.game_state['player']['unlockedLocations']
            challenge_index = self.game_state['currentChallengeIndex']
            active = challenge_index < len(challenges) and challenges[challenge_index]['locationName'] == name
            
            status = " "
            if active: status = ">"
            
            map_text.append(f"{status}{icon} {name}{'' if unlocked else ' (Locked)'}")
        self.map_label.config(text="\n".join(map_text))
            
    def show_message(self, text, color):
        self.message_var.set(text)
        self.message_label.config(fg=color)
        self.after(3000, lambda: self.message_var.set(""))
        
    def apply_penalty(self):
        if self.game_state['difficulty'] in ['hard', 'genius']:
            self.game_state['player']['health'] -= 10
        self.update_ui()
        if self.game_state['player']['health'] <= 0:
            self.end_game(False, "You ran out of health!")
            
    def run_computer_ai(self):
        if self.ai_solve_thread and self.ai_solve_thread.is_alive():
            return # AI is already running for this challenge
            
        self.ai_solve_thread = threading.Thread(target=self._ai_worker)
        self.ai_solve_thread.start()

    def _ai_worker(self):
        delays = {'easy': 20, 'moderate': 15, 'hard': 10, 'genius': 8}
        delay = delays[self.game_state['difficulty']] + random.uniform(0, 3)
        
        self.opponent_status_var.set("Status: Thinking...")
        
        start_time = time.time()
        while time.time() - start_time < delay:
            # If challenge changes, AI stops
            if self.game_state.get('stop_ai'):
                return
            time.sleep(0.1)

        # Check if player already solved it or if challenge changed
        if not self.game_state.get('stop_ai'):
            challenge = challenges[self.game_state['currentChallengeIndex']]
            self.game_state['opponent']['score'] += challenge['points']
            self.opponent_status_var.set("Status: Solved!")
            self.show_message("AI solved it first!", "orange")
            self.after(1500, lambda: self.load_challenge(self.game_state['currentChallengeIndex'] + 1))
            
    def end_game(self, win, reason=""):
        # Stop any running threads
        self.game_state['stop_timer'] = True
        self.game_state['stop_ai'] = True

        if win:
            title = "You've Been Rescued!"
            msg = f"Congratulations! You survived!\n\nFinal Score: {self.game_state['player']['score']}"
        else:
            title = "Game Over"
            msg = f"{reason}\n\nFinal Score: {self.game_state['player']['score']}"
            
        messagebox.showinfo(title, msg)
        self.reset_game()
        
    def start_timer(self, duration):
        remaining = duration
        while remaining > 0 and not self.game_state.get('stop_timer'):
            self.timer_var.set(f"⏳ Time: {remaining}s")
            time.sleep(1)
            remaining -= 1

        if not self.game_state.get('stop_timer'): # Timer ran out naturally
            self.game_state['player']['energy'] -= 15
            self.show_message("Time's up! You lost 15 energy.", "red")
            self.update_ui()
            if self.game_state['player']['energy'] <= 0:
                self.end_game(False, "You collapsed from exhaustion!")
            else:
                 self.after(10, lambda: self.load_challenge(self.game_state['currentChallengeIndex'] + 1))


if __name__ == "__main__":
    app = SQLGame()
    app.mainloop()

