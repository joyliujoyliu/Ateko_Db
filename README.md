# Ateko_Db
I'm building a backend service for a product and ordering platform used by an e-commerce client. The system must expose REST APIs that allow clients to browse products, create orders, and retrieve analytics.



## 1.  Setup
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

### Step 2: Configure the Database (MySQL)

Make sure MySQL is installed and running on your machine.

Create a new database for the project, e.g., ateko_db.

Import the database schema:

```
# From the terminal
mysql -u your_username -p < Ateko_DB.sql
```


### Step 3: Create a .env File

The .env file is used to store environment variables such as database credentials or API keys.

In your project folder, create a new file named .env.

Add your variables in the following format:

 <img width="984" height="504" alt="image" src="https://github.com/user-attachments/assets/51967195-61df-4787-962e-62b81dcc2994" />


### Step 4: Create a Virtual Environment

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

### Step 5: Activate the Virtual Environment

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

### Step 6: Install Dependencies

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

### Step 7: Run the API

Start the FastAPI server with:

```
uvicorn main:app --reload
```

### Optional: Freeze Dependencies

To make your project reproducible, save all installed packages:

```
pip freeze > requirements.txt
```

## 2. Endpoint Explainations

## 1. GET /products 
It will generate a list of product based on price range and active status.
<img width="3633" height="1593" alt="image" src="https://github.com/user-attachments/assets/14916b0c-18c8-4fcf-843d-8f27a7d64299" />

Once you put the vale and click excuse, it will give you a jason output like

<img width="3597" height="1011" alt="image" src="https://github.com/user-attachments/assets/1865414b-a040-4f05-b6bb-f9a17b096552" />


You can also copy the request url http://127.0.0.1:8000/products?min_price=1&max_price=10&active_only=true and paste it to postman git request
<img width="1746" height="1191" alt="image" src="https://github.com/user-attachments/assets/27270acc-818f-4a8c-88e1-d86e85c2e8d0" />


## 2. Offset-Based Pagination
It gives you a subset of the list based on limit (max number of product to return) and offset (after the number of rows to return)

<img width="3708" height="1362" alt="image" src="https://github.com/user-attachments/assets/97211c5b-f77a-48e8-b7b3-41c822efa719" />

For eg, if we put 5 for limit and 5 for offset, it gives you 5 item and the first one start from row 6
<img width="3573" height="1359" alt="image" src="https://github.com/user-attachments/assets/d3a37cbe-20eb-4923-89c4-43789279f035" />

<img width="1707" height="882" alt="image" src="https://github.com/user-attachments/assets/7bcf7e5f-449c-4a02-9306-447e5f9c0048" />


## 3. Cursor-Based Pagination

All products after the given created_at.
If multiple products have the same created_at, pick those with id greater than the cursor’s id.

<img width="3648" height="1449" alt="image" src="https://github.com/user-attachments/assets/48de05a1-4b44-47f3-870c-399f680f7827" />

<img width="3558" height="1041" alt="image" src="https://github.com/user-attachments/assets/889a6bbd-3354-46b4-a7bf-392b0f053342" />

<img width="1689" height="705" alt="image" src="https://github.com/user-attachments/assets/a820d50d-c43f-464b-94d1-bf07cdc50cdc" />

Note: if your dataset is small you can use offset, if it's large and keep going, it's better to use Cursor-Based Pagination
For eg:
Offset-based pagination (LIMIT 5 OFFSET 1000) requires skipping all previous rows in the database, which slows down for large datasets.
Cursor-based pagination uses a stable key (created_at + id) to jump directly to the next rows, no skipping, much faster for large tables.












