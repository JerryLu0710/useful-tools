# Project Architecture and Development Guide

This document provides a comprehensive overview of the project's architecture, coding standards, and software design principles. It is intended to be a guide for developers contributing to this project.

## 1. Project Architecture

This project is designed as a monorepo containing a collection of standalone command-line utilities. The architecture emphasizes modularity, separation of concerns, and reusability.

### 1.1. High-Level Overview

The project is a collection of Python scripts, each providing a specific utility. While the utilities are independent, they share a common structure and core components for configuration and logging.

### 1.2. Modular Design

Each utility is a self-contained module located in its own directory (e.g., `chinese_converter/`, `anime1_downloader/`). This modular design offers several advantages:

- **Isolation:** Each utility can have its own dependencies, reducing the risk of conflicts.
- **Scalability:** It is easy to add new utilities without affecting existing ones.
- **Maintainability:** The code for each utility is organized in a single place, making it easier to understand and maintain.

### 1.3. Shared Components

To promote code reuse and consistency, the project includes the following shared components in the root directory:

- **`config.py`:** A centralized module for managing configuration. It loads settings from a `.env` file and provides them to the rest of the application.
- **`logger_setup.py`:** A module that provides a consistent logging setup for all utilities.

### 1.4. Dependency Management

Dependencies are managed in `pyproject.toml`. Each utility has its own optional dependency group, allowing for a lean installation tailored to the user's needs. For example, to install the dependencies for the `chinese_converter` utility, one would run:

```bash
uv pip install -e '.[chinese_converter]'
```

## 2. Coding Standards and Practices

We adhere to the following standards to ensure a high-quality and consistent codebase.

### 2.1. Code Style

- **Formatting:** We recommend using a code formatter like **Black** or **Ruff** to ensure a uniform code style across the project.
- **Naming Conventions:** We follow standard Python naming conventions:
    - `snake_case` for functions, methods, and variables.
    - `PascalCase` for classes.
    - `UPPER_SNAKE_CASE` for constants.

### 2.2. Typing

We use Python's type hints for all function signatures and variable declarations. This improves code clarity, helps prevent bugs, and enhances the developer experience with better static analysis and code completion.

### 2.3. Docstrings

All modules, classes, and functions should have clear and concise docstrings that explain their purpose, arguments, and return values. We follow the **Google Python Style Guide** for docstrings.

## 3. Software Design Principles

We strive to follow established software design principles to create a robust and maintainable codebase.

### 3.1. Open/Closed Principle

> Software entities (classes, modules, functions, etc.) should be open for extension, but closed for modification.

We apply this principle in several places. For example, in the `chinese_converter` utility, the `get_handler` function allows for the addition of new file formats (e.g., `.pdf`, `.docx`) by creating new handler classes without modifying the existing `convert_file` function.

### 3.2. Single Responsibility Principle (SRP)

> A class should have only one reason to change.

Each class and module in this project should have a single, well-defined responsibility. For example:

- `EPUBHandler` is solely responsible for handling EPUB files.
- `config.py` is solely responsible for managing configuration.

### 3.3. Don't Repeat Yourself (DRY)

We avoid code duplication by using shared modules for common functionalities like logging and configuration. When you find yourself writing the same code in multiple places, consider refactoring it into a shared function or class.

## 4. Development Workflow

This section provides a brief guide for contributing to the project.

1.  **Create a Branch:** Before you start working on a new feature or bug fix, create a new branch from the `main` branch.
2.  **Write Code:** Write your code, following the standards and principles outlined in this document.
3.  **Write Tests:** Add unit tests for your new code to ensure it works as expected and to prevent future regressions.
4.  **Update Documentation:** If you add a new feature or change the behavior of an existing one, update the relevant documentation (`README.md`, `GEMINI.md`, etc.).
5.  **Submit a Pull Request:** Once your work is complete, submit a pull request to the `main` branch. Provide a clear description of your changes and why they are needed.
