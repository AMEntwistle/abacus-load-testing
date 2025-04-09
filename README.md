# README

## Installation and Setup

Follow these steps to install and run Locust for this repository:

### Prerequisites
- Python 3.12.6 (do not use 3.13.x due to a compatability issue)
- `pip` (Python package manager)
- `virtualenv` (optional but recommended)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Create and Activate a Virtual Environment (Optional)
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
```

### 3. Install Dependencies
Install the required Python packages using `pip`:
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory (if not already present) and set the required environment variables. Use `.env.shadow` as a reference:
```dotenv
GRAPHQL_URL=<your-graphql-url>
BEARER_TOKEN=<your-bearer-token>
```

### 5. Prepare GraphQL Query Files
Ensure the `graphqlQueries` folder contains the required `.gql` files (e.g., `getContract.gql`, `getTransactionTypesWithGroups.gql`).

### 6. Run Locust
Start Locust by running the following command:
```bash
locust
```

### 7. Access the Locust Web Interface
Open your browser and navigate to:
```
http://localhost:8089
```

### 8. Configure and Start the Test
1. Enter the number of users and spawn rate.
2. Provide the host URL (e.g., the value of `GRAPHQL_URL`).
3. Click "Start Swarming" to begin the test.

---

### Notes
- Ensure the `.gql` files are correctly formatted and located in the `graphqlQueries` directory.
- Use the `name` parameter in the Locust tasks to differentiate GraphQL calls in the report.