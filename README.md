# Farmacias El Sol

This repository contains a frontend clone of the Farmacias El Sol website, created using HTML and Tailwind CSS. The project replicates the main landing page and individual product category pages with a modern, responsive design.

## Features

- Responsive design using Tailwind CSS
- Main landing page with hero section and featured products
- Navigation menu with dropdown for product categories
- Individual pages for each product category displaying relevant products
- Consistent white, yellow, and blue color scheme
- Easy to extend and customize
- **User authentication and role-based access control (admin and user)**
- **Product management by admin (CRUD operations)**
- **User cart management with add/remove items**
- **Order processing: users can create orders from their cart, view order history**
- **Security middleware enforcing HTTPS and security headers**

## Project Structure

- `index.html`: Main landing page
- `dermocosmetica.html`, `medicamentos.html`, etc.: Individual category pages
- Backend Python files:
  - `user_system.py`: User authentication, product management, cart, and order processing APIs
  - `discount_service.py`: Discount code application API
  - `security_middleware.py`: Security headers and HTTPS enforcement middleware
- All pages include navigation and footer for consistent user experience
- `assets/`: Images and logos

## How to Run

### Frontend

Serve the frontend files using a simple HTTP server, for example:

```bash
python3 -m http.server 8000
```

Open your browser and navigate to:

```
http://localhost:8000
```

The frontend includes additional pages for cart and checkout to support the complete purchase flow.

### Backend

Run the Flask backend services:

```bash
python3 user_system.py
python3 discount_service.py
```

The backend provides APIs for user authentication, product management, cart, order processing, and discount application.

## Notes

- This project includes both frontend and backend components.
- Product images are placeholders and can be replaced with real images.
- The order processing feature allows users to create orders from their cart and view order history.
- Security best practices are implemented via middleware.
- This project is for demonstration purposes.

## License

This project is for demonstration purposes.

---

Created by Fefox-glitch
