# Contributing to AVID

Thanks for considering contributing to AVID! 🎉

---

## Getting Started

1. Fork & clone the AVID repo
2. Create a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # on Linux/Mac
   .venv\Scripts\activate      # on Windows
   ```
3. Go to the root of the AVID repo.
4. Install dependencies:

   ```bash
   pip install -e .[dev,rich] # on Linux/Windows
   pip install -e .[dev,rich,mac] # on Mac
   ```

---

## Development Workflow
### Development
1. Creat your feature branch
  ```bash
  git checkout -b feature/short-description
  ```
2. Make your code changes

Develop your idea or your bug fix in you're venv/repo clone.
If everything is ready, look for the next section to prepare your contribution for a pull request.
If you have ideas to improve, fix or somehow advance AVID, **please feel whole heartily invited and encouraged to
discuss the issues and ideas beforehand** over the GitHub issue section: https://github.com/MIC-DKFZ/AVID/issues  

### Pull request preparation
1. Format & lint your code before committing:

  ```bash
  black .
  isort .
  ```

2. Run tests:

  ```bash
  python -m unittest
  ```
Ensure that all tests are green. You may ignore skipped tests due to not available CLI tools as long as you change
does not impact those tools.

### Making a pull request (on GitHub)

1. Push your branch to your fork:
  ```bash
  git push origin feature/short-description
  ```
2. Go to your fork on GitHub and click Compare & pull request.
3. Include the following information:
   - A short, descriptive title
   - What changes you made 
   - Why these changes are necessary 
   - Any relevant issue numbers (e.g., Closes #42)
4. Ensure your branch passes CI checks:
   - All tests pass 
   - Black formatting applied

5. Request a review from maintainers if necessary. 
6. Once approved, a maintainer will merge your PR.
7. After merge, delete your feature branch locally and on your GitHub fork.


---

## Guidelines

- Follow [PEP8](https://peps.python.org/pep-0008/) coding style.
- Add tests for new features or bug fixes.
- Update documentation when you change public APIs.
- Keep commits small and meaningful.

---

## Reporting Issues

Please use the GitHub issue tracker for bugs and feature requests. Include:

- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (Python version, OS, etc.)

---

Happy hacking! 🚀
