# Ecommerce_site_py_project
Navira is a Django-based mini e-commerce web app built as a learning project. It showcases core full-stack concepts like backend logic, user authentication, and modern UI design, combining functionality with a clean, responsive interface and enhanced visuals for a smooth user experience.
# 🌸 Navira – Django E-Commerce Project

Navira is a mini e-commerce web application built using Django as part of a learning project. It demonstrates core full-stack development concepts such as backend logic, user authentication, and UI design.

This project focuses on combining functionality with aesthetics, featuring a clean, responsive interface with enhanced visuals and smooth user experience.

---

## ✨ Features

- 🛍️ Product listing and detail view  
- 🔐 User authentication (Login / Signup / Logout)  
- 🛒 Shopping cart functionality  
- 📦 Order summary (simulated checkout)  
- 🔍 Basic product search  
- 🎨 Enhanced UI with modern styling and animations  
- 📱 Responsive design  
- 🧑‍💼 Admin panel for managing products and orders  

---

## 💻 Tech Stack

- **Frontend:** HTML, CSS, Bootstrap / Tailwind  
- **Backend:** Django (Python)  
- **Database:** SQLite  

---

## 📂 Project Structure

```
ecommerce/
│── ecommerce/        # Main project settings
│   │── settings.py
│   │── urls.py
│
│── store/            # Main application
│   │── migrations/
│   │── templates/
│   │── static/
│   │── models.py
│   │── views.py
│   │── urls.py
│
│── manage.py         # Django command-line utility
```

---

## 🚀 How to Run Locally

1. Clone the repository:
```
git clone https://github.com/your-username/navira.git
cd navira
```

2. Create a virtual environment:
```
python -m venv env
```

3. Activate the environment:
```
env\Scripts\activate   # Windows
# OR
source env/bin/activate   # Mac/Linux
```

4. Install dependencies:
```
pip install django
```

5. Run migrations:
```
python manage.py makemigrations
python manage.py migrate
```

6. Create superuser (optional):
```
python manage.py createsuperuser
```

7. Start the development server:
```
python manage.py runserver
```

8. Open in browser:
```
http://127.0.0.1:8000/
```

---

## ⚠️ Note

This is a **learning-based project** and does not include real payment integration or live transactions.

---

## 🎯 Learning Outcomes

- Understanding Django project structure and workflow  
- Implementing authentication systems  
- Building cart and order functionality  
- Managing data using Django ORM  
- Improving frontend UI/UX design  

---

## 🚀 Future Improvements

- 💳 Payment gateway integration (Razorpay/Stripe)  
- 🏷️ Product categories and filters  
- ❤️ Wishlist feature  
- 📊 Admin dashboard improvements  
- 🌐 Deployment (Render / Railway)
