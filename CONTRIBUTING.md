# Contributing to TimeCraft

Thank you for your interest in contributing to TimeCraft! We welcome contributions from everyone and appreciate your efforts to improve this project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [How to Contribute](#how-to-contribute)
4. [Development Setup](#development-setup)
5. [Coding Standards](#coding-standards)
6. [Testing](#testing)
7. [Submitting Changes](#submitting-changes)
8. [Issue Reporting](#issue-reporting)
9. [Feature Requests](#feature-requests)
10. [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment
4. Create a new branch for your changes
5. Make your changes
6. Test your changes
7. Submit a pull request

## How to Contribute

There are many ways to contribute to TimeCraft:

- **Bug Reports**: Help us identify and fix bugs
- **Feature Requests**: Suggest new features or improvements
- **Code Contributions**: Submit bug fixes, new features, or improvements
- **Documentation**: Improve or expand our documentation
- **Testing**: Help test new features and report issues
- **Community Support**: Help other users in discussions and issues

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git

### Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/rafa-mori/timecraft.git
   cd timecraft
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-ai.txt  # For AI features
   ```

4. **Install development dependencies**:
   ```bash
   pip install pytest pytest-cov black flake8 mypy
   ```

5. **Verify installation**:
   ```bash
   python -m timecraft --help
   ```

## Coding Standards

### Python Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use [Black](https://black.readthedocs.io/) for code formatting
- Maximum line length: 88 characters (Black default)
- Use type hints where appropriate

### Code Formatting

Before submitting code, please run:

```bash
# Format code with Black
black src/ examples/ tests/

# Check code style with flake8
flake8 src/ examples/ tests/

# Type checking with mypy
mypy src/
```

### Documentation

- Write clear and concise docstrings for all functions, classes, and modules
- Follow [Google style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Update documentation when adding new features

### Commit Messages

Write clear and descriptive commit messages:

```
type(scope): description

body (optional)

footer (optional)
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```
feat(models): add LSTM model support

- Add LSTM implementation for time series forecasting
- Include model validation and parameter tuning
- Update documentation with usage examples

Closes #123
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_models.py

# Run tests with verbose output
pytest -v
```

### Writing Tests

- Write unit tests for all new functions and classes
- Aim for high test coverage (>80%)
- Use descriptive test names that explain what is being tested
- Include both positive and negative test cases

### Test Structure

```python
def test_function_name_should_return_expected_result():
    # Arrange
    input_data = ...
    expected_result = ...
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_result
```

## Submitting Changes

### Pull Request Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards

3. **Add tests** for your changes

4. **Run the test suite** to ensure all tests pass

5. **Commit your changes** with descriptive commit messages

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** from your fork to the main repository

### Pull Request Guidelines

- Provide a clear description of the changes
- Reference any related issues
- Include screenshots for UI changes
- Ensure all tests pass
- Update documentation if necessary
- Keep pull requests focused and atomic

### Pull Request Template

When creating a pull request, please include:

- **Description**: What does this PR do?
- **Type of Change**: Bug fix, new feature, documentation, etc.
- **Testing**: How has this been tested?
- **Checklist**: Have you followed the contribution guidelines?

## Issue Reporting

### Before Submitting an Issue

1. Check if the issue already exists in our [issue tracker](https://github.com/rafa-mori/timecraft/issues)
2. Try to reproduce the issue with the latest version
3. Gather relevant information (OS, Python version, TimeCraft version, etc.)

### Bug Reports

Please include:
- Clear description of the bug
- Steps to reproduce
- Expected vs. actual behavior
- Environment details (OS, Python version, etc.)
- Error messages or logs
- Minimal code example if applicable

### Use our bug report template

When reporting bugs, please use our [bug report template](.github/ISSUE_TEMPLATE/bug_report.md).

## Feature Requests

We welcome feature requests! Please:

1. Check if the feature already exists or is planned
2. Use our [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)
3. Provide clear use cases and examples
4. Explain why this feature would be valuable

## Community

### Getting Help

- **GitHub Discussions**: Ask questions and discuss ideas
- **Issues**: Report bugs and request features
- **Documentation**: Check our [documentation](https://rafa-mori.github.io/timecraft/)

### Communication Guidelines

- Be respectful and constructive
- Help others when possible
- Follow our Code of Conduct
- Use clear and descriptive titles for issues and discussions

## Recognition

Contributors will be recognized in:
- The project's README
- Release notes for significant contributions
- GitHub's contributor graph

## License

By contributing to TimeCraft, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---

Thank you for contributing to TimeCraft! Your efforts help make this project better for everyone.
