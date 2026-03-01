# Ateko_Db
I'm building a backend service for a product and ordering platform used by an e-commerce client. The system must expose REST APIs that allow clients to browse products, create orders, and retrieve analytics.

## 1. Setup
Follow these steps to set up the Ateko_DB FastAPI project locally.

### Step 1: Clone or Fork the Repository

Fork the Ateko_DB repository to your GitHub account (optional).

Clone it to your local machine:

```bash
git clone https://github.com/your-username/Ateko_DB.git
```
Navigate to the project folder:
```bash
cd Track_A_Ateko
```

### Step 2: Create a .env File

The .env file is used to store environment variables such as database credentials or API keys.

In your project folder, create a new file named .env.

Add your variables in the following format:

 <img width="984" height="504" alt="image" src="https://github.com/user-attachments/assets/51967195-61df-4787-962e-62b81dcc2994" />


### Step 3: Create a Virtual Environment

In the terminal (VS Code or PowerShell), run:
```bash
python -m venv .venv
```

This will create:
```
Track_A_Ateko
 └── .venv
     └── Scripts
```

### Step 4: Activate the Virtual Environment

```
.\.venv\Scripts\Activate.ps1
```
If you get a policy error, run this once:

```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then activate again:

```
.\.venv\Scripts\Activate.ps1
```

After activation, your terminal should show:

```
(.venv) PS C:\path\to\Track_A_Ateko>
```

Step 5: Install Dependencies

Once the virtual environment is active, install required packages:

```
pip install fastapi uvicorn sqlalchemy python-dotenv
```
If you are using a specific database like PostgreSQL or MySQL, also install the corresponding driver:

```
# PostgreSQL
pip install psycopg2-binary

# MySQL
pip install pymysql
```

Step 6: Run the API

Start the FastAPI server with:

```
uvicorn main:app --reload
```

Optional: Freeze Dependencies

To make your project reproducible, save all installed packages:

```
pip freeze > requirements.txt
```

