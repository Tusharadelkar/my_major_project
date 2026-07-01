import json
import os

questions = [
    # --- SOFTWARE ENGINEER: PYTHON (10) ---
    {
        "question": "What is the difference between list and tuple in Python, and when would you use each?",
        "role": "software engineer", "skill": "Python", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "Explain how Python's Global Interpreter Lock (GIL) affects multi-threaded programs.",
        "role": "software engineer", "skill": "Python", "difficulty": "hard", "type": "technical"
    },
    {
        "question": "What are decorators in Python, and how do you write a custom decorator?",
        "role": "software engineer", "skill": "Python", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "How does memory management and garbage collection work in Python?",
        "role": "software engineer", "skill": "Python", "difficulty": "hard", "type": "technical"
    },
    {
        "question": "What are generators and yield in Python, and how do they save memory?",
        "role": "software engineer", "skill": "Python", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "Explain the difference between deep copy and shallow copy in Python.",
        "role": "software engineer", "skill": "Python", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "How do list comprehensions work in Python, and when should you avoid them?",
        "role": "software engineer", "skill": "Python", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "What is the purpose of Python's virtualenv and requirements.txt?",
        "role": "software engineer", "skill": "Python", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "Explain how argument passing works in Python (pass-by-value vs. pass-by-reference).",
        "role": "software engineer", "skill": "Python", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "What are python's dunder (magic) methods, and how would you implement __str__ or __init__?",
        "role": "software engineer", "skill": "Python", "difficulty": "medium", "type": "technical"
    },

    # --- SOFTWARE ENGINEER: REACT (10) ---
    {
        "question": "Explain the React component lifecycle and how useEffect replaces older lifecycle methods.",
        "role": "software engineer", "skill": "React", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "What is the Virtual DOM, and how does React use it to optimize rendering performance?",
        "role": "software engineer", "skill": "React", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "Explain the difference between state and props in React.",
        "role": "software engineer", "skill": "React", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "What is React Context API, and how does it compare to state management libraries like Redux?",
        "role": "software engineer", "skill": "React", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "How do you optimize a React application's rendering performance (e.g. useMemo, useCallback, React.memo)?",
        "role": "software engineer", "skill": "React", "difficulty": "hard", "type": "technical"
    },
    {
        "question": "What are React custom hooks, and why would you write one?",
        "role": "software engineer", "skill": "React", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "Explain how React routing works in a Single Page Application (SPA).",
        "role": "software engineer", "skill": "React", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "What is the significance of the 'key' prop in React when rendering lists?",
        "role": "software engineer", "skill": "React", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "How does server-side rendering (SSR) in React/Next.js compare to client-side rendering (CSR)?",
        "role": "software engineer", "skill": "React", "difficulty": "hard", "type": "technical"
    },
    {
        "question": "How do you handle form state and form validation in React (controlled vs. uncontrolled components)?",
        "role": "software engineer", "skill": "React", "difficulty": "medium", "type": "technical"
    },

    # --- SOFTWARE ENGINEER: SQL (10) ---
    {
        "question": "What are the differences between INNER JOIN, LEFT JOIN, RIGHT JOIN, and OUTER JOIN?",
        "role": "software engineer", "skill": "SQL", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "Explain database indexing, how it works, and its impact on write vs. read performance.",
        "role": "software engineer", "skill": "SQL", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "What are ACID properties in a database management system? Explain each.",
        "role": "software engineer", "skill": "SQL", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "Explain the difference between WHERE and HAVING clauses in SQL.",
        "role": "software engineer", "skill": "SQL", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "What are window functions in SQL, and how do they differ from GROUP BY?",
        "role": "software engineer", "skill": "SQL", "difficulty": "hard", "type": "technical"
    },
    {
        "question": "Explain database normalization forms (1NF, 2NF, 3NF). Why normalization?",
        "role": "software engineer", "skill": "SQL", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "What are SQL transactions, and how do database locks prevent concurrency anomalies?",
        "role": "software engineer", "skill": "SQL", "difficulty": "hard", "type": "technical"
    },
    {
        "question": "How do foreign key constraints enforce referential integrity, and what is ON DELETE CASCADE?",
        "role": "software engineer", "skill": "SQL", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "What are Common Table Expressions (CTEs), and when would you use recursive CTEs?",
        "role": "software engineer", "skill": "SQL", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "Explain the difference between SQL (relational) and NoSQL (document/key-value) databases.",
        "role": "software engineer", "skill": "SQL", "difficulty": "easy", "type": "technical"
    },

    # --- SOFTWARE ENGINEER: DOCKER (10) ---
    {
        "question": "What is the difference between a Docker container and a virtual machine (VM)?",
        "role": "software engineer", "skill": "Docker", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "How do Docker images and layers work, and how can you optimize Dockerfile to reduce image size?",
        "role": "software engineer", "skill": "Docker", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "Explain the purpose of Docker volumes, and differentiate between bind mounts and named volumes.",
        "role": "software engineer", "skill": "Docker", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "What is Docker Compose, and when would you use it instead of docker run?",
        "role": "software engineer", "skill": "Docker", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "Explain how multi-stage Docker builds work and why they are beneficial.",
        "role": "software engineer", "skill": "Docker", "difficulty": "hard", "type": "technical"
    },
    {
        "question": "How do you handle container networking in Docker? Differentiate bridge and host networks.",
        "role": "software engineer", "skill": "Docker", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "What are Docker environment variables, and how do you securely manage credentials in production containers?",
        "role": "software engineer", "skill": "Docker", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "What is the difference between COPY and ADD instructions in a Dockerfile?",
        "role": "software engineer", "skill": "Docker", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "How do you implement health checks inside a Docker Compose service definition?",
        "role": "software engineer", "skill": "Docker", "difficulty": "hard", "type": "technical"
    },
    {
        "question": "What are the common strategies for logging container output in a containerized production setup?",
        "role": "software engineer", "skill": "Docker", "difficulty": "medium", "type": "technical"
    },

    # --- SOFTWARE ENGINEER: FASTAPI (10) ---
    {
        "question": "What is FastAPI, and how does it use Python type hints to perform request validation?",
        "role": "software engineer", "skill": "FastAPI", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "Explain how FastAPI's dependency injection system works. Why is it useful?",
        "role": "software engineer", "skill": "FastAPI", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "What is the difference between async def and def in FastAPI path operations, and when should you use each?",
        "role": "software engineer", "skill": "FastAPI", "difficulty": "hard", "type": "technical"
    },
    {
        "question": "How does FastAPI generate interactive Swagger UI API documentation automatically?",
        "role": "software engineer", "skill": "FastAPI", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "Explain how to handle CORS (Cross-Origin Resource Sharing) middleware in a FastAPI project.",
        "role": "software engineer", "skill": "FastAPI", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "How do you implement global exception handling and custom validation error overrides in FastAPI?",
        "role": "software engineer", "skill": "FastAPI", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "What is the role of Starlette and Pydantic in the architecture of FastAPI?",
        "role": "software engineer", "skill": "FastAPI", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "How do you implement background tasks in FastAPI, and when should you use Celery instead?",
        "role": "software engineer", "skill": "FastAPI", "difficulty": "hard", "type": "technical"
    },
    {
        "question": "Explain how security and authentication utilities (e.g. OAuth2, JWT) are integrated in FastAPI.",
        "role": "software engineer", "skill": "FastAPI", "difficulty": "hard", "type": "technical"
    },
    {
        "question": "How would you write integration tests for a FastAPI app using TestClient and pytest?",
        "role": "software engineer", "skill": "FastAPI", "difficulty": "medium", "type": "technical"
    },

    # --- SOFTWARE ENGINEER: GIT (10) ---
    {
        "question": "What is the difference between git merge and git rebase, and when would you use each?",
        "role": "software engineer", "skill": "Git", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "Explain git cherry-pick and how you pull a specific commit onto another branch.",
        "role": "software engineer", "skill": "Git", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "What is the purpose of git stash, and how do you apply or drop stashed changes?",
        "role": "software engineer", "skill": "Git", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "What is git reflog, and how can it save you if you accidentally deleted a branch?",
        "role": "software engineer", "skill": "Git", "difficulty": "hard", "type": "technical"
    },
    {
        "question": "How do merge conflicts arise, and what steps do you take to resolve them?",
        "role": "software engineer", "skill": "Git", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "What is the difference between git pull and git fetch?",
        "role": "software engineer", "skill": "Git", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "Explain how git reset works. Differentiate between soft, mixed, and hard resets.",
        "role": "software engineer", "skill": "Git", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "What is a detached HEAD state in Git, and how do you recover from it?",
        "role": "software engineer", "skill": "Git", "difficulty": "hard", "type": "technical"
    },
    {
        "question": "Explain how a standard git workflow (like Git Flow or GitHub Flow) operates in a team.",
        "role": "software engineer", "skill": "Git", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "How do you customize git behavior using git hooks, and give an example of a pre-commit hook.",
        "role": "software engineer", "skill": "Git", "difficulty": "medium", "type": "technical"
    },

    # --- SOFTWARE ENGINEER: SYSTEM DESIGN (10) ---
    {
        "question": "What is the difference between horizontal and vertical scaling?",
        "role": "software engineer", "skill": "System Design", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "Explain the concept of Load Balancing and list the common algorithms used (e.g. Round Robin).",
        "role": "software engineer", "skill": "System Design", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "What is the CAP theorem in distributed systems? Explain consistency, availability, and partition tolerance.",
        "role": "software engineer", "skill": "System Design", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "How does database sharding differ from partitioning, and what are the challenges of sharding?",
        "role": "software engineer", "skill": "System Design", "difficulty": "hard", "type": "technical"
    },
    {
        "question": "What is a Content Delivery Network (CDN), and how does it speed up web applications?",
        "role": "software engineer", "skill": "System Design", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "Explain caching strategies like Write-Through, Write-Back, and Cache-Aside. When is caching bad?",
        "role": "software engineer", "skill": "System Design", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "What is a microservice architecture, and how do services communicate (REST vs. gRPC vs. Message Queues)?",
        "role": "software engineer", "skill": "System Design", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "How do message brokers like Kafka or RabbitMQ enable asynchronous communication and event-driven design?",
        "role": "software engineer", "skill": "System Design", "difficulty": "hard", "type": "technical"
    },
    {
        "question": "Explain Rate Limiting, why we need it, and common algorithms (e.g., Token Bucket).",
        "role": "software engineer", "skill": "System Design", "difficulty": "hard", "type": "technical"
    },
    {
        "question": "Explain the concept of Consistent Hashing and why it is critical for caching clusters.",
        "role": "software engineer", "skill": "System Design", "difficulty": "hard", "type": "technical"
    },

    # --- SOFTWARE ENGINEER: DATA STRUCTURES & ALGORITHMS (10) ---
    {
        "question": "What is Big O notation, and how do you calculate the time complexity of a recursive function?",
        "role": "software engineer", "skill": "Data Structures", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "Explain the difference between a hash table and a binary search tree (BST). What are lookup complexities?",
        "role": "software engineer", "skill": "Data Structures", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "What is the difference between Depth First Search (DFS) and Breadth First Search (BFS)?",
        "role": "software engineer", "skill": "Algorithms", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "Explain how Dijkstra's algorithm finds the shortest path in a graph. What are its limitations?",
        "role": "software engineer", "skill": "Algorithms", "difficulty": "hard", "type": "technical"
    },
    {
        "question": "What is Dynamic Programming, and how does memoization differ from tabulation?",
        "role": "software engineer", "skill": "Algorithms", "difficulty": "hard", "type": "technical"
    },
    {
        "question": "Explain how a binary search algorithm works. What is its time complexity?",
        "role": "software engineer", "skill": "Algorithms", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "What is the difference between Quick Sort and Merge Sort? When would you use one over the other?",
        "role": "software engineer", "skill": "Algorithms", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "What is a Trie data structure, and how is it used for autocomplete features?",
        "role": "software engineer", "skill": "Data Structures", "difficulty": "hard", "type": "technical"
    },
    {
        "question": "How do you detect a cycle in a linked list? Explain Floyd's Cycle-Finding Algorithm (Tortoise and Hare).",
        "role": "software engineer", "skill": "Algorithms", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "Explain how a priority queue is implemented using a binary heap.",
        "role": "software engineer", "skill": "Data Structures", "difficulty": "medium", "type": "technical"
    },

    # --- DATA ANALYST: PANDAS & EXCEL (10) ---
    {
        "question": "How do you handle missing or null data in Pandas? Explain dropna vs fillna.",
        "role": "data analyst", "skill": "Pandas", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "Explain the difference between merge, join, and concat operations in Pandas.",
        "role": "data analyst", "skill": "Pandas", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "What is a Pivot Table in Excel or Pandas, and when would you use one to summarize data?",
        "role": "data analyst", "skill": "Excel", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "How do VLOOKUP, INDEX, and MATCH compare in Excel? What are index-match advantages?",
        "role": "data analyst", "skill": "Excel", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "What is the difference between groupby and pivot in Pandas?",
        "role": "data analyst", "skill": "Pandas", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "How do you optimize Pandas operations on large datasets (e.g. vectorization vs iteration)?",
        "role": "data analyst", "skill": "Pandas", "difficulty": "hard", "type": "technical"
    },
    {
        "question": "Explain how Excel macros and VBA work. What is their modern replacement (Power Query)?",
        "role": "data analyst", "skill": "Excel", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "How do you perform data cleaning (handling outliers, duplicates, type conversions) in Pandas?",
        "role": "data analyst", "skill": "Pandas", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "Explain the use of lambda functions and apply() in Pandas for custom transformations.",
        "role": "data analyst", "skill": "Pandas", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "What is exploratory data analysis (EDA), and what key statistics do you analyze first?",
        "role": "data analyst", "skill": "Pandas", "difficulty": "easy", "type": "technical"
    },

    # --- DATA ANALYST: TABLEAU & STATISTICS (10) ---
    {
        "question": "What is the difference between dimensions and measures in Tableau?",
        "role": "data analyst", "skill": "Tableau", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "Explain the difference between discrete (blue) and continuous (green) fields in Tableau.",
        "role": "data analyst", "skill": "Tableau", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "What are Level of Detail (LOD) expressions in Tableau, and when would you use them?",
        "role": "data analyst", "skill": "Tableau", "difficulty": "hard", "type": "technical"
    },
    {
        "question": "How do you explain the central limit theorem, and why is it important in statistical analysis?",
        "role": "data analyst", "skill": "Statistics", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "What is a p-value in statistics, and how do you interpret it in a hypothesis test?",
        "role": "data analyst", "skill": "Statistics", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "What is A/B testing? How do you calculate sample size and statistical power?",
        "role": "data analyst", "skill": "Statistics", "difficulty": "hard", "type": "technical"
    },
    {
        "question": "Explain Type I and Type II errors in statistics, and give examples.",
        "role": "data analyst", "skill": "Statistics", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "What is correlation vs. causation? Give an example of a spurious correlation.",
        "role": "data analyst", "skill": "Statistics", "difficulty": "easy", "type": "technical"
    },
    {
        "question": "How does linear regression work, and what are its key assumptions?",
        "role": "data analyst", "skill": "Statistics", "difficulty": "medium", "type": "technical"
    },
    {
        "question": "What is a Tableau dashboard action, and how does it enable interactive filtering?",
        "role": "data analyst", "skill": "Tableau", "difficulty": "easy", "type": "technical"
    },

    # --- BEHAVIORAL: LEADERSHIP & GROWTH (10) ---
    {
        "question": "Tell me about a time you had a conflict with a colleague and how you resolved it.",
        "role": "behavioral", "skill": "Conflict", "difficulty": "easy", "type": "behavioral"
    },
    {
        "question": "Describe a situation where you had to lead a project under tight deadlines.",
        "role": "behavioral", "skill": "Leadership", "difficulty": "medium", "type": "behavioral"
    },
    {
        "question": "Give an example of a mistake you made at work. What did you learn?",
        "role": "behavioral", "skill": "Growth", "difficulty": "easy", "type": "behavioral"
    },
    {
        "question": "Tell me about a time you worked on a team to build a complex system.",
        "role": "behavioral", "skill": "Collaboration", "difficulty": "easy", "type": "behavioral"
    },
    {
        "question": "How do you handle criticism or negative feedback from a manager?",
        "role": "behavioral", "skill": "Growth", "difficulty": "easy", "type": "behavioral"
    },
    {
        "question": "Tell me about a time you had to learn a new technology quickly for a project.",
        "role": "behavioral", "skill": "Growth", "difficulty": "medium", "type": "behavioral"
    },
    {
        "question": "Describe a time you disagreed with a major decision. How did you communicate your view?",
        "role": "behavioral", "skill": "Conflict", "difficulty": "medium", "type": "behavioral"
    },
    {
        "question": "Tell me about a time you went above and beyond to help a client or a team member.",
        "role": "behavioral", "skill": "Leadership", "difficulty": "easy", "type": "behavioral"
    },
    {
        "question": "How do you prioritize your tasks when handling multiple projects at the same time?",
        "role": "behavioral", "skill": "Leadership", "difficulty": "medium", "type": "behavioral"
    },
    {
        "question": "Describe a time when you had to work with a teammate whose working style was very different from yours.",
        "role": "behavioral", "skill": "Collaboration", "difficulty": "easy", "type": "behavioral"
    }
]

# Write to file
file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seed_questions.json")
with open(file_path, "w") as f:
    json.dump(questions, f, indent=2)

print(f"Generated {len(questions)} seed questions in {file_path}")
