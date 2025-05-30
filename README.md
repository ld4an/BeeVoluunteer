# 🐝 BeeVolunteer

**BeeVolunteer** is a Django-based web application designed to manage volunteering events and applications. The platform allows event organizers to post events and manage applications, while volunteers can browse active events and apply directly.

---

## 🚀 Features

- 🧑‍💼 **Organizer Dashboard**: Create, edit, and manage events.
- 🧑‍🤝‍🧑 **Volunteer Portal**: Browse active events and apply.
- 📬 **Application Tracking**: Organizers can accept/reject volunteer applications.
- ✅ **Status Updates**: Volunteers can see whether they have been accepted or not.
- 🔐 **JWT Authentication**: Secure login and registration for users.

---

## 📦 Tech Stack

- **Backend**: Python, Django REST Framework  
- **Frontend**: Django templates (HTML/CSS/JS) *(optional Angular integration planned)*  
- **Database**: Microsoft SQL Server

---

## 🛠️ Setup Instructions

1. **Clone the repository**

    ```bash
    git clone https://github.com/ld4an/BeeVoluunteer.git
    cd BeeVoluunteer
    ```

2. **Create a virtual environment and activate it**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Apply migrations**

    ```bash
    python manage.py migrate
    ```

5. **Run the development server**

    ```bash
    python manage.py runserver
    ```

6. **Access the app**  
    Open your browser and go to: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
---
## ✅ TODO

- [x] Event creation and volunteer application  
- [x] Application acceptance/rejection system  
- [ ] User profile pages  
- [ ] Email notifications  
- [ ] Angular frontend integration  

---

## 🤝 Contributing

Pull requests are welcome! If you have ideas or bug fixes, feel free to fork the repo and submit a PR.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
