## ❤️ Sponsors

OpenAuto is free and open-source thanks to our supporters.  
Your sponsorship helps cover development time, hosting, and future features.  
[Become a Sponsor »](https://github.com/sponsors/winterautollc)

📖 [See the full roadmap →] (https://github.com/winterautollc/OpenAutoCore/wiki/Roadmap)

# OpenAuto

**OpenAuto** is a free and open-source automotive shop management system built using **Python**, **PyQt6**, and **MySQL**. It is designed to help independent auto repair shops manage customers, vehicles, invoices, appointments, and more — all from one modular interface.

---

## 🚀 Features

- Customer and vehicle management
- Estimate and invoice tracking
- Scheduling and appointment calendar
- Custom pricing matrix
- MySQL database backend
- Modular PyQt6 UI with dark theme support
- Soft-delete/archive system to preserve data
- Multithreaded real-time UI updates

---

## Project Structure

```bash
OpenAuto/
└── openauto
    ├── managers             -- manages ui files
    ├── old_files            -- ignore
    ├── repositories         -- connects to db for changes
    ├── subclassed_widgets   -- subclassed widgets like qtablewidgets
    ├── theme                -- ui files from designer, icons etc...
    ├── ui                   -- generated uic files and MainWindow class
    └── utils                -- validator.py

```

---

## 🧪 Installation

```bash
# Clone the repository
git clone https://github.com/winterautollc/OpenAutoCore.git
cd OpenAuto

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements_windows.txt # use this for Windows
```

---

## 🛠 MySQL Setup

You’ll need to create a MySQL database and update `.env` variables:

```env
MYSQL_HOST=localhost
MYSQL_USER=openautoadmin
MYSQL_PASSWORD=OpenAuto1!
MYSQL_NAME=openauto
```

Optionally use `mysql_clone.py` to copy table structures for testing.

---

## 🖥 Usage

```bash
python main.py
```

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.  
You are free to use, modify, and distribute it — but proprietary forks are **not** allowed.

---

## ❤️ Contributing

Contributions are welcome! If you're interested in helping:
- Fork the repo
- Open a pull request
- Suggest features or report issues

---

## 📬 Contact

If you're an automotive shop interested in trying OpenAuto, or a developer looking to contribute, reach out at:

**📧 winterautomotivellc@gmail.com**

![Screenshot from 2025-09-13 21-10-17.png](assets/images/Screenshot%20from%202025-09-13%2021-10-17.png)
![Screenshot from 2025-09-13 21-10-27.png](assets/images/Screenshot%20from%202025-09-13%2021-10-27.png)
![Screenshot from 2025-09-13 21-10-48.png](assets/images/Screenshot%20from%202025-09-13%2021-10-48.png)



## Multi-workshop demo work (experimental branch)

The `multi-shop-foundation` branch is developing a central API and tenant
isolation model. It is **not yet safe for multi-workshop deployment**: the
legacy Windows client still connects directly to MySQL, and business tables
have not yet been fully scoped by workshop. See
[`docs/central-api-foundation-status.md`](docs/central-api-foundation-status.md)
and [`docs/database-tenant-inventory.md`](docs/database-tenant-inventory.md).
