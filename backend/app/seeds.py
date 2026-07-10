from sqlalchemy.orm import Session
from app.models import QuestionBank

SEED_QUESTIONS = [
    # --- DSA ---
    {
        "category": "DSA",
        "topic": "Arrays",
        "difficulty": "Medium",
        "question_text": "Given an array of integers 'nums' and an integer 'target', return indices of the two numbers such that they add up to 'target'. Explain your approach, how you would optimize the time complexity, and how you would handle duplicates or missing solutions.",
        "expected_keywords": ["Hash Map", "two sum", "O(N) time complexity", "complement", "single pass", "indices"]
    },
    {
        "category": "DSA",
        "topic": "Linked Lists",
        "difficulty": "Medium",
        "question_text": "Describe the difference between singly and doubly linked lists. How do you detect a cycle in a linked list? Write down the optimal algorithm and describe its time and space complexities.",
        "expected_keywords": ["Floyd's Cycle-Finding Algorithm", "slow pointer", "fast pointer", "cycle detection", "O(1) space complexity", "O(N) time complexity"]
    },
    {
        "category": "DSA",
        "topic": "Trees",
        "difficulty": "Medium",
        "question_text": "What is a Binary Search Tree (BST)? Explain how insertion works, what its worst-case time complexity is, and how self-balancing trees (such as AVL or Red-Black trees) prevent worst-case scenarios.",
        "expected_keywords": ["left subtree less", "right subtree greater", "balanced tree", "O(log N) average complexity", "O(N) worst case", "rotations"]
    },
    {
        "category": "DSA",
        "topic": "Graphs",
        "difficulty": "Medium",
        "question_text": "Compare Depth-First Search (DFS) and Breadth-First Search (BFS). Under what circumstances is BFS preferred over DFS? Describe the time and space complexity for both when searching a graph represented as an adjacency list.",
        "expected_keywords": ["Queue for BFS", "Stack or recursion for DFS", "shortest path", "O(V + E) time complexity", "adjacency list", "queue"]
    },
    
    # --- DBMS ---
    {
        "category": "DBMS",
        "topic": "Transactions",
        "difficulty": "Medium",
        "question_text": "Explain the ACID properties of database transactions. Why are they critical, and how does a relational database management system ensure the 'Isolation' property under concurrent transactions?",
        "expected_keywords": ["Atomicity", "Consistency", "Isolation", "Durability", "Locks", "Concurrency Control", "transaction levels", "dirty read"]
    },
    {
        "category": "DBMS",
        "topic": "Indexing",
        "difficulty": "Medium",
        "question_text": "What is a database index? Explain how B-Trees and B+ Trees work as indexes under the hood, and how indexing speeds up SELECT queries while potentially slowing down INSERT and UPDATE operations.",
        "expected_keywords": ["B+ Tree", "disk I/O operations", "leaf nodes linked list", "write overhead", "search speed", "index lookup"]
    },

    # --- OS ---
    {
        "category": "OS",
        "topic": "Virtual Memory",
        "difficulty": "Medium",
        "question_text": "Explain virtual memory, paging, page faults, and thrashing. How does the Operating System work with the Memory Management Unit (MMU) to map virtual address spaces to physical memory frames?",
        "expected_keywords": ["Paging", "Page table", "MMU", "Thrashing", "virtual address space", "page replacement algorithm", "TLB cache"]
    },
    {
        "category": "OS",
        "topic": "Processes vs Threads",
        "difficulty": "Medium",
        "question_text": "What are the primary differences between a Process and a Thread? Describe context switching and explain why switching between threads of the same process is faster than switching between processes.",
        "expected_keywords": ["Shared memory address space", "Context switching overhead", "Process Control Block", "Thread stack", "virtual memory swap"]
    },

    # --- OOP ---
    {
        "category": "OOP",
        "topic": "Polymorphism",
        "difficulty": "Medium",
        "question_text": "What is polymorphism in Object-Oriented Programming? Explain the differences between compile-time polymorphism (method overloading) and runtime polymorphism (method overriding) with simple examples.",
        "expected_keywords": ["Method Overriding", "Method Overloading", "dynamic dispatch", "inheritance", "virtual method table", "polymorphic behavior"]
    },
    {
        "category": "OOP",
        "topic": "Encapsulation",
        "difficulty": "Medium",
        "question_text": "Explain Encapsulation. How does it promote information hiding, and how do access modifiers (private, protected, public) help enforce encapsulation in class design?",
        "expected_keywords": ["Data Hiding", "Access Modifiers", "getter and setter methods", "coupling reduction", "internal representation protection"]
    }
]

def seed_questions(db: Session):
    """Checks if the question bank is empty. If it is, populates it with the standard seed questions."""
    count = db.query(QuestionBank).count()
    if count == 0:
        for q in SEED_QUESTIONS:
            db_q = QuestionBank(
                category=q["category"],
                topic=q["topic"],
                difficulty=q["difficulty"],
                question_text=q["question_text"],
                expected_keywords=q["expected_keywords"]
            )
            db.add(db_q)
        db.commit()
