# Interactive-Campus-Navigation-System-
A complete graph editor and pathfinding visualization tool featuring Breadth-First Search (BFS) and Depth-First Search (DFS) algorithms with animated path traversal, weighted nodes/edges, and full CRUD operations.


<img width="2598" height="1532" alt="Image 10-28-25 at 4 04 PM" src="https://github.com/user-attachments/assets/598258d9-6623-48c8-a871-05967c2ecc93" />

<img width="2598" height="1532" alt="Image 10-28-25 at 4 05 PM" src="https://github.com/user-attachments/assets/e321d4e0-c2d5-49a1-b220-2316b38920f7" />

BFS Path: 
<img width="2598" height="1532" alt="Image 10-28-25 at 4 06 PM (1)" src="https://github.com/user-attachments/assets/dce161fc-043c-48e6-943f-07ced8e52907" />

DFS Path: 
<img width="2598" height="1532" alt="Image 10-28-25 at 4 07 PM" src="https://github.com/user-attachments/assets/86a659e9-1dd7-4490-a537-867da34e8ae5" />




## ✨ Features
Complete Graph Editor 
- Click to place - building nodes on canvas
- Drag-and-scroll - canvas for large maps
- Custom naming - for each location
- Visual node weights - representing importance/capacity
- Delete nodes - with intelliget cascading deletion
- Delete edges - individually

## 🔗 Connection Management 
- Connect buildings with weighted edges
- Set distance and time for each path
- Mark paths as wheelchair accessible ♿
- Toggle paths open/closed dynamically
- Delete connections with confirmation
- Randomize weights for testing

## 🔍 Pathfinding Algorithms 
BFS (Breadth-First Search) - Finds shortest path by hop count 
DFS (Depth-First Search) - Explores deeply before backtracking 
Animated traversal shows algorithm in action 
Accesible-only mode for wheelchair routes 
Real-time statistics (distance, time, path length)

## 🎨 GUI
- Modern dark theme with vibrant colors
- Color-coded node effects
- Scrollable control panels

# Usage Guide
## Adding Buildings 
1. Enter a building name in the "Add Building" section
2. Click "📍 Click to Place"
3. Click anywhere on the canvas to place the building
4. Node size represents its weight/importance

## Creating Paths
1. Select "From" and "To" buildings from dropdowns
2. Enter distance(meters) and time (minutes)
3. Check ♿ if wheelchair accessible
4. Click "✓ Add Connection"

## Finding Paths
1. Select Start and Goal buildings
2. Optionally enable "♿ Accessible Routes Only"
3. Click BFS or DFS to run the algorithm
4. Watch the animated path traversal!
5. View results with statistics in the output panel

## Managing Connections 
- Toggle Closed: Temporarily close/open a path.
- Toggle Accessible: Change accessibility status.
- Delete Connection: Remove a connection permanently (with confirmation).
- Randomize Weights: Randomize all distances and times.

## Managing Nodes
- View all buildings: See complete list with weights.
- Delete Building: Remove a building and all its connections (with confirmation)
- Randomize Node Weights: Change building importance/capacity values.
- Larger nodes = higher weight/importance

## Algorithm Details 
## Breadth-First Search (BFS)
- Explores level by level using a queue (FIFO)
- Guarantees shortest path by hop count
- Time Complexity: O(V + E)
- Space Complexity: O(V)
- Best for: Finding shortest unweighted paths

## Depth-First Search (DFS)
- Explores deeply using recursion (stack-like)
- May not find shortest path but finds a path quickly
- Time Complexity: O(V + E)
- Space Complexity: O(V)
- Best for: MAze solving, exploring all possibilites
Where V = vertices (buildings), E = edges (path)

## 🎓Educational Value
This project demonstrates:

- Graph theory fundamentals
- Search algorithms (BFS vs DFS)
- Data structures (graphs, queues, dictionaries, sets)
- GUI programming with Tkinter
- Animation and visual feedback
- Path reconstruction techniques
- Accessibility considerations in routing

## 📝 License
MIT License
    
