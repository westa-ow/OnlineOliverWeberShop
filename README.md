# OnlineShop

A Django-based e-commerce service with multi-language support and core shop functionality.

---

## Table of Contents

- [Requirements](#requirements)  
- [Installation](#installation)  
- [Project Structure](#project-structure)  
- [Localization](#localization)  
- [Contributing](#contributing)  

[//]: # (- [License]&#40;#license&#41;  )

---

## Requirements

- Python 3.11+  
- pip  
- virtualenv or built-in venv  

---

## Installation

1. **Clone the repo**  
   ```bash
   git clone https://github.com/westa-ow/OnlineOliverWeberShop
   cd OnlineOliverWeberShop
   
2. **Create & activate a clean virtual environment**
    ```bash
    python -m venv .venv
    source .venv/bin/activate    # macOS/Linux
    .venv\Scripts\activate       # Windows

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt

4. **Configure environment variables**

    Copy .env file to 
    ```bash
    OnlineOliverWeberShop\OnlineShop\.env

5. **Add database key.json**

    Copy key.json file to 
    ```bash
    OnlineOliverWeberShop\credetionals\key.json

6. **Change variables in .env file to test mode**
    ```bash
    DEBUG=True
    ALLOWED_HOSTS=...,127.0.0.1
    FIREBASE_CREDENTIALS=/full/path/to/Project/credentials/key.json

7. **Apply migrations**
    ```bash
    python manage.py migrate

8. **Run the dev server**
    ```bash
    python manage.py runserver
   
---

## Project Structure
```text
.
├── manage.py
├── requirements.txt
├── OnlineShop/     — Django project settings & entry points
├── shop/           — main app (models, views, APIs, templates, static)
├── locale/         — translations (po/mo for de, es, fr, gb, it, ru)
└── docs/           — helper scripts & full tree (tree.py, project_tree.txt)
```

see [`docs/project_tree.txt`](docs/project_tree.txt) for full tree

---

## Localization


---

## Contributing

- Fork the repo.
- Create branch: feature/your-feature.
- Commit your changes and open a pull request.

