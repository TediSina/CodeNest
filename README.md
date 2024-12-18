# CodeNest

CodeNest is a programming-themed forum website powered by Django, showdown.js and highlight.js.

## Description

CodeNest is a vibrant, programming-themed forum website designed to bring developers together to share knowledge, discuss programming concepts, and showcase their coding projects. Built using Django for the backend, it leverages showdown.js to render Markdown-based content into HTML and highlight.js for syntax highlighting of code snippets, ensuring that discussions are both dynamic and visually engaging.

Whether you're a beginner seeking advice or an experienced developer contributing solutions, CodeNest provides a collaborative platform for all programming enthusiasts.

### Key Features

- **Markdown Support**: Post and comment using Markdown, powered by showdown.js for seamless conversion to HTML.
- **Syntax Highlighting**: Enjoy beautifully formatted code with highlight.js, supporting a wide range of programming languages.
- **User Authentication**: Securely register, log in, and manage your profile as part of the community.
- **Responsive Design**: Accessible on any device, providing an intuitive interface for discussions on the go.

## How to Run the Development Server

To set up and run the development server, follow these steps:

1. **Clone the Repository**

    ```bash
    git clone https://github.com/TediSina/CodeNest.git
    cd ammaf
    ```

2. **(Optional) Create a Virtual Environment**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Run Migrations**

    ```bash
    python manage.py migrate
    ```

5. **Set the Secret Key in the Configuration File**

    Create a `.env` file in the root directory of the repository.

    Add the following line to the file:

    ```env
    SECRET_KEY="enter_a_random_secret_key_here"
    ```

    Replace `enter_a_random_secret_key_here` with a strong, unique secret key.

6. **Start the Django Development Server**

    In another terminal, run:

    ```bash
    python manage.py runserver
    ```

7. **Access the Website**

    Open your web browser and navigate to `http://127.0.0.1:8000` to view the website.

## Notes

- Ensure you have Python and Django installed on your system.
- Any additional configurations or environment variables required for development should be specified in the `.env` file.

## License

MIT License

Copyright (c) 2024 Tedi Sina

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
