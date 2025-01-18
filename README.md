# Congo: An E-Commerce Project

Congo is a proof-of-concept e-commerce web application built using Flask, SQLite, and HTML/CSS. It allows users to browse products, manage a shopping cart, and simulate the checkout process. While the project is functional, it is intended for learning purposes and does not process real payments.

# Features

- User authentication (sign-up, log-in, log-out)

- Product browsing with search functionality

- Add products to a cart

- Dynamic cart management with tax calculations

- Checkout process with address and order management

- Address saving and pre-population for returning users

- Order summary page with estimated delivery date

# Prerequisites

To run Namazon, you need the following installed on your system:

Software Requirements:

Python: Version 3.7 or higher
- Ensure pip (Python's package manager) is also installed.

SQLite: Pre-installed with most Python installations.

Install the required Python packages using the following command:
pip install flask flask_sqlalchemy werkzeug

# Database Tables
Users: Stores user details, including email, password, and address information.

Products: Stores product details like name, price, description, and image URL.

Orders: Stores order details, such as user ID, total price, and address.

OrderProducts: Links orders to products with quantities.

# How to Run the Project
Navigate to the backend directory in your terminal.

Start the Flask development server:

py server.py

Open your web browser and navigate to:

http://localhost:5000/

# Known Limitations

- No real payment processing (pre-populated card data is used for demonstration purposes).

- The project is not secure for production use (e.g., lacks HTTPS and robust authentication).

- Limited product management functionality.

# Future Improvements

- Add product search filters and pagination.

- Implement a fully functional admin panel for product and order management.

- Enhance the UI with responsive design.
