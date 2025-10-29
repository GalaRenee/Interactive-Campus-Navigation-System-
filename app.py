from __future__ import annotations 
import tkinter as tk 
from tkinter import ttk, messagebox 
import random 
from dataclasses import dataclass, field 
from typing import Dict, List, Tuple, Optional, Set


# ------------- Model -------------

@dataclass
class Node:
    name: str
    x: int 
    y: int 
    weight: float = 1.0 # Represents importance, capacity , or traffic 
    canvas_id: Optional[int] = None 
    label_id: Optional[int] = None 
    
    
@dataclass 
class Edge:
    u: str
    v: str
    distance: float = 1.0 
    time: float = 1.0 
    accessible: bool = True 
    closed: bool = False 
    line_id: Optional[int] = None 
    label_id: Optional[int] = None 
    
    def key(self) -> Tuple[str, str]:
        return tuple(sorted((self.u, self.v)))
    
    
class Graph:
    def __init__(self) -> None:
        self.nodes: Dict[str, Node] = {}
        # store undirected edges by normalized pair key 
        self.edges: Dict[Tuple[str, str], Edge] = {} # Store connections between buildings 
        
    # ----- node ops -----
    def add_node(self, name: str, x: int, y: int) -> None:
        """Add a new building to the campus map."""
        if not name or name.strip() == "":
            raise ValueError("Building name cannot be empty.")
        if name in self.nodes:
            raise ValueError(f"Duplicate building name '{name}'.")
        self.nodes[name] = Node(name=name, x=int(x), y=int(y))
        
    def delete_node(self, name: str) -> int:
        """Delete a building and all its connections. Returns number of edges deleted."""
        if name not in self.nodes:
            raise ValueError(f"Building '{name}' does not exist.")
        
        # Delete all edges connected to this node 
        edges_to_delete = []
        for key in self.edges.keys():
            if name in key:
                edges_to_delete.append(key)
                
        for key in edges_to_delete:
            del self.edges[key]
            
        # Delete the node
        del self.nodes[name]
        return len(edges_to_delete)
        
    # ----- edge ops -----
    def add_edge(self, u: str, v: str, distance: float, time: float, accessible: bool):
        """Create a pathway between two buildings."""
        if u == v:
            raise ValueError("Cannot connect a building to itself.")
        if u not in self.nodes or v not in self.nodes:
            raise ValueError("Both buildings must exist.")
        # Using sorted tuple as a key so direction doesn't matter (undirected graph)
        key = tuple(sorted((u, v)))
        if key in self.edges:
            raise ValueError(f"An edge between '{u}' and '{v}' already exists.")
        if distance <= 0 or time <= 0:
            raise ValueError("Distance and time must be positive numbers.")
        self.edges[key] = Edge(u=u, v=v, distance=float(distance), time=float(time), accessible=bool(accessible))
     
     
    def delete_edge(self, u: str, v: str) -> None:
        """Delete a connection between two buildings."""   
        key = tuple(sorted((u, v)))
        if key not in self.edges:
            raise ValueError(f"No connection exists between '{u}' and '{v}'.")
        del self.edges[key]
        
    def neighbors(self, name: str, accessible_only: bool) -> List[str]:
        """Get all buildings connected to this one."""
        nbrs = []
        for (a,b), e in self.edges.items():
            # Skip closed paths 
            if e.closed:
                continue
            # Skip non-accessible if in accessible-only mode 
            if accessible_only and not e.accessible:
                continue
            # Add the other building to neighbors list 
            if a == name:
                nbrs.append(b)
            elif b == name:
                nbrs.append(a)
        return nbrs
        
    def get_edge(self, a: str, b: str) -> Optional[Edge]: 
        return self.edges.get(tuple(sorted((a, b))))
    
    def all_edge_keys(self) -> List[Tuple[str, str]]:
        return list(self.edges.keys())
    
    def randomize_weights(self) -> None:
        """Randomize distance/time within sensible ranges."""
        for e in self.edges.values():
            # Distance in meters (or arbitrary units), Time in minutes (arbitrary)
            e.distance = round(random.uniform(50, 500), 1)
            e.time = round(random.uniform(1, 10), 1)
            
    def randomize_node_Weights(self) -> None:
        """Randomize node weights representing importance/capacity/ traffic."""
        for node in self.nodes.values():
            # Weight from 0.5 to 3.0 (affects visual size)
            node.weight = round(random.uniform(0.5, 3.0), 1)
            
           
 # ------------- GUI Controller/Views -------------                
class App(tk.Tk):
    NODE_RADIUS = 20
     
    # Color Palette with hex codes 
    COLOR_PRIMARY = "#E3B1F6"
    COLOR_PRIMARY_LIGHT = "#F183C5"
    COLOR_PRIMARY_DARK = "#5E049A"
    
    COLOR_SECONDARY = "#ec4899"
    COLOR_ACCENT = "#06b6d4"
    COLOR_ACCENT_2 = "#14b8a6"
    
    COLOR_SUCCESS = "#22c55e"
    COLOR_WARNING = "#f59e0b"
    COLOR_ERROR = "#ef4444"
    
    COLOR_BG_DARK = "#08103E"
    COLOR_BG_MEDIUM = "#181A4B"
    COLOR_BG_CARD = "#1027A3"
    COLOR_BG_INPUT = "#4258D0"
    
    COLOR_TEXT_PRIMARY = "#FBC7EB"
    COLOR_TEXT_SECONDARY = "#FF518E"
    COLOR_TEXT_MUTED = "#F183C5"
    
    COLOR_CANVAS_BG = "#08103E"
    COLOR_NODE = "#E03372"
    COLOR_NODE_GLOW_1 = "#F183C5"
    COLOR_NODE_GLOW_2 = "#E3B1F6"
    COLOR_NODE_GLOW_3 = "#FBC7EB"
    COLOR_NODE_BORDER = "#FC9571"
    
    COLOR_EDGE_OPEN = "#475569"
    COLOR_EDGE_CLOSED = "#ef4444"
    COLOR_EDGE_NONACC = "#f59e0b"
    COLOR_PATH_HILITE = "#22c55e"
    
    
    def __init__(self):
        super().__init__()
        self.title("🎓 Interactive Campus Navigation (BFS & DFS)")
        # Compact window size 
        self.geometry("1320x780")
        self.minsize(1150, 680)
        self.configure(bg=self.COLOR_BG_DARK)
        
        self.graph = Graph()
        self.mode_place_node: bool = False
        self.pending_node_name: Optional[str] = None
        
        # traversal animation state
        self.anim_steps: List[Tuple[str, str]] = [] # sequence of (from, to) edges being traversed
        self.anim_index: int = 0 
        self.active_path: List[str] = []
        self.animating: bool = False
        
        self._configure_styles()
        self._build_ui()
        self._bind_events()
        self._load_sample_graph()
        
        
    def _configure_styles(self):
        """Configure modern ttk styles"""
        style = ttk.Style()
        style.theme_use('clam') # Modern base theme 
        
        # Comfigure colors
        style.configure('.',
                        background=self.COLOR_BG_CARD,
                        foreground=self.COLOR_TEXT_PRIMARY,
                        fieldbackground=self.COLOR_BG_INPUT,
                        font=('Segoe UI', 10))
        
        # Frame styling 
        style.configure('TFrame', background=self.COLOR_BG_CARD)
        # Label styling
        style.configure('TLabel', 
                        background=self.COLOR_BG_CARD,
                        foreground=self.COLOR_TEXT_PRIMARY,
                        font=('Segoe UI', 10))
        
        style.configure('Title.TLabel',
                        font=('Segoe UI', 11, 'bold'),
                        foreground=self.COLOR_PRIMARY_LIGHT)
        
        # Button styling 
        style.configure('TButton', 
                        background=self.COLOR_PRIMARY,
                        foreground='white',
                        borderwidth=0,
                        focuscolor='none',
                        font=('Segoe UI', 9, 'bold'), # Smaller font 
                        padding=(12, 8)) # Reduced padding 
        
        style.map('TButton',
                  background=[('active', self.COLOR_PRIMARY_LIGHT)])
        
        style.configure('Action.TButton',
                        background=self.COLOR_ACCENT)
        
        style.map('Action.TButton',
                  background=[('active', '#0891b2')])
        
        
        style.configure('Success.TButton',
                        background=self.COLOR_SUCCESS)
        
        style.map('Action.TButton',
                  background=[('active', '#16a34a')])
        
        # Entry styling 
        style.configure('TEntry',
                        fieldbackground=self.COLOR_BG_INPUT,
                        foreground=self.COLOR_TEXT_PRIMARY,
                        borderwidth=2,
                        relief='flat',
                        padding=6)
        
        # Combobox styling 
        style.configure('TCombobox',
                        fieldbackground=self.COLOR_BG_INPUT,
                        foreground=self.COLOR_TEXT_PRIMARY,
                        arrowcolor=self.COLOR_PRIMARY,
                        borderwidth=2,
                        padding=5)
        
        style.map('TCombobox',
                  fieldbackground=[('readonly', self.COLOR_BG_INPUT)])
                  
        # Checkbutton styling 
        style.configure('TCheckButton',
                        background=self.COLOR_BG_CARD,
                        foreground= self.COLOR_TEXT_PRIMARY, 
                        font=('Segoe UI', 10, 'bold'))
        
        style.map('TCheckButton', 
                  background=[('active', self.COLOR_BG_INPUT)])
    
    def _load_sample_graph(self):
        """Load a sample campus/facility map with buildings and pathways"""
        # Add key sample buildings with approximate positions on canvas
        # Format: (name, x, y, weight) - weight represents importance/capacity/traffic
        buildings = [
            # Left side  
            ("Arts Center", 150, 520),
            ("Student Center", 200, 450),
            ("Gym", 300, 280),
            ("Sports Complex", 390, 320),
            
            # Upper left 
            ("Parking A", 120, 140),
            ("Engineering", 520, 390),
            
            # Center 
            ("Library", 380, 480),
            ("Academic Building", 450,  680),
            
            # Upper middle 
            ("Lecture Hall", 480, 560),
            
            # Right side 
            ("Science Lab", 600, 420),
            
            # Lower center/right 
            ("Business Building", 420, 650),
            ("Theater", 280, 700),
            ("Admin Building", 520, 600)
        ]
        
        for name, x, y in buildings:
            self.graph.add_node(name, x, y)
            
        # Add pathways (edges) between buildings 
        # Format: (from, to, distance_meters, time_minutes, accessible)
        pathways = [
            ("Science Lab", "Engineering", 180, 2.5, True),
            ("Engineering", "Lecture Hall", 165, 2.5, True),
            
            # Central campus 
            ("Library", "Engineering", 180, 2.5, True),
            ("Library", "Lecture Hall", 140, 2.0, True),
            ("Library", "Student Center", 260, 4.0, True),
            ("Library", "Academic Building", 210, 3.0, True),
            
            # Student life area 
            ("Student Center", "Arts Center", 120, 2.0, True),
            ("Student Center", "Gym", 180, 2.5, True),
            ("Student Center", "Theater", 150, 2.5, True),
            
            
            # Athletic facilities 
            ("Gym", "Sports Complex", 120, 2.0, True),
            ("Gym", "Parking A", 220, 3.5, True),
            ("Sports Complex", "Library", 140, 2.0, False), # Stairs only 
            ("Sports Complex", "Engineering", 180, 2.5, True),
            
            
            # Lower campus 
            ("Business Building", "Academic Building", 145, 2.0, True),
            ("Business Building", "Admin Building", 160, 2.5, True),
            ("Business Building", "Theater", 195, 3.0, True),
            ("Admin Building", "Lecture Hall", 135, 2.0, True),
            
            # Additional connections
            ("Theater", "Arts Center", 420, 6.0, True),
            ("Lecture Hall", "Science Lab", 160, 2.5, True),
            ("Parking A", "Science Lab", 420, 6.0, True),
        ]
        
        for u, v, dist, time, acc in pathways:
            self.graph.add_edge(u, v, dist, time, acc)
            
        # Draw initial graph 
        self._redraw_all()
        self._refresh_node_lists()
        self._refresh_edge_list()
        
    def _toggle_edge_accessible(self):
        sel = self.listbox_edges.curselection()
        if not sel:
            messagebox.showwarning("No Selection", "Select an edge from the list.")
            return 
        keys = sorted(self.graph.edges.keys())
        idx = sel[0]
        if idx >= len(keys):
            return
        keys = keys[idx]
        e = self.graph.edges[keys]
        e.accessible = not e.accessible
        self._redraw_all()
        self._refresh_edge_list()
        
        
        
    # ----- UI -----
    def _build_ui(self):
        # Left: canvas
        header = tk.Frame(self, bg=self.COLOR_PRIMARY, height=60)
        header.pack(fill=tk.X, padx=20, pady=(15, 0))
        header.pack_propagate(False)
        
        title = tk.Label(header,
                         text="🎓Campus Navigator",
                         font=('Segoe UI', 18, 'bold'),
                         bg=self.COLOR_PRIMARY,
                         fg='white')
        title.pack(side=tk.LEFT, padx=20, pady=12)
        
        subtitle = tk.Label(header,
                            text="Intelligent Pathfinding • BFS & DFS",
                            font=('Segoe UI', 10),
                            bg=self.COLOR_PRIMARY,
                            fg=self.COLOR_TEXT_SECONDARY)
        subtitle.pack(side=tk.LEFT, pady=12)
        
        
        # Main container 
        main = tk.Frame(self, bg=self.COLOR_BG_DARK)
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=12) # More compact 
        
        
        # Left - Canvas with scrollbars 
        left = tk.Frame(main, bg=self.COLOR_PRIMARY)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))
        
        
        # Create canvas with larger scrollable region
        self.canvas = tk.Canvas(left, 
                                bg=self.COLOR_CANVAS_BG,
                                highlightthickness=0,
                                scrollregion=(0, 0, 1000, 900)) # Define scrollable area 
        
        
        # Add scrollbars 
        h_scrollbar = tk.Scrollbar(left, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scrollbar = tk.Scrollbar(left, orient=tk.VERTICAL, command=self.canvas.yview)
        
        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        
        # Pack scrollbars and canvas 
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        
        # Right - Controls with compact width
        right = tk.Frame(main, bg=self.COLOR_BG_DARK, width=350)
        right.pack(side=tk.RIGHT, fill=tk.Y)
        right.pack_propagate(False)
        
        
        # Scrollable area for controls 
        canvas_scroll = tk.Canvas(right, bg=self.COLOR_BG_DARK, highlightthickness=0)
        scrollbar = tk.Scrollbar(right, orient="vertical", command=canvas_scroll.yview)
        scroll_frame = tk.Frame(canvas_scroll, bg=self.COLOR_BG_DARK)
        
        scroll_frame.bind("<Configure>",
            lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")))
        
        canvas_scroll.create_window((0, 0), window=scroll_frame, anchor="nw", width=330)
        canvas_scroll.configure(yscrollcommand=scrollbar.set)
        
        # Enable mousewheel scrolling 
        def _on_mousewheel(event):
            canvas_scroll.yview_scroll(int(-1*(event.delta/120)), "units")
            
        canvas_scroll.bind_all("<MouseWheel>", _on_mousewheel) # Windows/Mac
        canvas_scroll.bind_all("<Button-4>", lambda e: canvas_scroll.yview_scroll(-1, "units")) # Linux up
        canvas_scroll.bind_all("<Button-5>", lambda e: canvas_scroll.yview_scroll(1, "units")) # Linux down
        
        canvas_scroll.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Build control sections
        self._create_card(scroll_frame, "📍 Add Building",
                          self._build_add_building)
        
        self._create_card(scroll_frame, "🔗 Connect Buildings",
                          self._build_edge_section)
        
        self._create_card(scroll_frame, "🔍 Find Path (BFS/DFS)",
                  self._building_pathfinding)
        
        self._create_card(scroll_frame, "⚡ Manage Buildings",
                  self._build_node_management)
        
        self._create_card(scroll_frame, "⚙️ Manage Connections", 
                          self._build_edge_management)
        
        self._create_card(scroll_frame, "📊 Results", 
                          self._build_output)
        
        self._create_card(scroll_frame, "🎨 Legend",
                          self._build_legend)
        
    def _create_card(self, parent, title, build_func):
            """Create a styled card"""
            card = tk.Frame(parent, bg=self.COLOR_BG_CARD)
            card.pack(fill=tk.X, pady=(0, 8)) # Reduced spacing 
            
            # Colored top border 
            top_border = tk.Frame(card, bg=self.COLOR_PRIMARY, height=3)
            top_border.pack(fill=tk.X)
            
            # Title
            title_label = tk.Label(card,
                                   text=title,
                                   font=('Segoe UI', 11, 'bold'), # Smaller font 
                                   bg=self.COLOR_BG_CARD,
                                   fg=self.COLOR_TEXT_PRIMARY)
            title_label.pack(anchor='w', padx=10, pady=(8, 5)) # Reduced padding 
            
            # Content 
            content = tk.Frame(card, bg=self.COLOR_BG_CARD)
            content.pack(fill=tk.BOTH, padx=10, pady=(0, 8)) # Reduced padding 
            
            build_func(content)
            return card 
        
    def _build_add_building(self, parent):
        tk.Label(parent, text="Building Name:",
                 bg=self.COLOR_BG_CARD,
                 fg=self.COLOR_TEXT_MUTED,
                 font=('Segoe UI', 8)).pack(anchor='w', pady=(0, 3)) # Smaller font and padding 
        
        self.entry_node_name = ttk.Entry(parent, width=28)
        self.entry_node_name.pack(fill=tk.X, pady=(0, 8))
        
        self.btn_place_node = ttk.Button(parent,
                                         text="📍 Click to Place",  #Shorter text
                                         command=self._start_place_node,
                                         style='Accent.TButton')
        self.btn_place_node.pack(fill=tk.X)
        
        
    def _build_edge_section(self, parent):
        row1 = tk.Frame(parent, bg=self.COLOR_BG_CARD)   
        row1.pack(fill=tk.X, pady=(0, 6)) # Reduced spacing 
        
        col1 = tk.Frame(row1, bg=self.COLOR_BG_CARD)
        col1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8)) # More spacing 
        tk.Label(col1, text="From:",
                 bg=self.COLOR_BG_CARD,
                 fg=self.COLOR_TEXT_MUTED,
                 font=('Segoe UI', 8)).pack(anchor='w', pady=(0, 3)) # Smaller 
        self.combo_u = ttk.Combobox(col1, state="readonly", values=[], width=12) # Setting explicit width 
        self.combo_u.pack(fill=tk.X)
        
        col2 = tk.Frame(row1, bg=self.COLOR_BG_CARD)
        col2.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 0))
        tk.Label(col2, text="To:",
                bg=self.COLOR_BG_CARD,
                fg=self.COLOR_TEXT_MUTED,
                font=('Segoe UI', 8)).pack(anchor='w', pady=(0, 3)) # Smaller 
        self.combo_v = ttk.Combobox(col2, state="readonly", values=[], width=12) # Setting explicit width 
        self.combo_v.pack(fill=tk.X)
        
        row2 = tk.Frame(parent, bg=self.COLOR_BG_CARD)
        row2.pack(fill=tk.X, pady=(0, 6)) # Reduced spacing 
        
        col1 = tk.Frame(row2, bg=self.COLOR_BG_CARD)
        col1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8)) # More spacing 
        tk.Label(col1, text="Distance (m):",
                 bg=self.COLOR_BG_CARD,
                 fg=self.COLOR_TEXT_MUTED,
                 font=('Segoe UI', 8)).pack(anchor='w', pady=(0, 3)) # Smaller 
        self.entry_dist = ttk.Entry(col1, width=12) # Setting explicit width 
        self.entry_dist.pack(fill=tk.X)
        self.entry_dist.insert(0, "150")
        
        col2 = tk.Frame(row2, bg=self.COLOR_BG_CARD)
        col2.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 0))
        tk.Label(col2, text="Time (min):",
                 bg=self.COLOR_BG_CARD,
                 fg=self.COLOR_TEXT_MUTED,
                 font=('Segoe UI', 8)).pack(anchor='w', pady=(0, 3)) # Smaller 
        self.entry_time = ttk.Entry(col2, width=12) # Setting explicit width 
        self.entry_time.pack(fill=tk.X)
        self.entry_time.insert(0, "2.5")
        
        self.var_accessible = tk.BooleanVar(value=True)
        ttk.Checkbutton(parent, 
                        text="♿ Wheelchair Accessible",
                        variable=self.var_accessible).pack(anchor='w', pady=(0, 6)) # Reduced spacing 
        
        ttk.Button(parent,
                   text= "✓ Add Connection",
                   command=self._add_edge,
                   style='Success.TButton').pack(fill=tk.X)
        
    def _build_edge_management(self, parent):
        tk.Label(parent, text="Current Connections:",
                 bg=self.COLOR_BG_CARD,
                 fg=self.COLOR_TEXT_MUTED,
                 font=('Segoe UI', 8)).pack(anchor='w', pady=(0, 3)) # Smaller font and spacing 
        
        # Listbox with fixed height 
        list_frame = tk.Frame(parent, bg=self.COLOR_BG_INPUT)
        list_frame.pack(fill=tk.X, pady=(0, 6)) # Reduced spacing 
        
        self.listbox_edges = tk.Listbox(list_frame,
                                        height=4,
                                        width=36, # Reduced width 
                                        bg=self.COLOR_BG_INPUT,
                                        fg=self.COLOR_TEXT_PRIMARY,
                                        font=('Consolas', 8), # Smaller font 
                                        selectbackground=self.COLOR_PRIMARY,
                                        relief='flat')
        self.listbox_edges.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scroll_edges = tk.Scrollbar(list_frame, command=self.listbox_edges.yview)
        scroll_edges.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox_edges.config(yscrollcommand=scroll_edges.set)
        
        # Buttton row for edge management 
        btnrow_edges_1 = tk.Frame(parent, bg=self.COLOR_BG_CARD)
        btnrow_edges_1.pack(fill=tk.X, pady=4)
        
        
        ttk.Button(btnrow_edges_1,
                   text="🚧 Toggle Closed",
                   command=self._toggle_edge_closed).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        
        ttk.Button(btnrow_edges_1, 
                   text="♿ Toggle Accessible",
                   command=self._toggle_edge_accessible).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))
        
         # Buttton row 2 for edge management (actions)
        btnrow_edges_2 = tk.Frame(parent, bg=self.COLOR_BG_CARD)
        btnrow_edges_2.pack(fill=tk.X, pady=4)
        
        ttk.Button(btnrow_edges_2,
                 text="🎲 Randomize Weights",
                 command=self._randomize_weights).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        
        # Delete button below
        ttk.Button(btnrow_edges_2, 
                 text="🗑️ Delete Connection",
                 command=self._delete_edge,
                 style='Action.TButton').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))
        
        
    def _build_node_management(self, parent):
        tk.Label(parent, text="Current Buildings:",
                 bg=self.COLOR_BG_CARD,
                 fg=self.COLOR_TEXT_MUTED,
                 font=('Segoe UI', 8)).pack(anchor='w', pady=(0, 3))
        
        # Listbox with fixed height 
        list_frame = tk.Frame(parent, bg=self.COLOR_BG_INPUT)
        list_frame.pack(fill=tk.X, pady=(0, 6))
        
        self.listbox_nodes = tk.Listbox(list_frame, 
                                     height=4, 
                                     width=36,
                                     bg=self.COLOR_BG_INPUT,
                                     fg=self.COLOR_TEXT_PRIMARY,
                                     font=('Consolas', 8),
                                     selectbackground=self.COLOR_PRIMARY,
                                     relief='flat')
        self.listbox_nodes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scroll_nodes = tk.Scrollbar(list_frame, command=self.listbox_nodes.yview)
        scroll_nodes.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox_nodes.config(yscrollcommand=scroll_nodes.set)
        
        tk.Label(parent, text="Node weights = importance/capacity",
                 bg=self.COLOR_BG_CARD,
                 fg=self.COLOR_TEXT_MUTED,
                 font=('Segoe UI', 8),
                 wraplength=300).pack(anchor='w', pady=(0, 6))
        
        ttk.Button(parent,
                   text="🎲 Randomize Node Weights",
                   command=self._randomize_node_weights,
                   style='Action.TButton').pack(fill=tk.X, pady=(0, 4))
        
        ttk.Button(parent,
                   text="🗑️ Delete Selected Building",
                   command=self._delete_node,
                   style='Action.TButton').pack(fill=tk.X)
        
        
    def _building_pathfinding(self, parent):
        row1 = tk.Frame(parent, bg=self.COLOR_BG_CARD)
        row1.pack(fill=tk.X, pady=(0, 6)) # Reduced spacing 
        
        col1 = tk.Frame(row1, bg=self.COLOR_BG_CARD)
        col1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8)) # More spacing 
        tk.Label(col1, text="Start:",
                 bg=self.COLOR_BG_CARD,
                 fg=self.COLOR_TEXT_MUTED,
                 font=('Segoe UI', 8)).pack(anchor='w', pady=(0, 3)) # Smaller 
        self.combo_start = ttk.Combobox(col1, state="readonly", values=[], width=12) # Setting explicit width 
        self.combo_start.pack(fill=tk.X)
        
        col2 = tk.Frame(row1, bg=self.COLOR_BG_CARD)
        col2.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 0))
        tk.Label(col2, text="Goal:",
                 bg=self.COLOR_BG_CARD,
                 fg=self.COLOR_TEXT_MUTED,
                 font=('Segoe UI', 8)).pack(anchor='w', pady=(0, 3)) # Smaller 
        self.combo_goal = ttk.Combobox(col2, state="readonly", values=[], width=12) # Setting explicit width 
        self.combo_goal.pack(fill=tk.X)
        
        self.var_accessible_only = tk.BooleanVar(value=False)
        ttk.Checkbutton(parent,
                        text="♿ Accessible Routes Only",
                        variable=self.var_accessible_only).pack(anchor='w', pady=(0, 6)) # Reduced spacing 
        
        btn_frame = tk.Frame(parent, bg=self.COLOR_BG_CARD)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame,
                   text="BFS",
                   command=lambda: self._run_search("BFS")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        
        ttk.Button(btn_frame,
                   text="DFS",
                   command=lambda: self._run_search("DFS")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))
        
    def _build_output(self, parent):
        text_frame = tk.Frame(parent, bg=self.COLOR_BG_INPUT)
        text_frame.pack(fill=tk.BOTH, expand=True)
            
        self.txt_output = tk.Text(text_frame,
                                    height=6,
                                    width=36,   # Reduced width
                                    bg=self.COLOR_BG_INPUT,
                                    fg=self.COLOR_TEXT_PRIMARY,
                                    font=('Consolas', 8),  # Smaller font
                                    wrap=tk.WORD,
                                    relief='flat',
                                    padx=6,
                                    pady=6)
        self.txt_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
        scroll_output = tk.Scrollbar(text_frame, command=self.txt_output.yview)
        scroll_output.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_output.config(yscrollcommand=scroll_output.set)
            
    def _build_legend(self, parent):
        items = [
            ("●", self.COLOR_NODE, "Building"),
            ("─", self.COLOR_EDGE_OPEN, "Open Path"),
            ("─", self.COLOR_EDGE_CLOSED, "Closed Path"),
            ("─", self.COLOR_EDGE_NONACC, "Non-Accessible"),
            ("─", self.COLOR_PATH_HILITE, "Found Path") 
        ]
            
        for symbol, color, label in items:
            row = tk.Frame(parent, bg=self.COLOR_BG_CARD)
            row.pack(fill=tk.X, pady=1)   # Reduced spacing 
                
            tk.Label(row,
                    text=symbol, 
                    font=('Segoe Ui', 12, 'bold'),  # Slightly smaler 
                    fg=color,
                    bg=self.COLOR_BG_CARD,
                    width=2). pack(side=tk.LEFT)
                
            tk.Label(row, 
                    text=label,
                    bg=self.COLOR_BG_CARD,
                    fg=self.COLOR_TEXT_SECONDARY, 
                    font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=(4, 0))  # Smaller font 
                
    def _bind_events(self):
        self.canvas.bind("<Button-1>", self._on_canvas_click)
            
    def _on_canvas_click(self, event):
        if not self.mode_place_node:
            return 
            
        # Get click position relative to canvas (accounting for scroll)
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
            
        name = self.entry_node_name.get().strip()
        if not name:
            messagebox.showerror("Empty Name", "Enter a building name.")
            return 
            
        try:
            self.graph.add_node(name, int(x), int(y))
            self.entry_node_name.delete(0, tk.END)
            self.mode_place_node = False
            self.btn_place_node.config(text="📍 Click to Place") # Match shorter text
            self._redraw_all()
            self._refresh_node_lists()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
                
    def _start_place_node(self):
        name = self.entry_node_name.get().strip()
        if not name:
            messagebox.showerror("Empty Name", "Enter a building name first.")
            return 
            
        self.mode_place_node = True
        self.btn_place_node.config(text="🎯 Click Now")  # Even shorter for active state 
            
            
    def _add_edge(self):
        u = self.combo_u.get().strip()
        v = self.combo_v.get().strip()
        dist_str = self.entry_dist.get().strip()
        time_str = self.entry_time.get().strip()
        accessible = self.var_accessible.get()
            
        if not u or not v:
            messagebox.showerror("Missing Info", "Select both buildings.")
            return
            
        try:
            dist = float(dist_str)
            time = float(time_str)
        except ValueError:
            messagebox.showerror("Invalid Input", "Distance and time must be numbers.")
            return 
            
        try:
            self.graph.add_edge(u, v, dist, time, accessible)
            self._redraw_all()
            self._refresh_edge_list()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
                
    def _refresh_node_lists(self):
        names = sorted(self.graph.nodes.keys())
        
        # Update combo boxes
        for combo in [self.combo_u, self.combo_v, self.combo_start, self.combo_goal]:
            combo['values'] = names 
            if names and not combo.get():
                combo.current(0)
                    
                    
        # Update node listbox
        self.listbox_nodes.delete(0, tk.END)   
        for name in names:
            node = self.graph.nodes[name]  
            line = f"{name} (weight: {node.weight})"   
            self.listbox_nodes.insert(tk.END, line)    
            
                    
    def _refresh_edge_list(self):
        self.listbox_edges.delete(0, tk.END)
        for (a, b), e in sorted(self.graph.edges.items()):
            status = "✓" if not e.closed else "✗"
            acc = "♿" if e.accessible else "⚠️"
            line = f"{status} {a}  ↔ {b} | {int(e.distance)}m, {e.time:.1f}min {acc}"
            self.listbox_edges.insert(tk.END, line)
                
    def _redraw_all(self):
        self.canvas.delete("all")
            
        # Draw edges first (so they're ebhind nodes)
        for (a, b), e in self.graph.edges.items():
            n1 = self.graph.nodes[a]
            n2 = self.graph.nodes[b]
                
            # Determine color 
            if e.closed:
                color = self.COLOR_EDGE_CLOSED
                width = 3
                dash = (5, 3)
            elif not e.accessible:
                color = self.COLOR_EDGE_NONACC
                width = 2
                dash = None 
            else:
                color = self.COLOR_EDGE_OPEN
                width = 2
                dash = None 
                    
            # Draw edge
            self.canvas.create_line(
                n1.x, n1.y, n2.x, n2.y, 
                fill=color,
                width=width,
                dash=dash
            )
                
            # Draw distance label 
            mid_x = (n1.x + n2.x) / 2
            mid_y = (n1.y + n2.y) / 2
            self.canvas.create_text(
                mid_x, mid_y,
                text=f"{int(e.distance)}m",
                fill=self.COLOR_TEXT_MUTED,
                font=('Segoe UI', 8)
            )
                
        # Draw nodes with glow effect 
        for name, node in self.graph.nodes.items():
            x, y = node.x, node.y 
            # Scale radius based on weight (0.5x to 3.0x the base size)
            r = self.NODE_RADIUS
                
            # Glow layers (outer to inner)
            glow_scale = node.weight * 0.8 # Slightly less glow scaling 
            self.canvas.create_oval(x-r-10, y-r-10, x+r+10, y+r+10, 
                                fill=self.COLOR_NODE_GLOW_1, outline='')
            self.canvas.create_oval(x-r-6, y-r-6, x+r+6, y+r+6, 
                                fill=self.COLOR_NODE_GLOW_2, outline='')
            self.canvas.create_oval(x-r-3, y-r-3, x+r+3, y+r+3, 
                                fill=self.COLOR_NODE_GLOW_3, outline='')
            
            # Main node
            self.canvas.create_oval(x-r, y-r, x+r, y+r,
                                    fill=self.COLOR_NODE, 
                                    outline=self.COLOR_NODE_BORDER, 
                                    width=2)
                
            # Label with weight indicator 
            self.canvas.create_text(x, y+r+15, 
                                    text=name,
                                    fill=self.COLOR_TEXT_PRIMARY,
                                    font=('Segoe UI', 9, 'bold'))
                
    def _toggle_edge_closed(self):
        sel = self.listbox_edges.curselection()
        if not sel:
            messagebox.showinfo("No Selection", "Select a connection to toggle.")
            return 
            
        idx = sel[0]
        keys = sorted(self.graph.edges.keys())
        if idx >= len(keys):
            return 
        key = keys[idx]
        e = self.graph.edges[key]
        e.closed = not e.closed
        self._redraw_all()
        self._refresh_edge_list()
        
    def _randomize_weights(self):
        """Randomize all edge distances and times"""
        if not self.graph.edges:
            messagebox.showinfo("No Edges", "Add some connections first!")
            return 
        
        self.graph.randomize_weights()
        self._redraw_all()
        self._refresh_edge_list()
        messagebox.showinfo("Sucess", "All edge weights have been randomized!")
        
    def _randomize_node_weights(self):
        """Randomize all node weights (importance/capacity)"""
        if not self.graph.nodes:
            messagebox.showinfo("No Buildings", "Add some buildings first!")
            return 
        
        self.graph.randomize_node_weights()
        self._redraw_all()
        self._refresh_node_lists()
        messagebox.showinfo("Sucess", f"All {len(self.graph.nodes)} building weights have been randomized!")
        
    def _delete_edge(self):
        """Delete the selected edge/connection"""
        sel = self.listbox_edges.curselection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a connection to delete.")
            return
        
        idx = sel[0]
        keys = sorted(self.graph.edges.keys())
        if idx >= len(keys):
            return 
        
        key = keys[idx]
        a, b = key 
        
        # Confirm deletion 
        if messagebox.askyesno("Confirm Delete", 
                               f"Delete connection between '{a}' and '{b}'?"):
            try:
                self.graph.delete_edge(a, b)
                self._redraw_all()
                self._refresh_Edge_list()
                messagebox.showinfo("Success", "Connection deleted!")
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                
    def _delete_node(self):
        """Delete the selected node/building and all its connections"""
        sel = self.listbox_nodes.curselection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a building to delete.")
            return
        
        idx = sel[0]
        names = sorted(self.graph.nodes.keys())
        if idx >= len(names):
            return
        
        name = names[idx]
        
        # Check how many edges will be deleted 
        edge_count = sum(1 for key in self.graph.edges.keys() if name in key)
        
        # Confirm deletion 
        msg = f"Delete building '{name}'?"
        if edge_count > 0:
            msg += f"\n\nThis will also delete {edge_count} connection(s)."
            
        if messagebox.askyesno("Confirm Delete", msg):
            try: 
                deleted_edges = self.graph.delete_node(name)
                self._redraw_all()
                self._refresh_node_lists()
                self._refresh_edge_list()
                messagebox.showinfo("Success", 
                                    f"Deleted '{name}' and {deleted_edges} connection(s)!")
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                
                          
    def _run_search(self, mode: str):
        """Execute BFS or DFS search and animate the result"""
        # Doesn't start new search if animation is running 
        if self.animating:
            return 
            
        # Get user's selected start and goal buildings 
        start = self.combo_start.get().strip()
        goal = self.combo_goal.get().strip()
            
        # Validate inputs 
        if not start or not goal:
            messagebox.showerror("Invalid Selection", "Buildings must exist.")
            return
        if start == goal:
            messagebox.showwarning("Same Node", "Start and goal are the same.")
            return
            
        # run the selected algorithm 
        accessible_only = self.var_accessible_only.get()
        if mode == "BFS":
            visited_order, path = self._bfs(start, goal, accessible_only)
        else:
            visited_order, path = self._dfs(start, goal, accessible_only)
                
                
        # Show results
        self._print_result(mode, visited_order, path)
        if not path:
            messagebox.showinfo("No Path", f"No path found between '{start}' and '{goal}'.")
            return 
            
        # Validate that path only uses real edges
        for i in range(len(path) - 1):
            if not self.graph.get_edge(path[i], path[i+1]):
                messagebox.showerror("Path Error", "Invalid path detected!")
                return 
                
        # Set up animation 
        self.anim_steps = [(path[i], path[i+1]) for i in range(len(path) - 1)]
        self.active_path = path 
        self.anim_index = 0 
        self.animating = True 
        self._redraw_all()
        self._animate_step()
            
    def _animate_step(self):
        if self.anim_index >= len(self.anim_steps):
            self.animating = False 
            return 
            
        a, b = self.anim_steps[self.anim_index]
        e = self.graph.get_edge(a, b)
        if e:
            n1, n2 = self.graph.nodes[a], self.graph.nodes[b]
                
            # Draw thick highlighted path
            self.canvas.create_line(
                n1.x, n1.y, n2.x, n2.y,
                fill=self.COLOR_SUCCESS,
                smooth=True
            )
                
            # Highlight nodes
            r = self.NODE_RADIUS
            for node in [n1, n2]:
                self.canvas.create_oval(
                    node.x - r - 2, node.y - r - 2,
                    node.x + r + 2, node.y + r + 2,
                    outline=self.COLOR_PATH_HILITE,
                    width=3, 
                    fill=''
                )
                    
        self.anim_index += 1
        self.after(450, self._animate_step)
            
    def _clear_highlights(self):
        self.anim_steps = []
        self.active_path =[]
        self.anim_index = 0 
        self.animating = False
        self._redraw_all()
            
    def _bfs(self, start: str, goal: str, accessible_only: bool):
            """ 
            Breadth-First Search - finds shortest path by hop count. 
            Explores level by level. 
            """
            from collections import deque
            q = deque([start]) # Queue for BFS - FIFO 
            parent: Dict[str, Optional[str]] = {start: None} # Trakc path for reconstruction
            visited: Set[str] = {start} # Keep track of visited buildings 
            visited_order: List[str] = [] # Order we visited buildings for the output 
                
            while q:
                u = q.popleft() # Get next building fom front of queue 
                visited_order.append(u)
                    
                # Found the destination 
                if u == goal:
                    break
                    
                # Check all neighboring buildings
                for w in self.graph.neighbors(u, accessible_only):
                    e = self.graph.get_edge(u, w)
                    # Skip if path is closed or not accessible
                    if not e or e.closed or (accessible_only and not e.accessible):
                        continue 
                    # If we heaven't visited this building yet 
                    if w not in visited:
                        visited.add(w)
                        parent[w] = u # Remembering how we got here 
                        q.append(w) # Add to queue to explore later
                            
                            
            # Build the final path start to goal 
            path = self._reconstruct_path(parent, start, goal)
            return visited_order, path
            
    def _dfs(self, start: str, goal: str, accessible_only: bool):
        """ 
        Depth-First Search - explores as far as possible before backtracking.
        Uses recursion (goes deep befor going wide)
        """
        visited: Set[str] = set()
        visited_order: List[str] = []
        parent: Dict[str, Optional[str]] = {start: None}
        found = False # Flag to stop once e find the goal 
            
        def rec(u: str):
            """REursive helper function to explore paths"""
            nonlocal found # Access outer variable 
            if found:
                return # Already found path, stop searching
                
            visited.add(u)
            visited_order.append(u)
                
            # Check if we reached the goal 
            if u == goal:
                found = True
                return 
                
            # Try each neighbor (goes deep on first valid path)
            for w in self.graph.neighbors(u, accessible_only):
                e = self.graph.get_edge(u, w)
                # Skip closed or inaccessible paths 
                if not e or e.closed or (accessible_only and not e.accessible):
                    continue
                if w not in visited:
                    parent[w] = u 
                    rec(w) # Recursively explore this path 
                        
                        
        # Start the recursive search 
        rec(start)
            
        # Build the path if we found one 
        path = self._reconstruct_path(parent, start, goal) if found else[]
        return visited_order, path 
        
    def _reconstruct_path(self, parent: Dict[str, Optional[str]], start: str, goal: str) -> List[str]:
        """Trace back from goal to start using parent pointers to build the path"""
        if goal not in parent:
            return[] # No path exists 
            
        # Build path backwards from goal to start
        path = [goal]
        cur = goal
        while parent[cur] is not None:
            cur = parent[cur]
            path.append(cur)
                
        path.reverse() # Flip it to go start -> goal
            
        # Verify path starts at the right place 
        return path if path and path[0] == start else []
        
    def _print_result(self, mode: str, visited_order: List[str], path: List[str]):
        """ Display the search results in the output box"""
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, f"🔍 {mode} Traversal Order:\n")
        self.txt_output.insert(tk.END, " → ".join(visited_order) + "\n\n")
            
        if path:
            # Calculate total distance and time for the path 
            total_dist = 0 
            total_time = 0 
                
            for i in range(len(path) - 1):
                e = self.graph.get_edge(path[i], path[i+1])
                if e:
                    total_dist += e.distance 
                    total_time += e.time
                        
            self.txt_output.insert(tk.END, f"✓ {mode} Path ({len(path)-1} edges):\n")
            self.txt_output.insert(tk.END, " → ".join(path) + "\n\n")
            self.txt_output.insert(tk.END, f"📏 Distance: {int(total_dist)} meters\n")
            self.txt_output.insert(tk.END, f"⏱️ Time: {total_time:.1f} minutes\n")
        else:
            self.txt_output.insert(tk.END, "✗ No path found.\n")
                
if __name__ == "__main__":
    app = App()
    app.mainloop()
                    
