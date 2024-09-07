# Invoicelytics
> TBD TODO Add URL here

Invoicelytics is a product that is meant to make it much easier working with invoices. All you need to do is uploading invoices in PDF format into Invoicelytics. Once that's done, you can ask questions about the invoices, such as:
- how much have i spent in the last 30 days?
- how many invoices coming from company ABC have been uploaded?
- how much money is due to company ABC?

# Running the project locally
1. Make sure you have Python installed and Docker installed
2. Open a shell, browse to this repository's root folder and run `docker compose up-d`. This will spin up a local instance of Postgres.
3. Install [Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)
4. Run `poetry install`
5. Then run `poetry shell` to activate the environment 
6. Now let's initialize the database structure. Run `yoyo apply` and keep hitting `y` until all database migrations are applied to your local database.
7. Notice that the migration scripts already created an initial entry in the `tenants` table for you. Let's also add a user, as you'll need credentials to enter the app. Open the `scripts/insert_user.py` script, adjust it to your emails address and preferred password, and run it with `python3 scripts/insert_user.py`
8. Create a file called `.env` to hold the environment variables. Copy the values provided in `.env.example`. Make sure to create a folder called `/tmp/invoicelytics`.
9. Still on `.env`, you're gonna need to provide an `OPENAI_API_KEY`. You can follow [these instructions](https://platform.openai.com/docs/quickstart) to obtain an API key. 
10. Before running the app, you'll also need to set up an environment variable in the shell: `export FLASK_APP=invoicelytics/run.py`
11. To start the app, run `poetry run python -m flask run`. The app should be available at http://127.0.0.1:5000 or http://localhost:5000 .
12. Use the credentials you created earlier and voilà, you're ready to use the product!

# High level description of folders

# invoicelytics
This is the main application directory containing the core logic and functionality of the Invoicelytics project. It includes various submodules and components such as blueprints, services, repositories, and integrations.

- **assistants**: Contains modules related to assistant functionalities, such as data extraction and chat assistants.
- **blueprints**: Houses the Flask blueprints for different parts of the application, including authentication, chat, home, invoice, and health check routes.
- **data_structures**: Defines data structures used within the application, such as invoice data points and uploaded files.
- **entities**: Contains the domain entities and ORM models representing the database tables.
- **integrations**: Manages integrations with external services, such as OpenAI.
- **repository**: Implements the data access layer, providing repositories for various entities.
- **services**: Includes service classes that encapsulate business logic and operations.
- **static**: Contains static files like CSS, JavaScript, and images.
- **support**: Provides utility functions and helper classes used across the application.
- **templates**: Stores HTML templates for rendering the web pages.

# db-migrations
Contains SQL migration scripts for setting up and updating the database schema.

# static
Houses static assets such as CSS, JavaScript, and image files used in the web application.

# templates
Includes HTML templates used by Flask to render the web pages.
