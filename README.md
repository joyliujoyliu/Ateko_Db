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

## 2. API Endpoint Explanations

### 1. GET /products 
Retrieves a list of products filtered by price range and active status.

**Web Interface Example:**

<img width="3633" height="1593" alt="image" src="https://github.com/user-attachments/assets/14916b0c-18c8-4fcf-843d-8f27a7d64299" />

After entering the filter values and clicking Execute, the API returns a JSON response:

<img width="3597" height="1011" alt="image" src="https://github.com/user-attachments/assets/1865414b-a040-4f05-b6bb-f9a17b096552" />

**Postman Example:**
You can also copy the request URL:
```
http://127.0.0.1:8000/products?min_price=1&max_price=10&active_only=true and paste it to postman git request
```
Paste it into Postman as a GET request:

<img width="1746" height="1191" alt="image" src="https://github.com/user-attachments/assets/27270acc-818f-4a8c-88e1-d86e85c2e8d0" />


### 2. Offset-Based Pagination
Returns a subset of products using limit (maximum number of products) and offset (starting row index).

<img width="3708" height="1362" alt="image" src="https://github.com/user-attachments/assets/97211c5b-f77a-48e8-b7b3-41c822efa719" />

Example: limit=5, offset=5 → returns 5 items starting from the 6th row.

<img width="3573" height="1359" alt="image" src="https://github.com/user-attachments/assets/d3a37cbe-20eb-4923-89c4-43789279f035" />

<img width="1707" height="882" alt="image" src="https://github.com/user-attachments/assets/7bcf7e5f-449c-4a02-9306-447e5f9c0048" />


### 3. Cursor-Based Pagination
Fetches all products after a given created_at timestamp. If multiple products share the same timestamp, it selects those with IDs greater than the cursor ID.

<img width="3648" height="1449" alt="image" src="https://github.com/user-attachments/assets/48de05a1-4b44-47f3-870c-399f680f7827" />

<img width="3558" height="1041" alt="image" src="https://github.com/user-attachments/assets/889a6bbd-3354-46b4-a7bf-392b0f053342" />

<img width="1689" height="705" alt="image" src="https://github.com/user-attachments/assets/a820d50d-c43f-464b-94d1-bf07cdc50cdc" />

**Note:**

* Use offset-based pagination for small datasets.

* Use cursor-based pagination for large, continuously growing datasets.

**Performance Tip:**

* LIMIT 5 OFFSET 1000 (offset-based) skips 1000 rows → slower for large datasets.

* Cursor-based pagination jumps directly using a stable key (created_at + id) → faster and more efficient.


### 4. POST /orders

Creates a new order for a customer. Steps include:

1. Validate customer existence.

2. Validate product existence.

3. Check stock availability.

4. Deduct stock if available.

5. Return the order record, including customer ID, order items, and total amount.
   
**Web Interface Example:**
<img width="3756" height="1755" alt="image" src="https://github.com/user-attachments/assets/02a56b80-a901-45f9-b53c-9ec3b27988f5" />

<img width="3510" height="930" alt="image" src="https://github.com/user-attachments/assets/a343b5ef-0423-46f8-81d3-8a30541a1810" />

**Postman Example:**

Switch to POST, paste the URL, and send the request:
<img width="1719" height="1281" alt="image" src="https://github.com/user-attachments/assets/e9d77148-8ede-4f32-90ad-48cedf57f10e" />

### 5. GET /orders/{order_id}
Retrieves complete order details, including:

* Order information

* Customer information

* List of order items
* 
<img width="3594" height="1491" alt="image" src="https://github.com/user-attachments/assets/6b9f6dfa-80ff-4c39-be0d-d7790e547495" />

<img width="1677" height="840" alt="image" src="https://github.com/user-attachments/assets/aa277aff-6ae7-4c58-b595-6b72b294372e" />












