# agentic-workflows

Agentic chatbots for learning purpose.

## Setup

1. **Clone the repository**
   ```sh
   git clone https://github.com/yourusername/agentic-workflows.git
   cd agentic-workflows
   ```

2. **Set up Python (recommended version: 3.13)**
   - You can use [pyenv](https://github.com/pyenv/pyenv) or your preferred method.

3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```
   Or, if using [uv](https://github.com/astral-sh/uv):
   ```sh
   uv pip install -r uv.lock
   ```

   Alternatively, install from `pyproject.toml`:
   ```sh
   pip install .
   ```

4. **Run the main script**
   ```sh
   python main.py
   ```

5. **Start Jupyter Notebook**
   ```sh
   jupyter notebook notebook_workouts/sample.ipynb
   ```

## Development

For development dependencies:
```sh
pip install ipykernel
```

## Project Structure

- `main.py` — Entry point
- `notebook_workouts/` — Example notebooks
- `pyproject.toml` — Project metadata and dependencies

## License

MIT License