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
   ```
   
2. **Create & activate a clean virtual environment**
    ```bash
    python -m venv venv
    source venv/bin/activate    # macOS/Linux
    venv\Scripts\activate       # Windows
   ```

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt
   ```

4. **Configure environment**  

   - 4.1. Copy `.env.example` to `.env`:
    ```bash
    cp .env.example .env        # macOS/Linux
    copy .env.example .env      # Windows
    ```
    ```env
      DEBUG=True
      ALLOWED_HOSTS=localhost,127.0.0.1
      FIREBASE_CREDENTIALS=credentials/key.json
    ```
    and fill all variables 
   

   - 4.2 Place service Firebase key to credentials/key.json 
    

5. **Apply migrations**
    ```bash
    python manage.py migrate
    ```

6. **Run the dev server**
    ```bash
    python manage.py runserver
    ```
   
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

- All `.po`-files live in `locale/<lang>/LC_MESSAGES/`.  
- To extract new strings:
  ```
  django-admin makemessages -l <lang_code>
  python manage.py translate_messages --locale <lang_code> --untranslated   
  python manage.py compilemessages
  ```


---

## Contributing

- Fork the repo.
- Create branch: feature/your-feature.
- Commit your changes and open a pull request.

