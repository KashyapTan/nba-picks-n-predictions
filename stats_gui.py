import tkinter as tk
from tkinter import ttk, messagebox
from helper.formula import get_player_season_stats, get_player_vs_team_stats
from helper.percentile import plot_player_percentiles_season, plot_player_percentiles_vs_team
from helper.gamelog import get_player_game_log
import threading
from PIL import Image, ImageTk
import os
import pandas as pd
from nba_api.stats.static import teams
from c import clear_charts_folder

class NBAStatsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NBA Player Statistics Viewer")
        self.root.geometry("1350x800")
        self.root.configure(bg='#000000')
        
        # Store image references to prevent garbage collection
        self.chart_images = []
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#000000')
        style.configure('TLabel', background='#000000', foreground='#ffffff', font=('Arial', 10))
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#ffffff')
        style.configure('Subtitle.TLabel', font=('Arial', 12, 'bold'), foreground='#ffffff')
        style.configure('Stat.TLabel', font=('Arial', 11), foreground='#ffffff')
        style.configure('TButton', font=('Arial', 10, 'bold'), padding=8)
        style.configure('TEntry', fieldbackground='#1a1a1a', foreground='#ffffff')
        style.configure('TCheckbutton', background='#000000', foreground='#ffffff')
        
        # Setup the GUI
        self.setup_gui()
    
    def find_team_abbreviation(self, team_input):
        """
        Find team abbreviation using the same logic as formula.py and percentile.py.
        Tries abbreviation, full name, then nickname.
        
        Returns:
        --------
        str or None: Team abbreviation if found, None otherwise
        """
        team_list = None
        
        # Try by abbreviation first (most specific)
        if len(team_input) <= 3:
            team_obj = teams.find_team_by_abbreviation(team_input.upper())
            if team_obj:
                team_list = [team_obj]
        
        # Try by full name before nickname (more specific)
        if not team_list:
            team_list = teams.find_teams_by_full_name(team_input)
        
        # Try by nickname last (can match multiple teams)
        if not team_list:
            team_list = teams.find_teams_by_nickname(team_input)
            # If nickname search returns multiple results, filter by checking if the nickname matches exactly
            if team_list and len(team_list) > 1:
                exact_matches = [t for t in team_list if t['nickname'].lower() == team_input.lower()]
                if exact_matches:
                    team_list = exact_matches
        
        if not team_list:
            return None
        
        if len(team_list) > 1:
            # Return None to indicate ambiguity
            return None
        
        return team_list[0]['abbreviation']
    
    def setup_gui(self):
        """Setup the GUI components"""
        # Main container with scrollbar
        main_canvas = tk.Canvas(self.root, bg='#000000', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        self.scrollable_frame = ttk.Frame(main_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel
        main_canvas.bind_all("<MouseWheel>", lambda e: main_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        main_frame = ttk.Frame(self.scrollable_frame, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Title
        title = ttk.Label(main_frame, text="NBA Player Statistics Analyzer", style='Title.TLabel')
        title.grid(row=0, column=0, columnspan=6, pady=(0, 20))
        
        # Input section
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=1, column=0, columnspan=6, pady=(0, 20), sticky="ew")
        
        # Player Name
        ttk.Label(input_frame, text="Player Name:").grid(row=0, column=0, padx=(0, 10), sticky=tk.W)
        self.player_entry = ttk.Entry(input_frame, width=25, font=('Arial', 10))
        self.player_entry.grid(row=0, column=1, padx=(0, 20), sticky="ew")
        self.player_entry.insert(0, "James Harden")
        
        # Team Name
        ttk.Label(input_frame, text="Opponent Team:").grid(row=0, column=2, padx=(0, 10), sticky=tk.W)
        self.team_entry = ttk.Entry(input_frame, width=25, font=('Arial', 10))
        self.team_entry.grid(row=0, column=3, sticky="ew")
        self.team_entry.insert(0, "76ers")
        
        # Configure input frame columns
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)
        
        # Season selection with scrollable frame
        season_frame = ttk.Frame(main_frame)
        season_frame.grid(row=2, column=0, columnspan=6, pady=(0, 10))
        
        ttk.Label(season_frame, text="Select Seasons:", style='Stat.TLabel').grid(row=0, column=0, padx=(0, 15), sticky=tk.W)
        
        # Create checkbuttons for seasons 2020-21 through 2025-26
        self.season_vars = {}
        seasons = ['2020-21', '2021-22', '2022-23', '2023-24', '2024-25', '2025-26']
        
        for i, season in enumerate(seasons):
            var = tk.BooleanVar(value=(season in ['2024-25', '2025-26']))  # Default last 2 seasons
            self.season_vars[season] = var
            ttk.Checkbutton(season_frame, text=season, variable=var).grid(row=0, column=i+1, padx=5)
        
        # Select/Deselect all buttons
        select_frame = ttk.Frame(season_frame)
        select_frame.grid(row=1, column=0, columnspan=7, pady=(5, 0))
        
        tk.Button(select_frame, text="Select All", command=self.select_all_seasons,
                 bg='#333333', fg='#ffffff', font=('Arial', 9), padx=10, pady=3, relief=tk.FLAT, cursor='hand2').grid(row=0, column=0, padx=5)
        tk.Button(select_frame, text="Deselect All", command=self.deselect_all_seasons,
                 bg='#333333', fg='#ffffff', font=('Arial', 9), padx=10, pady=3, relief=tk.FLAT, cursor='hand2').grid(row=0, column=1, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=6, pady=(0, 20))
        
        self.fetch_btn = tk.Button(button_frame, text="Fetch Statistics", command=self.fetch_stats,
                                   bg='#00d9ff', fg='#1a1a2e', font=('Arial', 11, 'bold'),
                                   padx=20, pady=8, relief=tk.FLAT, cursor='hand2')
        self.fetch_btn.grid(row=0, column=0, padx=5)
        
        clear_btn = tk.Button(button_frame, text="Clear Results", command=self.clear_results,
                             bg='#e74c3c', fg='white', font=('Arial', 11, 'bold'),
                             padx=20, pady=8, relief=tk.FLAT, cursor='hand2')
        clear_btn.grid(row=0, column=1, padx=5)
        
        # Status bar
        self.status_label = ttk.Label(main_frame, text="Ready", foreground='#999999', font=('Arial', 10, 'italic'))
        self.status_label.grid(row=4, column=0, columnspan=6, pady=(0, 10), sticky=tk.W)
        
        # Results container
        self.results_frame = ttk.Frame(main_frame)
        self.results_frame.grid(row=5, column=0, columnspan=6, sticky="nsew")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.scrollable_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.columnconfigure(3, weight=1)
        main_frame.columnconfigure(4, weight=1)
        main_frame.columnconfigure(5, weight=1)
        
    def select_all_seasons(self):
        for var in self.season_vars.values():
            var.set(True)
    
    def deselect_all_seasons(self):
        for var in self.season_vars.values():
            var.set(False)
        
    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update_idletasks()
        
    def clear_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        self.chart_images.clear()
        self.update_status("Results cleared")
    
    def create_stat_card(self, parent, title, stats_data, row, col, colspan=2):
        """Create a nice stat card with organized layout"""
        card = tk.Frame(parent, bg='#1a1a1a', relief=tk.RAISED, borderwidth=1, highlightbackground='#333333', highlightthickness=1)
        card.grid(row=row, column=col, columnspan=colspan, padx=10, pady=10, sticky="nsew")
        
        # Title
        title_label = tk.Label(card, text=title, bg='#1a1a1a', fg='#ffffff',
                              font=('Arial', 12, 'bold'), pady=10)
        title_label.pack(fill=tk.X)
        
        # Stats table
        table_frame = tk.Frame(card, bg='#1a1a1a')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Row headers (vertical)
        row_labels = ['Statistic', 'Average', 'Std Dev', 'CV %']
        for i, label in enumerate(row_labels):
            tk.Label(table_frame, text=label, bg='#2a2a2a', fg='#ffffff',
                    font=('Arial', 10, 'bold'), padx=10, pady=5,
                    relief=tk.FLAT).grid(row=i, column=0, sticky="ew")
        
        # Data columns
        stat_order = ['points', 'rebounds', 'assists', 'blocks', 'steals', '3pt']
        stat_names = ['Points', 'Rebounds', 'Assists', 'Blocks', 'Steals', '3PTM']
        
        col_num = 1
        for stat_key, stat_name in zip(stat_order, stat_names):
            if stat_key in stats_data['averages']:
                avg = stats_data['averages'][stat_key]
                std = stats_data['std_devs'][stat_key]
                cv = 100 * (std / avg) if avg > 0 else 0
                
                # Alternate column colors
                col_bg = '#0a0a0a' if col_num % 2 == 0 else '#1a1a1a'
                
                # Statistic name
                tk.Label(table_frame, text=stat_name, bg=col_bg, fg='#ffffff',
                        font=('Arial', 10), padx=10, pady=8).grid(row=0, column=col_num, sticky="ew")
                # Average
                tk.Label(table_frame, text=f"{avg:.1f}", bg=col_bg, fg='#ffffff',
                        font=('Arial', 10, 'bold'), padx=10, pady=8).grid(row=1, column=col_num, sticky="ew")
                # Std Dev
                tk.Label(table_frame, text=f"±{std:.1f}", bg=col_bg, fg='#cccccc',
                        font=('Arial', 10), padx=10, pady=8).grid(row=2, column=col_num, sticky="ew")
                # CV
                tk.Label(table_frame, text=f"{cv:.1f}%", bg=col_bg, fg='#999999',
                        font=('Arial', 10), padx=10, pady=8).grid(row=3, column=col_num, sticky="ew")
                
                col_num += 1
        
        # Games played info at bottom
        games_frame = tk.Frame(card, bg='#1a1a1a')
        games_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        tk.Label(games_frame, text=f"Games Played: {stats_data['games_played']}", 
                bg='#1a1a1a', fg='#ffffff', font=('Arial', 10, 'bold')).pack()
        
        # Configure column weights
        for i in range(col_num):
            table_frame.columnconfigure(i, weight=1)
    
    def create_chart_display(self, parent, image_path, title, row, col, colspan=3):
        """Display chart image in the GUI"""
        if not os.path.exists(image_path):
            return
        
        card = tk.Frame(parent, bg='#1a1a1a', relief=tk.RAISED, borderwidth=1, highlightbackground='#333333', highlightthickness=1)
        card.grid(row=row, column=col, columnspan=colspan, padx=10, pady=10, sticky="nsew")
        
        # Title
        title_label = tk.Label(card, text=title, bg='#1a1a1a', fg='#ffffff',
                              font=('Arial', 12, 'bold'), pady=10)
        title_label.pack(fill=tk.X)
        
        try:
            # Load and resize image
            img = Image.open(image_path)
            # Calculate new size maintaining aspect ratio
            original_width, original_height = img.size
            # Use a max width that scales with window
            new_width = min(1100, int(self.root.winfo_width() * 0.85)) if self.root.winfo_width() > 1 else 1100
            aspect_ratio = original_height / original_width
            new_height = int(new_width * aspect_ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            # Keep reference to prevent garbage collection
            self.chart_images.append(photo)
            
            # Display image
            img_label = tk.Label(card, image=photo, bg='#1a1a1a')
            img_label.pack(padx=10, pady=10)
        except Exception as e:
            tk.Label(card, text=f"Error loading chart: {str(e)}", 
                    bg='#1a1a1a', fg='#ff6b6b', font=('Arial', 10),
                    pady=20).pack()
    
    def create_game_log_display(self, parent, game_log_df, title, row, col, colspan=6):
        """Display game log in a scrollable table"""
        card = tk.Frame(parent, bg='#1a1a1a', relief=tk.RAISED, borderwidth=1, highlightbackground='#333333', highlightthickness=1)
        card.grid(row=row, column=col, columnspan=colspan, padx=10, pady=10, sticky="nsew")
        
        # Title
        title_label = tk.Label(card, text=title, bg='#1a1a1a', fg='#ffffff',
                              font=('Arial', 12, 'bold'), pady=10)
        title_label.pack(fill=tk.X)
        
        # Create frame for treeview and scrollbars
        tree_frame = tk.Frame(card, bg='#1a1a1a')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Style scrollbars
        scrollbar_style = ttk.Style()
        scrollbar_style.configure("Custom.Vertical.TScrollbar",
                                  background='#2a2a2a',
                                  troughcolor='#0a0a0a',
                                  bordercolor='#333333',
                                  arrowcolor='#ffffff',
                                  darkcolor='#2a2a2a',
                                  lightcolor='#2a2a2a')
        scrollbar_style.configure("Custom.Horizontal.TScrollbar",
                                  background='#2a2a2a',
                                  troughcolor='#0a0a0a',
                                  bordercolor='#333333',
                                  arrowcolor='#ffffff',
                                  darkcolor='#2a2a2a',
                                  lightcolor='#2a2a2a')
        
        # Create scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", style="Custom.Vertical.TScrollbar")
        
        # Create treeview
        columns = ['GAME_DATE', 'MATCHUP', 'WL', 'MIN', 'PTS', 'REB', 'AST', 'STL', 'BLK', 
                   'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'TS_PCT', 'PLUS_MINUS']
        # Filter to only include columns that exist in the dataframe
        columns = [col for col in columns if col in game_log_df.columns]
        
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', 
                           yscrollcommand=vsb.set, height=15)
        
        vsb.config(command=tree.yview)
        
        # Configure column headings and widths
        column_widths = {
            'GAME_DATE': 110,
            'MATCHUP': 130,
            'WL': 45,
            'MIN': 55,
            'PTS': 55,
            'REB': 55,
            'AST': 55,
            'STL': 55,
            'BLK': 55,
            'FGM': 55,
            'FGA': 55,
            'FG_PCT': 70,
            'FG3M': 55,
            'FG3A': 55,
            'FG3_PCT': 70,
            'FTM': 55,
            'FTA': 55,
            'FT_PCT': 70,
            'TS_PCT': 70,
            'PLUS_MINUS': 85
        }
        
        # Column header display names
        column_headers = {
            'FG_PCT': 'FG%',
            'FG3_PCT': '3P%',
            'FT_PCT': 'FT%',
            'TS_PCT': 'TS%'
        }
        
        for col in columns:
            header_text = column_headers.get(col, col)
            tree.heading(col, text=header_text, anchor='center')
            width = column_widths.get(col, 80)
            tree.column(col, width=width, anchor='center')
        
        # Style the treeview
        style = ttk.Style()
        style.configure("Treeview",
                       background="#0a0a0a",
                       foreground="#ffffff",
                       fieldbackground="#0a0a0a",
                       borderwidth=0,
                       relief='flat',
                       rowheight=30)
        style.configure("Treeview.Heading",
                       background="#1a1a1a",
                       foreground="#cccccc",
                       borderwidth=0,
                       relief='flat',
                       font=('Arial', 9))
        style.map('Treeview', 
                 background=[('selected', '#333333')],
                 foreground=[('selected', '#ffffff')])
        style.map('Treeview.Heading',
                 background=[('active', '#2a2a2a')])
        
        # Insert data
        for idx, row in game_log_df.iterrows():
            values = []
            for col in columns:
                val = row[col]
                # Format the value
                if col == 'MIN':
                    try:
                        values.append(f"{float(val):.0f}" if val else "0")
                    except:
                        values.append(str(val))
                elif col in ['FG_PCT', 'FG3_PCT', 'FT_PCT', 'TS_PCT']:
                    try:
                        values.append(f"{float(val)*100:.1f}%" if val else "0.0%")
                    except:
                        values.append(str(val))
                elif col == 'PLUS_MINUS':
                    try:
                        pm = float(val) if val else 0
                        values.append(f"{pm:+.0f}" if pm != 0 else "0")
                    except:
                        values.append(str(val))
                elif col in ['GAME_DATE', 'MATCHUP', 'WL']:
                    # Text columns - keep as is, show empty if blank
                    values.append(str(val) if val else "")
                else:
                    # Numeric columns - show 0 instead of blank
                    try:
                        num_val = float(val) if val else 0
                        values.append(str(int(num_val)) if num_val == int(num_val) else str(num_val))
                    except:
                        values.append(str(val) if val else "0")
            
            # Color code by win/loss
            wl_value = row['WL'] if 'WL' in game_log_df.columns else None
            if wl_value == 'W':
                tag = 'win'
            elif wl_value == 'L':
                tag = 'loss'
            else:
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            tree.insert('', 'end', values=values, tags=(tag,))
        
        # Configure row colors - subtle win/loss highlighting
        tree.tag_configure('win', background='#0d2818', foreground='#ffffff')  # Subtle green tint
        tree.tag_configure('loss', background='#281010', foreground='#ffffff')  # Subtle red tint
        tree.tag_configure('evenrow', background='#0a0a0a', foreground='#ffffff')
        tree.tag_configure('oddrow', background='#0a0a0a', foreground='#ffffff')
        
        # Pack elements
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Add summary info
        summary_frame = tk.Frame(card, bg='#1a1a1a')
        summary_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        total_games = len(game_log_df)
        wins = len(game_log_df[game_log_df['WL'] == 'W']) if 'WL' in game_log_df.columns else 0
        losses = total_games - wins
        
        summary_text = f"Total Games: {total_games}  |  Wins: {wins}  |  Losses: {losses}"
        tk.Label(summary_frame, text=summary_text, bg='#1a1a1a', fg='#ffffff',
                font=('Arial', 10, 'bold')).pack()
    
    def fetch_stats(self):
        player = self.player_entry.get().strip()
        team = self.team_entry.get().strip()
        
        if not player:
            messagebox.showerror("Error", "Please enter a player name")
            return
        if not team:
            messagebox.showerror("Error", "Please enter an opponent team")
            return
        
        # Get selected seasons
        selected_seasons = [season for season, var in self.season_vars.items() if var.get()]
        
        if not selected_seasons:
            messagebox.showerror("Error", "Please select at least one season")
            return
        
        # Disable button during fetch
        self.fetch_btn.config(state='disabled', text='Fetching...')
        self.clear_results()
        
        # Run in separate thread to prevent GUI freezing
        thread = threading.Thread(target=self.fetch_stats_thread, args=(player, team, selected_seasons))
        thread.daemon = True
        thread.start()
        
    def fetch_stats_thread(self, player, team, seasons):
        try:
            self.update_status("Fetching data from NBA API...")
            
            all_data = []
            
            # Reverse seasons to show most recent first
            for season in reversed(seasons):
                season_data = {
                    'season': season,
                    'season_stats': None,
                    'vs_team_stats': None,
                    'chart_path': None,
                    'vs_chart_path': None
                }
                
                # Season statistics
                self.update_status(f"Fetching {player} season stats for {season}...")
                try:
                    stats = get_player_season_stats(player, season)
                    season_data['season_stats'] = stats
                except Exception as e:
                    season_data['season_error'] = str(e)
                
                # VS Team statistics
                self.update_status(f"Fetching {player} vs {team} stats for {season}...")
                try:
                    stats = get_player_vs_team_stats(player, season, team)
                    season_data['vs_team_stats'] = stats
                except Exception as e:
                    season_data['vs_team_error'] = str(e)
                
                # Generate charts
                self.update_status(f"Generating percentile charts for {season}...")
                try:
                    chart_path = f"charts/{player.replace(' ', '_').lower()}_{season}.png"
                    plot_player_percentiles_season(player, season, save_path=chart_path)
                    season_data['chart_path'] = chart_path
                except Exception as e:
                    season_data['chart_error'] = str(e)
                
                try:
                    vs_chart_path = f"charts/{player.replace(' ', '_').lower()}_vs_{team.replace(' ', '_').lower()}_{season}.png"
                    plot_player_percentiles_vs_team(player, season, team, save_path=vs_chart_path)
                    season_data['vs_chart_path'] = vs_chart_path
                except Exception as e:
                    season_data['vs_chart_error'] = str(e)
                
                # Get game log
                self.update_status(f"Fetching game log for {season}...")
                try:
                    game_log_df = get_player_game_log(player, season)
                    season_data['game_log'] = game_log_df
                    
                    # Find team abbreviation using the same logic as formula.py and percentile.py
                    team_abbrev = self.find_team_abbreviation(team)
                    
                    if team_abbrev:
                        # Filter game log for VS team games using the abbreviation
                        # MATCHUP column contains strings like "LAC @ GSW" or "LAC vs. GSW"
                        vs_team_log = game_log_df[game_log_df['MATCHUP'].str.contains(team_abbrev, case=False, na=False)]
                        season_data['vs_team_log'] = vs_team_log if not vs_team_log.empty else None
                    else:
                        # Could not find team - store error info
                        season_data['vs_team_log'] = None
                        season_data['team_not_found'] = True
                    
                    # Debug: store actual matchups for troubleshooting
                    if season_data['vs_team_log'] is None and not game_log_df.empty:
                        unique_matchups = game_log_df['MATCHUP'].unique().tolist()
                        season_data['available_matchups'] = unique_matchups
                except Exception as e:
                    season_data['game_log_error'] = str(e)
                
                all_data.append(season_data)
            
            # Update GUI in main thread
            self.root.after(0, self.display_results, player, team, all_data)
            
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", f"An error occurred: {str(e)}")
        finally:
            self.root.after(0, self.enable_fetch_button)
    
    def display_results(self, player, team, all_data):
        current_row = 0
        
        # Configure results frame columns to be responsive
        for i in range(6):
            self.results_frame.columnconfigure(i, weight=1)
        
        for data in all_data:
            season = data['season']
            
            # Season header
            header = tk.Label(self.results_frame, text=f"Season {season}", 
                            bg='#000000', fg='#ffffff',
                            font=('Arial', 14, 'bold'), pady=15)
            header.grid(row=current_row, column=0, columnspan=6, sticky="ew")
            current_row += 1
            
            # Season stats card
            if data.get('season_stats'):
                self.create_stat_card(self.results_frame, 
                                     f"{player} - {season} Overall Stats",
                                     data['season_stats'], 
                                     current_row, 0, colspan=3)
            elif data.get('season_error'):
                error_label = tk.Label(self.results_frame, 
                                      text=f"Season Error: {data['season_error']}", 
                                      bg='#1a1a1a', fg='#ff6b6b',
                                      font=('Arial', 10), pady=20, padx=20)
                error_label.grid(row=current_row, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
            
            # VS Team stats card
            if data.get('vs_team_stats'):
                self.create_stat_card(self.results_frame, 
                                     f"{player} vs {team} - {season}",
                                     data['vs_team_stats'], 
                                     current_row, 3, colspan=3)
            elif data.get('vs_team_error'):
                error_label = tk.Label(self.results_frame, 
                                      text=f"VS Team Error: {data['vs_team_error']}", 
                                      bg='#1a1a1a', fg='#ff6b6b',
                                      font=('Arial', 10), pady=20, padx=20)
                error_label.grid(row=current_row, column=3, columnspan=3, padx=10, pady=10, sticky="ew")
            
            current_row += 1
            
            # Season chart
            if data.get('chart_path'):
                self.create_chart_display(self.results_frame, 
                                         data['chart_path'],
                                         f"{player} - {season} Percentile Distribution",
                                         current_row, 0, colspan=6)
                current_row += 1
            
            # VS Team chart
            if data.get('vs_chart_path'):
                self.create_chart_display(self.results_frame, 
                                         data['vs_chart_path'],
                                         f"{player} vs {team} - {season} Percentile Distribution",
                                         current_row, 0, colspan=6)
                current_row += 1
            
            # Game log
            if data.get('game_log') is not None:
                self.create_game_log_display(self.results_frame,
                                            data['game_log'],
                                            f"{player} - {season} Game Log (All Games)",
                                            current_row, 0, colspan=6)
                current_row += 1
            elif data.get('game_log_error'):
                error_label = tk.Label(self.results_frame, 
                                      text=f"Game Log Error: {data['game_log_error']}", 
                                      bg='#1a1a1a', fg='#ff6b6b',
                                      font=('Arial', 10), pady=20, padx=20)
                error_label.grid(row=current_row, column=0, columnspan=6, padx=10, pady=10, sticky="ew")
                current_row += 1
            
            # VS Team game log
            if data.get('vs_team_log') is not None:
                self.create_game_log_display(self.results_frame,
                                            data['vs_team_log'],
                                            f"{player} vs {team} - {season} Game Log",
                                            current_row, 0, colspan=6)
                current_row += 1
            else:
                # Show message when no VS team games found
                if data.get('team_not_found'):
                    message = f"Could not find team '{team}'. Please try using the team's full name, nickname, or 3-letter abbreviation."
                else:
                    message = f"No games found for {player} vs {team} in {season} season"
                
                no_games_label = tk.Label(self.results_frame, 
                                         text=message, 
                                         bg='#1a1a1a', fg='#999999',
                                         font=('Arial', 10, 'italic'), pady=10, padx=20)
                no_games_label.grid(row=current_row, column=0, columnspan=6, padx=10, pady=(10, 0), sticky="ew")
                current_row += 1
                
                # Show available matchups for debugging
                if 'available_matchups' in data:
                    matchups_text = "Available teams in this season:\n" + "\n".join(data['available_matchups'][:15])
                    if len(data['available_matchups']) > 15:
                        matchups_text += f"\n... and {len(data['available_matchups']) - 15} more"
                    
                    matchups_label = tk.Label(self.results_frame, text=matchups_text,
                                            font=("Arial", 8), bg='#1a1a1a', fg='#666666',
                                            justify='left', pady=10, padx=20)
                    matchups_label.grid(row=current_row, column=0, columnspan=6, padx=10, pady=(0, 10), sticky="ew")
                    current_row += 1
            
            # Add separator
            separator = tk.Frame(self.results_frame, height=2, bg='#333333')
            separator.grid(row=current_row, column=0, columnspan=6, sticky="ew", pady=20)
            current_row += 1
        
        self.update_status(f"Statistics loaded successfully for {len(all_data)} season(s)!")
        
    def enable_fetch_button(self):
        self.fetch_btn.config(state='normal', text='Fetch Statistics')

def main():
    root = tk.Tk()
    app = NBAStatsGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
